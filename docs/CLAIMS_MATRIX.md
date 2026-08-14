# Claims matrix

| Claim | README or About says | Code proves | Tests prove | Action |
| --- | --- | --- | --- | --- |
| Autonomous planning | Repository About claims LLM reasoning | RuleBasedPlanner is keyword-driven and deterministic; no provider call exists | Deterministic runtime tests | Describe as deterministic rule-based planning; do not claim LLM orchestration |
| Enterprise data tools | Repository About claims enterprise data tools | Optional web, Snowflake, and SageMaker modules exist; the governed default registry only wires web search, vector similarity, and synthesis | Default runtime tests cover vector and synthesis; no integration tests prove Snowflake or SageMaker | Do not use enterprise-data-tools as a system claim |
| Java planner | Java planners exist | Two duplicate keyword planners are present; Python runtime has no JPype or JAR invocation | No integration test | Remove Java as unintegrated duplicate code |
| Native vector operations | README claims optional C++ vector operations | ctypes loads libvector.so when present; Python cosine is fallback | Fallback and property tests define compatible mathematical behavior | Retain with explicit environment-dependent native availability |
| SQLite checkpoints | README claims durable checkpoints | SQLiteRunStore persists typed AgentRun JSON after transitions | Runtime persistence tests | Retain; qualify as single-process durability |
| Reproducible benchmark | README publishes a reference observation | Benchmark command emits machine-readable local deterministic control-loop metrics | Benchmark contract test | Retain as local microbenchmark only |

## Recommended GitHub About description

Deterministic, budgeted Python agent runtime with governed tools, SQLite checkpoints, FastAPI endpoints, and optional C++ cosine-similarity acceleration.

Update the GitHub About/description field manually; this workflow changes repository files, not GitHub repository metadata.
