"""RouterShell version helpers."""

from __future__ import annotations

from importlib.metadata import version as package_version
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

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
