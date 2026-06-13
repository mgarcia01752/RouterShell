### Summary
The Multipass VM workflow now provisions ten simulated 1G virtual network interfaces by default and verifies RouterShell can discover them during install testing. Documentation and pytest coverage were added for the network-device-shaped VM workflow.

### Modified Files
- tools/vm/multipass-common.sh
- tools/vm/multipass-create.sh
- tools/vm/multipass-test-install.sh
- tools/vm/README.md
- README.md
- install/README.md
- tests/tools/test_vm_workflow.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/python -m pytest tests/tools/test_vm_workflow.py -q` → pass, 4 passed
- `/opt/routershell/venv/bin/python -m ruff check tests/tools/test_vm_workflow.py` → pass
- `/opt/routershell/venv/bin/python -m pytest -q` → pass, 32 passed
- `/opt/routershell/venv/bin/python -m ruff check .` → pass
- `command -v multipass || true` → no Multipass binary found; live VM launch was not run in this environment

### Tests
- `pytest` → pass, 32 passed
- `ruff` → pass, all checks passed
- Live Multipass VM run → not run because Multipass is unavailable here

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

rs_vm_configure_virtual_interfaces
rs_vm_verify_virtual_interfaces

rs_vm_log "VM is ready."
multipass info "${RS_VM_NAME}"

# FILE: tools/vm/multipass-test-install.sh
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

# FILE: tools/vm/README.md
# RouterShell VM Install Testing

This directory contains a Multipass-based workflow for testing the generic
RouterShell Linux installer away from the development workstation.

This is a development workflow. It is not part of the production RouterShell
install process.

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
- Virtual network interfaces: `10`
- Virtual network interface names: `rs1g0` through `rs1g9`
- Virtual interface traffic shaping rate: `1gbit`

Override defaults with environment variables:

```bash
RS_VM_NAME=routershell-ubuntu-2404 RS_VM_IMAGE=24.04 tools/vm/multipass-create.sh
```

Override the simulated network-device shape:

```bash
RS_VM_VIRTUAL_INTERFACES=10 RS_VM_VIRTUAL_INTERFACE_PREFIX=rs1g tools/vm/multipass-create.sh
```

## Workflow

Create the VM:

```bash
tools/vm/multipass-create.sh
```

The create step configures ten Linux virtual network interfaces inside the VM
by default. These interfaces simulate a small network appliance for RouterShell
discovery and install testing without reconfiguring the development workstation.

Run the production install test:

```bash
tools/vm/multipass-test-install.sh
```

By default, the VM test runs:

```bash
sudo /tmp/RouterShell/install/install.sh
```

That production install captures a baseline snapshot in the VM under
`/var/lib/routershell/baseline`.

Use `--development` to test editable install mode with development dependencies:

```bash
tools/vm/multipass-test-install.sh --development
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
into the VM, extracts it under `/tmp/RouterShell`, runs the generic installer
in production mode by default, and verifies:

- `/usr/local/bin/routershell` exists and is executable.
- `/usr/local/bin/routershell-factory-reset` exists and is executable.
- `/opt/routershell/venv/bin/python` exists and is executable.
- `/var/lib/routershell/baseline/manifest.json` exists.
- The VM has the configured virtual network interfaces.
- The installed Python environment can import `routershell`, verify console
  entry functions, read the package version, and discover the virtual network
  interfaces.

The test intentionally does not start the interactive RouterShell CLI.

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

- [RouterShell FAQ](doc/faq.md)

## Linux Runtime Install

[README INSTALLATION](install/README.md)

RouterShell includes a generic installer for non-embedded Linux hosts such as
Ubuntu, Debian, Fedora, RHEL-compatible systems, and openSUSE. Embedded and
BusyBox-style targets are intentionally out of scope for this installer.

Production install is the default.
The installer captures a root-only baseline snapshot under
`/var/lib/routershell/baseline` before making install changes. Production
installs create `/etc/routershell/routershell.env` for launcher-loaded
environment settings. Development installs create a repo-local `.env` by
default; use `--global-env` to force the system environment file. The env file
sets `ROUTERSHELL_DB_FILE` so RouterShell stores runtime SQLite state outside
the installed Python package.

On first launch, `routershell` creates the runtime SQLite database when needed
and discovers Linux network interfaces into the interface database. Verify the
seeded interface state from the CLI:

```text
show interface database
```

Test installer changes in a disposable VM before running them on a development
workstation. Use `--development` only when testing editable installs with dev
dependencies; see [RouterShell VM Install Testing](tools/vm/README.md).
The VM workflow creates ten virtual network interfaces by default to simulate
a network-device install target.

```bash
sudo ./install/install.sh
routershell
```

## Run RouterShell From Source

```bash
PYTHONPATH=src python3 -m routershell
```

Run the factory reset workflow from source with:

```bash
PYTHONPATH=src python3 -m routershell --factory-reset
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

Runtime logs default to `/tmp/log/routershell.log`. Override logging for one
run with environment variables such as:

```bash
ROUTERSHELL_LOG_LEVEL=DEBUG routershell
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

Or run the standard software QA sweep with:

```bash
routershell-software-qa-checker
```

See [RouterShell Software QA Checker](doc/tests/software-qa.md) for the full
check sequence and options.

## Git Helpers

Git helper scripts live under `tools/git/`:

```bash
./tools/git/git-save.sh --commit-msg "Update RouterShell"
./tools/git/git-push.sh --commit-msg "Update RouterShell"
```

See [RouterShell Git Helpers](tools/git/README.md) for save, push, and guarded branch
history reset workflows.

## Tools

Operational and development tools are grouped under `tools/` by purpose.
Review [RouterShell Tools Layout](tools/reference/tools-layout.md) before
running scripts that can alter disks, networking, packages, or services.

## Release Helpers

Release helper scripts live under `tools/release/`:

```bash
./tools/release/check_version.py
./tools/release/release.py --next patch --dry-run
```

See [RouterShell Release Helpers](tools/release/README.md) for version checks,
dry runs, releases, and commit reports.

## License

RouterShell is licensed under the [Apache License 2.0](LICENSE). Distributions
must retain the [NOTICE](NOTICE) file.

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

This is the production runtime install path. Development tools and VM testing
helpers are not installed by default.

The installer:

- Captures a host/network baseline snapshot under `/var/lib/routershell/baseline`.
- Creates a RouterShell environment file for launcher-loaded settings.
- Installs required host packages for network management workflows.
- Creates a RouterShell runtime virtual environment under `/opt/routershell`.
- Installs RouterShell into that virtual environment.
- Adds `routershell` and `routershell-factory-reset` launchers under `/usr/local/bin`.
- Creates `/tmp/log` for RouterShell runtime logs.
- Warns if port 53 is already in use, but does not stop or remove existing services.

### Install Options

Capture a baseline snapshot and exit without installing RouterShell:

```bash
sudo ./install/install.sh --snapshot-only
```

Replace an existing baseline snapshot:

```bash
sudo ./install/install.sh --force-snapshot
```

Skip baseline capture:

```bash
sudo ./install/install.sh --no-snapshot
```

Install in development mode:

```bash
sudo ./install/install.sh --development
```

Development mode installs RouterShell editable with the Python `.[dev]`
dependencies from `pyproject.toml`. Use this for VM-based installer testing or
developer validation, not production hosts. Development mode creates a
repo-local `.env` file and the RouterShell launchers load it before starting
the CLI.

Force a repo-local `.env` file:

```bash
sudo ./install/install.sh --local-env
```

Force the system environment file:

```bash
sudo ./install/install.sh --global-env
```

The system environment file is `/etc/routershell/routershell.env` by default.
The `--global` flag is accepted as an alias for `--global-env`.

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

## Runtime Logging

RouterShell writes runtime logs to `/tmp/log/routershell.log` by default.
Logging is configured when the `routershell` and `routershell-factory-reset`
entry points start.

The installer creates an environment file that those launchers load before
starting RouterShell:

- Production installs create `/etc/routershell/routershell.env` by default.
- Development installs create `.env` in the RouterShell project root by default.
- `--local-env` and `--global-env` can override the default selection.

Existing environment variable values are preserved. If an env file already
exists, the installer appends missing required RouterShell keys without
overwriting existing values. The env file also defines `ROUTERSHELL_DB_FILE`,
which controls the SQLite runtime database path. Production installs default to
`/var/lib/routershell/routershell.db`; local/development installs default to
`.routershell/routershell.db` under the project root.

When `routershell` starts with an empty interface database, startup discovery
reads the Linux interface list and seeds RouterShell interface records. Confirm
the discovered entries from the CLI:

```text
show interface database
```

The log file uses rotation to avoid unbounded growth.

Override the log level for one run:

```bash
ROUTERSHELL_LOG_LEVEL=DEBUG routershell
```

Use a custom log file:

```bash
ROUTERSHELL_LOG_FILE=/tmp/log/routershell-debug.log routershell
```

Disable console logging:

```bash
ROUTERSHELL_LOG_CONSOLE=false routershell
```

Disable file logging:

```bash
ROUTERSHELL_LOG_FILE_ENABLED=false routershell
```

## Uninstall

Run the uninstaller from the repository root:

```bash
sudo ./install/uninstall.sh
```

The uninstaller removes RouterShell's runtime virtual environment and command launchers.
It does not remove shared operating-system packages such as Python, `iproute`, `dnsmasq`, `hostapd`, or `lshw`.
It also does not restore network state from the baseline snapshot.

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
- Production install is the default; development install requires `--development`.
- Production installs use the system environment file by default.
- Development installs use the repo-local `.env` file by default.
- Baseline snapshot capture is enabled by default and is not overwritten unless `--force-snapshot` is used.
- Baseline snapshots are saved root-only under `/var/lib/routershell/baseline`.
- Restore is intentionally not part of uninstall; it should be a separate explicit workflow.
- Embedded and image-built environments should get separate install logic once their requirements are better understood.
- VM-based install testing should be used before running this installer on a development workstation.
- See [RouterShell VM Install Testing](../tools/vm/README.md) for the Multipass test workflow.
- The VM test workflow creates ten virtual network interfaces by default so
  RouterShell discovery can be checked against a network-device-shaped target.

## Baseline Snapshot

The install-time baseline records current host and network state before
RouterShell makes install changes. This is intended for audit and future
restore tooling.

The snapshot includes:

- `/etc/os-release`, `/etc/hostname`, `/etc/hosts`, and `/etc/resolv.conf`.
- Hostname and kernel output.
- `ip address`, route, rule, and neighbor state when `ip` is available.
- Bridge link and VLAN state when `bridge` is available.
- `iptables-save`, `ip6tables-save`, and `nft list ruleset` when available.
- Network-related sysctl values when `sysctl` is available.
- Selected systemd service active/enabled states.
- Network configuration file metadata for common config directories.
- A `manifest.json` and `capture-status.log`.

Network configuration file contents are not copied to avoid capturing secrets
such as WiFi credentials. The snapshot is not restored automatically during
uninstall.

# FILE: tests/tools/test_vm_workflow.py
"""VM workflow script tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VM_TOOLS = REPO_ROOT / "tools" / "vm"


def test_vm_scripts_are_valid_bash() -> None:
    for script in VM_TOOLS.glob("*.sh"):
        subprocess.run(
            ["bash", "-n", str(script)],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )


def test_vm_common_defaults_to_ten_virtual_1g_interfaces() -> None:
    common_script = (VM_TOOLS / "multipass-common.sh").read_text()

    assert 'RS_VM_VIRTUAL_INTERFACES="${RS_VM_VIRTUAL_INTERFACES:-10}"' in common_script
    assert 'RS_VM_VIRTUAL_INTERFACE_PREFIX="${RS_VM_VIRTUAL_INTERFACE_PREFIX:-rs1g}"' in common_script
    assert 'RS_VM_VIRTUAL_INTERFACE_RATE="${RS_VM_VIRTUAL_INTERFACE_RATE:-1gbit}"' in common_script
    assert "ip link add name" in common_script
    assert "type dummy" in common_script
    assert "tc qdisc replace" in common_script


def test_vm_create_configures_and_verifies_virtual_interfaces() -> None:
    create_script = (VM_TOOLS / "multipass-create.sh").read_text()

    assert "rs_vm_configure_virtual_interfaces" in create_script
    assert "rs_vm_verify_virtual_interfaces" in create_script


def test_vm_install_test_verifies_routershell_interface_discovery() -> None:
    test_install_script = (VM_TOOLS / "multipass-test-install.sh").read_text()

    assert "rs_vm_configure_virtual_interfaces" in test_install_script
    assert "rs_vm_verify_virtual_interfaces" in test_install_script
    assert "Interface().get_os_network_interfaces()" in test_install_script
    assert "Missing RouterShell VM interfaces" in test_install_script
