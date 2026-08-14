# Evaluation harness boundary

This directory contains tested statistical primitives for future deterministic task-suite evaluation. It intentionally contains no measured agent-quality values.

A future result record must identify the benchmark command, commit SHA, task-suite version, seed set, task count, runtime environment, and the deterministic tool contracts used. For binary success, report the count and Wilson confidence interval. For continuous values such as steps, tool calls, budget used, and wall-clock latency, retain individual runs and report mean plus sample standard deviation only when at least two observations exist.

The existing autonomy_runtime benchmark remains a local control-plane microbenchmark. It does not measure LLM quality, web-search quality, or external tool performance.
