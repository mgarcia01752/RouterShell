### Summary
RouterShell now has a PyPNM-style software QA checker located under root release tooling at tools/release/qa_checker.py. The checker standardizes metadata, version, compile, shell syntax, Ruff, pytest, optional Pyright, and pycycle checks, with docs and unit coverage.

### Modified Files
- README.md
- pyproject.toml
- tools/release/qa_checker.py
- tools/release/README.md
- doc/tests/software-qa.md
- tests/tools/test_qa_checker.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/ruff check tools/release/qa_checker.py tests/tools/test_qa_checker.py pyproject.toml` -> pass; All checks passed
- `/opt/routershell/venv/bin/python -m pytest tests/tools/test_qa_checker.py` -> pass; 3 passed
- `/opt/routershell/venv/bin/python tools/release/qa_checker.py` -> pass; 14 passed, pycycle skipped because it is not installed in the current venv
- `/opt/routershell/venv/bin/python -m tools.release.qa_checker --skip-pycycle -- -k test_qa_checker` -> pass; 3 passed, 11 deselected
- `/opt/routershell/venv/bin/ruff check .` -> pass; All checks passed
- `/opt/routershell/venv/bin/python -m pytest` -> pass; 14 passed

### Tests
- `pytest tests/tools/test_qa_checker.py` -> pass; 3 passed
- `python tools/release/qa_checker.py` -> pass; full available QA sweep passed with 14 tests
- `ruff` -> pass for new checker files and full project

### Notes / Warnings
- pycycle was added to dev extras but is not installed in the current /opt/routershell/venv until dev dependencies are reinstalled.
- The checker source intentionally lives under tools/release rather than src/routershell.

### Remaining TODOs / Follow-Ups
- Reinstall dev extras and run routershell-software-qa-checker once pycycle is available.

# FILE: README.md
# RouterShell (WORK IN PROGRESS)

RouterShell is an open-source, IOS-like CLI distribution written in Python 3. It is designed to provide a flexible and user-friendly command-line interface for network administrators and enthusiasts, offering a comprehensive range of networking features and capabilities tailored to diverse needs.

**Key Features of RouterShell:**

1. **Interface Configurations:** RouterShell supports a variety of interface configurations, including:
   - **Loopback Interfaces:** Ideal for testing and diagnostics, loopback interfaces are easy to set up and provide a versatile tool for network validation.
   - **Physical Interfaces:** Compatibility with Ethernet, USB, wireless (WiFi and cellular) interfaces, making it adaptable to various hardware environments.
   - **Bridging:** Enables the connection of different network segments, which is beneficial in creating complex network topologies.
   - **VLAN Support:** Facilitates network segmentation and organization, which is crucial for larger, more intricate networks.

2. **Tunneling:** RouterShell includes support for tunneling protocols, such as GRE (Generic Routing Encapsulation), allowing the creation of point-to-point and point-to-multipoint tunnels. This feature enables the encapsulation of packets for secure and efficient transport across different network segments, which is useful in VPNs and cross-network communication.

3. **NAT (Network Address Translation) Support:** Provides NAT functionality, essential for translating private IP addresses to public IP addresses, commonly required in both home and enterprise network setups. This feature helps in conserving public IP addresses and adds a layer of security by masking internal network structures.

4. **Access Control List (ACL) and Firewall Support:** RouterShell supports ACLs and firewall functionalities, offering enhanced network security by controlling incoming and outgoing traffic based on predefined rules. This is crucial for protecting network resources and managing data flow effectively.

RouterShell aims to provide a comprehensive CLI experience similar to traditional network operating systems, with the flexibility and extensibility of Python, making it a valuable tool for managing and automating network environments.


Regarding its intended use:

- **Quick Router Deployment:** RouterShell is designed to expedite router setup using a minimal Linux image, a valuable feature when rapid deployment is crucial.

- **Router-on-a-Stick Configuration:** RouterShell supports the "router-on-a-stick" configuration, useful for scenarios requiring network segmentation.

- **Compatibility with Embedded Router Distributions:** While initially developed with a focus on Ubuntu, RouterShell's lower layers are designed to be OS-agnostic, potentially allowing compatibility with various lightweight Linux distributions.

In conclusion, RouterShell is a router CLI distribution with features well-suited for specific network setups and security requirements. However, it is crucial to thoroughly assess your specific networking needs and consider whether RouterShell aligns with them before selecting it as your networking solution. Its comprehensive feature set, including NAT support and access control list/firewall support, makes it a versatile choice for network administrators and enthusiasts looking to configure and manage network infrastructure efficiently.

## Table of Contents

- [Global Privileged EXEC Commands](doc/cli/global_priv_exec_cmd.md): Learn about global privileged EXEC commands for system-level tasks.

- [ARP (Address Resolution Protocol)](doc/cli/configure/arp.md): Understand ARP and how it works in RouterShell.

- [Bridge Configuration](doc/cli/configure/bridge.md): Configure and manage bridges in RouterShell.

- [DHCPv4/v6 Configuration](doc/cli/configure/dhcp.md): Explore DHCP (Dynamic Host Configuration Protocol) setup for IPv4 and IPv6.

- [Interface Configuration](doc/cli/configure/config.md): Configure and manage network interfaces in RouterShell.

- [NAT (Network Address Translation)](doc/cli/configure/nat.md): Set up Network Address Translation for your RouterShell router.

- [Route Configuration](doc/cli//configureroute.md): Understand the routing and how to configure it in RouterShell.

- [VLAN Configuration](doc/cli//configurevlan.md): Configure and manage VLANs in your RouterShell network.

- [System Configuration](doc/cli/global/system.md): Learn about system-level configuration options in RouterShell.

- [Wireless Configuration](doc/cli/configure/wireless.md): Explore wireless network configuration in RouterShell.

## Router Configuration Examples

Explore a variety of router configuration examples to help you get started with RouterShell:

These examples cover scenarios like configuring a four-port bridge with VLAN support, setting up a four-port switch, and configuring NAT for a two-port setup. You can access the detailed instructions and information in the respective configuration files.

- [Four-Port Bridge with VLAN Configuration](doc/cli/four_port_bridge_vlan_config.md): This example guides you through setting up a four-port bridge with VLAN support, allowing for network segmentation and efficient traffic management.

- [Four-Port Switch Configuration](doc/cli/four_port_switch_config.md): Learn how to configure a four-port switch, which is essential for creating a network with multiple connected devices.

- [Two-Port NAT Configuration](doc/cli/two_port_nat_config.md): Understand how to set up Network Address Translation (NAT) for a two-port router, enabling the translation of private IP addresses to public IP addresses.

These configuration examples serve as practical guides to help you implement specific networking setups with RouterShell. Refer to the linked documentation files for step-by-step instructions and detailed explanations.

Feel free to explore these examples and adapt them to your networking needs. If you have any questions or need further assistance, don't hesitate to contact our community or project team. Thank you for choosing RouterShell!

## Additional Resources

Please select the specific documentation file you are interested in from the table of contents above to access detailed information and instructions for configuring and using RouterShell.

If you have any questions or need further assistance, please feel free to reach out to our community or project team. Thank you for choosing RouterShell!

- [RouterShell FAQ](doc/faq.md)

## Linux Runtime Install

[README INSTALLATION](install/README.md)

RouterShell includes a generic installer for non-embedded Linux hosts such as
Ubuntu, Debian, Fedora, RHEL-compatible systems, and openSUSE. Embedded and
BusyBox-style targets are intentionally out of scope for this installer.

Production install is the default.
The installer captures a root-only baseline snapshot under
`/var/lib/routershell/baseline` before making install changes.

Test installer changes in a disposable VM before running them on a development
workstation. Use `--development` only when testing editable installs with dev
dependencies; see [RouterShell VM Install Testing](tools/vm/README.md).

```bash
sudo ./install/install.sh
routershell
```

## Run RouterShell From Source

```bash
PYTHONPATH=src python3 -m routershell
```

Run the factory reset workflow from source with:

```bash
PYTHONPATH=src python3 -m routershell --factory-reset
```

## Python Development Install

RouterShell now includes Python packaging metadata in `pyproject.toml`.
For local development, use an isolated virtual environment and install the
project in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

After installation, run the CLI entry point:

```bash
routershell
```

Factory reset is also exposed as a console entry point:

```bash
routershell-factory-reset
```

Runtime logs default to `/tmp/log/routershell.log`. Override logging for one
run with environment variables such as:

```bash
ROUTERSHELL_LOG_LEVEL=DEBUG routershell
```

Build distribution artifacts with:

```bash
python -m build
```

Run validation with:

```bash
python -m pytest
python -m ruff check .
```

Or run the standard software QA sweep with:

```bash
routershell-software-qa-checker
```

See [RouterShell Software QA Checker](doc/tests/software-qa.md) for the full
check sequence and options.

## Git Helpers

Git helper scripts live under `tools/git/`:

```bash
./tools/git/git-save.sh --commit-msg "Update RouterShell"
./tools/git/git-push.sh --commit-msg "Update RouterShell"
```

See [RouterShell Git Helpers](tools/git/README.md) for save, push, and guarded branch
history reset workflows.

## Tools

Operational and development tools are grouped under `tools/` by purpose.
Review [RouterShell Tools Layout](tools/reference/tools-layout.md) before
running scripts that can alter disks, networking, packages, or services.

## Release Helpers

Release helper scripts live under `tools/release/`:

```bash
./tools/release/check_version.py
./tools/release/release.py --next patch --dry-run
```

See [RouterShell Release Helpers](tools/release/README.md) for version checks,
dry runs, releases, and commit reports.

## License

RouterShell is licensed under the [Apache License 2.0](LICENSE). Distributions
must retain the [NOTICE](NOTICE) file.

## [TODO](todo.md)

# FILE: pyproject.toml
# SPDX-License-Identifier: Apache-2.0

[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "routershell"
version = "0.1.0"
description = "IOS-like Python CLI distribution for Linux router configuration workflows."
readme = "README.md"
requires-python = ">=3.10"
license = "Apache-2.0"
license-files = ["LICENSE", "NOTICE"]
authors = [
    { name = "Maurice Garcia" },
]
keywords = [
    "cli",
    "linux",
    "networking",
    "router",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: System Administrators",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: System :: Networking",
    "Topic :: System :: Systems Administration",
    "Typing :: Typed",
]
dependencies = [
    "argcomplete>=3.0",
    "beautifulsoup4>=4.12",
    "cmd2>=2.4",
    "jc>=1.25",
    "prettytable>=3.0",
    "prompt-toolkit>=3.0",
    "pyte>=0.8",
    "tabulate>=0.9",
]

[project.optional-dependencies]
dev = [
    "build>=1.2",
    "pycycle>=0.0.8",
    "pyright>=1.1.407",
    "pytest>=8.0",
    "ruff>=0.5",
    "twine>=5.0",
]

[project.scripts]
routershell = "routershell.cli:main"
routershell-factory-reset = "routershell.cli:factory_reset"
routershell-software-qa-checker = "tools.release.qa_checker:main"

[project.urls]
Homepage = "https://github.com/mgarcia01752/RouterShell"
Repository = "https://github.com/mgarcia01752/RouterShell"

[tool.setuptools]
package-dir = { "" = "src" }
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]
include = ["routershell*"]
namespaces = true

[tool.setuptools.package-data]
"routershell" = ["py.typed"]
"routershell.lib.db.sqlite_db" = ["*.sql"]
"routershell.lib.network_services.dhcp.dnsmasq" = ["*.conf"]

[tool.pytest.ini_options]
addopts = "-ra"
pythonpath = [
    "src",
]
testpaths = [
    "tests",
]

[tool.ruff]
src = ["src"]
target-version = "py310"
line-length = 120
exclude = [
    "tools",
    "src/routershell/lib/cli/config-bak",
    "**/*-bak.py",
    "**/*-orig.py",
]

[tool.ruff.lint]
select = [
    "F",
    "E",
    "W",
    "I",
    "B",
    "UP",
    "ANN",
    "SIM",
    "PERF",
]
ignore = [
    "E501",
    "B006",
    "ANN001",
    "ANN002",
    "ANN003",
    "ANN201",
    "ANN202",
    "ANN204",
    "ANN205",
    "ANN206",
    "W291",
    "W292",
    "W293",
    "B007",
    "B018",
    "B024",
    "B904",
    "E711",
    "F811",
    "F841",
    "SIM",
    "PERF",
    "UP022",
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "ANN",
]

[tool.pyright]
pythonVersion = "3.10"
pythonPlatform = "Linux"
include = ["src"]
exclude = [
    "**/__pycache__",
]
venvPath = "."
venv = ".venv"

# FILE: tools/release/qa_checker.py
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

# FILE: tools/release/README.md
# RouterShell Release Helpers

These scripts provide the RouterShell release workflow adapted from the PyPNM
release tooling.

## Version Check

Verify that the package version and `pyproject.toml` agree:

```bash
./tools/release/check_version.py
```

JSON output is also available:

```bash
./tools/release/check_version.py --json
```

## Software QA Checker

Run the standard local QA sweep:

```bash
./tools/release/qa_checker.py
```

After an editable dev install, the same checker is available as:

```bash
routershell-software-qa-checker
```

See [RouterShell Software QA Checker](../../doc/tests/software-qa.md) for the
full check sequence and options.

## Release Dry Run

Show the planned release steps without changing files:

```bash
./tools/release/release.py --next patch --dry-run
```

Supported version bump modes are:

```bash
--next major
--next minor
--next patch
```

An explicit version can also be supplied:

```bash
./tools/release/release.py --version 0.2.0 --dry-run
```

## Actual Release

Run from `main` or `hot-fix` with a clean working tree and an activated virtual
environment containing development dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
./tools/release/release.py --next patch
```

The release command updates version files, runs checks, commits the version
bump, creates an annotated tag, pushes the branch and tag, and writes a release
report under `release-reports/`.

Version updates are delegated to:

```bash
./tools/support/bump_version.py
```

Use this mode to test version changes and checks without committing or tagging:

```bash
./tools/release/release.py --next patch --test-release
```

## Commit Reports

Generate a release-style report for the current commit:

```bash
./tools/release/release.py --latest-commit-report
```

Generate a report for the previous commit:

```bash
./tools/release/release.py --last-commit-report
```

## Test Runner

Run unittest-compatible tests without pytest:

```bash
./tools/release/test-runner.py
```

# FILE: doc/tests/software-qa.md
# RouterShell Software QA Checker

RouterShell includes a lightweight software QA checker for local development
and simple CI pipelines.

Install development dependencies first:

```bash
python -m pip install -e ".[dev]"
```

Run the standard QA suite:

```bash
routershell-software-qa-checker
```

The checker source lives under `tools/release/qa_checker.py`.

The default suite runs:

- pyproject console-script metadata sanity check
- version consistency check
- Python source compilation
- shell script syntax checks
- Ruff
- pytest
- pycycle import cycle detection, when installed

Include Pyright static type checking with:

```bash
routershell-software-qa-checker --with-pyright
```

Skip pycycle when needed:

```bash
routershell-software-qa-checker --skip-pycycle
```

Pass additional arguments to pytest after `--`:

```bash
routershell-software-qa-checker -- -k typing --maxfail=1
```

The command exits with `0` when all selected checks pass. It returns the first
non-zero exit code when any selected check fails.

# FILE: tests/tools/test_qa_checker.py
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

