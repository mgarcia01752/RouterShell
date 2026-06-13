### Summary
Removed the obsolete root-level routershell_version.py module so RouterShell keeps version behavior inside the package and pyproject.toml remains the only stored version source. Updated coding-agent rules and packaging/git/test references to keep the project root clean for non-legacy RouterShell work.

### Modified Files
- CODING_AGENT.md
- pyproject.toml
- routershell_version.py (deleted)
- tests/test_packaging.py
- tools/git/README.md
- tools/git/git-common.sh

### Commands Executed And Results
- `rg -n "routershell_version|py-modules" pyproject.toml CODING_AGENT.md tests tools routershell README.md install -g !tools/agent-review/**` -> pass; no live references found
- `python3 -m py_compile routershell/__init__.py routershell/_version.py routershell/cli.py tools/release/check_version.py tools/release/release.py tools/support/bump_version.py tests/test_packaging.py` -> pass
- `python3 tools/release/check_version.py && python3 tools/support/bump_version.py --current` -> pass; version 0.1.0
- `bash -n install/install.sh install/uninstall.sh tools/git/git-common.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh tools/vm/multipass-common.sh tools/vm/multipass-create.sh tools/vm/multipass-test-install.sh tools/vm/multipass-shell.sh tools/vm/multipass-destroy.sh` -> pass
- `python3 -m venv /tmp/routershell-root-clean-check && /tmp/routershell-root-clean-check/bin/python -m pip install --upgrade pip && /tmp/routershell-root-clean-check/bin/python -m pip install -e .[dev]` -> pass
- `/tmp/routershell-root-clean-check/bin/python -m pytest` -> pass; 4 tests passed
- `/tmp/routershell-root-clean-check/bin/python -m ruff check routershell tools/release/check_version.py tools/release/release.py tools/support/bump_version.py tests/test_packaging.py` -> pass
- `/tmp/routershell-root-clean-check/bin/python -m build` -> pass; sdist and wheel built without routershell_version.py
- `bash -c source tools/git/git-common.sh; rs_run_quality_gates` -> pass available gates; pytest and Ruff skipped for system Python because they are not installed there

### Tests
- `pytest` -> pass; 4 tests passed
- `ruff` -> pass on touched Python files
- `python -m build` -> pass
- `tools/release/check_version.py` -> pass

### Notes / Warnings
- `routershell_version.py` was intentionally deleted; RouterShell is treated as non-legacy for package cleanup.
- Build artifacts under `dist/`, `build/`, and egg-info are ignored by git.

### Remaining TODOs / Follow-Ups
- None

# FILE: routershell_version.py
Deleted. Version access now lives in routershell.__version__ and routershell/_version.py.

# FILE: CODING_AGENT.md
<!-- SPDX-License-Identifier: GPL-2.0-or-later -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# AGENTS.md

This file provides guidance for coding agents working in this repository.
Keep it short, accurate, and updated when workflows change.

## Agent Permissions

<environment_context>
    <sandbox_mode>danger-full-access</sandbox_mode>
    <network_access>enabled</network_access>
    <!-- Access is governed by this file and explicit user approval -->
</environment_context>

## Project Basics

- Language: Python (3.10+)
- User shorthand: when Maurice says `RS`, treat it as `RouterShell`.
- This repo is NOT greenfield; extend existing code and patterns.
- Build/test entry points are defined in `pyproject.toml`, `Makefile`, or `scripts/`.
- Read `README.md` first for setup and usage.
- Type checking is strict; avoid `Any` and generic container types.
- Ruff compliance is required (do not auto-format unless explicitly requested).

## External Consumers (Compatibility Contract)

- PyPNM is the authoritative engine and is consumed by downstream repos (example: PyPNM-CMTS).
- Preserve public API stability unless the user explicitly approves breaking changes.
- Do not embed downstream app concerns into PyPNM (keep PyPNM reusable and transport-agnostic).
- If a change affects downstream repos, call it out explicitly before making it.

## Repo Conventions (PyPNM)

- Persistence is filesystem-based artifacts plus metadata persistence per the DB backend design:
  - Binaries and derived artifacts remain on disk under `.data/` roots.
  - Transaction/group/operation metadata is DB-backed (SQLite or Postgres) per `docs/design/db/`.
- DB backend selection is owned by PyPNM at install time (no runtime “auto switching”).
- SQLite is intended for single-writer deployments (standalone/lab/demo).
- Postgres is recommended for multi-worker / multi-process deployments.

## Documentation

- Docs must follow the existing repo docs layout and conventions.
- Update docs alongside code changes (choose the correct location by inspecting the existing docs tree; do not invent parallel structures).
- Do not modify `mkdocs.yml` or navigation unless explicitly required by the task.
- Markdown must render correctly in both MkDocs and GitHub.
- No emojis in documentation.
- Use generic placeholders:
  - MAC: `aa:bb:cc:dd:ee:ff`
  - IP: `192.168.0.100`
- Emojis are allowed only in `install.sh`; they are prohibited everywhere else.
- When adding new terms or acronyms, update `docs/definition/index.md` and keep entries in alphabetical order.
- After completing a task, create a single “agent review” file that concatenates the full contents of all files changed in that task (path and naming should follow existing repo practice).
- Always regenerate the agent review bundle after any subsequent edits so it reflects every changed file.
- When an error is fixed, add or update a FAQ entry with the error and resolution, and add a TODO entry noting the FAQ update requirement.

### Reuse Index

- Agents MUST consult the existing reuse / symbol index under `tools/agent-review/` (if present) before introducing new:
  - types, validators, ID formats, storage conventions, persistence adapters, or config namespaces
- Any deviation requires an explicit gap justification and user approval.

## DB Backend Migration (Locked Decisions)

Agents working on the DB backend refactor MUST follow the locked decisions recorded in the design docs (see `docs/design/db/`):

- PyPNM owns persistence, schema initialization, and DB APIs.
- Install-time backend selection via `install.sh` flags + interactive default to SQLite.
- Postgres secrets via env var overrides (no plaintext requirement in tracked JSON).
- Idempotent schema apply using shipped DDL assets + seeding `UNKNOWN` sysDescr + default artifact store(s).
- SQLite for single-writer; Postgres recommended for multi-worker / multi-process (especially downstream orchestration use).
- Paths stored in DB are portable (app-root relative), resolved at runtime.
- CI validates SQLite (required) and Postgres (service container, recommended as required).
- JSON ledger persistence is deprecated and removed from runtime paths (optional offline migrator only).

## Configuration

- `system.json` is the single source of truth.
- New configuration namespaces must be implemented as Pydantic BaseModels.
- BaseModels must use one-line `Field(..., description="...")`.
- Avoid generic `str` for semantic identifiers or paths in public models and APIs; use an existing semantic type or add a new alias in `src/pypnm/lib/types.py`.
- When working with MAC or inet strings, validate using `MacAddress()` or `Inet()` instead of assuming `str(...)` formatting is valid.
- Request override defaults: missing or null means use `system.json` defaults; blank strings are invalid.

## Timestamp Conventions

- All stored timestamps are epoch seconds.
- Convert to ISO-8601 only at display or external response boundaries.

## Coding Guidelines (Strict)

- No generic container imports (`Dict`, `List`, `Tuple`, `Union`).
  Use built-in types and `|`.
- Avoid `Any` unless unavoidable; isolate and justify its usage.
- Every function argument must be annotated.
- Avoid `None` returns; prefer empty values unless `None` is semantically required.
- Avoid magic numbers; use named constants.
- Prefer `BaseModel` over raw dicts for public/stateful structures (state, configuration, persistence records).
- dicts are allowed only for short-lived internal glue logic.
- Prefer classes with static methods over standalone functions.
- Public methods MUST have detailed docstrings.
- Private methods may have minimal docstrings.
- Avoid method-level debug logs.
- Do not add Ruff ignores (`# noqa`, `# ruff: noqa`). If an ignore is needed, ask for permission first.
- Logging pattern in classes:

  ```python
  self.logger = logging.getLogger(f"{self.__class__.__name__}")
  ```

- Prefer `match/case` over long if/else chains.
- No code should contain 3+ nested loops. 2 nested loops are discouraged unless necessary.
- No one-line if statements (E701).
- Preserve all existing whitespace and alignment.
- Never auto-format or re-align code.
- Do not enforce snake_case; keep existing naming conventions as-is.

## FastAPI Guidelines (PyPNM)

- Router files must be lean:
  - `router.py` contains routing glue only (APIRouter configuration, endpoint registration, HTTP status translation).
  - No business logic in `router.py`. Business logic must live in `service.py` for that route group (same folder) or a shared service module if reused.
- All request/response bodies must be Pydantic BaseModels.
- Prefer POST for payload submission and endpoint contracts (PyPNM default).
  - Allow GET only where already present or clearly appropriate (health, readiness, version, status).
- Reuse shared models under the existing `src/pypnm/api/common/` structure (inspect current tree before adding anything new).
- Do not block request paths with `time.sleep()`.

## Tests (Mandatory)

- Every phase deliverable MUST include pytest coverage for new or changed behavior.
- Do not claim a phase item is complete unless pytest has been added and executed (or a concrete blocker is documented).
- Tests must remain hermetic: no live CMTS/cable modem dependencies.

## Burndown Governance

- Agents MUST consult the current burndown and DB design docs before implementing work.
- Agents MUST NOT update burndown checkmarks unless explicitly instructed by the user.
- Code written does not imply progress accepted.

## Workflow Rules

- When the user says “train”, read code silently until told otherwise.
- Do not assume missing context; ask.
- Keep changes minimal and scoped.
- Do not refactor unrelated code.
- Avoid destructive commands unless explicitly requested.
- Do not print file contents into chat unless the user explicitly requests it; ask first if unsure.
- Always end tasks with an agent review bundle containing the full contents of all files touched in the task.
- Agent review bundles must start with the standard summary template block below (before any `# FILE:` sections).
- When the user says `CAT_FILES`, create a single bundle file containing the full contents of every file touched in the task, each preceded by `# FILE: <path>`, and provide the `cat` command for the bundle.
- Keep a brief summary of user prompts after any request for a commit message and track changes since the most recent commit message request.
- When asked for a commit message, respond with the format below, keep it succinct, and include all changes since the last commit message request.
- Before changing version behavior or release tooling, review `tools/git/`, `tools/release/`, and `tools/support/bump_version.py` to avoid version-control drift.
- `tools/git/git-save.sh` is the normal save-commit path and accepts `--commit-msg "<commit-msg>"`.
- `tools/release/release.py` is the supported flow for committed release version updates, tags, and pushes.

## Commit Message Format

- If the chat request starts with `commit-msg`, use the message as the value for `./tools/git/git-save.sh --commit-msg "<commit-msg>"`.
- Always include the `./tools/git/git-save.sh --commit-msg` prefix when responding to commit-message requests.
- First line: one-line summary, maximum 50 characters.
- First line must start with one of: `Feature:`, `Bugfix:`, `Docs:`, `Refactor:`, `Test:`, `Tooling:`, `Release:`.
- Detailed description lines are maximum 72 characters per line.
- Every line after the first must start with `-`.
- When the user asks for a commit message, provide plain text for direct paste into the terminal or UI text box.
- Do not wrap commit message suggestions in quotes, backticks, or code fences unless the user explicitly asks for that format.
- Prefer detailed commit messages that describe the current change set clearly.
- Do not default to a one-line commit message when the change set is broad; provide a title plus concise bullet points.
- Avoid redundant wording and avoid repeating the exact prior commit message suggestion unless the diff is unchanged and the user explicitly asks to reuse it.
- If the user asks for "in a text box", return plain text only.
- If the user asks for "in a markdown text box", return the commit message inside a fenced code block with `text`.

### Agent Review Bundle Summary Template (Standard)

Use this Summary block at the very top of every `*.review.md` bundle (before any `# FILE:` sections).

### Summary
<1–3 sentences describing what changed and why. Keep it factual and phase-scoped.>

### Modified Files
- <absolute or repo-relative path 1>
- <path 2>
- <path N>

### Commands Executed And Results
- `<command 1>` → <result (pass/fail + key output)>
- `<command 2>` → <result>
- `<command N>` → <result>

### Tests
- `pytest` → <pass/fail + notes>
- `ruff` → <pass/fail + notes>
- <other> → <pass/fail + notes>

### Notes / Warnings
- <any relevant warnings, deprecations, expected exclusions, or operational notes>
- <or: None>

### Remaining TODOs / Follow-Ups
- <todo 1>
- <todo 2>
- <or: None>

## Repo Hygiene

- License is GPL-2.0-or-later; keep SPDX headers aligned with `LICENSE`.
- For any modified or newly created file, update the SPDX header year to 2026.
- If a file already has a SPDX year and the year has changed, update it as a range (example: 2025 -> 2025-2026).
- Keep implementation code inside packages such as `routershell/` or `lib/`; do not add loose root-level Python modules unless they are established project entry points or standard configuration files.
- Treat RouterShell as non-legacy code for packaging decisions; avoid compatibility shims that keep obsolete root-level modules alive unless Maurice explicitly approves them.
- Keep `tools/` organized by category.
- Do not add files directly under `tools/` root.

## Agent Self-Checks

Before responding:

- Re-read this file and `README.md`.
- Confirm pytest coverage exists or is explicitly blocked.
- Confirm pytest and ruff output have no deprecation warnings (treat as failures).
- Confirm changes align to the current phase and do not leak scope.
- Confirm formatting and alignment are preserved.

## Training

When the user requests "train", read the following sources:

- `AGENTS.md`
- `docs/design/db/` (all files)
- `src/pypnm/lib/` (DB/persistence + config helpers)
- `src/pypnm/api/` (routing/service patterns, where applicable)
- `tools/agent-review/` (all files, if present)

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
python3 -m py_compile routershell/__init__.py routershell/_version.py routershell/cli.py lib/__init__.py
python3 -m compileall -q routershell src lib tools/release tools/support bridge_factory.py bridge_db-test.py test.py
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
  rs_run_check "compile packaging files" "${python_bin}" -m py_compile routershell/__init__.py routershell/_version.py routershell/cli.py lib/__init__.py
  rs_run_check "compile source tree" "${python_bin}" -m compileall -q routershell src lib tools/release tools/support bridge_factory.py bridge_db-test.py test.py
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
