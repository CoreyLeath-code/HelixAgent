# Changelog

All notable changes to HelixAgent are documented here.

The project follows Semantic Versioning and the Keep a Changelog format.

## [Unreleased]

### Added

### Changed

## [1.1.0] - 2026-08-18

### Added

- Python 3.10 and 3.11 CI matrix.
- API contract tests and expanded data-ingestion edge-case coverage.
- Coverage XML and JUnit test artifacts.
- Ruff correctness gates and Python syntax validation.
- Container build and live health smoke tests.
- CodeQL, Gitleaks, Trivy, pip-audit, Dependabot, and CycloneDX SBOM automation.
- GitHub Release artifacts and GHCR image publishing.
- Security, contribution, release-readiness, and nine-tier deployment-hygiene documentation.
- Evidence-driven semantic-tag release validation with source checksums, CycloneDX SBOM attachment, and reproducibility instructions.
- Three-way vector-backend benchmark infrastructure that writes measurements only when executed.

### Changed

- Hardened `DataIngestor` with file validation, split-parameter validation, deterministic partitioning, duplicate-column detection, and explicit types.
- Reworked the production image into isolated Java, C++, Python build stages and a non-root runtime stage.
- Made NumPy/BLAS the default cosine-similarity backend; the C++ ctypes backend is explicit opt-in interoperability and pure Python remains the degradation path.
- Hardened the ctypes boundary by coercing vectors to contiguous float64 buffers before pointer passing.
- Corrected vector-backend documentation to remove unsupported C++ performance claims.

## [1.0.0] - 2025-06-20

### Added

- Java task planner.
- C++ cosine-similarity library.
- Python agent orchestrator.
- FastAPI service.
- Initial Docker and test infrastructure.

[Unreleased]: https://github.com/CoreyLeath-code/HelixAgent/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/CoreyLeath-code/HelixAgent/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/CoreyLeath-code/HelixAgent/releases/tag/v1.0.0
