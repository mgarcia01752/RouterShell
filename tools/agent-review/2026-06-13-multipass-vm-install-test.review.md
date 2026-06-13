### Summary
Added a Multipass-based VM workflow for testing the RouterShell generic Linux installer away from the development workstation. The workflow can create a disposable Ubuntu VM, copy the current worktree into it, run the installer, verify the installed runtime, open a shell, and destroy the VM.

### Modified Files
- README.md
- install/README.md
- tools/vm/README.md
- tools/vm/multipass-common.sh
- tools/vm/multipass-create.sh
- tools/vm/multipass-test-install.sh
- tools/vm/multipass-shell.sh
- tools/vm/multipass-destroy.sh

### Commands Executed And Results
- `command -v multipass || true` -> pass; no Multipass binary found on PATH.
- `command -v vagrant || true` -> pass; no Vagrant binary found on PATH.
- `command -v virsh || true` -> pass; no libvirt `virsh` binary found on PATH.
- `command -v qemu-system-x86_64 || true` -> pass; no QEMU binary found on PATH.
- `chmod +x tools/vm/multipass-common.sh tools/vm/multipass-create.sh tools/vm/multipass-test-install.sh tools/vm/multipass-shell.sh tools/vm/multipass-destroy.sh && bash -n tools/vm/multipass-common.sh tools/vm/multipass-create.sh tools/vm/multipass-test-install.sh tools/vm/multipass-shell.sh tools/vm/multipass-destroy.sh install/install.sh install/uninstall.sh` -> pass.
- `tools/vm/multipass-test-install.sh --help` -> pass after executable bit was applied.
- `tools/vm/multipass-destroy.sh --help` -> pass.
- `rg -n "[[:blank:]]$" README.md install/README.md tools/vm || true` -> pass; no trailing whitespace found.

### Tests
- `bash -n` -> pass for VM scripts and install scripts.
- VM creation -> not run; Multipass is not installed on this host.
- Installer execution inside VM -> not run; requires Multipass.
- `pytest` -> not run; shell/docs-only VM harness update.
- `ruff` -> not run; shell/docs-only VM harness update.

### Notes / Warnings
- The harness defaults to Ubuntu 24.04 in Multipass.
- The install test copies the current worktree into the VM, so uncommitted installer changes can be tested before commit.
- The test intentionally verifies imports and launchers but does not start the interactive RouterShell CLI.

### Remaining TODOs / Follow-Ups
- Install Multipass on the development workstation or choose another VM provider.
- Run `tools/vm/multipass-create.sh` and `tools/vm/multipass-test-install.sh` once Multipass is available.
- Add Fedora/RHEL-compatible and openSUSE/SUSE VM variants after the Ubuntu path is proven.

# FILE: README.md
# RouterShell (WORK IN PROGRESS)

RouterShell is an open-source, IOS-like CLI distribution written in Python 3. It is designed to provide a flexible and user-friendly command-line interface for network administrators and enthusiasts, offering a comprehensive range of networking features and capabilities tailored to diverse needs.

**Key Features of RouterShell:**

1. **Interface Configurations:** RouterShell supports a variety of interface configurations, including:
   - **Loopback Interfaces:** Ideal for testing and diagnostics, loopback interfaces are easy to set up and provide a versatile tool for network validation.
   - **Physical Interfaces:** Compatibility with Ethernet, USB, wireless (WiFi and cellular) interfaces, making it adaptable to various hardware environments.
   - **Bridging:** Enables the connection of different network segments, which is beneficial in creating complex network topologies.
   - **VLAN Support:** Facilitates network segmentation and organization, which is crucial for larger, more intricate networks.

2. **Tunneling:** RouterShell includes support for tunneling protocols, such as GRE (Generic Routing Encapsulation), allowing the creation of point-to-point and point-to-multipoint tunnels. This feature enables the encapsulation of packets for secure and efficient transport across different network segments, which is useful in VPNs and cross-network communication.

3. **NAT (Network Address Translation) Support:** Provides NAT functionality, essential for translating private IP addresses to public IP addresses, commonly required in both home and enterprise network setups. This feature helps in conserving public IP addresses and adds a layer of security by masking internal network structures.

4. **Access Control List (ACL) and Firewall Support:** RouterShell supports ACLs and firewall functionalities, offering enhanced network security by controlling incoming and outgoing traffic based on predefined rules. This is crucial for protecting network resources and managing data flow effectively.

RouterShell aims to provide a comprehensive CLI experience similar to traditional network operating systems, with the flexibility and extensibility of Python, making it a valuable tool for managing and automating network environments.


Regarding its intended use:

- **Quick Router Deployment:** RouterShell is designed to expedite router setup using a minimal Linux image, a valuable feature when rapid deployment is crucial.

- **Router-on-a-Stick Configuration:** RouterShell supports the "router-on-a-stick" configuration, useful for scenarios requiring network segmentation.

- **Compatibility with Embedded Router Distributions:** While initially developed with a focus on Ubuntu, RouterShell's lower layers are designed to be OS-agnostic, potentially allowing compatibility with various lightweight Linux distributions.

In conclusion, RouterShell is a router CLI distribution with features well-suited for specific network setups and security requirements. However, it is crucial to thoroughly assess your specific networking needs and consider whether RouterShell aligns with them before selecting it as your networking solution. Its comprehensive feature set, including NAT support and access control list/firewall support, makes it a versatile choice for network administrators and enthusiasts looking to configure and manage network infrastructure efficiently.

## Table of Contents

- [Global Privileged EXEC Commands](doc/cli/global_priv_exec_cmd.md): Learn about global privileged EXEC commands for system-level tasks.

- [ARP (Address Resolution Protocol)](doc/cli/configure/arp.md): Understand ARP and how it works in RouterShell.

- [Bridge Configuration](doc/cli/configure/bridge.md): Configure and manage bridges in RouterShell.

- [DHCPv4/v6 Configuration](doc/cli/configure/dhcp.md): Explore DHCP (Dynamic Host Configuration Protocol) setup for IPv4 and IPv6.

- [Interface Configuration](doc/cli/configure/config.md): Configure and manage network interfaces in RouterShell.

- [NAT (Network Address Translation)](doc/cli/configure/nat.md): Set up Network Address Translation for your RouterShell router.

- [Route Configuration](doc/cli//configureroute.md): Understand the routing and how to configure it in RouterShell.

- [VLAN Configuration](doc/cli//configurevlan.md): Configure and manage VLANs in your RouterShell network.

- [System Configuration](doc/cli/global/system.md): Learn about system-level configuration options in RouterShell.

- [Wireless Configuration](doc/cli/configure/wireless.md): Explore wireless network configuration in RouterShell.

## Router Configuration Examples

Explore a variety of router configuration examples to help you get started with RouterShell:

These examples cover scenarios like configuring a four-port bridge with VLAN support, setting up a four-port switch, and configuring NAT for a two-port setup. You can access the detailed instructions and information in the respective configuration files.

- [Four-Port Bridge with VLAN Configuration](doc/cli/four_port_bridge_vlan_config.md): This example guides you through setting up a four-port bridge with VLAN support, allowing for network segmentation and efficient traffic management.

- [Four-Port Switch Configuration](doc/cli/four_port_switch_config.md): Learn how to configure a four-port switch, which is essential for creating a network with multiple connected devices.

- [Two-Port NAT Configuration](doc/cli/two_port_nat_config.md): Understand how to set up Network Address Translation (NAT) for a two-port router, enabling the translation of private IP addresses to public IP addresses.

These configuration examples serve as practical guides to help you implement specific networking setups with RouterShell. Refer to the linked documentation files for step-by-step instructions and detailed explanations.

Feel free to explore these examples and adapt them to your networking needs. If you have any questions or need further assistance, don't hesitate to contact our community or project team. Thank you for choosing RouterShell!

## Additional Resources

Please select the specific documentation file you are interested in from the table of contents above to access detailed information and instructions for configuring and using RouterShell.

If you have any questions or need further assistance, please feel free to reach out to our community or project team. Thank you for choosing RouterShell!

## Linux Runtime Install

[README INSTALLATION](install/README.md)

RouterShell includes a generic installer for non-embedded Linux hosts such as
Ubuntu, Debian, Fedora, RHEL-compatible systems, and openSUSE. Embedded and
BusyBox-style targets are intentionally out of scope for this installer.

Test installer changes in a disposable VM before running them on a development
workstation. See [RouterShell VM Install Testing](tools/vm/README.md).

```bash
sudo ./install/install.sh
routershell
```

## Run RouterShell From Source

```bash
./start.sh
```

## Python Development Install

RouterShell now includes Python packaging metadata in `pyproject.toml`.
For local development, use an isolated virtual environment and install the
project in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

After installation, run the CLI entry point:

```bash
routershell
```

Factory reset is also exposed as a console entry point:

```bash
routershell-factory-reset
```

Build distribution artifacts with:

```bash
python -m build
```

Run validation with:

```bash
python -m pytest
python -m ruff check .
```

## Git Helpers

Git helper scripts live under `tools/git/`:

```bash
./tools/git/git-save.sh --commit-msg "Update RouterShell"
./tools/git/git-push.sh --commit-msg "Update RouterShell"
```

See [RouterShell Git Helpers](tools/git/README.md) for save, push, and guarded branch
history reset workflows.

## Release Helpers

Release helper scripts live under `tools/release/`:

```bash
./tools/release/check_version.py
./tools/release/release.py --next patch --dry-run
```

See [RouterShell Release Helpers](tools/release/README.md) for version checks,
dry runs, releases, and commit reports.

## [TODO](todo.md)

# FILE: install/README.md
# RouterShell Installation Guide

This guide provides step-by-step instructions for installing and uninstalling RouterShell on a general-purpose Linux system.
This install path is for non-embedded hosts such as Ubuntu, Debian, Fedora, RHEL-compatible systems, and openSUSE.

BusyBox, Alpine, OpenWrt, Buildroot, Yocto images, and embedded/minimal router images are intentionally out of scope until those targets have a dedicated install design.

## Prerequisites

- You must have sudo privileges.
- The host must have internet access for operating-system packages and Python dependencies.
- The host must use `apt-get`, `dnf`, `yum`, or `zypper`.

## Supported Package Managers

- Debian/Ubuntu: `apt-get`
- Fedora/RHEL/CentOS compatible systems: `dnf` or `yum`
- openSUSE/SUSE: `zypper`

## Installation

Run the installer from the repository root:

```bash
sudo ./install/install.sh
```

The installer:

- Installs required host packages for network management workflows.
- Creates a RouterShell runtime virtual environment under `/opt/routershell`.
- Installs RouterShell into that virtual environment.
- Adds `routershell` and `routershell-factory-reset` launchers under `/usr/local/bin`.
- Creates `/tmp/log` for RouterShell runtime logs.
- Warns if port 53 is already in use, but does not stop or remove existing services.

### Install Options

Use a custom install root:

```bash
sudo ./install/install.sh --install-root /opt/routershell
```

Use a custom launcher directory:

```bash
sudo ./install/install.sh --bin-dir /usr/local/bin
```

Skip operating-system package installation:

```bash
sudo ./install/install.sh --skip-os-packages
```

Skip RouterShell Python package installation:

```bash
sudo ./install/install.sh --skip-python-package
```

After installation, run:

```bash
routershell
```

## Uninstall

Run the uninstaller from the repository root:

```bash
sudo ./install/uninstall.sh
```

The uninstaller removes RouterShell's runtime virtual environment and command launchers.
It does not remove shared operating-system packages such as Python, `iproute`, `dnsmasq`, `hostapd`, or `lshw`.

Remove RouterShell runtime logs as well:

```bash
sudo ./install/uninstall.sh --remove-runtime-logs
```

Use matching custom paths if they were used during install:

```bash
sudo ./install/uninstall.sh --install-root /opt/routershell --bin-dir /usr/local/bin
```

## Notes

- The generic installer is intended for normal Linux distributions first.
- Embedded and image-built environments should get separate install logic once their requirements are better understood.
- VM-based install testing should be used before running this installer on a development workstation.
- See [RouterShell VM Install Testing](../tools/vm/README.md) for the Multipass test workflow.

# FILE: tools/vm/README.md
# RouterShell VM Install Testing

This directory contains a Multipass-based workflow for testing the generic
RouterShell Linux installer away from the development workstation.

The VM workflow is for general-purpose Linux install testing only. BusyBox,
OpenWrt, Buildroot, Yocto/Poky images, and embedded router targets remain out
of scope until they have a dedicated install design.

## Prerequisites

- Multipass installed on the development workstation.
- Network access from the VM for OS packages and Python dependencies.

## Default VM

- Name: `routershell-install-test`
- Image: Ubuntu `24.04`
- CPUs: `2`
- Memory: `2G`
- Disk: `12G`

Override defaults with environment variables:

```bash
RS_VM_NAME=routershell-ubuntu-2404 RS_VM_IMAGE=24.04 tools/vm/multipass-create.sh
```

## Workflow

Create the VM:

```bash
tools/vm/multipass-create.sh
```

Run the install test:

```bash
tools/vm/multipass-test-install.sh
```

Open a shell inside the VM:

```bash
tools/vm/multipass-shell.sh
```

Delete the VM:

```bash
tools/vm/multipass-destroy.sh --purge
```

## What The Test Does

`multipass-test-install.sh` creates a tar archive of the current worktree,
excluding `.git`, `.venv`, caches, and build outputs. It transfers the archive
into the VM, extracts it under `/tmp/RouterShell`, runs the generic installer,
and verifies:

- `/usr/local/bin/routershell` exists and is executable.
- `/usr/local/bin/routershell-factory-reset` exists and is executable.
- `/opt/routershell/venv/bin/python` exists and is executable.
- The installed Python environment can import `routershell` and
  `routershell_version`.

The test intentionally does not start the interactive RouterShell CLI.

# FILE: tools/vm/multipass-common.sh
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

# FILE: tools/vm/multipass-create.sh
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

rs_vm_log "VM is ready."
multipass info "${RS_VM_NAME}"

# FILE: tools/vm/multipass-test-install.sh
#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

SKIP_OS_PACKAGES="${SKIP_OS_PACKAGES:-false}"

usage() {
  cat <<'EOF'
Copy the current RouterShell worktree into the Multipass VM and test install it.

Usage:
  multipass-test-install.sh [--skip-os-packages]

Environment:
  RS_VM_NAME       VM name. Default: routershell-install-test
  RS_VM_REPO_DIR   Path inside VM. Default: /tmp/RouterShell
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-os-packages)
      SKIP_OS_PACKAGES="true"
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
rs_vm_create_archive

rs_vm_log "Copying archive into VM."
multipass transfer "${RS_VM_ARCHIVE}" "${RS_VM_NAME}:/tmp/routershell-vm-test.tar.gz"

rs_vm_log "Refreshing VM test workspace."
multipass exec "${RS_VM_NAME}" -- bash -lc "rm -rf '${RS_VM_REPO_DIR}' && tar -xzf /tmp/routershell-vm-test.tar.gz -C /tmp"

install_cmd="sudo '${RS_VM_REPO_DIR}/install/install.sh'"
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
  /opt/routershell/venv/bin/python - <<'PY'
import routershell
import routershell_version

assert callable(routershell.main)
assert callable(routershell.factory_reset)
print(f'RouterShell import OK: {routershell_version.__version__}')
PY
"

rs_vm_log "Install test passed."

# FILE: tools/vm/multipass-shell.sh
#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

rs_vm_require_multipass
rs_vm_require_exists

multipass shell "${RS_VM_NAME}"

# FILE: tools/vm/multipass-destroy.sh
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
