#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

PURGE="false"

usage() {
  cat <<'EOF'
Delete the RouterShell Multipass test VM.

Usage:
  multipass-destroy.sh [--purge]

Options:
  --purge   Permanently purge deleted Multipass instances after deletion.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --purge)
      PURGE="true"
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

if ! rs_vm_exists; then
  rs_vm_log "VM '${RS_VM_NAME}' does not exist."
  exit 0
fi

rs_vm_log "Deleting VM '${RS_VM_NAME}'."
multipass delete "${RS_VM_NAME}"

if [[ "${PURGE}" == "true" ]]; then
  rs_vm_log "Purging deleted Multipass instances."
  multipass purge
else
  rs_vm_log "VM deleted. Run with --purge to reclaim disk space."
fi
