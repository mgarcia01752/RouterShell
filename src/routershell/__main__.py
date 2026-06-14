"""Module execution for RouterShell."""

from __future__ import annotations

from routershell import cli


def main() -> int:
    """Run RouterShell from ``python -m routershell``."""
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())
