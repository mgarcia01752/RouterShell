"""Import compatibility smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path


def test_lib_package_adds_legacy_import_path() -> None:
    """Importing ``lib`` exposes the existing top-level package path."""
    import lib

    lib_path = str(Path(lib.__file__).resolve().parent)

    assert lib_path in sys.path
