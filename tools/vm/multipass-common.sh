#!/usr/bin/env bash
set -euo pipefail

RS_VM_NAME="${RS_VM_NAME:-routershell-install-test}"
RS_VM_IMAGE="${RS_VM_IMAGE:-24.04}"
RS_VM_CPUS="${RS_VM_CPUS:-2}"
RS_VM_MEMORY="${RS_VM_MEMORY:-2G}"
RS_VM_DISK="${RS_VM_DISK:-12G}"
RS_VM_ARCHIVE="${RS_VM_ARCHIVE:-/tmp/routershell-vm-test.tar.gz}"
RS_VM_REPO_DIR="${RS_VM_REPO_DIR:-/tmp/RouterShell}"

rs_vm_log() {
  echo "[rs-vm] $*"
}

rs_vm_die() {
  echo "[rs-vm] ERROR: $*" >&2
  exit 1
}

rs_vm_require_multipass() {
  if ! command -v multipass >/dev/null 2>&1; then
    rs_vm_die "multipass is required. Install Multipass before running VM tests."
  fi
}

rs_vm_repo_root() {
  git rev-parse --show-toplevel
}

rs_vm_exists() {
  multipass info "${RS_VM_NAME}" >/dev/null 2>&1
}

rs_vm_require_exists() {
  if ! rs_vm_exists; then
    rs_vm_die "VM '${RS_VM_NAME}' does not exist. Run tools/vm/multipass-create.sh first."
  fi
}

rs_vm_create_archive() {
  local repo_root
  repo_root="$(rs_vm_repo_root)"

  rs_vm_log "Creating repository archive: ${RS_VM_ARCHIVE}"
  tar \
    --exclude=".git" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="build" \
    --exclude="dist" \
    -czf "${RS_VM_ARCHIVE}" \
    -C "${repo_root}/.." \
    "$(basename "${repo_root}")"
}
