"""Behavioral tests for the durable, governed autonomous control loop."""

import time
from pathlib import Path

from agent.autonomy.models import GoalSpec, RiskLevel, RunStatus, Task
from agent.autonomy.runtime import AutonomousRuntime
from agent.autonomy.store import SQLiteRunStore
from agent.autonomy.tools import ToolRegistry, ToolSpec


class StaticPlanner:
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks

    def create_plan(self, goal: GoalSpec) -> list[Task]:
        return [task.model_copy(deep=True) for task in self.tasks]

    def replan(self, run, failed):
        return run.plan


def runtime_for(tmp_path: Path, tasks: list[Task], registry: ToolRegistry) -> AutonomousRuntime:
    return AutonomousRuntime(
        planner=StaticPlanner(tasks),
        registry=registry,
        store=SQLiteRunStore(tmp_path / "runs.db"),
    )


def test_run_completes_and_persists_observation(tmp_path: Path) -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("echo", lambda args: args["value"], "Echo a value"))
    runtime = runtime_for(
        tmp_path,
        [Task(objective="Echo", tool="echo", arguments={"value": "evidence"})],
        registry,
    )

    submitted = runtime.submit("Produce evidence")
    completed = runtime.run(submitted.id)
    restored = runtime.store.get(submitted.id)

    assert completed.status == RunStatus.COMPLETED
    assert completed.final_output == "evidence"
    assert restored.observations[0].output == "evidence"


def test_write_tool_pauses_until_explicit_approval(tmp_path: Path) -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("write", lambda args: "written", "Write data", risk=RiskLevel.WRITE)
    )
    runtime = runtime_for(tmp_path, [Task(objective="Write", tool="write")], registry)

    submitted = runtime.submit("Write an artifact")
    paused = runtime.run(submitted.id)
    assert paused.status == RunStatus.WAITING_APPROVAL
    assert paused.tool_calls == 0

    runtime.approve(paused.id, paused.plan[0].id, True)
    completed = runtime.run(paused.id)
    assert completed.status == RunStatus.COMPLETED


def test_denied_approval_fails_without_tool_execution(tmp_path: Path) -> None:
    calls: list[str] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "write",
            lambda args: calls.append("called"),
            "Write data",
            risk=RiskLevel.WRITE,
        )
    )
    runtime = runtime_for(tmp_path, [Task(objective="Write", tool="write")], registry)
    paused = runtime.run(runtime.submit("Write").id)

    denied = runtime.approve(paused.id, paused.plan[0].id, False)
    assert denied.status == RunStatus.FAILED
    assert calls == []


def test_tool_budget_stops_run_safely(tmp_path: Path) -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("echo", lambda args: "ok", "Echo"))
    tasks = [Task(objective="One", tool="echo"), Task(objective="Two", tool="echo")]
    runtime = runtime_for(tmp_path, tasks, registry)

    completed = runtime.run(runtime.submit("Two steps", tool_budget=1).id)

    assert completed.status == RunStatus.FAILED
    assert "budget exhausted" in completed.error
    assert completed.tool_calls == 1


def test_failed_tool_retries_then_fails(tmp_path: Path) -> None:
    attempts = 0

    def fail(_args):
        nonlocal attempts
        attempts += 1
        raise RuntimeError("unavailable")

    registry = ToolRegistry()
    registry.register(ToolSpec("unstable", fail, "Always fails"))
    runtime = runtime_for(tmp_path, [Task(objective="Try", tool="unstable")], registry)

    completed = runtime.run(runtime.submit("Try safely").id)

    assert completed.status == RunStatus.FAILED
    assert attempts == 2
    assert "unavailable" in completed.error


def test_tool_timeout_returns_without_waiting_for_handler() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            "slow",
            lambda _args: time.sleep(0.5),
            "Slow operation",
            timeout_seconds=0.01,
        )
    )

    started = time.perf_counter()
    observation = registry.execute(Task(objective="Bound execution", tool="slow"))

    assert observation.success is False
    assert "timed out" in observation.error
    assert time.perf_counter() - started < 0.25
