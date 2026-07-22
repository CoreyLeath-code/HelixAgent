# HelixAgent

<p align="center">
  <strong>A modular AI-agent runtime with graph orchestration, polyglot tools, an observable API, and production-oriented delivery controls.</strong>
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
  <img src="https://img.shields.io/badge/LangGraph-orchestration-6C5CE7" alt="LangGraph">
  <img src="https://img.shields.io/badge/Docker-non--root-2496ED?logo=docker&logoColor=white" alt="Docker">
  <a href="https://helixagent-mzekflcbhda4zdchpyhjum.streamlit.app/"><img src="https://img.shields.io/badge/Live%20demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Live Streamlit demo"></a>
</p>

HelixAgent demonstrates how an agent workflow can combine Python orchestration with optional Java planning and C++ vector operations while remaining deployable as a single service. Native components degrade gracefully to Python implementations when their build artifacts are unavailable.

## Features

- **Graph-based agent execution:** LangGraph coordinates planning and tool execution through a typed state machine.
- **Polyglot tool integration:** JPype loads an optional Java planner, while `ctypes` loads an optimized C++ cosine-similarity library.
- **Resilient fallbacks:** Python planning and vector implementations keep the agent usable without native artifacts.
- **FastAPI service:** `/`, `/health`, and `/predict` endpoints with generated OpenAPI documentation.
- **Observability:** Prometheus metrics and OpenTelemetry instrumentation are attached to the API.
- **Interactive demo:** A Streamlit interface exercises the same agent runtime.
- **Container delivery:** Multi-stage Docker build, compiled C++ extension, non-root runtime, and container health check.
- **Automated assurance:** Python 3.10/3.11 tests, coverage artifacts, API and Streamlit smoke tests, container validation, CodeQL, Gitleaks, Trivy, dependency auditing, and CycloneDX SBOM generation.

## Architecture

```text
Client / Streamlit
        |
        v
     FastAPI  ----> Prometheus + OpenTelemetry
        |
        v
 LangGraph Agent
   |     |      |
   |     |      +--> Web search tool
   |     +---------> C++ vector library -> Python fallback
   +---------------> Java planner      -> Python fallback
```

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
pytest tests -v --cov=api --cov=src --cov-report=term-missing
ruff check api agent src tests streamlit_app.py
docker build -t helixagent .
docker run --rm -p 8000:8000 helixagent
```

## Project map

```text
api/                 FastAPI application and monitoring
agent/               LangGraph runtime, tools, Java, and C++
src/                 Data and application services
tests/               Unit, API, and data-processing tests
.github/workflows/   CI, security, and release automation
docs/                Engineering and deployment notes
```

## Project status

HelixAgent is an engineering portfolio project and reference implementation, not a managed commercial AI platform. The repository focuses on modularity, graceful degradation, observable services, automated validation, and secure delivery.

See [Security](SECURITY.md), [Contributing](CONTRIBUTING.md), [Changelog](CHANGELOG.md), and [deployment hygiene](docs/L6_DEPLOYMENT_HYGIENE.md).
