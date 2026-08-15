""""Reproducible three-way cosine-similarity backend benchmark.

The report contains measurements from the current machine only. It does not assert
a winner: NumPy is the default backend, the optional C++ path demonstrates ctypes
interop, and the Python implementation is a degradation path.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from agent.agent_core import (
    cosine_similarity_cpp,
    cosine_similarity_numpy,
    cosine_similarity_python,
    cpp_backend_available,
)

DEFAULT_SIZES = (128, 1_024, 10_000)


def percentile(values: list[float], percentile_value: float) -> float:
    """Return a nearest-rank percentile for a non-empty sample."""
    ordered = sorted(values)
    index = max(0, math.ceil(percentile_value * len(ordered)) - 1)
    return ordered[index]


def _time_backend(
    backend: Callable[[object, object], float],
    left: object,
    right: object,
    *,
    repetitions: int,
    warmup: int,
) -> dict[str, float]:
    for _ in range(warmup):
        backend(left, right)

    samples_us: list[float] = []
    for _ in range(repetitions):
        started = time.perf_counter_ns()
        backend(left, right)
        samples_us.append((time.perf_counter_ns() - started) / 1_000)

    return {
        "mean_us": round(statistics.fmean(samples_us), 6),
        "p50_us": round(statistics.median(samples_us), 6),
        "p95_us": round(percentile(samples_us, 0.95), 6),
    }


def run_benchmark(
    *,
    sizes: tuple[int, ...] = DEFAULT_SIZES,
    repetitions: int = 100,
    warmup: int = 10,
    seed: int = 17_290,
) -> dict[str, Any]:
    """Measure every available vector backend with deterministic input vectors."""
    if not sizes or any(size < 1 for size in sizes):
        raise ValueError("sizes must contain positive dimensions")
    if repetitions < 1 or warmup < 0:
        raise ValueError("repetitions must be positive and warmup cannot be negative")

    backends: list[tuple[str, Callable[[object, object], float]]] = [
        ("numpy", cosine_similarity_numpy),
        ("python", cosine_similarity_python),
    ]
    if cpp_backend_available():
        backends.insert(1, ("cpp", cosine_similarity_cpp))

    generator = np.random.default_rng(seed)
    measurements: list[dict[str, Any]] = []
    for size in sizes:
        left = np.ascontiguousarray(generator.standard_normal(size), dtype=np.float64)
        right = np.ascontiguousarray(generator.standard_normal(size), dtype=np.float64)
        for name, backend in backends:
            result = _time_backend(
                backend, left, right, repetitions=repetitions, warmup=warmup
            )
            measurements.append(
                {
                    "backend": name,
                    "vector_size": size,
                    "repetitions": repetitions,
                    **result,
                }
            )

    return {
        "benchmark": "vector_ops",
        "scope": "local cosine-similarity backend timings; no claim of cross-host performance",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor() or "not reported",
            "numpy": np.__version__,
        },
        "workload": {
            "sizes": list(sizes),
            "warmup_runs_per_backend": warmup,
            "measured_runs_per_backend": repetitions,
            "random_seed": seed,
            "cpp_backend_available": cpp_backend_available(),
        },
        "measurements": measurements,
    }


def print_table(report: dict[str, Any]) -> None:
    """Print the measured backend timings without ranking or interpretation."""
    print("backend | vector size | mean (us) | p50 (us) | p95 (us)")
    print("--- | ---: | ---: | ---: | ---:")
    for measurement in report["measurements"]:
        print(
            f"{measurement['backend']} | {measurement['vector_size']} | "
            f"{measurement['mean_us']:.6f} | {measurement['p50_us']:.6f} | "
            f"{measurement['p95_us']:.6f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=list(DEFAULT_SIZES))
    parser.add_argument("--repetitions", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--seed", type=int, default=17_290)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("vector-ops-results.json"),
        help="JSON artifact path written with the measurements from this run",
    )
    args = parser.parse_args()
    report = run_benchmark(
        sizes=tuple(args.sizes),
        repetitions=args.repetitions,
        warmup=args.warmup,
        seed=args.seed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print_table(report)
    print(f"JSON artifact: {args.output}")


if __name__ == "__main__":
    main()
