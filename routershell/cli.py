"""Console entry points for RouterShell."""

from __future__ import annotations

import sys
from pathlib import Path

import lib


def _bootstrap_legacy_imports() -> None:
    """Expose the installed ``lib`` directory for legacy top-level imports."""
    lib_path = Path(lib.__file__).resolve().parent
    lib_path_str = str(lib_path)
    if lib_path_str not in sys.path:
        sys.path.insert(0, lib_path_str)


def main() -> int:
    """Run the RouterShell interactive CLI."""
    _bootstrap_legacy_imports()
    from lib.cli.router_main_cli import RouterCLI

    RouterCLI().run()
    return 0


def factory_reset() -> int:
    """Run the RouterShell factory reset workflow."""
    _bootstrap_legacy_imports()
    from lib.system.system_start_up import SystemFactoryReset

    SystemFactoryReset()
    return 0
