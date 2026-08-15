"""Contract tests for the reproducible autonomy microbenchmark."""

from benchmarks.autonomy_runtime import run_benchmark
from benchmarks.vector_ops import run_benchmark as run_vector_benchmark


def test_autonomy_benchmark_reports_auditable_metrics() -> None:
    report = run_benchmark(iterations=3, warmup=1)

    assert report["workload"]["measured_runs"] == 3
    assert report["results"]["success_rate_percent"] == 100.0
    assert report["results"]["tool_calls"] == 6
    assert report["results"]["run_latency_ms_p95"] > 0



def test_vector_benchmark_reports_current_measurements() -> None:
    report = run_vector_benchmark(sizes=(4,), repetitions=2, warmup=1, seed=23)

    assert report["workload"]["sizes"] == [4]
    assert {"numpy", "python"} <= {
        measurement["backend"] for measurement in report["measurements"]
    }
    assert all(measurement["mean_us"] > 0 for measurement in report["measurements"])
