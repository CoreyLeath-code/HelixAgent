"""Tests for redacted, fail-open agent event telemetry."""

from __future__ import annotations

import json

import pytest

from agent.autonomy.models import GoalSpec, RiskLevel, Task
from agent.autonomy.runtime import AutonomousRuntime
from agent.autonomy.store import SQLiteRunStore
from agent.autonomy.tools import ToolRegistry, ToolSpec
from agent.telemetry.events import AgentEvent, EventType
from agent.telemetry.firehose import FirehoseEventSink, build_event_sink_from_env
from agent.telemetry.sink import NullEventSink


class FakeFirehoseClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def put_record_batch(self, **kwargs):
        self.calls.append(kwargs)
        return {"FailedPutCount": 0, "RequestResponses": [{} for _ in kwargs["Records"]]}


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[AgentEvent] = []

    def emit(self, event: AgentEvent) -> None:
        self.events.append(event)

    def close(self, timeout: float = 5.0) -> None:
        del timeout


class OneTaskPlanner:
    def create_plan(self, goal: GoalSpec) -> list[Task]:
        del goal
        return [Task(objective="Echo", tool="echo", arguments={"value": "sensitive-result"})]

    def replan(self, run, failed):
        del failed
        return run.plan


class ApprovalPlanner:
    def create_plan(self, goal: GoalSpec) -> list[Task]:
        del goal
        return [Task(objective="Write", tool="write")]

    def replan(self, run, failed):
        del failed
        return run.plan


def test_event_sink_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("HELIXAGENT_EVENT_SINK", raising=False)
    assert isinstance(build_event_sink_from_env(), NullEventSink)


def test_firehose_mode_requires_stream_name(monkeypatch) -> None:
    monkeypatch.setenv("HELIXAGENT_EVENT_SINK", "firehose")
    monkeypatch.delenv("HELIXAGENT_FIREHOSE_STREAM", raising=False)
    with pytest.raises(ValueError, match="HELIXAGENT_FIREHOSE_STREAM"):
        build_event_sink_from_env()


def test_firehose_batches_newline_delimited_json() -> None:
    client = FakeFirehoseClient()
    sink = FirehoseEventSink(
        "helixagent-events",
        client=client,
        batch_size=2,
        flush_interval_seconds=60.0,
    )
    sink.emit(AgentEvent(event_type=EventType.RUN_SUBMITTED, run_id="run-1"))
    sink.emit(AgentEvent(event_type=EventType.RUN_STARTED, run_id="run-1"))
    sink.close()

    assert len(client.calls) == 1
    assert client.calls[0]["DeliveryStreamName"] == "helixagent-events"
    records = client.calls[0]["Records"]
    assert len(records) == 2
    assert all(record["Data"].endswith(b"\n") for record in records)
    decoded = json.loads(records[0]["Data"].decode("utf-8"))
    assert decoded["schema_version"] == "1.0"
    assert decoded["event_type"] == "run.submitted"
    assert decoded["run_id"] == "run-1"


def test_runtime_emits_allowlisted_events_without_payload_content() -> None:
    registry = ToolRegistry()
    registry.register(ToolSpec("echo", lambda args: args["value"], "Echo"))
    sink = RecordingSink()
    runtime = AutonomousRuntime(
        planner=OneTaskPlanner(),
        registry=registry,
        store=SQLiteRunStore(":memory:"),
        event_sink=sink,
    )

    submitted = runtime.submit("sensitive objective")
    completed = runtime.run(submitted.id)

    assert completed.final_output == "sensitive-result"
    event_types = [event.event_type for event in sink.events]
    assert EventType.RUN_SUBMITTED in event_types
    assert EventType.PLAN_CREATED in event_types
    assert EventType.TASK_STARTED in event_types
    assert EventType.TASK_COMPLETED in event_types
    assert EventType.RUN_COMPLETED in event_types

    serialized = json.dumps([event.model_dump(mode="json") for event in sink.events])
    assert "sensitive objective" not in serialized
    assert "sensitive-result" not in serialized
    assert '"arguments"' not in serialized
    assert '"final_output"' not in serialized


def test_approved_run_emits_started_once_then_resumed() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("write", lambda args: "written", "Write", risk=RiskLevel.WRITE)
    )
    sink = RecordingSink()
    runtime = AutonomousRuntime(
        planner=ApprovalPlanner(),
        registry=registry,
        store=SQLiteRunStore(":memory:"),
        event_sink=sink,
    )

    submitted = runtime.submit("write something")
    paused = runtime.run(submitted.id)
    runtime.approve(paused.id, paused.plan[0].id, True)
    runtime.run(paused.id)

    event_types = [event.event_type for event in sink.events]
    assert event_types.count(EventType.RUN_STARTED) == 1
    assert event_types.count(EventType.RUN_RESUMED) == 1
