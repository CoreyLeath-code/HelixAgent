# HelixAgent Runtime Architecture

## High-level overview

HelixAgent is a single-service Python reference implementation of a bounded
plan/execute/observe/replan runtime. The shipped planner is deterministic and
rule-based; the planner protocol can support other implementations, but no model
provider, Java planner, or distributed scheduler is part of the runtime.

| Layer | Implementation | Role |
|---|---|---|
| Planner | Python | Deterministic typed-task proposal |
| Runtime | Python | Budgets, approval gates, retries, timeouts, and SQLite checkpoints |
| Vector operations | NumPy, optional C++ ctypes, Python | NumPy/BLAS default; C++ is an FFI demonstration; Python degrades when NumPy is unavailable |
| Service | FastAPI | Health, prediction, Prometheus, and OpenTelemetry endpoints |

## Execution flow

~~~mermaid
flowchart LR
    A[User prompt] --> B[Rule-based planner]
    B --> C[Python autonomous runtime]
    C --> D[SQLite checkpoints]
    C --> E[Governed tool registry]
    E --> F[NumPy cosine similarity default]
    F -. opt-in interop .-> G[Optional C++ ctypes binding]
    F -. NumPy unavailable .-> H[Pure-Python cosine similarity]
    C --> I[FastAPI response]
~~~

The runtime owns state transitions and execution bounds; the tool registry owns
risk and timeout policy; SQLite owns local checkpoint persistence. The optional
C++ shared library is not selected by default and is not presented as a
performance replacement for NumPy/BLAS.
