"""Console entry points for RouterShell."""

from __future__ import annotations

from routershell.logging_config import configure_logging


def main() -> int:
    """Run the RouterShell interactive CLI."""
    configure_logging()

    from routershell.lib.cli.router_main_cli import RouterCLI

    RouterCLI(system_start_up=True).run()
    return 0


def factory_reset() -> int:
    """Run the RouterShell factory reset workflow."""
    configure_logging()

    from routershell.lib.system.system_start_up import SystemFactoryReset

    SystemFactoryReset()
    return 0
