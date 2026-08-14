"""Adversarial contracts for runtime terminality and vector semantics."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from agent import agent_core
from agent.autonomy.models import GoalSpec, RunStatus, Task
from agent.autonomy.runtime import AutonomousRuntime
from agent.autonomy.store import SQLiteRunStore
from agent.autonomy.tools import ToolRegistry, ToolSpec


class StaticPlanner:
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks

    def create_plan(self, _goal: GoalSpec) -> list[Task]:
        return [task.model_copy(deep=True) for task in self.tasks]

    def replan(self, run, _failed):
        return run.plan


def make_runtime(tmp_path: Path, tasks: list[Task], registry: ToolRegistry) -> AutonomousRuntime:
    return AutonomousRuntime(
        planner=StaticPlanner(tasks),
        registry=registry,
        store=SQLiteRunStore(tmp_path / "invariants.db"),
    )


def test_completed_run_is_not_executed_twice(tmp_path: Path) -> None:
    calls: list[str] = []
    registry = ToolRegistry()
    registry.register(
        ToolSpec("once", lambda _arguments: calls.append("executed") or "done", "One call")
    )
    runtime = make_runtime(tmp_path, [Task(objective="Run once", tool="once")], registry)

    submitted = runtime.submit("Run one task")
    first = runtime.run(submitted.id)
    second = runtime.run(submitted.id)

    assert first.status is RunStatus.COMPLETED
    assert second.status is RunStatus.COMPLETED
    assert calls == ["executed"]
    assert second.tool_calls == 1


def test_unknown_planned_tool_fails_and_persists(tmp_path: Path) -> None:
    runtime = make_runtime(
        tmp_path,
        [Task(objective="Unknown", tool="missing_tool")],
        ToolRegistry(),
    )

    completed = runtime.run(runtime.submit("Exercise failure boundary").id)
    restored = runtime.store.get(completed.id)

    assert completed.status is RunStatus.FAILED
    assert "Unknown tool" in completed.error
    assert restored.status is RunStatus.FAILED
    assert restored.tool_calls == 0


def test_python_vector_fallback_defines_zero_and_dimension_behavior(monkeypatch) -> None:
    monkeypatch.setattr(agent_core, "_lib_vec", None)

    assert agent_core.cosine_sim([0.0, 0.0], [1.0, -1.0]) == 0.0
    with pytest.raises(ValueError, match="equal dimensions"):
        agent_core.cosine_sim([1.0], [1.0, 2.0])


@st.composite
def nonzero_vector_pairs(draw):
    dimension = draw(st.integers(min_value=1, max_value=12))
    values = st.floats(
        min_value=-1_000_000,
        max_value=1_000_000,
        allow_nan=False,
        allow_infinity=False,
    )
    left = draw(st.lists(values, min_size=dimension, max_size=dimension))
    right = draw(st.lists(values, min_size=dimension, max_size=dimension))
    if not any(left):
        left[0] = 1.0
    if not any(right):
        right[0] = -1.0
    return left, right


@given(nonzero_vector_pairs())
def test_python_cosine_fallback_satisfies_basic_properties(monkeypatch, pair) -> None:
    monkeypatch.setattr(agent_core, "_lib_vec", None)
    left, right = pair

    score = agent_core.cosine_sim(left, right)
    reverse = agent_core.cosine_sim(right, left)
    self_score = agent_core.cosine_sim(left, left)

    assert -1.0 - 1e-12 <= score <= 1.0 + 1e-12
    assert math.isclose(score, reverse, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(self_score, 1.0, rel_tol=1e-12, abs_tol=1e-12)
