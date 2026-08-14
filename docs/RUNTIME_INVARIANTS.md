# Runtime invariants and evidence boundary

## Verified runtime classification

HelixAgent is a deterministic rule-based planner with a typed Planner protocol. The runtime does not call an LLM provider. RuleBasedPlanner in agent/autonomy/planning.py maps objective keywords to typed tasks; a future model-backed planner must satisfy the same protocol and cannot bypass budgets, approvals, or persistence.

## Enforced invariants

| Invariant | Enforcement point | Test evidence |
| --- | --- | --- |
| Terminal runs are idempotent | AutonomousRuntime.run returns persisted completed or failed runs unchanged | terminal-run regression test |
| Unknown tools fail as persisted run failures | registry lookup is normalized at the runtime boundary | unknown-tool contract test |
| Side-effecting tools require approval | risk gate runs before tool execution | approval and denial tests |
| Tool and iteration budgets fail closed | loop guard precedes execution | budget test |
| Retries are bounded per task | task attempts are checked before retry | fault-injection test |
| Tool timeouts return control | registry uses a bounded future wait | timeout test |
| Checkpoints preserve run identity | SQLite stores the full typed run by stable ID | checkpoint tests |
| Vector fallback has defined semantics | Python cosine validates dimension and defines zero-vector result as 0.0 | property and fallback tests |

These are single-process SQLite semantics. They do not establish exactly-once external side effects, distributed leases, cross-process scheduling, or horizontal-concurrency safety.

## Checkpoint format

The current store persists Pydantic JSON for AgentRun in SQLite. It has no explicit schema-version field, so unknown future checkpoint schemas are not safely rejected or migrated. This is an identified limitation, not an implemented migration claim.
