# Autonomous Runtime

HelixAgent executes goals as durable, budgeted runs rather than treating one HTTP request as an
unbounded agent session. Every run contains a typed goal, plan, tasks, observations, approval
requests, budgets, and a terminal status.

## Control loop

1. The planner converts a goal into typed tasks.
2. The runtime checks iteration and tool-call budgets.
3. The tool registry validates the selected capability and its risk level.
4. Write or destructive tools pause for explicit approval.
5. Tool output becomes a persisted observation.
6. Failed tools retry within the task policy, then fail safely.
7. The runtime checkpoints after every state transition and can resume by run ID.
8. Successful observations are synthesized into the final result.

The default planner is deterministic so local development and tests do not require model
credentials. A model-backed planner can implement the `Planner` protocol and return the same
validated `Task` contracts without changing execution or safety behavior.

## API

Create an asynchronous run:

```http
POST /runs
Content-Type: application/json

{
  "objective": "Research an operational topic and summarize the evidence",
  "max_iterations": 12,
  "tool_budget": 10
}
```

Inspect a checkpointed run:

```http
GET /runs/{run_id}
```

Approve or reject a side-effecting task:

```http
POST /runs/{run_id}/approvals/{task_id}
Content-Type: application/json

{"approved": true}
```

`POST /predict` remains available as a synchronous compatibility endpoint.

## Safety invariants

- Unknown tools are rejected.
- Each tool declares a risk level and timeout.
- Side-effecting tools cannot execute without a recorded approval.
- Denied approvals fail the run without calling the tool.
- Tool and iteration budgets prevent infinite loops.
- Exceptions are normalized into observations instead of escaping the execution boundary.
- SQLite checkpoints make run history inspectable and resumable.

## Next production increments

- Add a provider-specific structured-output planner and critic behind the existing protocol.
- Move execution to a durable worker queue for multi-process deployments.
- Add PostgreSQL or Redis persistence for horizontally scaled workers.
- Add authenticated run ownership and authorization checks.
- Add signed artifact storage and retention policies.
- Expand the evaluation suite with prompt-injection, recovery, and side-effect scenarios.
