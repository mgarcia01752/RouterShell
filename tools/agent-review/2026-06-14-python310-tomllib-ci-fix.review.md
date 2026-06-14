### Summary
Fixed Python 3.10 CI compatibility for TOML parsing by adding the conditional `tomli` runtime dependency and `tomllib` fallback imports. Added coverage for the Python 3.10 dependency marker and documented the CI failure/resolution in the FAQ.

### Modified Files
- pyproject.toml
- src/routershell/_version.py
- tests/packaging/test_entry_points.py
- tests/packaging/test_version.py
- tools/release/check_version.py
- tools/release/qa_checker.py
- tools/support/bump_version.py
- doc/faq.md
- todo.md

### Commands Executed And Results
- `python -m pytest tests/packaging/test_entry_points.py tests/packaging/test_version.py tests/tools/test_qa_checker.py -q` -> pass, 8 passed.
- `python tools/release/check_version.py` -> pass, version match confirmed at 0.1.5.
- `python -m ruff check src/routershell/_version.py tests/packaging/test_entry_points.py tests/packaging/test_version.py tools/release/check_version.py tools/release/qa_checker.py tools/support/bump_version.py` -> pass, all checks passed.
- `python -m pytest -q` -> pass, 56 passed.
- `python -m ruff check .` -> pass, all checks passed.
- `python - <<'PY' ... ast.parse(..., feature_version=(3, 10)) ... PY` -> pass, Python 3.10 syntax parse passed.
- `bash -n tools/vm/*.sh install/install.sh install/uninstall.sh tools/maintenance/clean.sh` -> pass.

### Tests
- `pytest` -> pass, 56 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM, install, uninstall, and maintenance scripts.
- Python 3.10 syntax parse -> pass. Python 3.10 runtime was not installed locally, so the actual 3.10 CI job must verify the dependency install path.

### Notes / Warnings
- GitHub Actions logs were not downloadable from this environment because `gh` is not installed and the public Actions log API returned 403 without repository admin rights.
- The observed failure was the Python 3.10 Ubuntu 22.04 `Run tests` step; the fix targets the likely `tomllib` collection/import failure on Python 3.10.

### Remaining TODOs / Follow-Ups
- Re-run the GitHub Actions matrix to confirm the Python 3.10 job passes with the conditional `tomli` dependency.

# FILE: pyproject.toml
# SPDX-License-Identifier: Apache-2.0

[build-system]
requires = ["setuptools>=77", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "routershell"
version = "0.1.5"
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
    "tomli>=2.0; python_version < '3.11'",
]

[project.optional-dependencies]
dev = [
    "build>=1.2",
    "pycycle>=0.0.8",
    "pyright>=1.1.407",
    "pylint>=3.3",
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
include = [
    "src",
    "tests",
    "tools/release",
]
extraPaths = [
    "src",
    ".",
]
exclude = [
    "**/__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
]

# FILE: src/routershell/_version.py
"""RouterShell version helpers."""

from __future__ import annotations

from importlib.metadata import version as package_version
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

UNKNOWN_VERSION = "0.0.0+unknown"


def _read_source_tree_version() -> str:
    """Read the version from pyproject.toml when package metadata is unavailable."""
    pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    try:
        with pyproject_path.open("rb") as handle:
            pyproject = tomllib.load(handle)
    except OSError:
        return UNKNOWN_VERSION

    project = pyproject.get("project", {})
    version = project.get("version", UNKNOWN_VERSION)
    if not isinstance(version, str):
        return UNKNOWN_VERSION
    return version


def _read_package_version() -> str:
    """Read the installed package metadata version."""
    try:
        return package_version("routershell")
    except Exception:
        return UNKNOWN_VERSION


source_tree_version = _read_source_tree_version()
if source_tree_version != UNKNOWN_VERSION:
    __version__: str = source_tree_version
else:
    __version__ = _read_package_version()

# FILE: tests/packaging/test_entry_points.py
"""Console entry point metadata smoke tests."""

from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_pyproject_declares_console_entry_points() -> None:
    """Verify packaged console scripts point at package entry functions."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    scripts = pyproject["project"]["scripts"]

    assert scripts["routershell"] == "routershell.cli:main"
    assert scripts["routershell-factory-reset"] == "routershell.cli:factory_reset"


def test_pyproject_declares_python_310_tomli_dependency() -> None:
    """Verify Python 3.10 installs the TOML parser backport."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    dependencies = pyproject["project"]["dependencies"]

    assert "tomli>=2.0; python_version < '3.11'" in dependencies


def test_routershell_entry_point_functions_are_importable() -> None:
    """Verify console entry point functions import without starting the CLI."""
    from routershell import cli

    assert callable(cli.main)
    assert callable(cli.factory_reset)

# FILE: tests/packaging/test_version.py
"""Package version smoke tests."""

from __future__ import annotations

import importlib
import importlib.metadata
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_package_version_matches_pyproject() -> None:
    """Verify package version resolves from project metadata."""
    import routershell

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    assert routershell.__version__ == pyproject["project"]["version"]


def test_source_tree_version_overrides_stale_package_metadata(monkeypatch) -> None:
    """Verify release checks do not read stale editable-install metadata."""
    import routershell._version as version_module

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)

    monkeypatch.setattr(importlib.metadata, "version", lambda package_name: "0.0.1")
    reloaded_version_module = importlib.reload(version_module)

    assert reloaded_version_module.__version__ == pyproject["project"]["version"]

# FILE: tools/release/check_version.py
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

"""Verify RouterShell version consistency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


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
        source_path = root_path / "src"
        import_path = source_path if source_path.is_dir() else root_path
        if str(import_path) not in sys.path:
            sys.path.insert(0, str(import_path))
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
                    "try:\n"
                    "    import tomllib\n"
                    "except ModuleNotFoundError:\n"
                    "    import tomli as tomllib\n"
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

# FILE: tools/support/bump_version.py
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

"""Inspect or update the RouterShell project version."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

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

# FILE: doc/faq.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell FAQ

## Python 3.10 CI fails with missing tomllib

If the Python 3.10 GitHub Actions job fails during `python -m pytest -q` with
this error:

```text
ModuleNotFoundError: No module named 'tomllib'
```

make sure RouterShell includes the Python 3.10 TOML backport dependency and
uses the compatibility import fallback:

```python
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
```

The `tomllib` module is built into Python 3.11 and newer. Python 3.10 needs
`tomli`, which is installed through the conditional `pyproject.toml`
dependency.

## Install fails with setuptools InvalidConfigError

If `sudo ./install/install.sh --development` fails while getting editable
build requirements and reports this error:

```text
setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions
```

Update RouterShell to a version whose `pyproject.toml` uses the SPDX
`license = "Apache-2.0"` expression without deprecated license classifiers,
then rerun the installer:

```bash
sudo ./install/install.sh --development
```

This error is raised by newer setuptools releases during package metadata
validation.

## VSCode reports unresolved RouterShell imports

If VSCode or Pylance reports unresolved imports for `routershell` or
`tools.release.qa_checker`, reload the VSCode window after opening the
RouterShell workspace. The workspace settings select the installed development
interpreter at `/opt/routershell/venv/bin/python` and add the project `src`
layout plus release tooling paths to Python analysis.

If command-line Pyright is also needed, reinstall development extras:

```bash
/opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

If VSCode reports a Pylint `E0401:import-error` for a RouterShell module such
as `routershell.lib.cli.base.clear_mode`, make sure the workspace is using the
RouterShell interpreter and reload VSCode. The workspace settings configure the
Pylint extension to run from `/opt/routershell/venv/bin/python` with the
project `src` layout on the import path.

If the Pylint extension reports that Pylint is missing, refresh development
dependencies in the installer-created virtual environment:

```bash
sudo /opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

## RouterShell fails with unable to open database file

If `routershell` exits during startup with this error:

```text
RouterShellDB - ERROR - Error: unable to open database file
AttributeError: 'NoneType' object has no attribute 'cursor'
```

the launcher is missing a writable `ROUTERSHELL_DB_FILE` setting or is using an
older install. Reinstall RouterShell so the launcher-loaded env file gets any
missing required keys and the installed package receives the current DB path
code:

```bash
sudo ./install/install.sh --development
```

For local/development installs, the default database path is
`.routershell/routershell.db` under the project root. For production installs,
the default path is `/var/lib/routershell/routershell.db`.

## Interface database is empty after install

`routershell` should seed the interface database during startup when the
database has no interface records. Start the CLI normally:

```bash
routershell
```

Then verify the discovered interfaces:

```text
show interface database
```

If the database is still empty, confirm that the launcher-loaded environment
file defines a writable `ROUTERSHELL_DB_FILE` path and reinstall with the
current installer.

## Running configuration shows hostname None

If `show running-config` displays this line:

```text
hostname None
```

the runtime database is missing a RouterShell hostname value. Current
RouterShell startup seeds the hostname database value from the operating system
when it is blank, and running configuration output falls back to the OS
hostname instead of rendering `None`.

Start RouterShell normally, then check the running configuration again:

```bash
routershell
```

```text
show running-config
```

# FILE: todo.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell TODO

- Keep Python-version compatibility troubleshooting notes current when CI
  compatibility errors are fixed.
- Keep install troubleshooting notes current when installer errors are fixed.
- Keep IDE import troubleshooting notes current when workspace settings change.
- Keep runtime database troubleshooting notes current when DB path handling changes.
- Keep runtime display troubleshooting notes current when CLI output renders missing DB values.
