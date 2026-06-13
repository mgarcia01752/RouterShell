"""RouterShell version helpers."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

import tomllib


def _read_source_tree_version() -> str:
    """Read the version from pyproject.toml when package metadata is unavailable."""
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        with pyproject_path.open("rb") as handle:
            pyproject = tomllib.load(handle)
    except OSError:
        return "0.0.0+unknown"

    project = pyproject.get("project", {})
    version = project.get("version", "0.0.0+unknown")
    if not isinstance(version, str):
        return "0.0.0+unknown"
    return version


try:
    __version__: str = package_version("routershell")
except PackageNotFoundError:
    __version__ = _read_source_tree_version()
