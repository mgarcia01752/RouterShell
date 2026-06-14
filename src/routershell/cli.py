"""Console entry points for RouterShell."""

from __future__ import annotations

import argparse
from pathlib import Path

from routershell.lib.common.constants import STATUS_NOK
from routershell.lib.common.types import CommandArgs
from routershell.logging_config import configure_logging


def main(argv: CommandArgs | None = None) -> int:
    """Run the RouterShell interactive CLI."""
    parser = argparse.ArgumentParser(description="Run RouterShell.")
    parser.add_argument(
        "--config-file",
        type=Path,
        help="Load RouterShell commands from a configuration file and exit.",
    )
    parser.add_argument(
        "-f",
        "--factory-reset",
        action="store_true",
        help="Run the factory reset workflow.",
    )
    args = parser.parse_args(argv)

    if args.factory_reset:
        return factory_reset()

    if args.config_file and not args.config_file.is_file():
        parser.error(f"configuration file not found: {args.config_file}")

    configure_logging()

    from routershell.lib.cli.router_main_cli import RouterCLI

    router_cli = RouterCLI(system_start_up=True)
    if args.config_file:
        if router_cli.run(config_file=args.config_file) == STATUS_NOK:
            return 1
    else:
        router_cli.run()

    return 0


def factory_reset() -> int:
    """Run the RouterShell factory reset workflow."""
    configure_logging()

    from routershell.lib.system.system_start_up import SystemFactoryReset

    SystemFactoryReset()
    return 0
