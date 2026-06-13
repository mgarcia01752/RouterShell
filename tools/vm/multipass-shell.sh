#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

rs_vm_require_multipass
rs_vm_require_exists

multipass shell "${RS_VM_NAME}"
