"""Console entry points for RouterShell."""

from __future__ import annotations


def main() -> int:
    """Run the RouterShell interactive CLI."""
    from routershell.lib.cli.router_main_cli import RouterCLI

    RouterCLI().run()
    return 0


def factory_reset() -> int:
    """Run the RouterShell factory reset workflow."""
    from routershell.lib.system.system_start_up import SystemFactoryReset

    SystemFactoryReset()
    return 0
