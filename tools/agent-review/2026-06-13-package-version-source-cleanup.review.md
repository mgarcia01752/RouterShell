### Summary
Moved RouterShell version exposure into a real routershell package while keeping pyproject.toml as the only stored version source. Updated console entry points, release/version tooling, VM smoke checks, git quality gates, and packaging tests to use the package layout while retaining routershell_version.py as a compatibility shim.

### Modified Files
- pyproject.toml
- routershell.py (deleted)
- routershell/__init__.py
- routershell/_version.py
- routershell/cli.py
- routershell_version.py
- tests/test_packaging.py
- tools/git/README.md
- tools/git/git-common.sh
- tools/release/README.md
- tools/release/check_version.py
- tools/release/release.py
- tools/support/README.md
- tools/support/bump_version.py
- tools/vm/README.md
- tools/vm/multipass-test-install.sh

### Commands Executed And Results
- `python3 -m py_compile routershell/__init__.py routershell/_version.py routershell/cli.py routershell_version.py tools/release/check_version.py tools/release/release.py tools/support/bump_version.py tests/test_packaging.py` -> pass
- `python3 tools/release/check_version.py && python3 tools/support/bump_version.py --current && python3 tools/release/release.py --next patch --dry-run` -> pass
- `bash -n install/install.sh install/uninstall.sh tools/git/git-common.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh tools/vm/multipass-common.sh tools/vm/multipass-create.sh tools/vm/multipass-test-install.sh tools/vm/multipass-shell.sh tools/vm/multipass-destroy.sh` -> pass
- `python3 -m venv /tmp/routershell-version-cleanup-check && /tmp/routershell-version-cleanup-check/bin/python -m pip install --upgrade pip && /tmp/routershell-version-cleanup-check/bin/python -m pip install -e .[dev]` -> pass
- `/tmp/routershell-version-cleanup-check/bin/python -m pytest` -> pass; 5 tests passed
- `/tmp/routershell-version-cleanup-check/bin/python -m ruff check routershell routershell_version.py tools/release/check_version.py tools/release/release.py tools/support/bump_version.py tests/test_packaging.py` -> pass
- `/tmp/routershell-version-cleanup-check/bin/python -m ruff check .` -> fail; existing legacy repo issues outside the touched scope remain
- `bash -c source tools/git/git-common.sh; rs_run_quality_gates` -> pass available gates; pytest and Ruff skipped for system Python because they are not installed there
- `/tmp/routershell-version-cleanup-check/bin/python -m build` -> pass; sdist and wheel built
- package import/version smoke check -> pass; package metadata, routershell.__version__, compatibility shim, and CLI functions resolved

### Tests
- `pytest` -> pass; 5 tests passed
- `ruff` -> pass on touched Python files; full repo Ruff still fails on pre-existing legacy issues
- `python -m build` -> pass
- `tools/release/check_version.py` -> pass

### Notes / Warnings
- `pyproject.toml` is now the only stored version source.
- `routershell_version.py` remains as a compatibility shim for older callers.
- Full-repo Ruff is not clean yet due to existing legacy style and lint issues outside this task.

### Remaining TODOs / Follow-Ups
- Later remove `routershell_version.py` after downstream callers stop importing it.
- Clean existing full-repo Ruff findings in a separate scoped task.

# FILE: routershell.py
Deleted. Console entry points moved to routershell/cli.py.

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
routershell = "routershell.cli:main"
routershell-factory-reset = "routershell.cli:factory_reset"

[project.urls]
Homepage = "https://github.com/mgarcia01752/RouterShell"
Repository = "https://github.com/mgarcia01752/RouterShell"

[tool.setuptools]
py-modules = ["routershell_version"]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
include = ["routershell*", "lib*"]
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

# FILE: routershell/__init__.py
"""RouterShell package."""

from __future__ import annotations

from routershell._version import __version__

__all__ = ["__version__"]

# FILE: routershell/_version.py
"""RouterShell version helpers."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

import tomllib


def _read_source_tree_version() -> str:
    """Read the version from pyproject.toml when package metadata is unavailable."""
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        with pyproject_path.open("rb") as handle:
            pyproject = tomllib.load(handle)
    except OSError:
        return "0.0.0+unknown"

    project = pyproject.get("project", {})
    version = project.get("version", "0.0.0+unknown")
    if not isinstance(version, str):
        return "0.0.0+unknown"
    return version


try:
    __version__: str = package_version("routershell")
except PackageNotFoundError:
    __version__ = _read_source_tree_version()

# FILE: routershell/cli.py
"""Console entry points for RouterShell."""

from __future__ import annotations

import sys
from pathlib import Path

import lib


def _bootstrap_legacy_imports() -> None:
    """Expose the installed ``lib`` directory for legacy top-level imports."""
    lib_path = Path(lib.__file__).resolve().parent
    lib_path_str = str(lib_path)
    if lib_path_str not in sys.path:
        sys.path.insert(0, lib_path_str)


def main() -> int:
    """Run the RouterShell interactive CLI."""
    _bootstrap_legacy_imports()
    from lib.cli.router_main_cli import RouterCLI

    RouterCLI().run()
    return 0


def factory_reset() -> int:
    """Run the RouterShell factory reset workflow."""
    _bootstrap_legacy_imports()
    from lib.system.system_start_up import SystemFactoryReset

    SystemFactoryReset()
    return 0

# FILE: routershell_version.py
"""Compatibility shim for RouterShell package version."""

from __future__ import annotations

from routershell import __version__

__all__ = ["__version__"]

# FILE: tests/test_packaging.py
"""Packaging metadata and entry point smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

import tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_declares_console_entry_points() -> None:
    """Verify the packaged console scripts point at the compatibility launcher."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    scripts = pyproject["project"]["scripts"]

    assert scripts["routershell"] == "routershell.cli:main"
    assert scripts["routershell-factory-reset"] == "routershell.cli:factory_reset"


def test_lib_package_adds_legacy_import_path() -> None:
    """Importing ``lib`` exposes the legacy top-level package path."""
    import lib

    lib_path = str(Path(lib.__file__).resolve().parent)

    assert lib_path in sys.path


def test_routershell_entry_point_functions_are_importable() -> None:
    """The console entry point functions can be imported without starting the CLI."""
    from routershell import cli

    assert callable(cli.main)
    assert callable(cli.factory_reset)


def test_version_module_matches_pyproject() -> None:
    """The package version and pyproject version stay aligned."""
    import routershell

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    assert routershell.__version__ == pyproject["project"]["version"]


def test_legacy_version_shim_matches_package_version() -> None:
    """The legacy root version module remains compatible during migration."""
    import routershell
    import routershell_version

    assert routershell_version.__version__ == routershell.__version__

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
python3 -m py_compile routershell/__init__.py routershell/_version.py routershell/cli.py routershell_version.py lib/__init__.py
python3 -m compileall -q routershell src lib tools/release tools/support bridge_factory.py bridge_db-test.py test.py routershell_version.py
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
  rs_run_check "compile packaging files" "${python_bin}" -m py_compile routershell/__init__.py routershell/_version.py routershell/cli.py routershell_version.py lib/__init__.py
  rs_run_check "compile source tree" "${python_bin}" -m compileall -q routershell src lib tools/release tools/support bridge_factory.py bridge_db-test.py test.py routershell_version.py
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

Verify that the package version and `pyproject.toml` agree:

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
import sys
from pathlib import Path

import tomllib


class VersionCheckTool:
    """Verify version consistency between the package and pyproject.toml."""

    MAX_ROOT_SEARCH_DEPTH: int = 6
    PYPROJECT_RELATIVE: str = "pyproject.toml"
    EXIT_OK: int = 0
    EXIT_ERROR: int = 1
    EXIT_MISMATCH: int = 2

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
    def _read_version_from_pyproject(path: Path) -> str:
        """Extract the project version value from pyproject.toml."""
        try:
            with path.open("rb") as handle:
                pyproject = tomllib.load(handle)
        except OSError:
            return ""

        project = pyproject.get("project", {})
        version = project.get("version", "")
        if not isinstance(version, str):
            return ""
        return version

    @staticmethod
    def _read_version_from_package(root_path: Path) -> str:
        """Read the runtime package version."""
        if str(root_path) not in sys.path:
            sys.path.insert(0, str(root_path))
        try:
            import routershell
        except ImportError:
            return ""
        return routershell.__version__

    @staticmethod
    def _build_parser() -> argparse.ArgumentParser:
        """Build the CLI parser for the version check tool."""
        parser = argparse.ArgumentParser(
            description="Verify that the RouterShell package and pyproject.toml carry the same version."
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Print results as JSON.",
        )
        return parser

    @staticmethod
    def _emit_text(package_version: str, pyproject_version: str, status: str) -> None:
        """Emit human-readable output."""
        if status == "error":
            print("Version check failed: unable to read one or more version values.")
        print(f"routershell package: {package_version or 'missing'}")
        print(f"pyproject.toml: {pyproject_version or 'missing'}")
        if status == "mismatch":
            print("Version mismatch detected.")
        if status == "ok":
            print("Version match confirmed.")

    @staticmethod
    def _emit_json(package_version: str, pyproject_version: str, status: str) -> None:
        """Emit JSON output."""
        payload = {
            "package": package_version,
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
        pyproject_path = root_path / VersionCheckTool.PYPROJECT_RELATIVE

        package_version = VersionCheckTool._read_version_from_package(root_path)
        pyproject_version = VersionCheckTool._read_version_from_pyproject(pyproject_path)

        if not package_version or not pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(package_version, pyproject_version, "error")
            else:
                VersionCheckTool._emit_text(package_version, pyproject_version, "error")
            return VersionCheckTool.EXIT_ERROR

        if package_version != pyproject_version:
            if options.json:
                VersionCheckTool._emit_json(package_version, pyproject_version, "mismatch")
            else:
                VersionCheckTool._emit_text(package_version, pyproject_version, "mismatch")
            return VersionCheckTool.EXIT_MISMATCH

        if options.json:
            VersionCheckTool._emit_json(package_version, pyproject_version, "ok")
        else:
            VersionCheckTool._emit_text(package_version, pyproject_version, "ok")
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
    if normalized.startswith("lib/cli/") or normalized.startswith("src/") or normalized == "routershell/cli.py":
        return "CLI"
    if normalized.startswith("lib/db/"):
        return "Database"
    if normalized.startswith("lib/network_manager/"):
        return "Networking"
    if normalized.startswith("lib/network_services/") or normalized.startswith("lib/system/"):
        return "Services"
    if normalized.startswith("install/") or normalized == "start.sh":
        return "Install"
    if normalized in {"pyproject.toml", "routershell/_version.py", "routershell/__init__.py"}:
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
    """Update pyproject.toml via support tooling."""
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
    _run(["git", "add", str(PYPROJECT_FILE_PATH), str(README_FILE_PATH), str(DOCS_ROOT)], label="git-add")
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
        version = _read_pyproject_version()
        mode = "last-commit" if args.last_commit_report else "latest-commit"
        report_path = _write_release_report(target_commit, version, "n/a", current_branch, mode)
        print(f"Commit report saved to {report_path}")
        return

    current_version = _read_pyproject_version()

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
    if args.branch != current_branch:
        print(
            f"ERROR: --branch must match the current branch ({current_branch}); got {args.branch}.",
            file=sys.stderr,
        )
        sys.exit(1)
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

Update only `pyproject.toml` without rewriting README/doc tag placeholders:

```bash
./tools/support/bump_version.py --next patch --version-files-only
```

# FILE: tools/support/bump_version.py
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Maurice Garcia

"""Inspect or update the RouterShell project version."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final

import tomllib

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


def _read_current_version(pyproject_file: Path) -> str:
    """Read the current version from pyproject.toml."""
    if not pyproject_file.exists():
        print(f"ERROR: pyproject.toml not found: {pyproject_file}", file=sys.stderr)
        sys.exit(1)

    with pyproject_file.open("rb") as handle:
        pyproject = tomllib.load(handle)

    project = pyproject.get("project", {})
    version = project.get("version", "")
    if not isinstance(version, str) or not version:
        print(f"ERROR: Could not find [project].version in {pyproject_file}.", file=sys.stderr)
        sys.exit(1)
    return version


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
            "Inspect or update the [project].version field in pyproject.toml. "
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
        current = _read_current_version(PYPROJECT_FILE_PATH)
        print(f"Current version: {current}")
        sys.exit(0)

    if args.next is not None:
        if args.version is not None:
            print("ERROR: --next cannot be combined with an explicit version argument.", file=sys.stderr)
            sys.exit(1)
        current = _read_current_version(PYPROJECT_FILE_PATH)
        new_version = _compute_next_version(current, args.next)
    elif args.version is not None:
        current = _read_current_version(PYPROJECT_FILE_PATH)
        new_version = args.version
        _validate_version_string(new_version)
    else:
        print("ERROR: You must specify --current, --next <mode>, or an explicit version.", file=sys.stderr)
        sys.exit(1)

    if current == new_version:
        print(f"No change: version is already {current}.")
        sys.exit(0)

    _write_new_pyproject_version(PYPROJECT_FILE_PATH, new_version)
    if not args.version_files_only:
        _update_tag_tokens(f"v{new_version}")
    print(f"Updated version: {current} -> {new_version}")


if __name__ == "__main__":
    main()

# FILE: tools/vm/README.md
# RouterShell VM Install Testing

This directory contains a Multipass-based workflow for testing the generic
RouterShell Linux installer away from the development workstation.

This is a development workflow. It is not part of the production RouterShell
install process.

The VM workflow is for general-purpose Linux install testing only. BusyBox,
OpenWrt, Buildroot, Yocto/Poky images, and embedded router targets remain out
of scope until they have a dedicated install design.

## Prerequisites

- Multipass installed on the development workstation.
- Network access from the VM for OS packages and Python dependencies.

## Default VM

- Name: `routershell-install-test`
- Image: Ubuntu `24.04`
- CPUs: `2`
- Memory: `2G`
- Disk: `12G`

Override defaults with environment variables:

```bash
RS_VM_NAME=routershell-ubuntu-2404 RS_VM_IMAGE=24.04 tools/vm/multipass-create.sh
```

## Workflow

Create the VM:

```bash
tools/vm/multipass-create.sh
```

Run the production install test:

```bash
tools/vm/multipass-test-install.sh
```

By default, the VM test runs:

```bash
sudo /tmp/RouterShell/install/install.sh
```

That production install captures a baseline snapshot in the VM under
`/var/lib/routershell/baseline`.

Use `--development` to test editable install mode with development dependencies:

```bash
tools/vm/multipass-test-install.sh --development
```

Open a shell inside the VM:

```bash
tools/vm/multipass-shell.sh
```

Delete the VM:

```bash
tools/vm/multipass-destroy.sh --purge
```

## What The Test Does

`multipass-test-install.sh` creates a tar archive of the current worktree,
excluding `.git`, `.venv`, caches, and build outputs. It transfers the archive
into the VM, extracts it under `/tmp/RouterShell`, runs the generic installer
in production mode by default, and verifies:

- `/usr/local/bin/routershell` exists and is executable.
- `/usr/local/bin/routershell-factory-reset` exists and is executable.
- `/opt/routershell/venv/bin/python` exists and is executable.
- `/var/lib/routershell/baseline/manifest.json` exists.
- The installed Python environment can import `routershell`, verify console
  entry functions, and read the package version.

The test intentionally does not start the interactive RouterShell CLI.

# FILE: tools/vm/multipass-test-install.sh
#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

SKIP_OS_PACKAGES="${SKIP_OS_PACKAGES:-false}"
DEVELOPMENT_INSTALL="${DEVELOPMENT_INSTALL:-false}"

usage() {
  cat <<'EOF'
Copy the current RouterShell worktree into the Multipass VM and test install it.

Usage:
  multipass-test-install.sh [--development] [--skip-os-packages]

Environment:
  RS_VM_NAME       VM name. Default: routershell-install-test
  RS_VM_REPO_DIR   Path inside VM. Default: /tmp/RouterShell

By default, the VM test runs the production runtime install path. Use
--development to test editable install mode with development dependencies.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-os-packages)
      SKIP_OS_PACKAGES="true"
      shift
      ;;
    --development)
      DEVELOPMENT_INSTALL="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      rs_vm_die "Unknown argument: $1"
      ;;
  esac
done

rs_vm_require_multipass
rs_vm_require_exists
rs_vm_create_archive

rs_vm_log "Copying archive into VM."
multipass transfer "${RS_VM_ARCHIVE}" "${RS_VM_NAME}:/tmp/routershell-vm-test.tar.gz"

rs_vm_log "Refreshing VM test workspace."
multipass exec "${RS_VM_NAME}" -- bash -lc "rm -rf '${RS_VM_REPO_DIR}' && tar -xzf /tmp/routershell-vm-test.tar.gz -C /tmp"

install_cmd="sudo '${RS_VM_REPO_DIR}/install/install.sh'"
if [[ "${DEVELOPMENT_INSTALL}" == "true" ]]; then
  install_cmd="${install_cmd} --development"
fi

if [[ "${SKIP_OS_PACKAGES}" == "true" ]]; then
  install_cmd="${install_cmd} --skip-os-packages"
fi

rs_vm_log "Running RouterShell installer inside VM."
multipass exec "${RS_VM_NAME}" -- bash -lc "${install_cmd}"

rs_vm_log "Verifying RouterShell runtime install."
multipass exec "${RS_VM_NAME}" -- bash -lc "
  set -euo pipefail
  test -x /usr/local/bin/routershell
  test -x /usr/local/bin/routershell-factory-reset
  test -x /opt/routershell/venv/bin/python
  sudo test -f /var/lib/routershell/baseline/manifest.json
  /opt/routershell/venv/bin/python - <<'PY'
import routershell
from routershell import cli

assert callable(cli.main)
assert callable(cli.factory_reset)
print(f'RouterShell import OK: {routershell.__version__}')
PY
"

rs_vm_log "Install test passed."
