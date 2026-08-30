"""Pluggable event-sink contract used by the autonomous runtime."""

from __future__ import annotations

from typing import Protocol

from agent.telemetry.events import AgentEvent


class EventSink(Protocol):
    def emit(self, event: AgentEvent) -> None:
        """Accept one lifecycle event without changing runtime correctness."""

    def close(self, timeout: float = 5.0) -> None:
        """Flush pending telemetry when the sink owns background resources."""


class NullEventSink:
    """Credential-free default used for local development and tests."""

    def emit(self, event: AgentEvent) -> None:
        del event

    def close(self, timeout: float = 5.0) -> None:
        del timeout
