from __future__ import annotations

import sys

from tools.release.qa_checker import _build_commands, _parse_args


def test_build_commands_includes_standard_router_shell_gates() -> None:
    commands = _build_commands(include_pyright=False, include_pycycle=True, pytest_args=[])
    labels = [label for label, _command in commands]

    assert labels == [
        "pyproject metadata",
        "version consistency",
        "compile source",
        "shell syntax",
        "ruff",
        "pytest",
        "pycycle",
    ]


def test_build_commands_adds_pyright_before_pytest() -> None:
    commands = _build_commands(include_pyright=True, include_pycycle=False, pytest_args=["-k", "typing"])
    labels = [label for label, _command in commands]
    pytest_command = dict(commands)["pytest"]

    assert labels == [
        "pyproject metadata",
        "version consistency",
        "compile source",
        "shell syntax",
        "ruff",
        "pyright",
        "pytest",
    ]
    assert pytest_command == [sys.executable, "-m", "pytest", "-k", "typing"]


def test_parse_args_splits_pytest_passthrough() -> None:
    parsed_args, pytest_args = _parse_args(["--with-pyright", "--", "-k", "fast"])

    assert parsed_args.with_pyright is True
    assert parsed_args.skip_pycycle is False
    assert pytest_args == ["-k", "fast"]
