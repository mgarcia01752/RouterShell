### Summary
Updated the installer so repo-local environment installs use the project `.venv` and install RouterShell editable with development dependencies. Documentation and installer tests now cover the local `.venv` pytest workflow and preserve production/global installs as runtime-only.

### Modified Files
- README.md
- install/README.md
- install/install.sh
- tests/install/test_install_env.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/python -m pytest tests/install/test_install_env.py -q` -> pass, 12 passed.
- `/opt/routershell/venv/bin/python -m ruff check tests/install/test_install_env.py` -> pass, all checks passed.
- `bash -n install/install.sh install/uninstall.sh` -> pass.
- `/opt/routershell/venv/bin/python -m pytest -q` -> pass, 46 passed.
- `/opt/routershell/venv/bin/python -m ruff check .` -> pass, all checks passed.
- `bash -n tools/vm/*.sh install/install.sh install/uninstall.sh` -> pass.

### Tests
- `pytest` -> pass, 46 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM scripts, install script, and uninstall script.

### Notes / Warnings
- `pyproject.toml` remains modified from the earlier failed release bump and is intentionally not included in this review bundle.
- Local env installs now create/use `${PROJECT_ROOT}/.venv`; if run with sudo, the local venv is chowned back to the invoking sudo user when possible.

### Remaining TODOs / Follow-Ups
- Re-run `sudo ./install/install.sh --local-env` or `sudo ./install/install.sh --development` to refresh the project `.venv` with pytest and dev tools.

# FILE: README.md
# RouterShell (WORK IN PROGRESS)

[![CI](https://github.com/mgarcia01752/RouterShell/actions/workflows/ci.yml/badge.svg)](https://github.com/mgarcia01752/RouterShell/actions/workflows/ci.yml)
![Python 3.10-3.13](https://img.shields.io/badge/python-3.10--3.13-blue)
![Ubuntu 22.04 and 24.04](https://img.shields.io/badge/ubuntu-22.04%20%7C%2024.04-orange)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

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

RouterShell includes a generic installer for non-embedded Linux hosts.
Ubuntu 22.04 LTS and Ubuntu 24.04 LTS are the primary supported Linux targets
for the current development workflow, with Python 3.10 through Python 3.13
covered by CI. Debian, Fedora, RHEL-compatible systems, and openSUSE remain
intended generic Linux targets, but the committed CI matrix is currently
Ubuntu-focused. Embedded and BusyBox-style targets are intentionally out of
scope for this installer.

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
On apt/snapd systems, `--development` also installs Multipass for the VM
workflow.

```bash
sudo ./install/install.sh
routershell
```

Apply a command file and exit:

```bash
routershell --config-file ./config/startup-config.cfg
```

The file uses the same RouterShell commands that can be pasted into the
interactive CLI. Test configuration files in the disposable VM workflow before
applying them to a real host.

## Run RouterShell From Source

```bash
PYTHONPATH=src python3 -m routershell
```

Apply a command file from source:

```bash
PYTHONPATH=src python3 -m routershell --config-file ./config/startup-config.cfg
```

Run the factory reset workflow from source with:

```bash
PYTHONPATH=src python3 -m routershell --factory-reset
```

## Python Development Install

RouterShell now includes Python packaging metadata in `pyproject.toml`.
For installer-managed local development, use the local environment install:

```bash
sudo ./install/install.sh --local-env
.venv/bin/python -m pytest
```

For manual local development, use an isolated virtual environment and install
the project in editable mode:

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
On apt/snapd systems, development mode also installs Multipass so the
`tools/vm/` installer test workflow can create disposable RouterShell test VMs.
Production installs do not install Multipass.

Force a repo-local `.env` file:

```bash
sudo ./install/install.sh --local-env
```

Local environment installs use the project `.venv` and install RouterShell
editable with development dependencies. After a local environment install,
project-local tools such as pytest are available from the repository:

```bash
cd ~/Projects/RouterShell
.venv/bin/python -m pytest
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

Apply a RouterShell command file and exit:

```bash
routershell --config-file ./config/startup-config.cfg
```

The command file uses the same RouterShell commands that can be pasted into the
interactive CLI. Validate configuration files in a disposable VM before using
them on a real host.

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
- Development installs use the repo-local `.env` file and project `.venv` by default.
- Local environment installs use the project `.venv` with development dependencies.
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

# FILE: install/install.sh
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT="${ROUTERSHELL_INSTALL_ROOT:-/opt/routershell}"
BIN_DIR="${ROUTERSHELL_BIN_DIR:-/usr/local/bin}"
STATE_DIR="${ROUTERSHELL_STATE_DIR:-/var/lib/routershell}"
SYSTEM_ENV_DIR="${ROUTERSHELL_SYSTEM_ENV_DIR:-/etc/routershell}"
SYSTEM_ENV_FILE="${ROUTERSHELL_SYSTEM_ENV_FILE:-${SYSTEM_ENV_DIR}/routershell.env}"
LOCAL_ENV_FILE="${PROJECT_ROOT}/.env"
LOCAL_VENV_DIR="${PROJECT_ROOT}/.venv"
BASELINE_DIR="${STATE_DIR}/baseline"
VENV_DIR="${INSTALL_ROOT}/venv"
SKIP_OS_PACKAGES="false"
SKIP_PYTHON_PACKAGE="false"
DEVELOPMENT_INSTALL="false"
INSTALL_VM_TOOLS="${ROUTERSHELL_INSTALL_VM_TOOLS:-true}"
SKIP_SNAPSHOT="false"
FORCE_SNAPSHOT="false"
SNAPSHOT_ONLY="false"
ENV_SCOPE="auto"
ACTIVE_ENV_FILE=""

usage() {
  cat <<'EOF'
Install RouterShell on a general-purpose Linux host.

Usage:
  install.sh [--install-root PATH] [--bin-dir PATH] [--development] [--local-env] [--global-env] [--snapshot-only] [--force-snapshot] [--no-snapshot] [--skip-os-packages] [--skip-python-package]

Options:
  --install-root       Runtime install root. Default: /opt/routershell
  --bin-dir            Directory for command launchers. Default: /usr/local/bin
  --development        Install RouterShell editable with development dependencies and VM test tooling.
  --local-env          Create/load a repo-local .env file.
  --global-env         Create/load the system env file. Default for production.
  --global             Alias for --global-env.
  --snapshot-only      Capture the host baseline snapshot and exit.
  --force-snapshot     Replace an existing baseline snapshot.
  --no-snapshot        Skip baseline snapshot capture.
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
    --development)
      DEVELOPMENT_INSTALL="true"
      shift
      ;;
    --local-env)
      ENV_SCOPE="local"
      shift
      ;;
    --global-env|--global)
      ENV_SCOPE="global"
      shift
      ;;
    --snapshot-only)
      SNAPSHOT_ONLY="true"
      shift
      ;;
    --force-snapshot)
      FORCE_SNAPSHOT="true"
      shift
      ;;
    --no-snapshot)
      SKIP_SNAPSHOT="true"
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

validate_snapshot_options() {
  if [[ "${SNAPSHOT_ONLY}" == "true" && "${SKIP_SNAPSHOT}" == "true" ]]; then
    die "--snapshot-only cannot be used with --no-snapshot."
  fi
}

select_env_file() {
  local resolved_scope="${ENV_SCOPE}"

  if [[ "${resolved_scope}" == "auto" ]]; then
    if [[ "${DEVELOPMENT_INSTALL}" == "true" ]]; then
      resolved_scope="local"
    else
      resolved_scope="global"
    fi
  fi

  case "${resolved_scope}" in
    local)
      ACTIVE_ENV_FILE="${LOCAL_ENV_FILE}"
      ;;
    global)
      ACTIVE_ENV_FILE="${SYSTEM_ENV_FILE}"
      ;;
    *)
      die "Unsupported environment file scope: ${ENV_SCOPE}"
      ;;
  esac
}

select_python_venv() {
  if [[ "${ACTIVE_ENV_FILE}" == "${LOCAL_ENV_FILE}" ]]; then
    VENV_DIR="${LOCAL_VENV_DIR}"
  else
    VENV_DIR="${INSTALL_ROOT}/venv"
  fi
}

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

write_file_if_present() {
  local source_path="$1"
  local target_name="$2"

  if [[ -e "${source_path}" ]]; then
    cp -a "${source_path}" "${BASELINE_DIR}/${target_name}"
    echo "copy:${source_path}:ok" >> "${BASELINE_DIR}/capture-status.log"
  else
    echo "copy:${source_path}:missing" >> "${BASELINE_DIR}/capture-status.log"
  fi
}

capture_command() {
  local label="$1"
  local output_file="$2"
  shift 2

  if "$@" > "${BASELINE_DIR}/${output_file}" 2> "${BASELINE_DIR}/${output_file}.stderr"; then
    echo "command:${label}:ok" >> "${BASELINE_DIR}/capture-status.log"
  else
    echo "command:${label}:failed" >> "${BASELINE_DIR}/capture-status.log"
  fi
}

capture_command_if_available() {
  local required_command="$1"
  local label="$2"
  local output_file="$3"
  shift 3

  if command -v "${required_command}" >/dev/null 2>&1; then
    capture_command "${label}" "${output_file}" "$@"
  else
    echo "command:${label}:missing:${required_command}" >> "${BASELINE_DIR}/capture-status.log"
  fi
}

capture_network_config_metadata() {
  local output_file="${BASELINE_DIR}/network-config-files.txt"

  : > "${output_file}"
  for config_path in \
    /etc/netplan \
    /etc/network \
    /etc/NetworkManager/system-connections \
    /etc/systemd/network \
    /etc/sysconfig/network \
    /etc/sysconfig/network-scripts
  do
    if [[ -e "${config_path}" ]]; then
      {
        echo "# ${config_path}"
        find "${config_path}" -maxdepth 2 -printf "%M %u %g %s %TY-%Tm-%Td %TH:%TM %p\n" 2>/dev/null || true
        echo
      } >> "${output_file}"
    fi
  done
}

capture_service_state() {
  local output_file="${BASELINE_DIR}/systemd-services.tsv"
  local service

  {
    echo -e "service\tis-active\tis-enabled"
    for service in dnsmasq hostapd ssh sshd NetworkManager systemd-networkd systemd-resolved; do
      if command -v systemctl >/dev/null 2>&1; then
        echo -e "${service}\t$(systemctl is-active "${service}" 2>/dev/null || true)\t$(systemctl is-enabled "${service}" 2>/dev/null || true)"
      else
        echo -e "${service}\tsystemctl-missing\tsystemctl-missing"
      fi
    done
  } > "${output_file}"
}

write_snapshot_manifest() {
  local install_mode="production"
  local snapshot_timestamp

  if [[ "${DEVELOPMENT_INSTALL}" == "true" ]]; then
    install_mode="development"
  fi

  snapshot_timestamp="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

  cat > "${BASELINE_DIR}/manifest.json" <<EOF
{
  "schema_version": 1,
  "created_at_utc": "${snapshot_timestamp}",
  "hostname": "$(hostname 2>/dev/null || true)",
  "kernel": "$(uname -r 2>/dev/null || true)",
  "os_id": "${OS_ID}",
  "os_name": "${OS_NAME}",
  "package_manager": "${PACKAGE_MANAGER}",
  "install_mode": "${install_mode}",
  "baseline_dir": "${BASELINE_DIR}",
  "restore_supported": false,
  "notes": [
    "Snapshot is captured before RouterShell installation changes.",
    "Uninstall does not restore this baseline.",
    "Network configuration file contents are not copied to avoid capturing secrets."
  ]
}
EOF
}

capture_baseline_snapshot() {
  if [[ "${SKIP_SNAPSHOT}" == "true" ]]; then
    log "Skipping baseline snapshot by request."
    return
  fi

  if [[ -e "${BASELINE_DIR}/manifest.json" && "${FORCE_SNAPSHOT}" != "true" ]]; then
    log "Baseline snapshot already exists at ${BASELINE_DIR}; leaving it unchanged."
    return
  fi

  if [[ -e "${BASELINE_DIR}" && "${FORCE_SNAPSHOT}" == "true" ]]; then
    rm -rf "${BASELINE_DIR}"
  fi

  install -d -m 0700 "${BASELINE_DIR}"
  : > "${BASELINE_DIR}/capture-status.log"

  log "Capturing baseline snapshot at ${BASELINE_DIR}."

  write_file_if_present /etc/os-release os-release
  write_file_if_present /etc/hostname etc-hostname
  write_file_if_present /etc/hosts hosts
  write_file_if_present /etc/resolv.conf resolv.conf

  capture_command "hostname" "hostname.txt" hostname
  capture_command "uname" "uname.txt" uname -a
  capture_command_if_available ip "ip-address-json" "ip-address.json" ip -json address show
  capture_command_if_available ip "ip-address" "ip-address.txt" ip address show
  capture_command_if_available ip "ip-route-json" "ip-route.json" ip -json route show table all
  capture_command_if_available ip "ip-route" "ip-route.txt" ip route show table all
  capture_command_if_available ip "ip-rule" "ip-rule.txt" ip rule show
  capture_command_if_available ip "ip-neigh" "ip-neigh.txt" ip neigh show
  capture_command_if_available bridge "bridge-link" "bridge-link.txt" bridge link show
  capture_command_if_available bridge "bridge-vlan" "bridge-vlan.txt" bridge vlan show
  capture_command_if_available iptables-save "iptables-save" "iptables-save.v4" iptables-save
  capture_command_if_available ip6tables-save "ip6tables-save" "ip6tables-save.v6" ip6tables-save
  capture_command_if_available nft "nft-ruleset" "nft-list-ruleset.txt" nft list ruleset
  capture_command_if_available sysctl "sysctl-net" "sysctl-net.conf" bash -c "sysctl -a 2>/dev/null | awk '/^net\\./ { print }'"

  capture_service_state
  capture_network_config_metadata
  write_snapshot_manifest

  chmod -R go-rwx "${BASELINE_DIR}"
}

write_env_defaults() {
  local env_file="$1"
  local db_file

  db_file="$(env_db_file "${env_file}")"

  cat > "${env_file}" <<EOF
# RouterShell environment file.
# This file is loaded by RouterShell command launchers.

ROUTERSHELL_PROJECT_ROOT="${PROJECT_ROOT}"
ROUTERSHELL_DB_FILE="${db_file}"
ROUTERSHELL_LOG_LEVEL="INFO"
ROUTERSHELL_LOG_FILE="/tmp/log/routershell.log"
ROUTERSHELL_LOG_CONSOLE="true"
ROUTERSHELL_LOG_FILE_ENABLED="true"
EOF
}

env_db_file() {
  local env_file="$1"

  if [[ "${env_file}" == "${LOCAL_ENV_FILE}" ]]; then
    printf '%s\n' "${PROJECT_ROOT}/.routershell/routershell.db"
  else
    printf '%s\n' "${STATE_DIR}/routershell.db"
  fi
}

append_env_default_if_missing() {
  local env_file="$1"
  local key="$2"
  local value="$3"

  if grep -q "^${key}=" "${env_file}"; then
    return
  fi

  printf '%s="%s"\n' "${key}" "${value}" >> "${env_file}"
  log "Added missing ${key} to ${env_file}."
}

ensure_env_defaults() {
  local env_file="$1"

  append_env_default_if_missing "${env_file}" "ROUTERSHELL_PROJECT_ROOT" "${PROJECT_ROOT}"
  append_env_default_if_missing "${env_file}" "ROUTERSHELL_DB_FILE" "$(env_db_file "${env_file}")"
  append_env_default_if_missing "${env_file}" "ROUTERSHELL_LOG_LEVEL" "INFO"
  append_env_default_if_missing "${env_file}" "ROUTERSHELL_LOG_FILE" "/tmp/log/routershell.log"
  append_env_default_if_missing "${env_file}" "ROUTERSHELL_LOG_CONSOLE" "true"
  append_env_default_if_missing "${env_file}" "ROUTERSHELL_LOG_FILE_ENABLED" "true"
}

create_env_file() {
  local env_dir

  [[ -n "${ACTIVE_ENV_FILE}" ]] || die "Environment file path was not selected."

  if [[ -e "${ACTIVE_ENV_FILE}" ]]; then
    ensure_env_defaults "${ACTIVE_ENV_FILE}"
    log "Environment file already exists at ${ACTIVE_ENV_FILE}; preserved existing values."
    return
  fi

  env_dir="$(dirname "${ACTIVE_ENV_FILE}")"
  install -d -m 0755 "${env_dir}"
  write_env_defaults "${ACTIVE_ENV_FILE}"

  if [[ "${ACTIVE_ENV_FILE}" == "${LOCAL_ENV_FILE}" && -n "${SUDO_UID:-}" && -n "${SUDO_GID:-}" ]]; then
    chown "${SUDO_UID}:${SUDO_GID}" "${ACTIVE_ENV_FILE}"
    chmod 0600 "${ACTIVE_ENV_FILE}"
  elif [[ "${ACTIVE_ENV_FILE}" == "${LOCAL_ENV_FILE}" ]]; then
    chmod 0600 "${ACTIVE_ENV_FILE}"
  else
    chmod 0644 "${ACTIVE_ENV_FILE}"
  fi

  log "Created environment file at ${ACTIVE_ENV_FILE}."
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
        snapd \
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

install_development_vm_tools() {
  if [[ "${DEVELOPMENT_INSTALL}" != "true" ]]; then
    return
  fi

  if [[ "${INSTALL_VM_TOOLS}" == "false" ]]; then
    log "Skipping development VM tooling by ROUTERSHELL_INSTALL_VM_TOOLS=false."
    return
  fi

  if command -v multipass >/dev/null 2>&1; then
    log "Multipass is already installed."
    return
  fi

  if [[ "${PACKAGE_MANAGER}" != "apt" ]]; then
    die "Development VM tooling requires Multipass. Automatic Multipass install is currently supported on apt/snapd systems only."
  fi

  if ! command -v snap >/dev/null 2>&1; then
    die "snap is required to install Multipass. Re-run without --skip-os-packages so snapd can be installed."
  fi

  log "Installing Multipass for RouterShell development VM testing."
  snap install multipass
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
  local install_dev_dependencies="false"
  local venv_parent

  if [[ "${DEVELOPMENT_INSTALL}" == "true" || "${ACTIVE_ENV_FILE}" == "${LOCAL_ENV_FILE}" ]]; then
    install_dev_dependencies="true"
  fi

  if [[ "${VENV_DIR}" == "${LOCAL_VENV_DIR}" ]]; then
    venv_parent="$(dirname "${VENV_DIR}")"
    install -d -m 0755 "${venv_parent}"
  else
    install -d -m 0755 "${INSTALL_ROOT}"
  fi

  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip

  if [[ "${install_dev_dependencies}" == "true" ]]; then
    "${VENV_DIR}/bin/python" -m pip install -e "${PROJECT_ROOT}[dev]"
  else
    "${VENV_DIR}/bin/python" -m pip install "${PROJECT_ROOT}"
  fi

  if [[ "${VENV_DIR}" == "${LOCAL_VENV_DIR}" && -n "${SUDO_UID:-}" && -n "${SUDO_GID:-}" ]]; then
    chown -R "${SUDO_UID}:${SUDO_GID}" "${VENV_DIR}"
  fi
}

install_launchers() {
  install -d -m 0755 "${BIN_DIR}"

  cat > "${BIN_DIR}/routershell" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -r "${ACTIVE_ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ACTIVE_ENV_FILE}"
  set +a
fi
exec "${VENV_DIR}/bin/routershell" "\$@"
EOF

  cat > "${BIN_DIR}/routershell-factory-reset" <<EOF
#!/usr/bin/env bash
set -euo pipefail
if [[ -r "${ACTIVE_ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ACTIVE_ENV_FILE}"
  set +a
fi
exec "${VENV_DIR}/bin/routershell-factory-reset" "\$@"
EOF

  chmod 0755 "${BIN_DIR}/routershell" "${BIN_DIR}/routershell-factory-reset"
}

prepare_runtime_dirs() {
  install -d -m 1777 /tmp/log
}

main() {
  require_root
  validate_snapshot_options
  load_os_release
  reject_embedded_targets
  detect_package_manager
  select_env_file
  select_python_venv

  log "Detected ${OS_NAME} with package manager: ${PACKAGE_MANAGER}"
  capture_baseline_snapshot

  if [[ "${SNAPSHOT_ONLY}" == "true" ]]; then
    log "Snapshot-only mode complete."
    exit 0
  fi

  if [[ "${SKIP_OS_PACKAGES}" == "true" ]]; then
    log "Skipping operating-system package installation."
  else
    install_os_packages
  fi

  install_development_vm_tools

  warn_port_53_owner
  prepare_runtime_dirs
  create_env_file

  if [[ "${SKIP_PYTHON_PACKAGE}" == "true" ]]; then
    log "Skipping RouterShell Python package installation."
  else
    check_python_venv
    if [[ "${DEVELOPMENT_INSTALL}" == "true" || "${ACTIVE_ENV_FILE}" == "${LOCAL_ENV_FILE}" ]]; then
      log "Installing RouterShell editable with development dependencies."
    else
      log "Installing RouterShell in production runtime mode."
    fi
    install_runtime_package
    install_launchers
  fi

  log "RouterShell installation complete."
  log "Run RouterShell with: routershell"
}

if [[ "${ROUTERSHELL_INSTALL_SH_NO_MAIN:-false}" != "true" ]]; then
  main
fi

# FILE: tests/install/test_install_env.py
"""Installer environment file behavior tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_bash(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", script],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )


def test_install_help_documents_env_options() -> None:
    result = subprocess.run(
        ["bash", "install/install.sh", "--help"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "--local-env" in result.stdout
    assert "--global-env" in result.stdout
    assert "--global" in result.stdout


def test_development_install_selects_local_env(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    system_env = tmp_path / "etc" / "routershell.env"
    project_root.mkdir()

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
source install/install.sh
PROJECT_ROOT={project_root}
LOCAL_ENV_FILE="${{PROJECT_ROOT}}/.env"
LOCAL_VENV_DIR="${{PROJECT_ROOT}}/.venv"
SYSTEM_ENV_FILE={system_env}
DEVELOPMENT_INSTALL=true
ENV_SCOPE=auto
select_env_file
select_python_venv
create_env_file
printf '%s\\n' "${{ACTIVE_ENV_FILE}}"
printf '%s\\n' "${{VENV_DIR}}"
"""

    result = _run_bash(script)
    local_env = project_root / ".env"
    local_venv = project_root / ".venv"

    assert str(local_env) in result.stdout
    assert str(local_venv) in result.stdout
    assert local_env.exists()
    assert "ROUTERSHELL_LOG_LEVEL" in local_env.read_text()
    assert f'ROUTERSHELL_DB_FILE="{project_root}/.routershell/routershell.db"' in local_env.read_text()
    assert not system_env.exists()


def test_production_install_selects_global_env(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    system_env = tmp_path / "etc" / "routershell.env"
    project_root.mkdir()

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
source install/install.sh
PROJECT_ROOT={project_root}
LOCAL_ENV_FILE="${{PROJECT_ROOT}}/.env"
LOCAL_VENV_DIR="${{PROJECT_ROOT}}/.venv"
SYSTEM_ENV_FILE={system_env}
STATE_DIR={tmp_path}/state
DEVELOPMENT_INSTALL=false
ENV_SCOPE=auto
select_env_file
select_python_venv
create_env_file
printf '%s\\n' "${{ACTIVE_ENV_FILE}}"
printf '%s\\n' "${{VENV_DIR}}"
"""

    result = _run_bash(script)

    assert str(system_env) in result.stdout
    assert "/opt/routershell/venv" in result.stdout
    assert system_env.exists()
    assert "ROUTERSHELL_LOG_FILE" in system_env.read_text()
    assert f'ROUTERSHELL_DB_FILE="{tmp_path}/state/routershell.db"' in system_env.read_text()
    assert not (project_root / ".env").exists()


def test_local_env_selects_project_venv(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    system_env = tmp_path / "etc" / "routershell.env"
    project_root.mkdir()

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
source install/install.sh
PROJECT_ROOT={project_root}
LOCAL_ENV_FILE="${{PROJECT_ROOT}}/.env"
LOCAL_VENV_DIR="${{PROJECT_ROOT}}/.venv"
SYSTEM_ENV_FILE={system_env}
DEVELOPMENT_INSTALL=false
ENV_SCOPE=local
select_env_file
select_python_venv
printf '%s\\n' "${{ACTIVE_ENV_FILE}}"
printf '%s\\n' "${{VENV_DIR}}"
"""

    result = _run_bash(script)

    assert str(project_root / ".env") in result.stdout
    assert str(project_root / ".venv") in result.stdout


def test_runtime_package_installs_dev_extras_for_local_env(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    venv_dir = project_root / ".venv"
    command_log = tmp_path / "commands.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    python3 = bin_dir / "python3"
    python3.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {command_log}\n"
        "if [[ \"$1 $2\" == '-m venv' ]]; then\n"
        "  mkdir -p \"$3/bin\"\n"
        "  cat > \"$3/bin/python\" <<'PYEOF'\n"
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {command_log}\n"
        "PYEOF\n"
        "  chmod +x \"$3/bin/python\"\n"
        "fi\n"
    )
    python3.chmod(0o755)

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
export PATH={bin_dir}:$PATH
source install/install.sh
PROJECT_ROOT={project_root}
LOCAL_ENV_FILE="${{PROJECT_ROOT}}/.env"
LOCAL_VENV_DIR="${{PROJECT_ROOT}}/.venv"
ACTIVE_ENV_FILE="${{LOCAL_ENV_FILE}}"
VENV_DIR="${{LOCAL_VENV_DIR}}"
DEVELOPMENT_INSTALL=false
install_runtime_package
"""

    _run_bash(script)
    log_text = command_log.read_text()

    assert f"-m venv {venv_dir}" in log_text
    assert "-m pip install --upgrade pip" in log_text
    assert f"-m pip install -e {project_root}[dev]" in log_text


def test_runtime_package_installs_runtime_deps_for_global_env(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    install_root = tmp_path / "install-root"
    venv_dir = install_root / "venv"
    command_log = tmp_path / "commands.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    project_root.mkdir()
    python3 = bin_dir / "python3"
    python3.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {command_log}\n"
        "if [[ \"$1 $2\" == '-m venv' ]]; then\n"
        "  mkdir -p \"$3/bin\"\n"
        "  cat > \"$3/bin/python\" <<'PYEOF'\n"
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$*\" >> {command_log}\n"
        "PYEOF\n"
        "  chmod +x \"$3/bin/python\"\n"
        "fi\n"
    )
    python3.chmod(0o755)

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
export PATH={bin_dir}:$PATH
source install/install.sh
PROJECT_ROOT={project_root}
INSTALL_ROOT={install_root}
VENV_DIR="${{INSTALL_ROOT}}/venv"
ACTIVE_ENV_FILE={tmp_path}/routershell.env
DEVELOPMENT_INSTALL=false
install_runtime_package
"""

    _run_bash(script)
    log_text = command_log.read_text()

    assert f"-m venv {venv_dir}" in log_text
    assert "-m pip install --upgrade pip" in log_text
    assert f"-m pip install {project_root}" in log_text
    assert "[dev]" not in log_text


def test_existing_env_gets_missing_required_defaults(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    local_env = project_root / ".env"
    project_root.mkdir()
    local_env.write_text('ROUTERSHELL_LOG_LEVEL="DEBUG"\n')

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
source install/install.sh
PROJECT_ROOT={project_root}
LOCAL_ENV_FILE="${{PROJECT_ROOT}}/.env"
ACTIVE_ENV_FILE="${{LOCAL_ENV_FILE}}"
create_env_file
"""

    _run_bash(script)
    env_text = local_env.read_text()

    assert 'ROUTERSHELL_LOG_LEVEL="DEBUG"' in env_text
    assert f'ROUTERSHELL_DB_FILE="{project_root}/.routershell/routershell.db"' in env_text
    assert 'ROUTERSHELL_LOG_FILE="/tmp/log/routershell.log"' in env_text


def test_launchers_source_selected_env_file(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    env_file = tmp_path / "routershell.env"
    venv_dir = tmp_path / "venv"

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
source install/install.sh
BIN_DIR={bin_dir}
ACTIVE_ENV_FILE={env_file}
VENV_DIR={venv_dir}
install_launchers
"""

    _run_bash(script)
    launcher = bin_dir / "routershell"
    launcher_text = launcher.read_text()

    assert f'source "{env_file}"' in launcher_text
    assert f'exec "{venv_dir}/bin/routershell"' in launcher_text


def test_development_vm_tools_install_multipass_with_snap(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    log_file = tmp_path / "snap.log"
    bin_dir.mkdir()
    snap = bin_dir / "snap"
    snap.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> {log_file}\n")
    snap.chmod(0o755)

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
export PATH={bin_dir}:$PATH
source install/install.sh
DEVELOPMENT_INSTALL=true
PACKAGE_MANAGER=apt
command() {{
  if [[ "$1" == "-v" && "$2" == "multipass" ]]; then
    return 1
  fi
  builtin command "$@"
}}
install_development_vm_tools
"""

    _run_bash(script)

    assert log_file.read_text().strip() == "install multipass"


def test_production_install_skips_development_vm_tools(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    log_file = tmp_path / "snap.log"
    bin_dir.mkdir()
    snap = bin_dir / "snap"
    snap.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> {log_file}\n")
    snap.chmod(0o755)

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
export PATH={bin_dir}:$PATH
source install/install.sh
DEVELOPMENT_INSTALL=false
PACKAGE_MANAGER=apt
install_development_vm_tools
"""

    _run_bash(script)

    assert not log_file.exists()


def test_development_vm_tools_can_be_skipped_with_env(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    log_file = tmp_path / "snap.log"
    bin_dir.mkdir()
    snap = bin_dir / "snap"
    snap.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> {log_file}\n")
    snap.chmod(0o755)

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
export ROUTERSHELL_INSTALL_VM_TOOLS=false
export PATH={bin_dir}:$PATH
source install/install.sh
DEVELOPMENT_INSTALL=true
PACKAGE_MANAGER=apt
install_development_vm_tools
"""

    _run_bash(script)

    assert not log_file.exists()


def test_development_vm_tools_require_apt_snap_for_auto_install() -> None:
    script = """
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
source install/install.sh
DEVELOPMENT_INSTALL=true
PACKAGE_MANAGER=dnf
command() {
  if [[ "$1" == "-v" && "$2" == "multipass" ]]; then
    return 1
  fi
  builtin command "$@"
}
install_development_vm_tools
"""

    result = subprocess.run(
        ["bash", "-c", script],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "Automatic Multipass install is currently supported on apt/snapd systems only" in result.stderr
