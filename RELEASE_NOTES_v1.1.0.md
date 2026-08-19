# HelixAgent v1.1.0

This release packages the existing runtime and aligns its release evidence with the implementation already on `main`. It covers validation, delivery, documentation correction, and the existing vector-backend design without adding a performance claim or a new product capability.

## Tag-triggered release contract

Pushing a newly created annotated `v1.1.0` tag triggers **HelixAgent Release**. The workflow checks out the exact tag commit; verifies the tag, `pyproject.toml` version, and changelog section; runs Ruff, pytest, the release-image C++-interop probe, CodeQL, secret scanning, and CycloneDX SBOM generation; then attaches a source archive, SHA-256 checksum, `helixagent-release-sbom`, and reproduction instructions to the GitHub Release before publishing the validated GHCR image.

## Added

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

## Changed

- Hardened `DataIngestor` with file validation, split-parameter validation, deterministic partitioning, duplicate-column detection, and explicit types.
- Reworked the production image into isolated Java, C++, Python build stages and a non-root runtime stage.
- Made NumPy/BLAS the default cosine-similarity backend; the C++ ctypes backend is explicit opt-in interoperability and pure Python remains the degradation path.
- Hardened the ctypes boundary by coercing vectors to contiguous float64 buffers before pointer passing.
- Corrected vector-backend documentation to remove unsupported C++ performance claims.

## Verification

- SBOM artifact: `helixagent-release-sbom` (CycloneDX JSON).
- Source checksum: `sha256sum` of the deterministic `git archive` source tarball (`gzip -n`).
- Reproduce the release gates:

  ~~~bash
  pip install -r requirements-dev.txt
  ruff check api agent src tests streamlit_app.py --select E9,F63,F7,F82
  pytest
  docker build -t helixagent-release .
  python -m benchmarks.vector_ops --output vector-ops-results.json
  ~~~
