### Summary
Cleaned the RouterShell project root by removing stale manual test scripts and old src entry points, then moved useful packaging smoke tests into a clearer tests/packaging layout. Added package-native module execution with python -m routershell and simplified start.sh to use it.

### Modified Files
- README.md
- bridge_db-test.py (deleted)
- bridge_factory.py (deleted)
- src/factory-reset.py (deleted)
- src/main.py (deleted)
- start.sh
- test.py (deleted)
- tests/test_packaging.py (deleted)
- routershell/__main__.py
- tests/packaging/test_entry_points.py
- tests/packaging/test_imports.py
- tests/packaging/test_version.py
- tools/git/README.md
- tools/git/git-common.sh

### Commands Executed And Results
- `rg -n "bridge_db-test|bridge_factory|test\\.py|src/main|src/factory-reset|tests/test_packaging|python3 -m routershell|./start.sh|factory-reset.py|main.py" README.md pyproject.toml tests tools install routershell start.sh CODING_AGENT.md -g !tools/agent-review/**` -> pass; only new source-run README references remain
- `python3 -m py_compile routershell/__init__.py routershell/__main__.py routershell/_version.py routershell/cli.py tests/packaging/test_entry_points.py tests/packaging/test_imports.py tests/packaging/test_version.py` -> pass
- `bash -n start.sh install/install.sh install/uninstall.sh tools/git/git-common.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh tools/vm/multipass-common.sh tools/vm/multipass-create.sh tools/vm/multipass-test-install.sh tools/vm/multipass-shell.sh tools/vm/multipass-destroy.sh` -> pass
- `python3 -m routershell --help` -> pass; module help printed
- `./start.sh --help` -> pass; delegated to module help
- `/tmp/routershell-root-clean-check/bin/python -m pytest` -> pass; 4 tests passed
- `/tmp/routershell-root-clean-check/bin/python -m ruff check routershell tests/packaging tools/release/check_version.py tools/release/release.py tools/support/bump_version.py` -> pass
- `/tmp/routershell-root-clean-check/bin/python -m build` -> pass; sdist and wheel built
- `python3 tools/release/check_version.py && bash -c source tools/git/git-common.sh; rs_run_quality_gates` -> pass available gates; pytest and Ruff skipped for system Python because they are not installed there
- `rm -rf .pytest_cache .ruff_cache __pycache__ tests/__pycache__ tests/packaging/__pycache__ src build dist routershell.egg-info` -> pass; removed ignored/generated local cleanup directories

### Tests
- `pytest` -> pass; 4 tests passed
- `ruff` -> pass on touched Python files and tests
- `python -m build` -> pass
- `tools/release/check_version.py` -> pass

### Notes / Warnings
- Deleted root-level manual scripts because they were host-mutating scratch utilities, not automated tests.
- `start.sh` remains as a thin convenience wrapper around `python3 -m routershell`.

### Remaining TODOs / Follow-Ups
- None

# FILE: bridge_db-test.py
Deleted during project-root and tests cleanup.

# FILE: bridge_factory.py
Deleted during project-root and tests cleanup.

# FILE: src/factory-reset.py
Deleted during project-root and tests cleanup.

# FILE: src/main.py
Deleted during project-root and tests cleanup.

# FILE: test.py
Deleted during project-root and tests cleanup.

# FILE: tests/test_packaging.py
Deleted during project-root and tests cleanup.

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
python3 -m routershell
```

Run the factory reset workflow from source with:

```bash
python3 -m routershell --factory-reset
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

Build distribution artifacts with:

```bash
python -m build
```

Run validation with:

```bash
python -m pytest
python -m ruff check .
```

## Git Helpers

Git helper scripts live under `tools/git/`:

```bash
./tools/git/git-save.sh --commit-msg "Update RouterShell"
./tools/git/git-push.sh --commit-msg "Update RouterShell"
```

See [RouterShell Git Helpers](tools/git/README.md) for save, push, and guarded branch
history reset workflows.

## Release Helpers

Release helper scripts live under `tools/release/`:

```bash
./tools/release/check_version.py
./tools/release/release.py --next patch --dry-run
```

See [RouterShell Release Helpers](tools/release/README.md) for version checks,
dry runs, releases, and commit reports.

## [TODO](todo.md)

# FILE: start.sh
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python3}"

cd "${PROJECT_ROOT}"
mkdir -p /tmp/log
exec "${PYTHON_BIN}" -m routershell "$@"

# FILE: routershell/__main__.py
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

# FILE: tests/packaging/test_entry_points.py
"""Console entry point metadata smoke tests."""

from __future__ import annotations

from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_pyproject_declares_console_entry_points() -> None:
    """Verify packaged console scripts point at package entry functions."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    scripts = pyproject["project"]["scripts"]

    assert scripts["routershell"] == "routershell.cli:main"
    assert scripts["routershell-factory-reset"] == "routershell.cli:factory_reset"


def test_routershell_entry_point_functions_are_importable() -> None:
    """Verify console entry point functions import without starting the CLI."""
    from routershell import cli

    assert callable(cli.main)
    assert callable(cli.factory_reset)

# FILE: tests/packaging/test_imports.py
"""Import compatibility smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path


def test_lib_package_adds_legacy_import_path() -> None:
    """Importing ``lib`` exposes the existing top-level package path."""
    import lib

    lib_path = str(Path(lib.__file__).resolve().parent)

    assert lib_path in sys.path

# FILE: tests/packaging/test_version.py
"""Package version smoke tests."""

from __future__ import annotations

from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_package_version_matches_pyproject() -> None:
    """Verify package version resolves from project metadata."""
    import routershell

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    assert routershell.__version__ == pyproject["project"]["version"]

# FILE: tools/git/README.md
# RouterShell Git Helpers

These scripts provide RouterShell Git workflow helpers adapted from the PyPNM
tooling style.

## Save Current Work

Run local quality gates, stage all changes, and create a timestamped commit:

```bash
./tools/git/git-save.sh --commit-msg "Add RouterShell packaging"
```

Push after committing:

```bash
./tools/git/git-save.sh --commit-msg "Add RouterShell packaging" --push
```

## Commit And Push

Create a commit and push the current branch:

```bash
./tools/git/git-push.sh --commit-msg "Add RouterShell packaging"
```

Pushing branches other than `main` or `hot-fix` requires confirmation.

## Reset Branch History

Rewrite a branch as a fresh orphan history:

```bash
./tools/git/git-reset-branch-history.sh --branch main --message "Initial RouterShell clean commit"
```

This command force-pushes. By default it creates a remote backup branch first.
Run it only when you intentionally want to rewrite branch history.

## Quality Gates

The save and push helpers run these RouterShell checks by default:

```bash
./tools/release/check_version.py
python3 -m py_compile routershell/__init__.py routershell/__main__.py routershell/_version.py routershell/cli.py lib/__init__.py
python3 -m compileall -q routershell lib tests tools/release tools/support
bash -n start.sh install/install.sh install/uninstall.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh tools/git/git-common.sh
```

If `pytest` or `ruff` are installed, the helpers also run:

```bash
python3 -m pytest
python3 -m ruff check .
```

Use `--skip-checks` only when you are intentionally saving work that is not
ready for validation.

# FILE: tools/git/git-common.sh
#!/usr/bin/env bash
set -euo pipefail

rs_run_check() {
  local label="$1"
  shift

  echo "[check] ${label}..."
  if "$@"; then
    echo "[pass]  ${label}"
  else
    echo "[fail]  ${label}" >&2
    exit 1
  fi
}

rs_require_git_repo() {
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: This script must be run inside a Git repository." >&2
    exit 1
  fi
}

rs_repo_root() {
  git rev-parse --show-toplevel
}

rs_python() {
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi

  echo "ERROR: python3 or python is required." >&2
  exit 1
}

rs_run_quality_gates() {
  local python_bin
  python_bin="$(rs_python)"

  rs_run_check "pyproject metadata" "${python_bin}" - <<'PY'
import tomllib
from pathlib import Path

with Path("pyproject.toml").open("rb") as handle:
    pyproject = tomllib.load(handle)

assert pyproject["project"]["name"] == "routershell"
assert pyproject["project"]["scripts"]["routershell"] == "routershell.cli:main"
assert pyproject["project"]["scripts"]["routershell-factory-reset"] == "routershell.cli:factory_reset"
PY

  rs_run_check "version consistency" "${python_bin}" tools/release/check_version.py
  rs_run_check "compile packaging files" "${python_bin}" -m py_compile routershell/__init__.py routershell/__main__.py routershell/_version.py routershell/cli.py lib/__init__.py
  rs_run_check "compile source tree" "${python_bin}" -m compileall -q routershell lib tests tools/release tools/support
  rs_run_check "shell syntax" bash -n start.sh install/install.sh install/uninstall.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh tools/git/git-common.sh

  if "${python_bin}" -m pytest --version >/dev/null 2>&1; then
    rs_run_check "pytest" "${python_bin}" -m pytest
  else
    echo "[skip]  pytest (not installed)"
  fi

  if "${python_bin}" -m ruff --version >/dev/null 2>&1; then
    rs_run_check "ruff check" "${python_bin}" -m ruff check .
  else
    echo "[skip]  ruff check (not installed)"
  fi
}
