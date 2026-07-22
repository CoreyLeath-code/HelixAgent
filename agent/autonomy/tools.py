"""Governed tool registry with typed metadata, budgets, retries, and timeouts."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
from typing import Any, Callable

from agent.autonomy.models import Observation, RiskLevel, Task


ToolHandler = Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    handler: ToolHandler
    description: str
    risk: RiskLevel = RiskLevel.READ_ONLY
    timeout_seconds: float = 15.0


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def execute(self, task: Task) -> Observation:
        spec = self.get(task.tool)
        started = time.perf_counter()
        pool = ThreadPoolExecutor(max_workers=1)
        future = pool.submit(spec.handler, task.arguments)
        try:
            output = future.result(spec.timeout_seconds)
            pool.shutdown(wait=True)
            return Observation(
                task_id=task.id,
                tool=task.tool,
                success=True,
                output=output,
                duration_ms=(time.perf_counter() - started) * 1_000,
            )
        except FutureTimeout:
            future.cancel()
            pool.shutdown(wait=False, cancel_futures=True)
            error = f"Tool timed out after {spec.timeout_seconds:.1f}s"
        except Exception as exc:  # noqa: BLE001 - tool boundary normalizes failures
            pool.shutdown(wait=True)
            error = f"{type(exc).__name__}: {exc}"
        return Observation(
            task_id=task.id,
            tool=task.tool,
            success=False,
            error=error,
            duration_ms=(time.perf_counter() - started) * 1_000,
        )
