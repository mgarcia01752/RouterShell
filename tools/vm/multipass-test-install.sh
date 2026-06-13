#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

SKIP_OS_PACKAGES="${SKIP_OS_PACKAGES:-false}"
DEVELOPMENT_INSTALL="${DEVELOPMENT_INSTALL:-false}"

usage() {
  cat <<'EOF'
Copy the current RouterShell worktree into the Multipass VM and test install it.

Usage:
  multipass-test-install.sh [--development] [--skip-os-packages]

Environment:
  RS_VM_NAME                       VM name. Default: routershell-install-test
  RS_VM_REPO_DIR                   Path inside VM. Default: /tmp/RouterShell
  RS_VM_VIRTUAL_INTERFACES         Virtual interface count. Default: 10
  RS_VM_VIRTUAL_INTERFACE_PREFIX   Interface name prefix. Default: rs1g

By default, the VM test runs the production runtime install path. Use
--development to test editable install mode with development dependencies.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-os-packages)
      SKIP_OS_PACKAGES="true"
      shift
      ;;
    --development)
      DEVELOPMENT_INSTALL="true"
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
rs_vm_require_exists
rs_vm_configure_virtual_interfaces
rs_vm_verify_virtual_interfaces
rs_vm_create_archive

rs_vm_log "Copying archive into VM."
multipass transfer "${RS_VM_ARCHIVE}" "${RS_VM_NAME}:/tmp/routershell-vm-test.tar.gz"

rs_vm_log "Refreshing VM test workspace."
multipass exec "${RS_VM_NAME}" -- bash -lc "rm -rf '${RS_VM_REPO_DIR}' && tar -xzf /tmp/routershell-vm-test.tar.gz -C /tmp"

install_cmd="sudo '${RS_VM_REPO_DIR}/install/install.sh'"
if [[ "${DEVELOPMENT_INSTALL}" == "true" ]]; then
  install_cmd="${install_cmd} --development"
fi

if [[ "${SKIP_OS_PACKAGES}" == "true" ]]; then
  install_cmd="${install_cmd} --skip-os-packages"
fi

rs_vm_log "Running RouterShell installer inside VM."
multipass exec "${RS_VM_NAME}" -- bash -lc "${install_cmd}"

rs_vm_log "Verifying RouterShell runtime install."
multipass exec "${RS_VM_NAME}" -- bash -lc "
  set -euo pipefail
  test -x /usr/local/bin/routershell
  test -x /usr/local/bin/routershell-factory-reset
  test -x /opt/routershell/venv/bin/python
  sudo test -f /var/lib/routershell/baseline/manifest.json
  /opt/routershell/venv/bin/python - <<'PY'
import routershell
from routershell import cli
from routershell.lib.network_manager.network_operations.interface import Interface

assert callable(cli.main)
assert callable(cli.factory_reset)
expected = [f'${RS_VM_VIRTUAL_INTERFACE_PREFIX}{index}' for index in range(${RS_VM_VIRTUAL_INTERFACES})]
interfaces = Interface().get_os_network_interfaces()
missing = [interface for interface in expected if interface not in interfaces]
assert not missing, f'Missing RouterShell VM interfaces: {missing}'
print(f'RouterShell import OK: {routershell.__version__}')
PY
"

rs_vm_log "Install test passed."
