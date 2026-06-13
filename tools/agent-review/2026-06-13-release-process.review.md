### Summary
Added RouterShell release tooling adapted from PyPNM's release workflow and support tooling. The new process includes version consistency checks, support-based version bumping, dry-run releases, actual release automation, commit reports, a pytest-style function test runner fallback, and release documentation.

### Modified Files
- .gitignore
- README.md
- pyproject.toml
- routershell_version.py
- tests/test_packaging.py
- tools/git/README.md
- tools/git/git-common.sh
- tools/release/README.md
- tools/release/check_version.py
- tools/release/release.py
- tools/release/test-runner.py
- tools/support/README.md
- tools/support/bump_version.py

### Commands Executed And Results
- `find /home/dev01/Projects/PyPNM/tools/release -maxdepth 3 -type f -print | sort` → pass; identified PyPNM source release scripts.
- `sed -n '1,1160p' /home/dev01/Projects/PyPNM/tools/release/release.py` → pass; read source release workflow.
- `find /home/dev01/Projects/PyPNM/tools/support -maxdepth 3 -type f -print | sort` → pass; identified support bump script.
- `sed -n '1,420p' /home/dev01/Projects/PyPNM/tools/support/bump_version.py` → pass; read source support workflow.
- `python3 tools/support/bump_version.py --current` → pass; current version is 0.1.0.
- `python3 tools/support/bump_version.py --next patch --version-files-only && python3 tools/release/check_version.py && python3 tools/support/bump_version.py 0.1.0 --version-files-only && python3 tools/release/check_version.py` → pass; temporary bump to 0.1.1 succeeded and was restored to 0.1.0.
- `python3 tools/release/check_version.py` → pass; `routershell_version.py` and `pyproject.toml` both report 0.1.0.
- `python3 tools/release/check_version.py --json` → pass; emitted JSON status ok.
- `python3 -m py_compile tools/release/check_version.py tools/release/release.py tools/release/test-runner.py routershell_version.py tools/support/bump_version.py` → pass.
- `bash -n tools/git/git-common.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh start.sh install/install.sh install/uninstall.sh` → pass.
- `python3 tools/release/test-runner.py` → pass; 4/4 packaging smoke tests passed using function-test fallback.
- `python3 tools/release/release.py --next patch --dry-run` → pass; planned 0.1.0 -> 0.1.1.
- `python3 tools/release/release.py --latest-commit-report` → pass; generated report, then generated output was removed and report directories were added to `.gitignore`.
- `bash -c 'source tools/git/git-common.sh; rs_run_quality_gates'` → pass; available checks passed; pytest and ruff skipped because not installed.
- `find . -name '__pycache__' -type d -prune -exec rm -rf {} +` → pass; removed generated validation caches.

### Tests
- `tools/release/test-runner.py` → pass; 4/4 function tests passed.
- `pytest` → skipped by quality gate because pytest is not installed in this interpreter.
- `ruff` → skipped by quality gate because Ruff is not installed in this interpreter.
- `bash -n` → pass for release and git-adjacent shell scripts.
- RouterShell quality gates → pass for available checks.

### Notes / Warnings
- Actual releases require a clean working tree, `main` or `hot-fix`, and an active virtual environment with development dependencies installed.
- Dry-run releases are allowed from development branches.
- Generated `release-reports/` and `test_reports/` directories are ignored by git.
- The current environment lacks `pip`, `build`, `pytest`, and `ruff`, so full release build/test/lint execution is blocked until `.[dev]` is installed in a virtual environment.

### Remaining TODOs / Follow-Ups
- Run `python -m pip install -e ".[dev]"` in a virtual environment, then verify actual `python -m pytest`, `python -m ruff check .`, and `python -m build`.
- Decide whether RouterShell should add secret scanning release gates similar to PyPNM once security tooling exists under `tools/security/`.

# FILE: .gitignore
# vscode
*.code-workspace

# databases - sqlite
*.db

#RouterShell Configurations
config/*.cfg*

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/
release-reports/
test_reports/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore
#  and can be added to the global gitignore or merged into this file.  For a more nuclear
#  option (not recommended) you can uncomment the following to ignore the entire idea folder.
#.idea/

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

## Running RouterShell (Temporary until install script is ready)

[README INSTALLATION](install/README.md)

## Run RouterShell

```bash
./start.sh
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

# FILE: pyproject.toml
[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "routershell"
version = "0.1.0"
description = "IOS-like Python CLI distribution for Linux router configuration workflows."
readme = "README.md"
requires-python = ">=3.10"
license = "GPL-2.0-or-later"
license-files = ["LICENSE"]
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
    "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: System :: Networking",
    "Topic :: System :: Systems Administration",
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
    "pytest>=8.0",
    "ruff>=0.5",
    "twine>=5.0",
]

[project.scripts]
routershell = "routershell:main"
routershell-factory-reset = "routershell:factory_reset"

[project.urls]
Homepage = "https://github.com/mgarcia01752/RouterShell"
Repository = "https://github.com/mgarcia01752/RouterShell"

[tool.setuptools]
py-modules = ["routershell", "routershell_version"]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
include = ["lib*"]
namespaces = true

[tool.setuptools.package-data]
"lib.db.sqlite_db" = ["*.sql"]
"lib.network_services.dhcp.dnsmasq" = ["*.conf"]

[tool.pytest.ini_options]
addopts = "-ra"
testpaths = [
    "tests",
]

[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = [
    "E",
    "F",
    "I",
    "W",
]

# FILE: routershell_version.py
"""RouterShell package version."""

from __future__ import annotations

__version__: str = "0.1.0"

# FILE: tests/test_packaging.py
"""Packaging metadata and entry point smoke tests."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_declares_console_entry_points() -> None:
    """Verify the packaged console scripts point at the compatibility launcher."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    scripts = pyproject["project"]["scripts"]

    assert scripts["routershell"] == "routershell:main"
    assert scripts["routershell-factory-reset"] == "routershell:factory_reset"


def test_lib_package_adds_legacy_import_path() -> None:
    """Importing ``lib`` exposes the legacy top-level package path."""
    import lib

    lib_path = str(Path(lib.__file__).resolve().parent)

    assert lib_path in sys.path


def test_routershell_entry_point_functions_are_importable() -> None:
    """The console entry point functions can be imported without starting the CLI."""
    import routershell

    assert callable(routershell.main)
    assert callable(routershell.factory_reset)


def test_version_module_matches_pyproject() -> None:
    """The package version module and pyproject version stay aligned."""
    import routershell_version

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    assert routershell_version.__version__ == pyproject["project"]["version"]

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
python3 -m py_compile routershell.py lib/__init__.py
python3 -m compileall -q src lib tools/release tools/support bridge_factory.py bridge_db-test.py test.py routershell_version.py
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
assert pyproject["project"]["scripts"]["routershell"] == "routershell:main"
assert pyproject["project"]["scripts"]["routershell-factory-reset"] == "routershell:factory_reset"
PY

  rs_run_check "version consistency" "${python_bin}" tools/release/check_version.py
  rs_run_check "compile packaging files" "${python_bin}" -m py_compile routershell.py lib/__init__.py
  rs_run_check "compile source tree" "${python_bin}" -m compileall -q src lib tools/release tools/support bridge_factory.py bridge_db-test.py test.py routershell_version.py
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

# FILE: tools/release/README.md
# RouterShell Release Helpers

These scripts provide the RouterShell release workflow adapted from the PyPNM
release tooling.

## Version Check

Verify that `routershell_version.py` and `pyproject.toml` agree:

```bash
./tools/release/check_version.py
```

JSON output is also available:

```bash
./tools/release/check_version.py --json
```

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

# FILE: tools/release/check_version.py
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""Verify RouterShell version consistency."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


class VersionCheckTool:
    """Verify version consistency between routershell_version.py and pyproject.toml."""

    MAX_ROOT_SEARCH_DEPTH: int = 6
    VERSION_FILE_RELATIVE: str = "routershell_version.py"
    PYPROJECT_RELATIVE: str = "pyproject.toml"
    VERSION_PATTERN: str = r'__version__\s*(?::\s*[^=]+)?=\s*"([^"]+)"'
    PYPROJECT_PATTERN: str = r'^\s*version\s*=\s*"([^"]+)"\s*$'
    EXIT_OK: int = 0
    EXIT_ERROR: int = 1
    EXIT_MISMATCH: int = 2

    @staticmethod
    def _read_text(path: Path) -> str:
        """Read a file as UTF-8 text; return empty string when unavailable."""
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""

    @staticmethod
    def _find_project_root(start_path: Path) -> Path:
        """Walk upwards to locate pyproject.toml, fallback to start path."""
        current = start_path
        for _ in range(VersionCheckTool.MAX_ROOT_SEARCH_DEPTH):
            if (current / VersionCheckTool.PYPROJECT_RELATIVE).is_file():
                return current
            if current.parent == current:
                break
            current = current.parent
        return start_path

    @staticmethod
    def _read_version_from_file(path: Path) -> str:
        """Extract the __version__ value from routershell_version.py."""
        text = VersionCheckTool._read_text(path)
        if not text:
            return ""
        match = re.search(VersionCheckTool.VERSION_PATTERN, text)
        if not match:
            return ""
        return match.group(1)

    @staticmethod
    def _read_version_from_pyproject(path: Path) -> str:
        """Extract the project version value from pyproject.toml."""
        text = VersionCheckTool._read_text(path)
        if not text:
            return ""
        match = re.search(VersionCheckTool.PYPROJECT_PATTERN, text, re.MULTILINE)
        if not match:
            return ""
        return match.group(1)

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser for the version check tool."""
        parser = argparse.ArgumentParser(
            description="Verify that routershell_version.py and pyproject.toml carry the same version."
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print results as JSON.",
        )
        return parser

    @staticmethod
    def _emit_text(version_file_version: str, pyproject_version: str, status: str) -> None:
        """Emit human-readable output."""
        if status == "error":
            print("Version check failed: unable to read one or more version values.")
        print(f"routershell_version.py: {version_file_version or 'missing'}")
        print(f"pyproject.toml: {pyproject_version or 'missing'}")
        if status == "mismatch":
            print("Version mismatch detected.")
        if status == "ok":
            print("Version match confirmed.")

    @staticmethod
    def _emit_json(version_file_version: str, pyproject_version: str, status: str) -> None:
        """Emit JSON output."""
        payload = {
            "version_py": version_file_version,
            "pyproject": pyproject_version,
            "match": status == "ok",
            "status": status,
        }
        print(json.dumps(payload, ensure_ascii=True))

    @staticmethod
    def run(options: argparse.Namespace) -> int:
        """Print versions from tracked files and return a status code."""
        script_dir = Path(__file__).resolve().parent
        root_path = VersionCheckTool._find_project_root(script_dir)
        version_path = root_path / VersionCheckTool.VERSION_FILE_RELATIVE
        pyproject_path = root_path / VersionCheckTool.PYPROJECT_RELATIVE

        version_file_version = VersionCheckTool._read_version_from_file(version_path)
        pyproject_version = VersionCheckTool._read_version_from_pyproject(pyproject_path)

        if not version_file_version or not pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(version_file_version, pyproject_version, "error")
            else:
                VersionCheckTool._emit_text(version_file_version, pyproject_version, "error")
            return VersionCheckTool.EXIT_ERROR

        if version_file_version != pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(version_file_version, pyproject_version, "mismatch")
            else:
                VersionCheckTool._emit_text(version_file_version, pyproject_version, "mismatch")
            return VersionCheckTool.EXIT_MISMATCH

        if options.json:
            VersionCheckTool._emit_json(version_file_version, pyproject_version, "ok")
        else:
            VersionCheckTool._emit_text(version_file_version, pyproject_version, "ok")
        return VersionCheckTool.EXIT_OK


if __name__ == "__main__":
    parser = VersionCheckTool._build_parser()
    args = parser.parse_args()
    sys.exit(VersionCheckTool.run(args))

# FILE: tools/release/release.py
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""RouterShell release automation."""

from __future__ import annotations

import argparse
import atexit
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Final


VERSION_FILE_PATH: Final[Path] = Path("routershell_version.py")
BUMP_SCRIPT_PATH: Final[Path] = Path("tools/support") / "bump_version.py"
PYPROJECT_FILE_PATH: Final[Path] = Path("pyproject.toml")
README_FILE_PATH: Final[Path] = Path("README.md")
DOCS_ROOT: Final[Path] = Path("doc")
WORKFLOWS_DIR: Final[Path] = Path(".github") / "workflows"
README_TAG_PATTERN: Final[re.Pattern[str]] = re.compile(r'TAG="v\d+\.\d+\.\d+(?:-rc\d+)?"')

VERSION_PART_SEPARATOR: Final[str] = "."
EXPECTED_VERSION_PARTS: Final[int] = 3
MAJOR_INDEX: Final[int] = 0
MINOR_INDEX: Final[int] = 1
PATCH_INDEX: Final[int] = 2
RC_SUFFIX_PREFIX: Final[str] = "-rc"
RC_DEFAULT_NUMBER: Final[int] = 1

REPORT_DIR_NAME: Final[str] = "release-reports"
REPORT_FILE_PREFIX: Final[str] = "release-report"
REPORT_SECTIONS: Final[list[str]] = [
    "Docs",
    "CLI",
    "Database",
    "Networking",
    "Services",
    "Install",
    "Packaging",
    "Tests",
    "Tools",
]
REPORT_HEADERS: Final[list[str]] = ["Section", "Files Changed"]

SUMMARY: dict[str, str] = {}
RELEASE_LOG_DIR: Path | None = None


def _run(
    cmd: list[str],
    check: bool = True,
    *,
    label: str | None = None,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess command, capturing output for logging on failure."""
    if capture_output:
        proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    else:
        proc = subprocess.run(cmd, text=True, check=False)

    if proc.returncode != 0:
        if capture_output:
            _log_command_failure(label or Path(cmd[0]).name, proc)
        if check:
            raise subprocess.CalledProcessError(proc.returncode, cmd, output=proc.stdout, stderr=proc.stderr)
    return proc


def _init_release_logging() -> None:
    """Create a temporary directory for failed-command logs."""
    global RELEASE_LOG_DIR
    if RELEASE_LOG_DIR is not None:
        return
    logs_dir = Path(REPORT_DIR_NAME) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    RELEASE_LOG_DIR = Path(tempfile.mkdtemp(prefix="routershell-release-logs-", dir=str(logs_dir)))
    print(f"[release] Command failures will be logged under: {RELEASE_LOG_DIR}")


def _sanitize_label(label: str) -> str:
    """Return a filesystem-safe label."""
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", label.strip().lower())
    return safe or "cmd"


def _log_command_failure(label: str, result: subprocess.CompletedProcess[str]) -> None:
    """Write stdout and stderr for a failed command."""
    if RELEASE_LOG_DIR is None:
        return
    safe_label = _sanitize_label(label)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = RELEASE_LOG_DIR / f"{safe_label}-{timestamp}.log"
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    args = result.args if isinstance(result.args, list | tuple) else [str(result.args)]
    log_path.write_text(
        f"$ {' '.join(str(arg) for arg in args)}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}\n",
        encoding="utf-8",
    )
    print(f"[release] {label} failed; see {log_path}")


def _format_state(state: str) -> str:
    """Format a release step state."""
    return state.upper()


def _print_status(label: str, state: str) -> None:
    """Record and print a release step status."""
    SUMMARY[label] = state
    print(f"{_format_state(state)} {label}")


def _print_release_summary() -> None:
    """Print the final release step summary."""
    if not SUMMARY:
        return
    print("\nRelease step summary:")
    for label, state in SUMMARY.items():
        print(f" {_format_state(state)} {label}")
    if RELEASE_LOG_DIR:
        print(f"Failure logs, if any, stored in: {RELEASE_LOG_DIR}")


atexit.register(_print_release_summary)


def _ensure_git_repo() -> None:
    """Ensure the current directory is inside a git repository."""
    result = _run(["git", "rev-parse", "--is-inside-work-tree"], check=False, label="git-repo")
    if result.returncode != 0:
        print("ERROR: release must run inside a git repository.", file=sys.stderr)
        sys.exit(1)


def _ensure_clean_worktree() -> None:
    """Ensure the git working tree has no uncommitted changes."""
    result = _run(["git", "status", "--porcelain"], check=False, label="git-status")
    output = (result.stdout or "").strip()
    if output:
        print("ERROR: Working tree is not clean. Commit or stash changes first.", file=sys.stderr)
        sys.exit(1)


def _get_current_branch() -> str:
    """Return the current branch name."""
    result = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], label="git-branch")
    return result.stdout.strip()


def _ensure_release_branch_allowed() -> None:
    """Fail fast unless running on an allowed release branch."""
    current_branch = _get_current_branch()
    if current_branch not in ("main", "hot-fix"):
        print("ERROR: release can only be performed on 'main' or 'hot-fix'.", file=sys.stderr)
        sys.exit(1)


def _get_head_commit() -> str:
    """Return the current HEAD commit."""
    result = _run(["git", "rev-parse", "HEAD"], label="git-rev-parse")
    return result.stdout.strip()


def _get_previous_commit() -> str | None:
    """Return the previous commit if one exists."""
    result = _run(["git", "rev-parse", "HEAD~1"], check=False, label="git-rev-parse-prev")
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _collect_commit_files(commit: str) -> list[str]:
    """Collect file paths touched by a commit."""
    result = _run(["git", "show", "--pretty=format:", "--name-only", commit], label="git-show")
    return [line.strip() for line in (result.stdout or "").splitlines() if line.strip()]


def _classify_path(path: str) -> str:
    """Classify a changed path for release reporting."""
    normalized = path.replace("\\", "/").lower()
    if normalized.startswith("doc/") or normalized == "readme.md":
        return "Docs"
    if normalized.startswith("lib/cli/") or normalized.startswith("src/") or normalized == "routershell.py":
        return "CLI"
    if normalized.startswith("lib/db/"):
        return "Database"
    if normalized.startswith("lib/network_manager/"):
        return "Networking"
    if normalized.startswith("lib/network_services/") or normalized.startswith("lib/system/"):
        return "Services"
    if normalized.startswith("install/") or normalized == "start.sh":
        return "Install"
    if normalized in {"pyproject.toml", "routershell_version.py"}:
        return "Packaging"
    if normalized.startswith("tests/"):
        return "Tests"
    if normalized.startswith("tools/"):
        return "Tools"
    return "Other"


def _summarize_sections(paths: list[str]) -> dict[str, int]:
    """Count changed files by report section."""
    counts = {section: 0 for section in REPORT_SECTIONS}
    counts["Other"] = 0
    for path in paths:
        section = _classify_path(path)
        counts[section] = counts.get(section, 0) + 1
    return counts


def _render_markdown_table(counts: dict[str, int]) -> str:
    """Render a markdown table for section counts."""
    rows = [(section, str(counts.get(section, 0))) for section in REPORT_SECTIONS]
    if counts.get("Other", 0) > 0:
        rows.append(("Other", str(counts["Other"])))
    lines = [f"| {REPORT_HEADERS[0]} | {REPORT_HEADERS[1]} |", "| --- | --- |"]
    lines.extend(f"| {section} | {count} |" for section, count in rows)
    return "\n".join(lines)


def _collect_workflows() -> list[tuple[str, str]]:
    """Collect GitHub workflow names and paths."""
    if not WORKFLOWS_DIR.exists():
        return []
    workflows: list[tuple[str, str]] = []
    for path in sorted(list(WORKFLOWS_DIR.glob("*.yml")) + list(WORKFLOWS_DIR.glob("*.yaml"))):
        workflows.append((path.name, os.path.relpath(path, Path.cwd())))
    return workflows


def _write_release_report(commit: str, version: str, tag_name: str, branch: str, report_mode: str) -> Path:
    """Write a markdown release or commit report."""
    report_dir = Path(REPORT_DIR_NAME)
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = report_dir / f"{REPORT_FILE_PREFIX}-{version}-{timestamp}.md"
    files = sorted(_collect_commit_files(commit))
    counts = _summarize_sections(files)
    workflows = _collect_workflows()

    lines = [
        f"# RouterShell {report_mode} report",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Branch: {branch}",
        f"- Source commit: `{commit}`",
        f"- Release version: `{version}`",
        f"- Release tag: `{tag_name}`",
        "",
        "## Workflows",
        "",
    ]
    if workflows:
        lines.extend(f"- `{name}` (`{path}`)" for name, path in workflows)
    else:
        lines.append("_No workflows found._")

    lines.extend(["", "## Change Summary", "", _render_markdown_table(counts), "", "## Files", ""])
    if files:
        lines.extend(f"- `{path}`" for path in files)
    else:
        lines.append("_No files detected._")
    lines.append("")

    if SUMMARY:
        lines.extend(["## Release Step Summary", ""])
        lines.extend(f"- {state.upper()} {label}" for label, state in SUMMARY.items())
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def _read_current_version() -> str:
    """Read the current __version__ value."""
    if not VERSION_FILE_PATH.exists():
        print(f"ERROR: Version file not found: {VERSION_FILE_PATH}", file=sys.stderr)
        sys.exit(1)
    text = VERSION_FILE_PATH.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*(?::\s*[^=]+)?=\s*"([^"]+)"', text)
    if not match:
        print(f"ERROR: Could not find __version__ in {VERSION_FILE_PATH}.", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def _read_pyproject_version() -> str:
    """Read the [project].version value from pyproject.toml."""
    if not PYPROJECT_FILE_PATH.exists():
        print(f"ERROR: pyproject.toml not found: {PYPROJECT_FILE_PATH}", file=sys.stderr)
        sys.exit(1)
    text = PYPROJECT_FILE_PATH.read_text(encoding="utf-8")
    match = re.search(r'^\s*version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if not match:
        print(f"ERROR: Could not find [project].version in {PYPROJECT_FILE_PATH}.", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def _validate_version_string(version: str) -> None:
    """Validate MAJOR.MINOR.PATCH version strings."""
    core_version = version.split(RC_SUFFIX_PREFIX, 1)[0]
    parts = core_version.split(VERSION_PART_SEPARATOR)
    if len(parts) != EXPECTED_VERSION_PARTS or not all(part.isdigit() for part in parts):
        print(f"ERROR: Invalid version '{version}'. Expected MAJOR.MINOR.PATCH.", file=sys.stderr)
        sys.exit(1)


def _parse_version_parts(version: str) -> list[int]:
    """Parse a semantic version into numeric parts."""
    _validate_version_string(version)
    core_version = version.split(RC_SUFFIX_PREFIX, 1)[0]
    return [int(part) for part in core_version.split(VERSION_PART_SEPARATOR)]


def _compute_next_version(current_version: str, mode: str) -> str:
    """Compute the next semantic version."""
    parts = _parse_version_parts(current_version)
    match mode:
        case "major":
            parts[MAJOR_INDEX] += 1
            parts[MINOR_INDEX] = 0
            parts[PATCH_INDEX] = 0
        case "minor":
            parts[MINOR_INDEX] += 1
            parts[PATCH_INDEX] = 0
        case "patch":
            parts[PATCH_INDEX] += 1
        case _:
            print(f"ERROR: Unsupported next mode '{mode}'.", file=sys.stderr)
            sys.exit(1)
    return VERSION_PART_SEPARATOR.join(str(part) for part in parts)


def _update_version_files(new_version: str) -> None:
    """Update routershell_version.py and pyproject.toml via support tooling."""
    if not BUMP_SCRIPT_PATH.exists():
        print(f"ERROR: Version bump script not found: {BUMP_SCRIPT_PATH}", file=sys.stderr)
        sys.exit(1)
    _run([sys.executable, str(BUMP_SCRIPT_PATH), new_version, "--version-files-only"], label="bump-version")


def _update_readme_tag(new_tag: str) -> None:
    """Rewrite TAG placeholders to the new release tag in README and docs."""
    paths = [README_FILE_PATH]
    if DOCS_ROOT.exists():
        paths.extend(path for path in DOCS_ROOT.rglob("*.md") if path.is_file())

    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        updated_text, count = README_TAG_PATTERN.subn(f'TAG="{new_tag}"', text)
        if count:
            path.write_text(updated_text, encoding="utf-8")
            print(f"Updated TAG placeholders in {path} to {new_tag}")


def _ensure_virtualenv() -> None:
    """Ensure release is running inside a virtual environment."""
    if os.environ.get("VIRTUAL_ENV"):
        return
    if getattr(sys, "base_prefix", sys.prefix) != sys.prefix:
        return
    print("ERROR: Release must run inside a Python virtual environment.", file=sys.stderr)
    print("Suggested setup:", file=sys.stderr)
    print("  python3 -m venv .venv && . .venv/bin/activate && python -m pip install -e '.[dev]'", file=sys.stderr)
    sys.exit(1)


def _run_tests(skip_tests: bool) -> None:
    """Run pytest unless skipped."""
    if skip_tests:
        _print_status("Tests", "skip")
        return
    result = _run([sys.executable, "-m", "pytest"], check=False, label="pytest")
    if result.returncode != 0:
        print("ERROR: pytest failed. Aborting release.", file=sys.stderr)
        _print_status("Tests", "fail")
        sys.exit(result.returncode)
    _print_status("Tests", "pass")


def _run_ruff(skip_ruff: bool) -> None:
    """Run Ruff unless skipped."""
    if skip_ruff:
        _print_status("Ruff", "skip")
        return
    result = _run([sys.executable, "-m", "ruff", "check", "."], check=False, label="ruff")
    if result.returncode != 0:
        print("ERROR: Ruff failed. Aborting release.", file=sys.stderr)
        _print_status("Ruff", "fail")
        sys.exit(result.returncode)
    _print_status("Ruff", "pass")


def _run_build(skip_build: bool) -> None:
    """Run python -m build unless skipped."""
    if skip_build:
        _print_status("Build", "skip")
        return
    result = _run([sys.executable, "-m", "build"], check=False, label="build")
    if result.returncode != 0:
        print("ERROR: build failed. Aborting release.", file=sys.stderr)
        _print_status("Build", "fail")
        sys.exit(result.returncode)
    _print_status("Build", "pass")


def _run_version_check() -> None:
    """Run the release version consistency check."""
    result = _run([sys.executable, "tools/release/check_version.py"], check=False, label="check-version")
    if result.returncode != 0:
        print(result.stdout or "", end="")
        print(result.stderr or "", end="", file=sys.stderr)
        _print_status("Version check", "fail")
        sys.exit(result.returncode)
    _print_status("Version check", "pass")


def _commit_version_bump(new_version: str) -> None:
    """Commit version bump files."""
    _run(["git", "add", str(VERSION_FILE_PATH), str(PYPROJECT_FILE_PATH), str(README_FILE_PATH)], label="git-add")
    _run(["git", "commit", "-m", f"Release {new_version}"], label="git-commit")


def _create_tag(new_version: str, tag_prefix: str, tag_suffix: str = "") -> str:
    """Create an annotated git tag."""
    tag_name = f"{tag_prefix}{new_version}{tag_suffix}"
    _run(["git", "tag", "-a", tag_name, "-m", f"Release {new_version}"], label="git-tag")
    return tag_name


def _push_branch_and_tag(branch: str, tag_name: str) -> None:
    """Push release branch and tag."""
    _run(["git", "push", "origin", branch], label="git-push-branch")
    _run(["git", "push", "origin", tag_name], label="git-push-tag")


def _build_parser() -> argparse.ArgumentParser:
    """Build the release CLI parser."""
    parser = argparse.ArgumentParser(description="Automate a RouterShell release.")
    parser.add_argument("--version", help="Explicit release version in MAJOR.MINOR.PATCH format.")
    parser.add_argument("--next", choices=["major", "minor", "patch"], help="Compute the next version.")
    parser.add_argument("--branch", default="main", help="Branch to release from.")
    parser.add_argument("--tag-prefix", default="v", help="Prefix for git tags.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest.")
    parser.add_argument("--skip-ruff", action="store_true", help="Skip Ruff.")
    parser.add_argument("--skip-build", action="store_true", help="Skip python -m build.")
    parser.add_argument("--test-release", action="store_true", help="Run checks and restore previous version.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without modifying files.")
    parser.add_argument("--last-commit-report", action="store_true", help="Generate a report for HEAD~1.")
    parser.add_argument("--latest-commit-report", action="store_true", help="Generate a report for HEAD.")
    return parser


def main() -> None:
    """Run RouterShell release automation."""
    _ensure_git_repo()
    args = _build_parser().parse_args()

    if args.last_commit_report and args.latest_commit_report:
        print("ERROR: report modes cannot be combined.", file=sys.stderr)
        sys.exit(1)

    current_branch = _get_current_branch()
    if args.last_commit_report or args.latest_commit_report:
        target_commit = _get_previous_commit() if args.last_commit_report else _get_head_commit()
        if not target_commit:
            print("ERROR: unable to resolve report commit.", file=sys.stderr)
            sys.exit(1)
        version = _read_current_version()
        mode = "last-commit" if args.last_commit_report else "latest-commit"
        report_path = _write_release_report(target_commit, version, "n/a", current_branch, mode)
        print(f"Commit report saved to {report_path}")
        return

    current_version = _read_current_version()
    pyproject_version = _read_pyproject_version()
    if current_version != pyproject_version:
        print(
            f"ERROR: Version mismatch between {VERSION_FILE_PATH} ({current_version}) "
            f"and pyproject.toml ({pyproject_version}).",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.version and args.next:
        print("ERROR: --version and --next cannot be used together.", file=sys.stderr)
        sys.exit(1)

    new_version = args.version if args.version else _compute_next_version(current_version, args.next or "patch")
    _validate_version_string(new_version)
    if new_version == current_version:
        print(f"No change: version is already {current_version}.")
        return

    release_tag = f"{args.tag_prefix}{new_version}"
    if args.dry_run:
        print("Dry run: the following actions would be performed:")
        print("  1) Ensure git working tree is clean")
        print(f"  2) Update version {current_version} -> {new_version}")
        print(f"  3) Update README/doc TAG placeholders to {release_tag}")
        print("  4) Run version check")
        if not args.skip_tests:
            print("  5) Run pytest")
        if not args.skip_ruff:
            print("  6) Run Ruff")
        if not args.skip_build:
            print("  7) Build distribution artifacts")
        if args.test_release:
            print(f"  8) Restore version files back to {current_version}")
        else:
            print(f"  8) Commit version bump, tag {release_tag}, and push")
        return

    _ensure_release_branch_allowed()
    _ensure_virtualenv()
    _init_release_logging()
    _ensure_clean_worktree()

    print(f"Current version: {current_version}")
    print(f"Planned version: {new_version}")
    answer = input("Proceed with release? [y/N]: ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted.")
        sys.exit(1)

    report_commit = _get_head_commit()
    _update_version_files(new_version)
    _update_readme_tag(release_tag)
    _run_version_check()
    _run_tests(args.skip_tests)
    _run_ruff(args.skip_ruff)
    _run_build(args.skip_build)

    if args.test_release:
        print("Restoring version files after test release.")
        _update_version_files(current_version)
        _update_readme_tag(f"{args.tag_prefix}{current_version}")
        _print_status("Commit", "skip")
        _print_status("Tag", "skip")
        _print_status("Push", "skip")
        return

    _commit_version_bump(new_version)
    tag_name = _create_tag(new_version, args.tag_prefix)
    _push_branch_and_tag(args.branch, tag_name)
    _print_status("Release report", "pass")
    report_path = _write_release_report(report_commit, new_version, tag_name, args.branch, "release")
    print(f"Release report saved to {report_path}")
    print(f"Release {new_version} completed on branch '{args.branch}' with tag '{tag_name}'.")


if __name__ == "__main__":
    main()

# FILE: tools/release/test-runner.py
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""RouterShell unittest discovery runner."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
import traceback
import unittest
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TestResult:
    """Container for individual test file results."""

    file_path: str
    tests_run: int
    failures: int
    errors: int
    skipped: int
    success: bool
    duration: float


@dataclass
class TestSummary:
    """Container for overall test execution summary."""

    total_files: int
    successful_files: int
    failed_files: int
    total_tests: int
    total_failures: int
    total_errors: int
    total_skipped: int
    total_duration: float
    results: list[TestResult]


class RouterShellTestRunner:
    """Discover and run unittest-compatible tests."""

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser."""
        parser = argparse.ArgumentParser(description="Run RouterShell unittest tests.")
        parser.add_argument("--tests-dir", default="tests", help="Directory containing tests.")
        parser.add_argument("--pattern", default="test_*.py", help="Test file pattern.")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
        parser.add_argument("--failfast", action="store_true", help="Stop on first failure.")
        parser.add_argument("--json-report", action="store_true", help="Write a JSON report.")
        parser.add_argument("--output-dir", default="test_reports", help="Report output directory.")
        return parser

    @staticmethod
    def _discover(tests_dir: Path, pattern: str) -> list[Path]:
        """Discover test files."""
        if not tests_dir.exists():
            raise FileNotFoundError(f"Tests directory not found: {tests_dir}")
        return sorted(tests_dir.rglob(pattern))

    @staticmethod
    def _run_file(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run tests from one file."""
        start = time.time()
        loader = unittest.TestLoader()
        suite = loader.discover(str(path.parent), pattern=path.name)
        runner = unittest.TextTestRunner(verbosity=2 if verbose else 1, failfast=failfast)
        result = runner.run(suite)
        tests_run = result.testsRun
        errors = len(result.errors)
        failures = len(result.failures)

        if tests_run == 0:
            function_result = RouterShellTestRunner._run_function_tests(path, verbose, failfast)
            tests_run = function_result.tests_run
            errors = errors + function_result.errors
            failures = failures + function_result.failures

        return TestResult(
            file_path=str(path),
            tests_run=tests_run,
            failures=failures,
            errors=errors,
            skipped=len(result.skipped),
            success=failures == 0 and errors == 0,
            duration=time.time() - start,
        )

    @staticmethod
    def _run_function_tests(path: Path, verbose: bool, failfast: bool) -> TestResult:
        """Run pytest-style module-level test functions without pytest."""
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            return TestResult(str(path), 0, 0, 1, 0, False, 0.0)

        module = importlib.util.module_from_spec(spec)
        project_root = Path.cwd()
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        try:
            spec.loader.exec_module(module)
        finally:
            sys.path = original_path

        functions = [
            value
            for name, value in vars(module).items()
            if name.startswith("test_") and callable(value)
        ]
        failures = 0
        errors = 0
        original_path = sys.path.copy()
        sys.path.insert(0, str(project_root))
        for function in functions:
            try:
                function()
                if verbose:
                    print(f"PASS {function.__name__}")
            except AssertionError:
                failures = failures + 1
                traceback.print_exc()
                if failfast:
                    break
            except Exception:
                errors = errors + 1
                traceback.print_exc()
                if failfast:
                    break
        sys.path = original_path

        return TestResult(
            file_path=str(path),
            tests_run=len(functions),
            failures=failures,
            errors=errors,
            skipped=0,
            success=failures == 0 and errors == 0,
            duration=0.0,
        )

    @staticmethod
    def _write_json(summary: TestSummary, output_dir: Path) -> None:
        """Write a JSON test report."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "summary": {
                "total_files": summary.total_files,
                "successful_files": summary.successful_files,
                "failed_files": summary.failed_files,
                "total_tests": summary.total_tests,
                "total_failures": summary.total_failures,
                "total_errors": summary.total_errors,
                "total_skipped": summary.total_skipped,
                "total_duration": summary.total_duration,
            },
            "results": [result.__dict__ for result in summary.results],
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"JSON report generated: {output_path}")

    @staticmethod
    def run(options: argparse.Namespace) -> int:
        """Run discovered tests and return a process status."""
        tests_dir = Path(options.tests_dir)
        start = time.time()
        test_files = RouterShellTestRunner._discover(tests_dir, options.pattern)
        if not test_files:
            print(f"No test files found matching {options.pattern!r} in {tests_dir}.")
            return 1

        results: list[TestResult] = []
        for path in test_files:
            print(f"Running {path}...")
            result = RouterShellTestRunner._run_file(path, options.verbose, options.failfast)
            results.append(result)
            if options.failfast and not result.success:
                break

        summary = TestSummary(
            total_files=len(results),
            successful_files=sum(1 for result in results if result.success),
            failed_files=sum(1 for result in results if not result.success),
            total_tests=sum(result.tests_run for result in results),
            total_failures=sum(result.failures for result in results),
            total_errors=sum(result.errors for result in results),
            total_skipped=sum(result.skipped for result in results),
            total_duration=time.time() - start,
            results=results,
        )

        print("\nTest summary")
        print(f"Files: {summary.successful_files}/{summary.total_files} passed")
        print(f"Tests: {summary.total_tests - summary.total_failures - summary.total_errors}/{summary.total_tests} passed")
        print(f"Failures: {summary.total_failures}")
        print(f"Errors: {summary.total_errors}")
        print(f"Skipped: {summary.total_skipped}")
        print(f"Duration: {summary.total_duration:.3f}s")

        if options.json_report:
            RouterShellTestRunner._write_json(summary, Path(options.output_dir))

        return 0 if summary.failed_files == 0 else 1


def main() -> int:
    """Run the RouterShell unittest runner."""
    parser = RouterShellTestRunner._build_parser()
    try:
        return RouterShellTestRunner.run(parser.parse_args())
    except KeyboardInterrupt:
        print("Test execution interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"FATAL ERROR: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())

# FILE: tools/support/README.md
# RouterShell Support Tools

Support tools are small helpers used by release and workflow scripts.

## Version Bump

Show the current version:

```bash
./tools/support/bump_version.py --current
```

Apply the next patch version:

```bash
./tools/support/bump_version.py --next patch
```

Set an explicit version:

```bash
./tools/support/bump_version.py 0.2.0
```

Update only version files without rewriting README/doc tag placeholders:

```bash
./tools/support/bump_version.py --next patch --version-files-only
```

# FILE: tools/support/bump_version.py
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""Inspect or update RouterShell version files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final


VERSION_FILE_PATH: Final[Path] = Path("routershell_version.py")
PYPROJECT_FILE_PATH: Final[Path] = Path("pyproject.toml")
DOC_TAG_ROOT: Final[Path] = Path("doc")
VERSION_PART_SEPARATOR: Final[str] = "."
EXPECTED_VERSION_PARTS: Final[int] = 3
MAJOR_INDEX: Final[int] = 0
MINOR_INDEX: Final[int] = 1
PATCH_INDEX: Final[int] = 2
TAG_PATTERN: Final[re.Pattern[str]] = re.compile(r'TAG="v\d+\.\d+\.\d+(?:-rc\d+)?"')


def _validate_version_string(version: str) -> None:
    """Validate that the version string matches MAJOR.MINOR.PATCH."""
    core_version = version.split("-rc", 1)[0]
    parts = core_version.split(VERSION_PART_SEPARATOR)
    if len(parts) != EXPECTED_VERSION_PARTS or not all(part.isdigit() for part in parts):
        print(f"ERROR: Invalid version '{version}'. Expected MAJOR.MINOR.PATCH.", file=sys.stderr)
        sys.exit(1)


def _read_current_version(version_file: Path) -> str:
    """Read the current __version__ value from the version file."""
    if not version_file.exists():
        print(f"ERROR: Version file not found: {version_file}", file=sys.stderr)
        sys.exit(1)

    text = version_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*(?::\s*[^=]+)?=\s*"([^"]+)"', text)
    if not match:
        print(f"ERROR: Could not find __version__ assignment in {version_file}.", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def _write_new_version(version_file: Path, new_version: str) -> None:
    """Write the new version into the version file."""
    text = version_file.read_text(encoding="utf-8")
    updated_text, count = re.subn(
        r'__version__\s*(?::\s*[^=]+)?=\s*"[^"]+"',
        f'__version__: str = "{new_version}"',
        text,
        count=1,
    )
    if count != 1:
        print(f"ERROR: Could not replace __version__ in {version_file}.", file=sys.stderr)
        sys.exit(1)
    version_file.write_text(updated_text, encoding="utf-8")


def _write_new_pyproject_version(pyproject_file: Path, new_version: str) -> None:
    """Write the new version into pyproject.toml [project].version."""
    if not pyproject_file.exists():
        print(f"ERROR: pyproject.toml not found: {pyproject_file}", file=sys.stderr)
        sys.exit(1)

    text = pyproject_file.read_text(encoding="utf-8")
    updated_text, count = re.subn(
        r'^(\s*version\s*=\s*)"[^"]+"',
        rf'\g<1>"{new_version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        print(f"ERROR: Could not replace [project].version in {pyproject_file}.", file=sys.stderr)
        sys.exit(1)
    pyproject_file.write_text(updated_text, encoding="utf-8")


def _update_tag_tokens(tag: str) -> None:
    """Rewrite TAG=\"vX.Y.Z\" occurrences in README and doc/*.md files."""
    paths = [Path("README.md")]
    if DOC_TAG_ROOT.exists():
        paths.extend(path for path in DOC_TAG_ROOT.rglob("*.md") if path.is_file())

    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        updated_text, count = TAG_PATTERN.subn(f'TAG="{tag}"', text)
        if count:
            path.write_text(updated_text, encoding="utf-8")


def _compute_next_version(current_version: str, mode: str) -> str:
    """Compute the next version by incrementing the requested component."""
    _validate_version_string(current_version)
    parts = [int(part) for part in current_version.split("-rc", 1)[0].split(VERSION_PART_SEPARATOR)]

    match mode:
        case "major":
            parts[MAJOR_INDEX] = parts[MAJOR_INDEX] + 1
            parts[MINOR_INDEX] = 0
            parts[PATCH_INDEX] = 0
        case "minor":
            parts[MINOR_INDEX] = parts[MINOR_INDEX] + 1
            parts[PATCH_INDEX] = 0
        case "patch":
            parts[PATCH_INDEX] = parts[PATCH_INDEX] + 1
        case _:
            print(f"ERROR: Unsupported --next mode '{mode}'.", file=sys.stderr)
            sys.exit(1)

    return VERSION_PART_SEPARATOR.join(str(part) for part in parts)


def main() -> None:
    """CLI entry point for inspecting or updating the RouterShell version."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect or update the __version__ string in routershell_version.py and "
            "the [project].version field in pyproject.toml. "
            "Version format: MAJOR.MINOR.PATCH."
        )
    )
    parser.add_argument("version", nargs="?", help="Explicit version to set, e.g. 0.2.0.")
    parser.add_argument("--current", action="store_true", help="Show the current version and exit.")
    parser.add_argument("--next", choices=["major", "minor", "patch"], help="Compute and apply the next version.")
    parser.add_argument(
        "--version-files-only",
        action="store_true",
        help="Update only version files; skip README/doc tag rewrites.",
    )

    args = parser.parse_args()

    if args.current:
        if args.version is not None or args.next is not None:
            print("ERROR: --current cannot be combined with a version argument or --next.", file=sys.stderr)
            sys.exit(1)
        current = _read_current_version(VERSION_FILE_PATH)
        print(f"Current version: {current}")
        sys.exit(0)

    if args.next is not None:
        if args.version is not None:
            print("ERROR: --next cannot be combined with an explicit version argument.", file=sys.stderr)
            sys.exit(1)
        current = _read_current_version(VERSION_FILE_PATH)
        new_version = _compute_next_version(current, args.next)
    elif args.version is not None:
        current = _read_current_version(VERSION_FILE_PATH)
        new_version = args.version
        _validate_version_string(new_version)
    else:
        print("ERROR: You must specify --current, --next <mode>, or an explicit version.", file=sys.stderr)
        sys.exit(1)

    if current == new_version:
        print(f"No change: version is already {current}.")
        sys.exit(0)

    _write_new_version(VERSION_FILE_PATH, new_version)
    _write_new_pyproject_version(PYPROJECT_FILE_PATH, new_version)
    if not args.version_files_only:
        _update_tag_tokens(f"v{new_version}")
    print(f"Updated version: {current} -> {new_version}")


if __name__ == "__main__":
    main()

