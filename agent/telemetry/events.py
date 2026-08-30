"""Allowlisted agent lifecycle events for durable telemetry export."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from agent.autonomy.models import RiskLevel, RunStatus, utc_now


class EventType(str, Enum):
    RUN_SUBMITTED = "run.submitted"
    RUN_STARTED = "run.started"
    RUN_RESUMED = "run.resumed"
    PLAN_CREATED = "plan.created"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_RETRY = "task.retry"
    TASK_FAILED = "task.failed"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_DENIED = "approval.denied"
    RUN_BUDGET_EXHAUSTED = "run.budget_exhausted"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"


class AgentEvent(BaseModel):
    """Redacted operational metadata safe for the optional cloud event lake.

    Raw objectives, tool arguments, observation outputs, approval reasons, and
    final outputs are intentionally excluded from this schema.
    """

    schema_version: Literal["1.0"] = "1.0"
    event_type: EventType
    run_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    status: RunStatus | None = None
    task_id: str | None = None
    tool: str | None = None
    risk: RiskLevel | None = None
    attempt: int | None = None
    iteration: int | None = None
    tool_calls: int | None = None
    plan_size: int | None = None
    duration_ms: float | None = None
