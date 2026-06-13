"""Module execution for RouterShell."""

from __future__ import annotations

import argparse

from routershell import cli


def main() -> int:
    """Run RouterShell from ``python -m routershell``."""
    parser = argparse.ArgumentParser(description="Run RouterShell from the source tree.")
    parser.add_argument(
        "-f",
        "--factory-reset",
        action="store_true",
        help="Run the factory reset workflow.",
    )
    args = parser.parse_args()

    if args.factory_reset:
        return cli.factory_reset()
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
