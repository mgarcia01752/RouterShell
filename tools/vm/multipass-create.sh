#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

rs_vm_require_multipass

if rs_vm_exists; then
  rs_vm_log "VM '${RS_VM_NAME}' already exists."
  multipass info "${RS_VM_NAME}"
  exit 0
fi

rs_vm_log "Launching VM '${RS_VM_NAME}' from image '${RS_VM_IMAGE}'."
multipass launch "${RS_VM_IMAGE}" \
  --name "${RS_VM_NAME}" \
  --cpus "${RS_VM_CPUS}" \
  --memory "${RS_VM_MEMORY}" \
  --disk "${RS_VM_DISK}"

rs_vm_log "Waiting for cloud-init."
multipass exec "${RS_VM_NAME}" -- cloud-init status --wait

rs_vm_configure_virtual_interfaces
rs_vm_verify_virtual_interfaces

rs_vm_log "VM is ready."
multipass info "${RS_VM_NAME}"
