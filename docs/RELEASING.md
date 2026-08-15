# Releasing HelixAgent

## Release policy

HelixAgent uses semantic versions and immutable, tag-driven evidence releases.

- **PATCH**: bug fixes, documentation corrections, and small internal improvements.
- **MINOR**: backward-compatible capabilities or meaningful engineering milestones.
- **MAJOR**: intentional breaking public API changes.

A commit message does not determine a version. The maintainer selects it after reviewing
the public API, the changelog, and the validation evidence.

## Preflight

Before creating a release tag:

1. Merge the intended change set to `main`.
2. Set `[project].version` in `pyproject.toml` to the release version without the
   `v` prefix.
3. Move the corresponding items from `[Unreleased]` into a dated
   `## [X.Y.Z]` section in `CHANGELOG.md`.
4. Run the repository validation commands:

   ~~~bash
   pip install -r requirements-dev.txt
   ruff check .
   pytest
   docker build -t helixagent-release .
   ~~~

5. Review the changelog for evidence-bound statements only. Do not add benchmark,
   coverage, or performance values unless they came from a documented run.

The release workflow verifies the version/tag and changelog-section consistency. A
mismatch fails before publication.

## Create a release

From the validated `main` commit:

~~~bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
~~~

Only semantic-version tags matching `v*.*.*` start the release workflow. The
workflow checks out the exact tag commit, runs validation and security/SBOM work,
then creates a GitHub Release only if those required jobs succeed. It refuses to
overwrite an existing GitHub Release.

## Evidence artifacts

A successful release attaches:

- a source archive made from the tagged commit;
- a SHA-256 checksum for that archive;
- a CycloneDX SBOM; and
- release reproduction instructions.

The workflow does not run vector timing on GitHub-hosted hardware because shared
runner measurements are not a useful performance claim. Reproduce the vector
experiment on the target host instead:

~~~bash
python -m benchmarks.vector_ops --output vector-ops-results.json
~~~

NumPy/BLAS is the default vector backend. The C++ ctypes backend demonstrates safe
native interoperability and is not claimed to outperform NumPy/BLAS. Pure Python
is the fallback when NumPy is unavailable.
