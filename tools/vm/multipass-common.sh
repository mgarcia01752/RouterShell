#!/usr/bin/env bash
set -euo pipefail

RS_VM_NAME="${RS_VM_NAME:-routershell-install-test}"
RS_VM_IMAGE="${RS_VM_IMAGE:-24.04}"
RS_VM_CPUS="${RS_VM_CPUS:-2}"
RS_VM_MEMORY="${RS_VM_MEMORY:-2G}"
RS_VM_DISK="${RS_VM_DISK:-12G}"
RS_VM_ARCHIVE="${RS_VM_ARCHIVE:-/tmp/routershell-vm-test.tar.gz}"
RS_VM_REPO_DIR="${RS_VM_REPO_DIR:-/tmp/RouterShell}"
RS_VM_VIRTUAL_INTERFACES="${RS_VM_VIRTUAL_INTERFACES:-10}"
RS_VM_VIRTUAL_INTERFACE_PREFIX="${RS_VM_VIRTUAL_INTERFACE_PREFIX:-rs1g}"
RS_VM_VIRTUAL_INTERFACE_RATE="${RS_VM_VIRTUAL_INTERFACE_RATE:-1gbit}"

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

rs_vm_validate_virtual_interface_count() {
  if [[ ! "${RS_VM_VIRTUAL_INTERFACES}" =~ ^[0-9]+$ ]]; then
    rs_vm_die "RS_VM_VIRTUAL_INTERFACES must be a non-negative integer."
  fi
}

rs_vm_configure_virtual_interfaces() {
  rs_vm_validate_virtual_interface_count

  if [[ "${RS_VM_VIRTUAL_INTERFACES}" == "0" ]]; then
    rs_vm_log "Skipping virtual network interface setup."
    return 0
  fi

  rs_vm_log "Configuring ${RS_VM_VIRTUAL_INTERFACES} virtual ${RS_VM_VIRTUAL_INTERFACE_RATE} interfaces."
  multipass exec "${RS_VM_NAME}" -- sudo bash -s -- \
    "${RS_VM_VIRTUAL_INTERFACE_PREFIX}" \
    "${RS_VM_VIRTUAL_INTERFACES}" \
    "${RS_VM_VIRTUAL_INTERFACE_RATE}" <<'EOF'
set -euo pipefail

prefix="$1"
count="$2"
rate="$3"

modprobe dummy >/dev/null 2>&1 || true

for index in $(seq 0 $((count - 1))); do
  interface_name="${prefix}${index}"

  if ! ip link show dev "${interface_name}" >/dev/null 2>&1; then
    ip link add name "${interface_name}" type dummy
  fi

  ip link set dev "${interface_name}" mtu 1500
  ip link set dev "${interface_name}" up
  tc qdisc replace dev "${interface_name}" root tbf rate "${rate}" burst 128kb latency 50ms >/dev/null 2>&1 || true
done
EOF
}

rs_vm_verify_virtual_interfaces() {
  rs_vm_validate_virtual_interface_count

  if [[ "${RS_VM_VIRTUAL_INTERFACES}" == "0" ]]; then
    return 0
  fi

  rs_vm_log "Verifying virtual network interfaces."
  multipass exec "${RS_VM_NAME}" -- bash -s -- \
    "${RS_VM_VIRTUAL_INTERFACE_PREFIX}" \
    "${RS_VM_VIRTUAL_INTERFACES}" <<'EOF'
set -euo pipefail

prefix="$1"
count="$2"

for index in $(seq 0 $((count - 1))); do
  ip link show dev "${prefix}${index}" >/dev/null
done
EOF
}
