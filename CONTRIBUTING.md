# Contributing to HelixAgent

Thank you for contributing to HelixAgent. Changes should preserve correctness, reproducibility, security, and operational clarity across the Python, Java, and C++ components.

## Development setup

```bash
git clone https://github.com/CoreyLeath-code/HelixAgent.git
cd HelixAgent
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Build the native components when working on cross-language execution:

```bash
cd java && mvn -B package && cd ..
g++ -O3 -shared -std=c++17 -fPIC agent/cpp/vector.cpp -o agent/cpp/libvector.so
```

## Required validation

```bash
ruff check api agent src tests --select E9,F63,F7,F82
python -m compileall -q api agent src tests
pytest tests -v --cov=api --cov=src --cov-report=term-missing
docker build -t helixagent:local .
```

## Pull-request standard

- Use a focused branch and conventional commit messages.
- Explain the problem, design choice, test evidence, operational impact, and rollback plan.
- Add or update tests for behavior changes.
- Do not commit credentials, tokens, `.env` files, generated artifacts, or production data.
- Preserve API compatibility unless the PR documents a migration path.

## Review criteria

Reviewers should assess correctness, security, failure behavior, observability, reproducibility, performance, maintainability, deployment impact, and rollback safety.
