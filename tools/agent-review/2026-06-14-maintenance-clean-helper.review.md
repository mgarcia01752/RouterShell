### Summary
Added a RouterShell maintenance cleanup helper based on the PyPNM clean workflow, scoped to RouterShell-generated local artifacts. The default full cleanup preserves coding-agent review bundles, while `--all-force` includes those bundles, and both full cleanup modes delegate RouterShell VM removal to the existing Multipass cleanup script with `--all --purge`.

### Modified Files
- tools/maintenance/clean.sh
- tools/maintenance/README.md
- tools/reference/tools-layout.md
- tests/tools/test_clean_workflow.py

### Commands Executed And Results
- `bash -n tools/maintenance/clean.sh` -> pass.
- `/opt/routershell/venv/bin/python -m pytest tests/tools/test_clean_workflow.py -q` -> pass, 8 passed.
- `/opt/routershell/venv/bin/python -m ruff check tests/tools/test_clean_workflow.py` -> pass, all checks passed.
- `/opt/routershell/venv/bin/python -m pytest -q` -> pass, 55 passed.
- `/opt/routershell/venv/bin/python -m ruff check .` -> pass, all checks passed.
- `bash -n tools/maintenance/clean.sh tools/vm/*.sh install/install.sh install/uninstall.sh` -> pass.

### Tests
- `pytest` -> pass, 55 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for maintenance, VM, install, and uninstall scripts.

### Notes / Warnings
- `tools/maintenance/clean.sh --all` preserves `tools/agent-review/*.review.md`.
- `tools/maintenance/clean.sh --all-force` removes agent review bundles and delegates VM cleanup to `tools/vm/multipass-cleanup.sh --all --purge`.
- Existing uncommitted installer changes and the `pyproject.toml` version bump were not part of this cleanup-helper change.

### Remaining TODOs / Follow-Ups
- None.

# FILE: tools/maintenance/clean.sh
#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Maurice Garcia

set -euo pipefail

script_name="$(basename "$0")"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
default_root="$(cd "${script_dir}/../.." && pwd)"

ROOT_DIR="${default_root}"
declare -a ACTIONS=()

usage() {
  cat <<EOF
Usage: ${script_name} [OPTIONS] [ROOT_DIR]

Options:
  --all             Clean Python caches, build artifacts, runtime state,
                    release reports, and RouterShell VMs.
  --all-force       Clean everything in --all plus agent review bundles.
  --python          Clean Python caches and test artifacts.
  --build           Clean build/, dist/, and *.egg-info artifacts.
  --runtime         Clean local RouterShell runtime state and logs.
  --release         Clean release reports and release failure logs.
  --agent-review    Clean coding-agent review bundles.
  --vm              Clean RouterShell-created Multipass VMs.
  -h, --help        Show this help and exit.

ROOT_DIR defaults to the RouterShell repository root.
EOF
}

log() {
  echo "[clean] $*"
}

safe_rm() {
  local path

  for path in "$@"; do
    if [[ -e "${path}" || -L "${path}" ]]; then
      rm -rf "${path}"
      log "Removed: ${path}"
    fi
  done
}

clean_python() {
  log "Cleaning Python caches and test artifacts."

  find "${ROOT_DIR}" \
    -path "${ROOT_DIR}/.git" -prune -o \
    -path "${ROOT_DIR}/.venv" -prune -o \
    -type d -name "__pycache__" -print -exec rm -rf {} +

  find "${ROOT_DIR}" \
    -path "${ROOT_DIR}/.git" -prune -o \
    -path "${ROOT_DIR}/.venv" -prune -o \
    -type f -name "*.pyc" -print -exec rm -f {} +

  safe_rm \
    "${ROOT_DIR}/.pytest_cache" \
    "${ROOT_DIR}/.ruff_cache" \
    "${ROOT_DIR}/.mypy_cache" \
    "${ROOT_DIR}/.pyright" \
    "${ROOT_DIR}/.coverage" \
    "${ROOT_DIR}/coverage.xml"
}

clean_build() {
  log "Cleaning build artifacts."

  safe_rm \
    "${ROOT_DIR}/build" \
    "${ROOT_DIR}/dist"

  safe_rm "${ROOT_DIR}"/*.egg-info
  safe_rm "${ROOT_DIR}/src"/*.egg-info
}

clean_runtime() {
  log "Cleaning local RouterShell runtime state."

  safe_rm \
    "${ROOT_DIR}/.routershell" \
    "${ROOT_DIR}/routershell-vm-test.tar.gz" \
    "${ROOT_DIR}/logs"
}

clean_release() {
  log "Cleaning release reports."
  safe_rm "${ROOT_DIR}/release-reports"
}

clean_agent_review() {
  log "Cleaning agent review bundles."
  safe_rm "${ROOT_DIR}/tools/agent-review"/*.review.md
}

clean_vm() {
  local vm_cleanup_script="${ROOT_DIR}/tools/vm/multipass-cleanup.sh"

  log "Cleaning RouterShell Multipass VMs."
  if [[ ! -x "${vm_cleanup_script}" ]]; then
    log "VM cleanup script missing or not executable: ${vm_cleanup_script}"
    return 1
  fi

  "${vm_cleanup_script}" --all --purge
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all|--all-force|--python|--build|--runtime|--release|--agent-review|--vm)
      ACTIONS+=("$1")
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      ROOT_DIR="$1"
      shift
      ;;
  esac
done

if [[ "${#ACTIONS[@]}" -eq 0 ]]; then
  usage
  exit 1
fi

ROOT_DIR="$(realpath "${ROOT_DIR}")"
log "Cleaning in root directory: ${ROOT_DIR}"

for action in "${ACTIONS[@]}"; do
  case "${action}" in
    --all)
      clean_python
      clean_build
      clean_runtime
      clean_release
      clean_vm
      ;;
    --all-force)
      clean_python
      clean_build
      clean_runtime
      clean_release
      clean_agent_review
      clean_vm
      ;;
    --python)
      clean_python
      ;;
    --build)
      clean_build
      ;;
    --runtime)
      clean_runtime
      ;;
    --release)
      clean_release
      ;;
    --agent-review)
      clean_agent_review
      ;;
    --vm)
      clean_vm
      ;;
  esac
done

log "Cleanup complete."

# FILE: tools/maintenance/README.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell Maintenance Tools

## Cleanup

`clean.sh` removes generated local artifacts from a RouterShell workspace.
Run targeted cleanup when possible, and use `--all` only when intentionally
resetting local generated state.

```bash
tools/maintenance/clean.sh --python
tools/maintenance/clean.sh --build
tools/maintenance/clean.sh --runtime
```

Full cleanup:

```bash
tools/maintenance/clean.sh --all
```

Full cleanup preserves `tools/agent-review/*.review.md`. To also remove agent
review bundles, use:

```bash
tools/maintenance/clean.sh --all-force
```

`--all` also clears RouterShell-created Multipass VMs by delegating to:

```bash
tools/vm/multipass-cleanup.sh --all --purge
```

The cleanup script does not remove the project `.venv` during Python cache
cleanup.

# FILE: tools/reference/tools-layout.md
<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright (c) 2026 Maurice Garcia -->

# RouterShell Tools Layout

Tools are grouped by purpose so destructive host operations are easier to
identify before running them.

## Categories

- `agent-review/`: Coding-agent review bundles for completed tasks.
- `dev/`: Local development cleanup helpers.
- `disk/`: Disk inspection, formatting, and boot media helpers. These can be
  destructive.
- `examples/`: Example generators and usage demonstrations. Examples should not
  modify system files unless an explicit output path or flag is provided.
- `git/`: RouterShell Git save, push, and branch-history helpers.
- `hardware/`: Host hardware inspection helpers.
- `maintenance/`: Repository cleanup helpers for generated local artifacts.
- `network/`: Network lab and interface mutation helpers. These can change host
  links, routes, firewall state, and wireless services.
- `reference/`: Captured command references and static notes.
- `release/`: Version checks, release automation, and release reports.
- `services/`: Service setup, teardown, and simulation helpers. These can
  install, remove, start, or stop host services.
- `support/`: Small support helpers used by release or workflow scripts.
- `vm/`: Disposable VM workflows for installer testing.

## Safety

Review scripts under `disk/`, `network/`, and `services/` before running them.
Prefer disposable VM testing for workflows that can alter host networking,
packages, disks, or service state.

# FILE: tests/tools/test_clean_workflow.py
"""Maintenance cleanup script tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLEAN_SCRIPT = REPO_ROOT / "tools" / "maintenance" / "clean.sh"
MAINTENANCE_README = REPO_ROOT / "tools" / "maintenance" / "README.md"
TOOLS_LAYOUT = REPO_ROOT / "tools" / "reference" / "tools-layout.md"


def test_clean_script_is_valid_bash() -> None:
    subprocess.run(
        ["bash", "-n", str(CLEAN_SCRIPT)],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def test_clean_script_documents_expected_router_shell_actions() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert "--python" in clean_script
    assert "--build" in clean_script
    assert "--runtime" in clean_script
    assert "--release" in clean_script
    assert "--agent-review" in clean_script
    assert "--vm" in clean_script
    assert "--all" in clean_script
    assert "--all-force" in clean_script


def test_clean_script_preserves_virtualenv_while_cleaning_python_cache() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert '-path "${ROOT_DIR}/.venv" -prune' in clean_script
    assert '-type d -name "__pycache__"' in clean_script
    assert '-type f -name "*.pyc"' in clean_script
    assert '"${ROOT_DIR}/.pytest_cache"' in clean_script
    assert '"${ROOT_DIR}/.ruff_cache"' in clean_script


def test_clean_script_removes_build_and_runtime_artifacts() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert '"${ROOT_DIR}/build"' in clean_script
    assert '"${ROOT_DIR}/dist"' in clean_script
    assert '"${ROOT_DIR}/src"/*.egg-info' in clean_script
    assert '"${ROOT_DIR}/.routershell"' in clean_script
    assert '"${ROOT_DIR}/release-reports"' in clean_script
    assert '"${ROOT_DIR}/tools/agent-review"/*.review.md' in clean_script


def test_clean_all_delegates_vm_cleanup_to_vm_script() -> None:
    clean_script = CLEAN_SCRIPT.read_text()

    assert 'vm_cleanup_script="${ROOT_DIR}/tools/vm/multipass-cleanup.sh"' in clean_script
    assert '"${vm_cleanup_script}" --all --purge' in clean_script
    assert "clean_vm" in clean_script


def test_clean_all_preserves_agent_review_until_all_force() -> None:
    clean_script = CLEAN_SCRIPT.read_text()
    all_block = clean_script.split('    --all)\n', maxsplit=1)[1].split("      ;;\n", maxsplit=1)[0]
    all_force_block = clean_script.split('    --all-force)\n', maxsplit=1)[1].split("      ;;\n", maxsplit=1)[0]

    assert "clean_agent_review" not in all_block
    assert "clean_agent_review" in all_force_block


def test_tools_layout_documents_maintenance_category() -> None:
    tools_layout = TOOLS_LAYOUT.read_text()

    assert "`maintenance/`" in tools_layout
    assert "Repository cleanup helpers" in tools_layout


def test_maintenance_readme_documents_vm_cleanup_delegation() -> None:
    maintenance_readme = MAINTENANCE_README.read_text()

    assert "tools/maintenance/clean.sh --all" in maintenance_readme
    assert "tools/maintenance/clean.sh --all-force" in maintenance_readme
    assert "tools/vm/multipass-cleanup.sh --all --purge" in maintenance_readme
    assert "does not remove the project `.venv`" in maintenance_readme
