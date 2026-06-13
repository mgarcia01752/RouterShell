### Summary
Reworked the RouterShell non-embedded Linux installer to support general-purpose distributions through apt, dnf, yum, and zypper. The installer now rejects embedded/minimal targets, installs RouterShell into an isolated runtime virtual environment, creates command launchers, and leaves existing DNS services and shared OS packages alone.

### Modified Files
- README.md
- install/README.md
- install/install.sh
- install/uninstall.sh

### Commands Executed And Results
- `bash -n install/install.sh install/uninstall.sh start.sh tools/git/git-common.sh tools/git/git-save.sh tools/git/git-push.sh tools/git/git-reset-branch-history.sh` -> pass.
- `python3 tools/release/check_version.py` -> pass; `routershell_version.py` and `pyproject.toml` both report 0.1.0.
- `python3 -m py_compile routershell.py routershell_version.py tools/release/check_version.py tools/support/bump_version.py` -> pass.
- `python3 tools/release/test-runner.py` -> pass; 4/4 packaging smoke tests passed.
- `./install/install.sh --help >/tmp/routershell-install-help.txt && ./install/uninstall.sh --help >/tmp/routershell-uninstall-help.txt && wc -l /tmp/routershell-install-help.txt /tmp/routershell-uninstall-help.txt` -> pass; help output generated for both scripts.
- `rg -n "[[:blank:]]$" README.md install/README.md install/install.sh install/uninstall.sh || true` -> pass; no trailing whitespace found.
- `bash -c 'source tools/git/git-common.sh; rs_run_quality_gates'` -> pass for available checks; pytest and Ruff skipped because they are not installed.

### Tests
- `tools/release/test-runner.py` -> pass; 4/4 packaging smoke tests passed.
- `bash -n` -> pass for updated install scripts and git-adjacent shell scripts.
- RouterShell quality gates -> pass for available checks.
- `pytest` -> skipped by quality gate because pytest is not installed in this interpreter.
- `ruff` -> skipped by quality gate because Ruff is not installed in this interpreter.

### Notes / Warnings
- The installer was not executed against the development workstation.
- Embedded and image-built targets remain intentionally unsupported by this installer.
- Port 53 ownership is now warned about only; the installer no longer kills the owning process.
- The uninstaller intentionally does not remove shared OS packages.

### Remaining TODOs / Follow-Ups
- Test the installer inside disposable VMs for Ubuntu/Debian, Fedora/RHEL-compatible, and openSUSE/SUSE targets.
- Install development dependencies in a local virtual environment so pytest and Ruff can run instead of being skipped.

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

# FILE: install/install.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT="${ROUTERSHELL_INSTALL_ROOT:-/opt/routershell}"
BIN_DIR="${ROUTERSHELL_BIN_DIR:-/usr/local/bin}"
VENV_DIR="${INSTALL_ROOT}/venv"
SKIP_OS_PACKAGES="false"
SKIP_PYTHON_PACKAGE="false"

usage() {
  cat <<'EOF'
Install RouterShell on a general-purpose Linux host.

Usage:
  install.sh [--install-root PATH] [--bin-dir PATH] [--skip-os-packages] [--skip-python-package]

Options:
  --install-root       Runtime install root. Default: /opt/routershell
  --bin-dir            Directory for command launchers. Default: /usr/local/bin
  --skip-os-packages   Do not install operating-system packages.
  --skip-python-package
                       Do not create the runtime virtual environment or install RouterShell.
  -h, --help           Show this help.

Supported targets:
  Debian/Ubuntu, Fedora/RHEL/CentOS compatible systems, and openSUSE/SUSE.

Unsupported targets:
  BusyBox, Alpine, OpenWrt, Buildroot, Yocto images, and embedded/minimal router images.
EOF
}

log() {
  echo "[${SCRIPT_NAME}] $*"
}

die() {
  echo "[${SCRIPT_NAME}] ERROR: $*" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-root)
      shift
      [[ -n "${1:-}" ]] || die "--install-root requires a path."
      INSTALL_ROOT="$1"
      VENV_DIR="${INSTALL_ROOT}/venv"
      shift
      ;;
    --bin-dir)
      shift
      [[ -n "${1:-}" ]] || die "--bin-dir requires a path."
      BIN_DIR="$1"
      shift
      ;;
    --skip-os-packages)
      SKIP_OS_PACKAGES="true"
      shift
      ;;
    --skip-python-package)
      SKIP_PYTHON_PACKAGE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
done

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    die "Run this installer as root, for example: sudo ./install/install.sh"
  fi
}

load_os_release() {
  if [[ ! -r /etc/os-release ]]; then
    die "Unable to detect Linux distribution because /etc/os-release is missing."
  fi

  # shellcheck disable=SC1091
  source /etc/os-release

  OS_ID="${ID:-unknown}"
  OS_ID_LIKE="${ID_LIKE:-}"
  OS_NAME="${PRETTY_NAME:-${OS_ID}}"
}

reject_embedded_targets() {
  local id_tokens
  id_tokens=" ${OS_ID} ${OS_ID_LIKE} "

  case "${id_tokens}" in
    *" alpine "*|*" openwrt "*|*" buildroot "*|*" yocto "*|*" poky "*)
      die "Unsupported target '${OS_NAME}'. Embedded/minimal distributions are intentionally out of scope."
      ;;
  esac

  if command -v busybox >/dev/null 2>&1 && [[ ! -d /usr/lib/systemd && ! -d /etc/systemd ]]; then
    die "BusyBox-style targets are intentionally out of scope for this installer."
  fi
}

detect_package_manager() {
  if command -v apt-get >/dev/null 2>&1; then
    PACKAGE_MANAGER="apt"
    return
  fi

  if command -v dnf >/dev/null 2>&1; then
    PACKAGE_MANAGER="dnf"
    return
  fi

  if command -v yum >/dev/null 2>&1; then
    PACKAGE_MANAGER="yum"
    return
  fi

  if command -v zypper >/dev/null 2>&1; then
    PACKAGE_MANAGER="zypper"
    return
  fi

  die "No supported package manager found. Expected apt-get, dnf, yum, or zypper."
}

install_os_packages() {
  case "${PACKAGE_MANAGER}" in
    apt)
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y \
        bridge-utils \
        dnsmasq \
        ethtool \
        hostapd \
        iproute2 \
        iw \
        lshw \
        lsof \
        net-tools \
        openssl \
        python3 \
        python3-pip \
        python3-venv \
        traceroute
      ;;
    dnf|yum)
      "${PACKAGE_MANAGER}" install -y \
        bridge-utils \
        dnsmasq \
        ethtool \
        hostapd \
        iproute \
        iw \
        lshw \
        lsof \
        net-tools \
        openssl \
        python3 \
        python3-pip \
        traceroute
      ;;
    zypper)
      zypper --non-interactive refresh
      zypper --non-interactive install -y \
        bridge-utils \
        dnsmasq \
        ethtool \
        hostapd \
        iproute2 \
        iw \
        lshw \
        lsof \
        net-tools \
        openssl \
        python3 \
        python3-pip \
        python3-virtualenv \
        traceroute
      ;;
    *)
      die "Unsupported package manager: ${PACKAGE_MANAGER}"
      ;;
  esac
}

check_python_venv() {
  if ! python3 -m venv --help >/dev/null 2>&1; then
    die "python3 venv support is not available after package installation."
  fi
}

warn_port_53_owner() {
  if command -v lsof >/dev/null 2>&1 && lsof -i :53 >/dev/null 2>&1; then
    log "Port 53 is already in use. RouterShell may need DNS service changes during runtime."
    log "The installer will not stop or remove the existing service."
  fi
}

install_runtime_package() {
  install -d -m 0755 "${INSTALL_ROOT}"
  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip
  "${VENV_DIR}/bin/python" -m pip install "${PROJECT_ROOT}"
}

install_launchers() {
  install -d -m 0755 "${BIN_DIR}"

  cat > "${BIN_DIR}/routershell" <<EOF
#!/usr/bin/env bash
exec "${VENV_DIR}/bin/routershell" "\$@"
EOF

  cat > "${BIN_DIR}/routershell-factory-reset" <<EOF
#!/usr/bin/env bash
exec "${VENV_DIR}/bin/routershell-factory-reset" "\$@"
EOF

  chmod 0755 "${BIN_DIR}/routershell" "${BIN_DIR}/routershell-factory-reset"
}

prepare_runtime_dirs() {
  install -d -m 1777 /tmp/log
}

main() {
  require_root
  load_os_release
  reject_embedded_targets
  detect_package_manager

  log "Detected ${OS_NAME} with package manager: ${PACKAGE_MANAGER}"

  if [[ "${SKIP_OS_PACKAGES}" == "true" ]]; then
    log "Skipping operating-system package installation."
  else
    install_os_packages
  fi

  warn_port_53_owner
  prepare_runtime_dirs

  if [[ "${SKIP_PYTHON_PACKAGE}" == "true" ]]; then
    log "Skipping RouterShell Python package installation."
  else
    check_python_venv
    install_runtime_package
    install_launchers
  fi

  log "RouterShell installation complete."
  log "Run RouterShell with: routershell"
}

main

# FILE: install/uninstall.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
INSTALL_ROOT="${ROUTERSHELL_INSTALL_ROOT:-/opt/routershell}"
BIN_DIR="${ROUTERSHELL_BIN_DIR:-/usr/local/bin}"
REMOVE_RUNTIME_LOGS="false"

usage() {
  cat <<'EOF'
Uninstall RouterShell from a general-purpose Linux host.

Usage:
  uninstall.sh [--install-root PATH] [--bin-dir PATH] [--remove-runtime-logs]

Options:
  --install-root        Runtime install root. Default: /opt/routershell
  --bin-dir             Directory containing command launchers. Default: /usr/local/bin
  --remove-runtime-logs Remove /tmp/log RouterShell runtime logs.
  -h, --help            Show this help.

This script removes RouterShell's runtime virtual environment and launchers.
It does not remove shared operating-system packages such as Python, iproute,
dnsmasq, hostapd, or lshw.
EOF
}

log() {
  echo "[${SCRIPT_NAME}] $*"
}

die() {
  echo "[${SCRIPT_NAME}] ERROR: $*" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-root)
      shift
      [[ -n "${1:-}" ]] || die "--install-root requires a path."
      INSTALL_ROOT="$1"
      shift
      ;;
    --bin-dir)
      shift
      [[ -n "${1:-}" ]] || die "--bin-dir requires a path."
      BIN_DIR="$1"
      shift
      ;;
    --remove-runtime-logs)
      REMOVE_RUNTIME_LOGS="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown argument: $1"
      ;;
  esac
done

require_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    die "Run this uninstaller as root, for example: sudo ./install/uninstall.sh"
  fi
}

guard_install_root() {
  case "${INSTALL_ROOT}" in
    /|/opt|/usr|/usr/local|/home|/root)
      die "Refusing to remove broad install root: ${INSTALL_ROOT}"
      ;;
  esac
}

remove_launchers() {
  rm -f "${BIN_DIR}/routershell" "${BIN_DIR}/routershell-factory-reset"
}

remove_runtime() {
  guard_install_root
  rm -rf "${INSTALL_ROOT}"
}

remove_runtime_logs() {
  if [[ "${REMOVE_RUNTIME_LOGS}" != "true" ]]; then
    return
  fi

  rm -f /tmp/log/routershell.log /tmp/log/routershell-command.log
}

main() {
  require_root
  remove_launchers
  remove_runtime
  remove_runtime_logs
  log "RouterShell uninstall complete."
}

main
