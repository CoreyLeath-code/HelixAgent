"""Contract tests for the reproducible autonomy microbenchmark."""

from benchmarks.autonomy_runtime import run_benchmark


def test_autonomy_benchmark_reports_auditable_metrics() -> None:
    report = run_benchmark(iterations=3, warmup=1)

    assert report["workload"]["measured_runs"] == 3
    assert report["results"]["success_rate_percent"] == 100.0
    assert report["results"]["tool_calls"] == 6
    assert report["results"]["run_latency_ms_p95"] > 0
