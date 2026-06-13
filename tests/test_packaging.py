"""Packaging metadata and entry point smoke tests."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_declares_console_entry_points() -> None:
    """Verify the packaged console scripts point at the compatibility launcher."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    scripts = pyproject["project"]["scripts"]

    assert scripts["routershell"] == "routershell:main"
    assert scripts["routershell-factory-reset"] == "routershell:factory_reset"


def test_lib_package_adds_legacy_import_path() -> None:
    """Importing ``lib`` exposes the legacy top-level package path."""
    import lib

    lib_path = str(Path(lib.__file__).resolve().parent)

    assert lib_path in sys.path


def test_routershell_entry_point_functions_are_importable() -> None:
    """The console entry point functions can be imported without starting the CLI."""
    import routershell

    assert callable(routershell.main)
    assert callable(routershell.factory_reset)


def test_version_module_matches_pyproject() -> None:
    """The package version module and pyproject version stay aligned."""
    import routershell_version

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    assert routershell_version.__version__ == pyproject["project"]["version"]
