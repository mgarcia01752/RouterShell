### Summary
Adapted the PyPNM Git helper workflow into RouterShell save, push, and guarded branch-history reset scripts. Renamed the helper files to remove the `rs-` prefix while keeping `RS` only as Maurice's shorthand in agent instructions.

### Modified Files
- CODING_AGENT.md
- README.md
- tools/git/README.md
- tools/git/git-common.sh
- tools/git/git-save.sh
- tools/git/git-push.sh
- tools/git/git-reset-branch-history.sh

### Commands Executed And Results
- `find /home/dev01/Projects/PyPNM/tools/git -maxdepth 3 -type f -print | sort` → pass; identified PyPNM source scripts.
- `sed -n '1,260p' /home/dev01/Projects/PyPNM/tools/git/git-save.sh` → pass; read source save workflow.
- `sed -n '1,260p' /home/dev01/Projects/PyPNM/tools/git/git-push.sh` → pass; read source push workflow.
- `sed -n '1,320p' /home/dev01/Projects/PyPNM/tools/git/git-reset-branch-history.sh` → pass; read source reset workflow.
- `bash -n tools/git/git-common.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh` → pass.
- stale prefixed helper reference scan → pass; no old prefixed helper references remain.
- `rg -n "\bRS\b" CODING_AGENT.md README.md tools/git` → pass; only intended `CODING_AGENT.md` shorthand note remains.
- `bash -c 'source tools/git/git-common.sh; rs_run_quality_gates'` → pass; pyproject, version consistency, compile, and shell syntax checks passed; pytest and ruff skipped because not installed.
- `find . -name '__pycache__' -type d -prune -exec rm -rf {} +` → pass; removed generated validation caches.

### Tests
- `pytest` → skipped by quality gate because pytest is not installed in this interpreter.
- `ruff` → skipped by quality gate because Ruff is not installed in this interpreter.
- `bash -n` → pass for the updated git scripts.
- RouterShell quality gates → pass for available checks.

### Notes / Warnings
- The git helper filenames are now `git-common.sh`, `git-save.sh`, `git-push.sh`, and `git-reset-branch-history.sh`.
- The history reset helper is intentionally guarded with clean-worktree checks, backup branch creation by default, and an exact `YES` confirmation prompt.

### Remaining TODOs / Follow-Ups
- Install `.[dev]` in a virtual environment so quality gates can run pytest and Ruff instead of skipping them.
- Decide whether additional secret-scanning helpers should be brought over from PyPNM once RouterShell has an equivalent security tools layout.

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

# FILE: tools/git/git-save.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="v1.0.0"

usage() {
  cat <<'EOF'
Stage and commit the current RouterShell Git repository.

Usage:
  git-save.sh [--commit-msg "Message"] [--push] [--skip-checks]

Options:
  --commit-msg   Commit message prefix (default: "Update RouterShell").
  --push         Push the current branch after commit.
  --skip-checks  Skip local quality gates.
  -h, --help     Show this help.
  -v, --version  Show script version.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/git-common.sh"

commit_msg="Update RouterShell"
do_push="false"
skip_checks="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit-msg)
      shift
      if [[ "${1:-}" == "" ]] || [[ "${1}" =~ ^[[:space:]]*$ ]]; then
        echo "ERROR: --commit-msg requires a non-empty value." >&2
        exit 1
      fi
      commit_msg="$1"
      shift
      ;;
    --push)
      do_push="true"
      shift
      ;;
    --skip-checks)
      skip_checks="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -v|--version)
      echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

rs_require_git_repo
cd "$(rs_repo_root)"

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "${current_branch}" == "HEAD" ]]; then
  echo "ERROR: Detached HEAD detected. Check out a branch before committing." >&2
  exit 1
fi

pending_changes="$(git status --short)"

echo "========================================"
echo "RouterShell Git Save"
echo "Branch: ${current_branch}"
echo "Changes:"
if [[ -z "${pending_changes}" ]]; then
  echo "  (none)"
else
  printf '%s\n' "${pending_changes}"
fi
echo "========================================"

if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

if [[ "${skip_checks}" != "true" ]]; then
  echo "Running RouterShell quality gates..."
  rs_run_quality_gates
else
  echo "Quality gates skipped by request."
fi

timestamp="$(date +'%Y-%m-%d %H:%M:%S')"
final_msg="${commit_msg} - ${timestamp}"

echo "Staging changes..."
git add -A

echo "Creating commit..."
git commit -m "${final_msg}"

if [[ "${do_push}" == "true" ]]; then
  remote_name="$(git config branch."${current_branch}".remote || true)"
  push_remote="${remote_name:-origin}"

  echo "Pushing to ${push_remote} (${current_branch})..."
  if [[ -z "${remote_name}" ]]; then
    git push -u "${push_remote}" "${current_branch}"
  else
    git push "${push_remote}" "${current_branch}"
  fi
else
  echo "Push skipped. Use --push to push."
fi

echo "Done."

# FILE: tools/git/git-push.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="v1.0.0"

usage() {
  cat <<'EOF'
Auto-commit and push the current RouterShell Git repository.

Usage:
  git-push.sh [--commit-msg "Message"] [--skip-checks]

If --commit-msg is not supplied, a timestamped "Auto-push RouterShell" message is used.
Pushing non-main branches requires two confirmations.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/git-common.sh"

commit_msg=""
skip_checks="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit-msg)
      shift
      if [[ "${1:-}" == "" ]] || [[ "${1}" =~ ^[[:space:]]*$ ]]; then
        echo "ERROR: --commit-msg requires a non-empty value." >&2
        exit 1
      fi
      commit_msg="$1"
      shift
      ;;
    --skip-checks)
      skip_checks="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -v|--version)
      echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

rs_require_git_repo
cd "$(rs_repo_root)"

current_branch="$(git rev-parse --abbrev-ref HEAD)"
if [[ "${current_branch}" == "HEAD" ]]; then
  echo "ERROR: Detached HEAD detected. Check out a branch before pushing." >&2
  exit 1
fi

if [[ -z "${commit_msg}" ]]; then
  commit_msg="Auto-push RouterShell: $(date +'%Y-%m-%d %H:%M:%S')"
fi

if [[ "${current_branch}" != "main" && "${current_branch}" != "hot-fix" ]]; then
  echo "WARNING: Current branch is '${current_branch}' (not main/hot-fix)." >&2
  echo "WARNING: This branch may not exist on the remote repository." >&2
  read -r -p "Continue anyway? [y/N]: " confirm_first
  if [[ "${confirm_first,,}" != "y" && "${confirm_first,,}" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi

  read -r -p "Are you really sure you want to push '${current_branch}'? [y/N]: " confirm_second
  if [[ "${confirm_second,,}" != "y" && "${confirm_second,,}" != "yes" ]]; then
    echo "Aborted."
    exit 1
  fi
fi

if git diff --quiet && git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

if [[ "${skip_checks}" != "true" ]]; then
  echo "Running RouterShell quality gates..."
  rs_run_quality_gates
else
  echo "Quality gates skipped by request."
fi

echo "Staging changes..."
git add -A

echo "Creating commit..."
git commit -m "${commit_msg}"

remote_name="$(git config branch."${current_branch}".remote || true)"
push_remote="${remote_name:-origin}"

echo "Pushing to ${push_remote} (${current_branch})..."
if [[ -z "${remote_name}" ]]; then
  git push -u "${push_remote}" "${current_branch}"
else
  if ! git push "${push_remote}" "${current_branch}"; then
    echo "Initial push failed; retrying with upstream setup..."
    git push -u "${push_remote}" "${current_branch}"
  fi
fi

echo "Done."

# FILE: tools/git/git-reset-branch-history.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="v1.0.0"

REMOTE="origin"
BRANCH="main"
COMMIT_MESSAGE="Initial RouterShell clean commit"
ALLOW_DIRTY_WORKTREE="0"
CREATE_BACKUP="1"

usage() {
  cat <<EOF
${SCRIPT_NAME} - Rewrite a RouterShell Git branch as a fresh orphan history.

Usage:
  ${SCRIPT_NAME} [options]

Options:
  --remote NAME          Remote name to push to (default: origin)
  --branch NAME          Branch name to rewrite (default: main)
  --message TEXT         Commit message for the new initial commit
                         (default: "Initial RouterShell clean commit")
  --allow-dirty          Allow running with a dirty working tree.
  --no-backup            Do NOT create a backup branch before rewriting.
  -h, --help             Show this help message.
  -v, --version          Show script version.

WARNING:
  This script force-pushes and rewrites history on the target branch.
  By default it creates and pushes a backup branch first.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --message)
      COMMIT_MESSAGE="${2:-}"
      shift 2
      ;;
    --allow-dirty)
      ALLOW_DIRTY_WORKTREE="1"
      shift
      ;;
    --no-backup)
      CREATE_BACKUP="0"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -v|--version)
      echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${REMOTE}" || -z "${BRANCH}" || -z "${COMMIT_MESSAGE}" ]]; then
  echo "ERROR: --remote, --branch, and --message values must be non-empty." >&2
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "ERROR: This script must be run inside a Git repository." >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "${repo_root}"

if [[ "${ALLOW_DIRTY_WORKTREE}" != "1" ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "ERROR: Working tree is not clean." >&2
    echo "Commit, stash, or discard changes before running this script," >&2
    echo "or re-run with --allow-dirty if you are sure." >&2
    exit 1
  fi
fi

echo "Remote: ${REMOTE}"
echo "Branch: ${BRANCH}"
echo
if [[ "${CREATE_BACKUP}" == "1" ]]; then
  echo "This will:"
  echo "  - Create a BACKUP branch from the current '${BRANCH}' tip on '${REMOTE}'"
  echo "  - Create a NEW orphan history for branch '${BRANCH}'"
  echo "  - Use the CURRENT WORKING TREE as the new initial commit"
  echo "  - FORCE-PUSH the rewritten branch to remote '${REMOTE}'"
else
  echo "This will:"
  echo "  - Create a NEW orphan history for branch '${BRANCH}'"
  echo "  - Use the CURRENT WORKING TREE as the new initial commit"
  echo "  - FORCE-PUSH the rewritten branch to remote '${REMOTE}'"
  echo "  - Skip backup branch creation"
fi
echo
read -r -p "Type YES to continue: " confirm

if [[ "${confirm}" != "YES" ]]; then
  echo "Aborted."
  exit 1
fi

echo "Fetching latest refs from '${REMOTE}'..."
git fetch "${REMOTE}"

echo "Checking out branch '${BRANCH}'..."
git checkout "${BRANCH}"

echo "Pulling latest from '${REMOTE}/${BRANCH}'..."
git pull "${REMOTE}" "${BRANCH}"

backup_branch=""
if [[ "${CREATE_BACKUP}" == "1" ]]; then
  current_commit="$(git rev-parse HEAD)"
  timestamp="$(date +%Y%m%d-%H%M%S)"
  backup_branch="${BRANCH}-backup-${timestamp}"

  echo "Creating backup branch '${backup_branch}' at ${current_commit}..."
  git branch "${backup_branch}" "${current_commit}"

  echo "Pushing backup branch '${backup_branch}' to remote '${REMOTE}'..."
  git push "${REMOTE}" "${backup_branch}"
fi

orphan_branch="__rs_orphan_reset_${BRANCH}"

echo "Creating orphan branch '${orphan_branch}'..."
git checkout --orphan "${orphan_branch}"

echo "Staging all files for new initial commit..."
git add -A

echo "Creating new initial commit..."
git commit -m "${COMMIT_MESSAGE}"

echo "Renaming orphan branch '${orphan_branch}' to '${BRANCH}'..."
git branch -M "${BRANCH}"

echo "Force-pushing rewritten branch '${BRANCH}' to remote '${REMOTE}'..."
git push -f "${REMOTE}" "${BRANCH}"

echo
echo "Done."
echo "Branch '${BRANCH}' on '${REMOTE}' now has a fresh history with a new initial commit."
if [[ "${CREATE_BACKUP}" == "1" ]]; then
  echo "Previous history is preserved on backup branch: ${backup_branch}"
else
  echo "No backup branch was created."
fi

