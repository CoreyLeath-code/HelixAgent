"""Typed contracts shared by planning, execution, persistence, and the API."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskLevel(str, Enum):
    READ_ONLY = "read_only"
    WRITE = "write"
    DESTRUCTIVE = "destructive"


class GoalSpec(BaseModel):
    objective: str = Field(min_length=1, max_length=4_000)
    success_criteria: list[str] = Field(default_factory=list)


class Task(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    objective: str
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    expected_output: str = "A valid tool result"
    risk: RiskLevel = RiskLevel.READ_ONLY
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    max_attempts: int = 2


class Observation(BaseModel):
    task_id: str
    tool: str
    success: bool
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    created_at: datetime = Field(default_factory=utc_now)


class ApprovalRequest(BaseModel):
    task_id: str
    tool: str
    risk: RiskLevel
    reason: str
    approved: bool | None = None


class AgentRun(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    goal: GoalSpec
    plan: list[Task] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    approvals: list[ApprovalRequest] = Field(default_factory=list)
    status: RunStatus = RunStatus.PENDING
    current_task: int = 0
    iterations: int = 0
    max_iterations: int = Field(default=12, ge=1, le=100)
    tool_budget: int = Field(default=10, ge=1, le=100)
    tool_calls: int = 0
    final_output: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()
