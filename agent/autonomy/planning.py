"""Pluggable planning and critique policies.

The protocol accepts a model-backed implementation without coupling the runtime
to one provider. The deterministic policy remains available for tests and for
deployments without model credentials.
"""

from __future__ import annotations

from typing import Protocol

from agent.autonomy.models import AgentRun, GoalSpec, RiskLevel, Task, TaskStatus


class Planner(Protocol):
    def create_plan(self, goal: GoalSpec) -> list[Task]: ...

    def replan(self, run: AgentRun, failed: Task) -> list[Task]: ...


class RuleBasedPlanner:
    """Safe baseline planner used when no model-backed planner is injected."""

    def create_plan(self, goal: GoalSpec) -> list[Task]:
        objective = goal.objective
        lower = objective.lower()
        tasks: list[Task] = []
        if "search" in lower or "research" in lower or "web" in lower:
            tasks.append(
                Task(
                    objective="Collect relevant public evidence",
                    tool="web_search",
                    arguments={"query": objective, "max_results": 5},
                    expected_output="A sourced list of relevant search results",
                )
            )
        if "vector" in lower or "similarity" in lower:
            tasks.append(
                Task(
                    objective="Calculate the requested vector comparison",
                    tool="vector_similarity",
                    arguments={"left": [1, 0, 1], "right": [0.5, 0, 0.5]},
                    expected_output="A cosine-similarity score",
                )
            )
        tasks.append(
            Task(
                objective="Synthesize observations against the goal",
                tool="synthesize",
                arguments={"goal": objective},
                expected_output="A concise result grounded in prior observations",
                risk=RiskLevel.READ_ONLY,
            )
        )
        return tasks

    def replan(self, run: AgentRun, failed: Task) -> list[Task]:
        if failed.attempts < failed.max_attempts:
            failed.status = TaskStatus.PENDING
            return run.plan
        return run.plan
