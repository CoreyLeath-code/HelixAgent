# Autonomy Runtime Benchmark

## Research question

What orchestration and checkpoint overhead does the deterministic HelixAgent control loop add
when external network and model latency are removed?

## Experimental design

- Workload: `Compare vector similarity`.
- Planner: deterministic `RuleBasedPlanner`.
- Tasks per run: one vector-similarity task and one synthesis task.
- Persistence: a fresh temporary SQLite database per benchmark invocation.
- Execution: sequential runs in one process.
- Exclusions: web requests, model inference, provider retries, and concurrent clients.
- Timing source: Python `time.perf_counter()`.
- Percentiles: nearest-rank over measured samples after warmup.

The benchmark reports:

- completion rate: completed runs divided by measured runs;
- run latency: submission, state transitions, tool execution, and checkpoint writes;
- checkpoint read latency: restoration of the completed run by ID;
- sequential throughput: measured runs divided by total measured wall time; and
- tool calls: a workload-integrity check.

## Reference observation

Command:

```bash
python -m benchmarks.autonomy_runtime --iterations 200 --warmup 20
```

Environment: Python 3.12.13, Windows 11 build 26200, AMD64 Family 25 Model 97 Stepping 2.
Collected July 22, 2026.

| Metric | Result |
|---|---:|
| Completion rate | 100.0% (200/200) |
| Run latency mean | 7.860 ms |
| Run latency p50 | 7.798 ms |
| Run latency p95 | 8.629 ms |
| Checkpoint read p50 | 0.092 ms |
| Checkpoint read p95 | 0.119 ms |
| Sequential throughput | 125.666 runs/s |
| Tool calls | 400 |

## Interpretation

This sample establishes a regression baseline for the local deterministic control plane. It does
not demonstrate production capacity or agent quality. Network tools and model-backed planners
will normally dominate end-to-end latency and require separate datasets, quality rubrics, cost
tracking, and provider-specific experiments.

## Threats to validity

- Results are sensitive to CPU, filesystem, antivirus, power policy, Python version, and system load.
- SQLite performance does not predict a distributed database or multi-worker deployment.
- Sequential throughput does not represent concurrent API throughput.
- The deterministic workload does not measure planning correctness or research quality.
- A single reference run is insufficient for cross-version statistical significance.

For change comparisons, run both commits on the same host, use at least 200 measured samples,
report the full environment, and compare distributions rather than a single mean.
