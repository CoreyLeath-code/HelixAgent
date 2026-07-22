"""Reproducible microbenchmark for the deterministic autonomous runtime.

This measures orchestration and SQLite checkpoint overhead only. It deliberately
excludes network tools and model inference so runs remain comparable and do not
depend on credentials or provider latency.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from agent.autonomy.runtime import AutonomousRuntime
from agent.autonomy.store import SQLiteRunStore


def percentile(values: list[float], percentile_value: float) -> float:
    """Return a nearest-rank percentile for a non-empty sample."""
    ordered = sorted(values)
    index = max(0, math.ceil(percentile_value * len(ordered)) - 1)
    return ordered[index]


def run_benchmark(iterations: int = 100, warmup: int = 10) -> dict[str, Any]:
    if iterations < 1 or warmup < 0:
        raise ValueError("iterations must be positive and warmup cannot be negative")

    with tempfile.TemporaryDirectory(prefix="helixagent-benchmark-") as directory:
        with SQLiteRunStore(Path(directory) / "runs.db") as store:
            runtime = AutonomousRuntime(store=store)

            for _ in range(warmup):
                warmup_run = runtime.submit("Compare vector similarity")
                runtime.run(warmup_run.id)

            latencies_ms: list[float] = []
            recovery_latencies_ms: list[float] = []
            completed = 0
            tool_calls = 0
            started_suite = time.perf_counter()

            for _ in range(iterations):
                started = time.perf_counter()
                run = runtime.submit("Compare vector similarity")
                result = runtime.run(run.id)
                latencies_ms.append((time.perf_counter() - started) * 1_000)

                recovery_started = time.perf_counter()
                restored = store.get(run.id)
                recovery_latencies_ms.append(
                    (time.perf_counter() - recovery_started) * 1_000
                )
                completed += restored.status.value == "completed"
                tool_calls += result.tool_calls

            suite_seconds = time.perf_counter() - started_suite

    return {
        "benchmark": "deterministic_vector_control_loop",
        "scope": "local orchestration and SQLite checkpoints; no network or model calls",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor() or "not reported",
        },
        "workload": {
            "measured_runs": iterations,
            "warmup_runs": warmup,
            "tasks_per_run": 2,
        },
        "results": {
            "success_rate_percent": round(completed / iterations * 100, 3),
            "run_latency_ms_mean": round(statistics.fmean(latencies_ms), 3),
            "run_latency_ms_p50": round(statistics.median(latencies_ms), 3),
            "run_latency_ms_p95": round(percentile(latencies_ms, 0.95), 3),
            "checkpoint_read_ms_p50": round(statistics.median(recovery_latencies_ms), 3),
            "checkpoint_read_ms_p95": round(percentile(recovery_latencies_ms, 0.95), 3),
            "throughput_runs_per_second": round(iterations / suite_seconds, 3),
            "tool_calls": tool_calls,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=10)
    args = parser.parse_args()
    json.dump(run_benchmark(args.iterations, args.warmup), sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
