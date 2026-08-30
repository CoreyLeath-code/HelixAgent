"""Budgeted plan/execute/observe/critique/replan autonomous control loop."""

from __future__ import annotations

from agent.autonomy.models import (
    AgentRun,
    ApprovalRequest,
    GoalSpec,
    RiskLevel,
    RunStatus,
    Task,
    TaskStatus,
)
from agent.autonomy.planning import Planner, RuleBasedPlanner
from agent.autonomy.store import SQLiteRunStore
from agent.autonomy.tools import ToolRegistry, ToolSpec
from agent.telemetry.events import AgentEvent, EventType
from agent.telemetry.firehose import build_event_sink_from_env
from agent.telemetry.sink import EventSink


class AutonomousRuntime:
    def __init__(
        self,
        *,
        planner: Planner | None = None,
        registry: ToolRegistry | None = None,
        store: SQLiteRunStore | None = None,
        event_sink: EventSink | None = None,
    ) -> None:
        self.planner = planner or RuleBasedPlanner()
        self.registry = registry or self._default_registry()
        self.store = store or SQLiteRunStore()
        self.event_sink = event_sink or build_event_sink_from_env()

    @staticmethod
    def _default_registry() -> ToolRegistry:
        from agent.agent_core import cosine_sim
        from agent.tools.web_search import search_and_summarize

        registry = ToolRegistry()
        registry.register(
            ToolSpec(
                name="web_search",
                description="Search public web results",
                handler=lambda args: search_and_summarize(
                    str(args["query"]), int(args.get("max_results", 5))
                ),
                timeout_seconds=20,
            )
        )
        registry.register(
            ToolSpec(
                name="vector_similarity",
                description="Calculate cosine similarity",
                handler=lambda args: cosine_sim(args["left"], args["right"]),
            )
        )
        registry.register(
            ToolSpec(
                name="synthesize",
                description="Produce a deterministic evidence summary",
                handler=lambda args: "Goal: "
                + str(args["goal"])
                + "\nEvidence:\n"
                + "\n".join(str(item) for item in args.get("observations", [])),
            )
        )
        return registry

    def _emit(
        self,
        event_type: EventType,
        run: AgentRun,
        *,
        task: Task | None = None,
        risk: RiskLevel | None = None,
        duration_ms: float | None = None,
        plan_size: int | None = None,
    ) -> None:
        event = AgentEvent(
            event_type=event_type,
            run_id=run.id,
            status=run.status,
            task_id=task.id if task else None,
            tool=task.tool if task else None,
            risk=risk if risk is not None else (task.risk if task else None),
            attempt=task.attempts if task else None,
            iteration=run.iterations,
            tool_calls=run.tool_calls,
            plan_size=plan_size,
            duration_ms=duration_ms,
        )
        try:
            self.event_sink.emit(event)
        except Exception:  # noqa: BLE001 - telemetry cannot change runtime correctness
            return

    def submit(
        self, objective: str, *, max_iterations: int = 12, tool_budget: int = 10
    ) -> AgentRun:
        run = AgentRun(
            goal=GoalSpec(objective=objective),
            max_iterations=max_iterations,
            tool_budget=tool_budget,
        )
        run.plan = self.planner.create_plan(run.goal)
        self.store.save(run)
        self._emit(EventType.RUN_SUBMITTED, run)
        self._emit(EventType.PLAN_CREATED, run, plan_size=len(run.plan))
        return run

    def run(self, run_id: str) -> AgentRun:
        run = self.store.get(run_id)
        if run.status in (RunStatus.COMPLETED, RunStatus.FAILED):
            return run

        run.status = RunStatus.RUNNING
        self.store.save(run)
        self._emit(EventType.RUN_STARTED, run)

        while run.current_task < len(run.plan):
            if run.iterations >= run.max_iterations or run.tool_calls >= run.tool_budget:
                run.status = RunStatus.FAILED
                run.error = "Autonomy budget exhausted before the goal was satisfied"
                self.store.save(run)
                self._emit(EventType.RUN_BUDGET_EXHAUSTED, run)
                self._emit(EventType.RUN_FAILED, run)
                return run

            task = run.plan[run.current_task]
            try:
                spec = self.registry.get(task.tool)
            except KeyError as exc:
                run.status = RunStatus.FAILED
                run.error = str(exc)
                self.store.save(run)
                self._emit(EventType.RUN_FAILED, run, task=task)
                return run
            if spec.risk != RiskLevel.READ_ONLY and not self._is_approved(run, task.id):
                created_request = False
                if not any(item.task_id == task.id for item in run.approvals):
                    run.approvals.append(
                        ApprovalRequest(
                            task_id=task.id,
                            tool=task.tool,
                            risk=spec.risk,
                            reason=f"{task.tool} can modify external state",
                        )
                    )
                    created_request = True
                run.status = RunStatus.WAITING_APPROVAL
                self.store.save(run)
                if created_request:
                    self._emit(EventType.APPROVAL_REQUESTED, run, task=task, risk=spec.risk)
                return run

            task.status = TaskStatus.RUNNING
            task.attempts += 1
            run.iterations += 1
            run.tool_calls += 1
            self._emit(EventType.TASK_STARTED, run, task=task, risk=spec.risk)
            if task.tool == "synthesize":
                task.arguments["observations"] = [
                    item.output for item in run.observations if item.success
                ]
            observation = self.registry.execute(task)
            run.observations.append(observation)

            if observation.success:
                task.status = TaskStatus.COMPLETED
                run.current_task += 1
                self.store.save(run)
                self._emit(
                    EventType.TASK_COMPLETED,
                    run,
                    task=task,
                    risk=spec.risk,
                    duration_ms=observation.duration_ms,
                )
            elif task.attempts < task.max_attempts:
                task.status = TaskStatus.PENDING
                run.plan = self.planner.replan(run, task)
                self.store.save(run)
                self._emit(
                    EventType.TASK_RETRY,
                    run,
                    task=task,
                    risk=spec.risk,
                    duration_ms=observation.duration_ms,
                )
            else:
                task.status = TaskStatus.FAILED
                run.status = RunStatus.FAILED
                run.error = observation.error
                self.store.save(run)
                self._emit(
                    EventType.TASK_FAILED,
                    run,
                    task=task,
                    risk=spec.risk,
                    duration_ms=observation.duration_ms,
                )
                self._emit(EventType.RUN_FAILED, run, task=task, risk=spec.risk)
                return run

        run.status = RunStatus.COMPLETED
        successful = [str(item.output) for item in run.observations if item.success]
        run.final_output = "\n".join(successful)
        self.store.save(run)
        self._emit(EventType.RUN_COMPLETED, run)
        return run

    def approve(self, run_id: str, task_id: str, approved: bool) -> AgentRun:
        run = self.store.get(run_id)
        request = next((item for item in run.approvals if item.task_id == task_id), None)
        if request is None:
            raise KeyError(f"No approval request for task {task_id}")
        request.approved = approved
        task = next((item for item in run.plan if item.id == task_id), None)
        if not approved:
            run.status = RunStatus.FAILED
            run.error = f"Approval denied for {request.tool}"
        else:
            run.status = RunStatus.PENDING
        self.store.save(run)
        self._emit(
            EventType.APPROVAL_APPROVED if approved else EventType.APPROVAL_DENIED,
            run,
            task=task,
            risk=request.risk,
        )
        if not approved:
            self._emit(EventType.RUN_FAILED, run, task=task, risk=request.risk)
        return run

    @staticmethod
    def _is_approved(run: AgentRun, task_id: str) -> bool:
        return any(item.task_id == task_id and item.approved is True for item in run.approvals)
