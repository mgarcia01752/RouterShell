"""Package version smoke tests."""

from __future__ import annotations

import importlib
import importlib.metadata
from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_package_version_matches_pyproject() -> None:
    """Verify package version resolves from project metadata."""
    import routershell

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    assert routershell.__version__ == pyproject["project"]["version"]


def test_source_tree_version_overrides_stale_package_metadata(monkeypatch) -> None:
    """Verify release checks do not read stale editable-install metadata."""
    import routershell._version as version_module

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    monkeypatch.setattr(importlib.metadata, "version", lambda package_name: "0.0.1")
    reloaded_version_module = importlib.reload(version_module)

    assert reloaded_version_module.__version__ == pyproject["project"]["version"]
