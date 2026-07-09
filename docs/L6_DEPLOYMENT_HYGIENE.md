# HelixAgent L6 Nine-Tier Deployment Hygiene

This document defines the engineering maturity baseline and automated evidence for HelixAgent.

## Tier 1 — Source Hygiene

- Python syntax validation.
- High-confidence Ruff correctness checks.
- Reproducible development dependencies.
- Explicit type annotations in critical data-ingestion paths.

## Tier 2 — Test Engineering

- Python 3.10 and 3.11 compatibility matrix.
- Data-ingestion happy-path, validation, and reproducibility tests.
- FastAPI root, health, prediction, and validation contract tests.
- Coverage XML and JUnit evidence artifacts.

## Tier 3 — Static Quality

- Ruff correctness gates.
- CodeQL analysis.
- Compile-time syntax validation.
- Pull-request evidence retained as CI artifacts.

## Tier 4 — Security Engineering

- Gitleaks current-tree secret scanning.
- Trivy filesystem vulnerability scanning.
- Private vulnerability reporting guidance.
- GitHub code-scanning integration through SARIF.

## Tier 5 — Supply-Chain Hygiene

- Dependabot for Python, GitHub Actions, Docker, and Maven.
- pip-audit reports.
- CycloneDX SBOM generation.
- Explicit runtime and development dependency manifests.

## Tier 6 — Reproducible Runtime

- Dedicated Java, C++, and Python build stages.
- Minimal Python runtime image.
- Non-root runtime identity.
- Explicit health check and deterministic Uvicorn entry point.

## Tier 7 — Continuous Delivery

- Pull-request and main-branch verification.
- Superseded-run cancellation.
- Multi-version test matrix.
- Live container health smoke test.
- Release-readiness contract.

## Tier 8 — Release Engineering

- Semantic version tag trigger.
- GitHub Release source artifacts.
- Generated release notes.
- GHCR container publishing.

## Tier 9 — Operational Governance

- SECURITY.md disclosure process.
- CONTRIBUTING.md validation and review standard.
- Semantic changelog.
- Auditable CI evidence for tests, coverage, security, dependency findings, and SBOMs.

## Promotion Standard

A change is release-ready when tests, compatibility checks, static quality, container health validation, security workflows, and release metadata checks are green. Advisory findings should become focused remediation issues rather than being hidden or ignored.
