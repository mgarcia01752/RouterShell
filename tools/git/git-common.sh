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
  rs_run_check "compile source tree" "${python_bin}" -m compileall -q routershell lib tests tools/examples tools/hardware tools/release tools/support
  rs_run_check "shell syntax" bash -c 'find start.sh install tools -path "tools/agent-review" -prune -o -name "*.sh" -exec bash -n {} \;'

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
