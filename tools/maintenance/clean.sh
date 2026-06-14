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
