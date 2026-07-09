# Changelog

All notable changes to HelixAgent are documented here.

The project follows Semantic Versioning and the Keep a Changelog format.

## [Unreleased]

### Added

- Python 3.10 and 3.11 CI matrix.
- API contract tests and expanded data-ingestion edge-case coverage.
- Coverage XML and JUnit test artifacts.
- Ruff correctness gates and Python syntax validation.
- Container build and live health smoke tests.
- CodeQL, Gitleaks, Trivy, pip-audit, Dependabot, and CycloneDX SBOM automation.
- GitHub Release artifacts and GHCR image publishing.
- Security, contribution, release-readiness, and nine-tier deployment-hygiene documentation.

### Changed

- Hardened `DataIngestor` with file validation, split-parameter validation, deterministic partitioning, duplicate-column detection, and explicit types.
- Reworked the production image into isolated Java, C++, Python build stages and a non-root runtime stage.

## [1.0.0] - 2025-06-20

### Added

- Java task planner.
- C++ cosine-similarity library.
- Python agent orchestrator.
- FastAPI service.
- Initial Docker and test infrastructure.

[Unreleased]: https://github.com/CoreyLeath-code/HelixAgent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/CoreyLeath-code/HelixAgent/releases/tag/v1.0.0
