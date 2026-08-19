"""Resolve HelixAgent's version from installed package metadata or pyproject.toml."""

from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

_PROJECT_VERSION = re.compile(r'^version\s*=\s*"(?P<version>[^"]+)"\s*$', re.MULTILINE)


def get_version() -> str:
    """Return the installed distribution version or the source-tree project version."""
    try:
        return version("helixagent")
    except PackageNotFoundError:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        match = _PROJECT_VERSION.search(pyproject.read_text(encoding="utf-8"))
        if match is None:
            raise RuntimeError("Could not determine the HelixAgent project version.")
        return match.group("version")
