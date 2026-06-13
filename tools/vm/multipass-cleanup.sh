#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

PURGE="false"
DRY_RUN="false"
CLEAN_ALL="false"

usage() {
  cat <<'EOF'
Delete RouterShell Multipass test VMs.

Usage:
  multipass-cleanup.sh [--all] [--dry-run] [--purge]

Options:
  --all      Delete every Multipass instance whose name starts with "routershell-".
             Without --all, only RS_VM_NAME is deleted.
  --dry-run  Show which VMs would be deleted without deleting them.
  --purge    Permanently purge deleted Multipass instances after deletion.
  -h, --help Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      CLEAN_ALL="true"
      shift
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
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

mapfile -t vm_names < <(
  multipass list --format csv |
    awk -F, -v vm_name="${RS_VM_NAME}" -v clean_all="${CLEAN_ALL}" '
      NR == 1 { next }
      clean_all == "true" && $1 ~ /^routershell-/ { print $1; next }
      clean_all != "true" && $1 == vm_name { print $1 }
    '
)

if [[ "${#vm_names[@]}" -eq 0 ]]; then
  rs_vm_log "No RouterShell Multipass VMs matched cleanup scope."
  exit 0
fi

for vm_name in "${vm_names[@]}"; do
  if [[ "${DRY_RUN}" == "true" ]]; then
    rs_vm_log "Would delete VM '${vm_name}'."
  else
    rs_vm_log "Deleting VM '${vm_name}'."
    multipass delete "${vm_name}"
  fi
done

if [[ "${PURGE}" == "true" ]]; then
  if [[ "${DRY_RUN}" == "true" ]]; then
    rs_vm_log "Would purge deleted Multipass instances."
  else
    rs_vm_log "Purging deleted Multipass instances."
    multipass purge
  fi
fi
