### Summary
Fixed release version checking after a pyproject bump by making source-tree imports prefer the root `pyproject.toml` version before installed package metadata. Added pytest coverage for stale editable-install metadata so release checks do not fail after bumping the project version.

### Modified Files
- src/routershell/_version.py
- tests/packaging/test_version.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/python tools/release/check_version.py` -> pass, package and pyproject both reported 0.1.1.
- `/opt/routershell/venv/bin/python -m pytest tests/packaging/test_version.py -q` -> pass, 2 passed.
- `/opt/routershell/venv/bin/python -m ruff check src/routershell/_version.py tests/packaging/test_version.py` -> pass, all checks passed.
- `/opt/routershell/venv/bin/python -m pytest -q` -> pass, 43 passed.
- `/opt/routershell/venv/bin/python -m ruff check .` -> pass, all checks passed.
- `bash -n tools/vm/*.sh install/install.sh install/uninstall.sh` -> pass.

### Tests
- `pytest` -> pass, 43 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM scripts, install script, and uninstall script.

### Notes / Warnings
- `pyproject.toml` is currently bumped to 0.1.1 from the failed release attempt; this bundle does not include it because that change pre-existed the fix.
- A plain release rerun from this dirty state will not work until the worktree is made clean or the failed version bump is intentionally restored.

### Remaining TODOs / Follow-Ups
- Decide whether to restore `pyproject.toml` to 0.1.0 before saving this fix, or intentionally keep the failed 0.1.1 bump and handle release/tagging manually.

# FILE: src/routershell/_version.py
"""RouterShell version helpers."""

from __future__ import annotations

from importlib.metadata import version as package_version
from pathlib import Path

import tomllib

UNKNOWN_VERSION = "0.0.0+unknown"


def _read_source_tree_version() -> str:
    """Read the version from pyproject.toml when package metadata is unavailable."""
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    try:
        with pyproject_path.open("rb") as handle:
            pyproject = tomllib.load(handle)
    except OSError:
        return UNKNOWN_VERSION

    project = pyproject.get("project", {})
    version = project.get("version", UNKNOWN_VERSION)
    if not isinstance(version, str):
        return UNKNOWN_VERSION
    return version


def _read_package_version() -> str:
    """Read the installed package metadata version."""
    try:
        return package_version("routershell")
    except Exception:
        return UNKNOWN_VERSION


source_tree_version = _read_source_tree_version()
if source_tree_version != UNKNOWN_VERSION:
    __version__: str = source_tree_version
else:
    __version__ = _read_package_version()

# FILE: tests/packaging/test_version.py
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
