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
  if [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
    printf '%s\n' "${VIRTUAL_ENV}/bin/python"
    return
  fi

  if [[ -x "/opt/routershell/venv/bin/python" ]]; then
    printf '%s\n' "/opt/routershell/venv/bin/python"
    return
  fi

  if [[ -x ".venv/bin/python" ]]; then
    printf '%s\n' ".venv/bin/python"
    return
  fi

  if command -v python >/dev/null 2>&1; then
    command -v python
    return
  fi

  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  echo "ERROR: python3 or python is required." >&2
  exit 1
}

rs_run_quality_gates() {
  local python_bin
  python_bin="$(rs_python)"

  rs_run_check "RouterShell software QA checker" "${python_bin}" tools/release/qa_checker.py --skip-pycycle
}
