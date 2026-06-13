#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

"""RouterShell software QA checker."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TypeAlias

Command: TypeAlias = tuple[str, list[str]]
CommandLabel: TypeAlias = str
ExitCode: TypeAlias = int


def _repo_root() -> Path:
    """Return the RouterShell repository root."""
    return Path(__file__).resolve().parents[2]


def _run_command(label: CommandLabel, command: Sequence[str], repo_root: Path) -> ExitCode:
    """Run one QA command and return its exit code."""
    print(f"\n=== [{label}] running: {' '.join(command)} ===", flush=True)
    try:
        process = subprocess.run(command, check=False, cwd=repo_root)
    except FileNotFoundError:
        print(f"=== [{label}] NOT FOUND on PATH ===", flush=True)
        return 127

    if process.returncode == 0:
        print(f"=== [{label}] OK ===", flush=True)
    else:
        print(f"=== [{label}] FAILED (exit code {process.returncode}) ===", flush=True)

    return process.returncode


def _build_commands(include_pyright: bool, include_pycycle: bool, pytest_args: Sequence[str]) -> list[Command]:
    """Build the ordered RouterShell QA command list."""
    python_bin = sys.executable
    commands: list[Command] = [
        (
            "pyproject metadata",
            [
                python_bin,
                "-c",
                (
                    "import tomllib; "
                    "from pathlib import Path; "
                    "data = tomllib.loads(Path('pyproject.toml').read_text()); "
                    "assert data['project']['name'] == 'routershell'; "
                    "assert data['project']['scripts']['routershell'] == 'routershell.cli:main'; "
                    "assert data['project']['scripts']['routershell-factory-reset'] == 'routershell.cli:factory_reset'; "
                    "assert data['project']['scripts']['routershell-software-qa-checker'] "
                    "== 'tools.release.qa_checker:main'"
                ),
            ],
        ),
        ("version consistency", [python_bin, "tools/release/check_version.py"]),
        (
            "compile source",
            [
                python_bin,
                "-m",
                "compileall",
                "-q",
                "src",
                "tests",
                "tools/examples",
                "tools/hardware",
                "tools/release",
                "tools/support",
            ],
        ),
        (
            "shell syntax",
            [
                "bash",
                "-c",
                'find start.sh install tools -path "tools/agent-review" -prune -o -name "*.sh" -exec bash -n {} \\;',
            ],
        ),
        ("ruff", [python_bin, "-m", "ruff", "check", "."]),
        ("pytest", [python_bin, "-m", "pytest", *pytest_args]),
    ]

    if include_pyright:
        commands.insert(5, ("pyright", [python_bin, "-m", "pyright"]))

    if include_pycycle:
        commands.append(("pycycle", ["pycycle", "--here"]))

    return commands


def _parse_args(argv: Sequence[str]) -> tuple[argparse.Namespace, list[str]]:
    """Parse QA checker arguments and pytest passthrough arguments."""
    parser = argparse.ArgumentParser(description="Run RouterShell software QA checks.")
    parser.add_argument("--with-pyright", action="store_true", help="Run pyright after Ruff.")
    parser.add_argument("--skip-pycycle", action="store_true", help="Skip import cycle detection.")

    if "--" not in argv:
        return parser.parse_args(argv), []

    separator_index = list(argv).index("--")
    return parser.parse_args(argv[:separator_index]), list(argv[separator_index + 1:])


def main(argv: Sequence[str] | None = None) -> None:
    """Run the standard RouterShell software QA suite."""
    parsed_args, pytest_args = _parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = _repo_root()
    include_pycycle = not parsed_args.skip_pycycle

    if include_pycycle and shutil.which("pycycle") is None:
        print("[skip]  pycycle (not installed); install dev extras to enable cycle checks", flush=True)
        include_pycycle = False

    commands = _build_commands(
        include_pyright=parsed_args.with_pyright,
        include_pycycle=include_pycycle,
        pytest_args=pytest_args,
    )

    overall_exit_code = 0
    for label, command in commands:
        exit_code = _run_command(label, command, repo_root)
        if exit_code != 0 and overall_exit_code == 0:
            overall_exit_code = exit_code

    print("\n=== RouterShell Software QA Suite Finished ===", flush=True)
    if overall_exit_code == 0:
        print("All checks passed.", flush=True)
    else:
        print(f"One or more checks failed (exit code {overall_exit_code}).", flush=True)

    raise SystemExit(overall_exit_code)


if __name__ == "__main__":
    main()
