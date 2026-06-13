"""Console entry point metadata smoke tests."""

from __future__ import annotations

from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_pyproject_declares_console_entry_points() -> None:
    """Verify packaged console scripts point at package entry functions."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    scripts = pyproject["project"]["scripts"]

    assert scripts["routershell"] == "routershell.cli:main"
    assert scripts["routershell-factory-reset"] == "routershell.cli:factory_reset"


def test_routershell_entry_point_functions_are_importable() -> None:
    """Verify console entry point functions import without starting the CLI."""
    from routershell import cli

    assert callable(cli.main)
    assert callable(cli.factory_reset)
