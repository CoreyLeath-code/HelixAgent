# HelixAgent

<p align="center">
  <strong>Durable autonomous-agent runtime in Python: a bounded plan/execute/observe/replan loop with governed tools, approval gates, and SQLite checkpoints for resumable runs. FastAPI service with Prometheus + OpenTelemetry, NumPy/BLAS vector operations, optional C++ ctypes interop, pure-Python fallback, and reproducible benchmarks.</strong>
</p>

<p align="center">
  <a href="https://github.com/CoreyLeath-code/HelixAgent/actions/workflows/ci-cd.yml"><img src="https://github.com/CoreyLeath-code/HelixAgent/actions/workflows/ci-cd.yml/badge.svg?branch=main" alt="CI"></a>
  <a href="https://github.com/CoreyLeath-code/HelixAgent/actions/workflows/security.yml"><img src="https://github.com/CoreyLeath-code/HelixAgent/actions/workflows/security.yml/badge.svg?branch=main" alt="Security"></a>
  <a href="https://github.com/CoreyLeath-code/HelixAgent/releases"><img src="https://img.shields.io/github/v/release/CoreyLeath-code/HelixAgent?include_prereleases&sort=semver" alt="Latest release"></a>
  <a href="https://github.com/CoreyLeath-code/HelixAgent/blob/main/LICENSE"><img src="https://img.shields.io/github/license/CoreyLeath-code/HelixAgent" alt="MIT license"></a>
  <img src="https://img.shields.io/github/last-commit/CoreyLeath-code/HelixAgent/main" alt="Last commit">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?logo=python&logoColor=white" alt="Python 3.10 and 3.11">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Autonomy-budgeted%20control%20loop-6C5CE7" alt="Budgeted autonomous control loop">
  <img src="https://img.shields.io/badge/State-SQLite%20checkpoints-003B57?logo=sqlite&logoColor=white" alt="SQLite checkpoints">
  <img src="https://img.shields.io/badge/Benchmarks-reproducible-2E8B57" alt="Reproducible benchmarks">
  <img src="https://img.shields.io/badge/Docker-non--root-2496ED?logo=docker&logoColor=white" alt="Docker">
  <a href="https://helixagent-mzekflcbhda4zdchpyhjum.streamlit.app/"><img src="https://img.shields.io/badge/Live%20demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Live Streamlit demo"></a>
</p>

HelixAgent is a durable Python agent runtime built around a bounded plan/execute/observe/replan loop with governed tools, approval gates, and SQLite checkpoints. Its included planner is deterministic and rule-based; the planner protocol is extensible, but no model provider is implemented. NumPy is the default cosine-similarity backend. The optional C++ ctypes binding is an FFI demonstration, not a performance claim; a scale-stable Python implementation is retained only for NumPy-unavailable environments.

## Features

- **Bounded autonomous execution:** A typed plan/execute/observe/replan loop enforces iteration and tool-call budgets.
- **Deterministic planning and vector backends:** The typed planner protocol uses a rule-based default; NumPy/BLAS is the default vector path, while the opt-in `ctypes` binding demonstrates C++ interop.
- **Resilient fallbacks:** The pure-Python vector implementation is used only if the declared NumPy dependency is unavailable.
- **FastAPI service:** `/`, `/health`, and `/predict` endpoints with generated OpenAPI documentation.
- **Observability:** Prometheus metrics and OpenTelemetry instrumentation are attached to the API.
- **Interactive demo:** A Streamlit interface exercises the same agent runtime.
- **Container delivery:** Multi-stage Docker build, compiled C++ extension, non-root runtime, and container health check.
- **Automated assurance:** Python 3.10/3.11 tests, coverage artifacts, API and Streamlit smoke tests, container validation, CodeQL, Gitleaks, Trivy, dependency auditing, and CycloneDX SBOM generation.
- **Durable autonomy:** Budgeted plan/execute/observe/replan runs, SQLite checkpoints, retries, tool timeouts, explicit approval gates, and resumable run APIs.

## Architecture

```text
Client / Streamlit
        |
        v
     FastAPI  ----> Prometheus + OpenTelemetry
        |
        v
 Autonomous runtime ----> SQLite checkpoints
   |        |       |
   |        |       +--> Governed tool registry + approval gates
   |        +----------> NumPy (BLAS) default -> optional C++ via ctypes (interop demo) -> pure-Python fallback
   +-------------------> Planner protocol -> deterministic default
```

The runtime separates policy from mechanism: planners propose typed tasks, the runtime owns
budgets and state transitions, the registry owns tool risk and timeout policy, and the store owns
durability. This keeps a future model planner from bypassing execution invariants.

| Concern | Design decision | Operational tradeoff |
|---|---|---|
| Recovery | Checkpoint every run transition in SQLite | Simple single-node durability; distributed workers require leases and a shared store |
| Safety | Pause write/destructive tools for explicit approval | Safer default with additional operator latency |
| Runaway control | Bound iterations, tool calls, retries, and tool duration | Predictable cost; a valid long task may exhaust its budget |
| Planner extensibility | Typed `Planner` protocol with rule-based default | Credential-free execution; no model provider is implemented |
| Vector interop and fallback | NumPy/BLAS default, optional C++ ctypes binding, Python degradation path | Portable behavior; C++ demonstrates FFI and is not claimed to beat BLAS |

Runtime invariants are covered by tests: terminal states are persisted, denied tools are never
executed, budget exhaustion fails closed, retries are bounded, and timeout responses do not wait
for a slow handler. The database location is configurable with `HELIXAGENT_RUN_DB`; the container
uses the writable non-root path `/app/data/helixagent_runs.db`.

## Research metrics and benchmarks

The benchmark is a deterministic microbenchmark of orchestration plus SQLite checkpoints. It
does **not** include network search, model inference, or provider latency.

| Metric | Reference result |
|---|---:|
| Successful runs | 200/200 (100%) |
| End-to-end latency, p50 | 7.798 ms |
| End-to-end latency, p95 | 8.629 ms |
| Checkpoint read latency, p50 | 0.092 ms |
| Checkpoint read latency, p95 | 0.119 ms |
| Sequential throughput | 125.666 runs/s |

Reference environment: Python 3.12.13, Windows 11 build 26200, AMD64; 20 warmups, 200 measured
runs, two deterministic tasks per run, measured July 22, 2026. These are reference observations,
not production SLOs or cross-hardware claims. Reproduce locally with:

```bash
python -m benchmarks.autonomy_runtime --iterations 200 --warmup 20
python -m benchmarks.vector_ops --output vector-ops-results.json
```

See [benchmark methodology and limitations](docs/BENCHMARKS.md) for metric definitions and the
evaluation boundary. CI also uploads a fresh `benchmark-results.json` artifact on Python 3.11.

## Vector-operations benchmark

The vector benchmark measures the NumPy default, the optional C++ ctypes backend when its shared library is present, and the pure-Python implementation. It reports measurements from the machine that runs it; it does not rank backends or claim that C++ outperforms BLAS.

~~~bash
python -m benchmarks.vector_ops --sizes 128 1024 10000 --warmup 10 --repetitions 100 --output vector-ops-results.json
~~~

| Backend | 128 | 1k | 10k |
|---|---|---|---|
| NumPy | <fill after running: python -m benchmarks.vector_ops> | <fill after running: python -m benchmarks.vector_ops> | <fill after running: python -m benchmarks.vector_ops> |
| C++ ctypes (when available) | <fill after running: python -m benchmarks.vector_ops> | <fill after running: python -m benchmarks.vector_ops> | <fill after running: python -m benchmarks.vector_ops> |
| Pure Python | <fill after running: python -m benchmarks.vector_ops> | <fill after running: python -m benchmarks.vector_ops> | <fill after running: python -m benchmarks.vector_ops> |

## Evidence boundaries

The CI matrix exercises Python 3.10 and 3.11 quality/tests, container API health, and Streamlit startup; security and supply-chain workflows run separately. Runtime contract coverage includes terminal-run idempotence, approval gating, bounded retries and budgets, persisted failure for unknown tools, and Python vector fallback properties. The C++ path remains optional and environment-dependent; it is an FFI demonstration rather than a claim of better performance than NumPy.

For the full claim-to-evidence map, invariant definitions, and reproducible statistical primitives, see [claims matrix](docs/CLAIMS_MATRIX.md), [runtime invariants](docs/RUNTIME_INVARIANTS.md), and [evaluation notes](benchmarks/eval/README.md).

## Quick start

Requires Python 3.10 or newer.

```bash
git clone https://github.com/CoreyLeath-code/HelixAgent.git
cd HelixAgent
python -m venv .venv
```

Activate the environment, then install and run the API:

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Open [Swagger UI](http://localhost:8000/docs), or verify the service:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Compare vectors and summarize the result."}'
```

Run the Streamlit demo locally:

```bash
streamlit run streamlit_app.py
```

## Test and container workflows

```bash
pip install -r requirements-dev.txt
pytest tests -v --cov=agent --cov=api --cov=src --cov-report=term-missing
ruff check api agent src tests streamlit_app.py
python -m benchmarks.autonomy_runtime --iterations 200 --warmup 20
docker build -t helixagent .
docker run --rm -p 8000:8000 helixagent
```

## Releases and reproducibility

Maintainers create releases by pushing a validated semantic-version tag; the tag workflow
validates the exact commit before it can create a GitHub Release.

~~~bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
~~~

See [release procedure and evidence artifacts](docs/RELEASING.md) for the required
changelog/version update, validation, and reproducibility guidance.

## Project map

```text
api/                 FastAPI application and monitoring
agent/               Autonomous runtime, planner/tool contracts, and optional C++
src/                 Data and application services
tests/               Unit, API, and data-processing tests
.github/workflows/   CI, security, and release automation
docs/                Engineering and deployment notes
```

## Project status

HelixAgent is an engineering portfolio project and reference implementation, not a managed commercial AI platform. The repository focuses on modularity, graceful degradation, observable services, automated validation, and secure delivery.

See [Autonomous runtime](docs/AUTONOMY.md), [Security](SECURITY.md), [Contributing](CONTRIBUTING.md), [Changelog](CHANGELOG.md), and [deployment hygiene](docs/L6_DEPLOYMENT_HYGIENE.md).
