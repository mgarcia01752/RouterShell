"""Package import smoke tests."""

from __future__ import annotations

from pathlib import Path


def test_routershell_lib_package_is_nested_under_src() -> None:
    """Verify the implementation package lives under ``src/routershell/lib``."""
    import routershell.lib as routershell_lib

    lib_path = Path(routershell_lib.__file__).resolve().parent

    assert lib_path.parts[-3:] == ("src", "routershell", "lib")
