### Summary
RouterShell now runs startup discovery from the normal console entry point and uses unprivileged Linux interface discovery so a blank runtime database can seed interface records. User docs now describe first-launch interface seeding and verification, with pytest coverage for startup invocation, unprivileged discovery, and blank DB population.

### Modified Files
- README.md
- install/README.md
- doc/faq.md
- src/routershell/cli.py
- src/routershell/lib/network_manager/network_operations/interface.py
- tests/packaging/test_interface_auto_discovery.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/python -m pytest tests/packaging/test_interface_auto_discovery.py -q` → pass, 3 passed
- `/opt/routershell/venv/bin/python -m ruff check src/routershell/cli.py src/routershell/lib/network_manager/network_operations/interface.py tests/packaging/test_interface_auto_discovery.py` → pass
- `/opt/routershell/venv/bin/python -m pytest -q` → pass, 25 passed
- `/opt/routershell/venv/bin/python -m ruff check .` → pass
- `ROUTERSHELL_DB_FILE=<temp>/routershell.db PYTHONPATH=src /opt/routershell/venv/bin/python ...` → pass, temp DB populated with discovered interfaces; sudo link-up calls failed in the restricted shell but did not block DB seeding

### Tests
- `pytest` → pass, 25 passed
- `ruff` → pass, all checks passed

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

# FILE: doc/faq.md
# RouterShell FAQ

## Install fails with setuptools InvalidConfigError

If `sudo ./install/install.sh --development` fails while getting editable
build requirements and reports this error:

```text
setuptools.errors.InvalidConfigError: License classifiers have been superseded by license expressions
```

Update RouterShell to a version whose `pyproject.toml` uses the SPDX
`license = "Apache-2.0"` expression without deprecated license classifiers,
then rerun the installer:

```bash
sudo ./install/install.sh --development
```

This error is raised by newer setuptools releases during package metadata
validation.

## VSCode reports unresolved RouterShell imports

If VSCode or Pylance reports unresolved imports for `routershell` or
`tools.release.qa_checker`, reload the VSCode window after opening the
RouterShell workspace. The workspace settings select the installed development
interpreter at `/opt/routershell/venv/bin/python` and add the project `src`
layout plus release tooling paths to Python analysis.

If command-line Pyright is also needed, reinstall development extras:

```bash
/opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

If VSCode reports a Pylint `E0401:import-error` for a RouterShell module such
as `routershell.lib.cli.base.clear_mode`, make sure the workspace is using the
RouterShell interpreter and reload VSCode. The workspace settings configure the
Pylint extension to run from `/opt/routershell/venv/bin/python` with the
project `src` layout on the import path.

If the Pylint extension reports that Pylint is missing, refresh development
dependencies in the installer-created virtual environment:

```bash
sudo /opt/routershell/venv/bin/python -m pip install -e ".[dev]"
```

## RouterShell fails with unable to open database file

If `routershell` exits during startup with this error:

```text
RouterShellDB - ERROR - Error: unable to open database file
AttributeError: 'NoneType' object has no attribute 'cursor'
```

the launcher is missing a writable `ROUTERSHELL_DB_FILE` setting or is using an
older install. Reinstall RouterShell so the launcher-loaded env file gets any
missing required keys and the installed package receives the current DB path
code:

```bash
sudo ./install/install.sh --development
```

For local/development installs, the default database path is
`.routershell/routershell.db` under the project root. For production installs,
the default path is `/var/lib/routershell/routershell.db`.

## Interface database is empty after install

`routershell` should seed the interface database during startup when the
database has no interface records. Start the CLI normally:

```bash
routershell
```

Then verify the discovered interfaces:

```text
show interface database
```

If the database is still empty, confirm that the launcher-loaded environment
file defines a writable `ROUTERSHELL_DB_FILE` path and reinstall with the
current installer.

# FILE: src/routershell/cli.py
"""Console entry points for RouterShell."""

from __future__ import annotations

from routershell.logging_config import configure_logging


def main() -> int:
    """Run the RouterShell interactive CLI."""
    configure_logging()

    from routershell.lib.cli.router_main_cli import RouterCLI

    RouterCLI(system_start_up=True).run()
    return 0


def factory_reset() -> int:
    """Run the RouterShell factory reset workflow."""
    configure_logging()

    from routershell.lib.system.system_start_up import SystemFactoryReset

    SystemFactoryReset()
    return 0

# FILE: src/routershell/lib/network_manager/network_operations/interface.py
import ipaddress
import json
import logging
import os

from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import (
    InetAddressText,
    InetCidrText,
    InterfaceName,
    MacAddressText,
    NatPoolName,
    PredicateResult,
    StatusResult,
)
from routershell.lib.db.interface_db import InterfaceDatabase
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.common.phy import Duplex, Speed, State
from routershell.lib.network_manager.network_operations.arp import Arp, Encapsulate
from routershell.lib.network_manager.network_operations.nat import Nat, NATDirection
from routershell.lib.network_manager.network_operations.network_mgr import NetworkManager


class InvalidInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class Interface(NetworkManager, InterfaceDatabase):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().INTERFACE)
        self.arg = arg

    def clear_interface_arp(self, interface_name: InterfaceName | None=None) -> StatusResult:
        """
        Clear the ARP cache for a specific network interface using iproute2.

        This method clears the ARP cache for the specified network interface using the iproute2 tool.

        Args:
            interface_name (str, optional): The name of the network interface to clear the ARP cache for.
                If not provided, the ARP cache for all interfaces will be cleared. Defaults to None.

        Returns:
            StatusResult: STATUS_OK if the ARP cache was successfully cleared, STATUS_NOK otherwise.
        """

        if interface_name:
            # Clear the ARP cache for a specific interface
            self.run(['sudo', 'ip', 'neigh', 'flush', 'dev', interface_name], suppress_error=True)
        else:
            # Clear the ARP cache for all interfaces
            self.run(['sudo', 'ip', 'neigh', 'flush', 'all'], suppress_error=True)
        return STATUS_OK
    
    def get_os_network_interfaces(self, interface_type: InterfaceType | None = None) -> list[str]:
        """
        Retrieve network interface names based on their type. If no type is specified, retrieves all interfaces.

        Args:
            interface_type (InterfaceType | None): The type of network interface to retrieve.
                - InterfaceType.LOOPBACK: Retrieve loopback interfaces.
                - InterfaceType.ETHERNET: Retrieve Ethernet interfaces.
                - InterfaceType.WIRELESS: Retrieve wireless interfaces.

        Returns:
            list[str]: A list of network interface names of the specified type, or all if no type is specified.
        """
        output = self.run(['ip', '-json', 'link', 'show'], suppress_error=True, sudo=False)
        
        if not output.stdout:
            return []
        
        try:
            os_interfaces = json.loads(output.stdout)
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to decode interface list JSON: {e}")
            return []

        interfaces = []
        for os_interface in os_interfaces:
            iface_name = os_interface.get("ifname", "")
            link_type = os_interface.get("link_type", "")

            if interface_type is None:
                if link_type == "loopback":
                    continue
                interfaces.append(iface_name)
            elif interface_type == InterfaceType.LOOPBACK:
                if link_type == "loopback":
                    interfaces.append(iface_name)
            elif interface_type == InterfaceType.ETHERNET:
                if link_type == "ether" and not self._is_wireless_os_interface(iface_name):
                    interfaces.append(iface_name)
            elif interface_type == InterfaceType.WIRELESS_WIFI:
                if self._is_wireless_os_interface(iface_name):
                    interfaces.append(iface_name)

        return interfaces

    def _is_wireless_os_interface(self, interface_name: InterfaceName) -> PredicateResult:
        """
        Determine whether the operating system exposes an interface as wireless.

        Args:
            interface_name (str): The network interface name.

        Returns:
            PredicateResult: True if the interface has Linux wireless metadata,
                False otherwise.
        """
        return PredicateResult(os.path.isdir(f"/sys/class/net/{interface_name}/wireless"))
    
    def does_os_interface_exist(self, interface_name: InterfaceName, include_loopbacks: bool=True) -> PredicateResult:
        """
        Determine if a network interface with the specified name exists on the current system.

        This method utilizes the 'ip -json address show' command to retrieve a list of all network interfaces
        present on the system and subsequently verifies if the provided interface name is included in the
        command's output. It also checks for labeled sub-interfaces of loopback.

        Args:
            interface_name (str): The name of the network interface to be checked.
            include_loopbacks (bool): Whether to include loopback interfaces in the check.

        Returns:
            StatusResult: A boolean value indicating the existence of the specified interface.
            - True: The interface exists.
            - False: otherwise
        """
        try:
            result = self.run(['ip', '-json', 'address', 'show'], suppress_error=True)
            
            if result.exit_code:
                self.log.debug(f"does_os_interface_exist() returned a non-zero exit code: {result.exit_code}")
                return False
            
            interfaces = json.loads(result.stdout)
            
            for interface in interfaces:
                ifname = interface.get("ifname", "")
                
                # Check for the main interface
                if ifname == interface_name:
                    if "loopback" in interface.get("link_type", "") and not include_loopbacks:
                        continue
                    return True
                
                # Check for labeled sub-interfaces under loopback (lo)
                if ifname == "lo" and include_loopbacks:
                    for addr_info in interface.get("addr_info", []):
                        label = addr_info.get("label", "")
                        if label == interface_name:
                            return True

            self.log.debug(f"does_os_interface_exist() '{interface_name}' does not exist")
            return False
                
        except Exception as e:
            self.log.error(f"Exception in does_os_interface_exist: {e}")
            return False

    def get_os_interface_type(self, interface_name: InterfaceName, include_loopback_labels: bool=True) -> InterfaceType:
        """
        Get the type of a network interface (physical, virtual, or VLAN) based on its name.

        Args:
            interface_name (str): The name of the network interface to query.

        Returns:
            InterfaceType: The type of the interface, which can be 'ETHERNET', 'VIRTUAL', 'VLAN', 'BRIDGE', 'LOOPBACK', or 'UNKNOWN'.
        """
        
        if include_loopback_labels:
            if interface_name in Interface().get_os_lo_labels():
                self.log.debug(f'interface" {interface_name} is a type {InterfaceType.LOOPBACK.value}')
                return InterfaceType.LOOPBACK
        
        result = self.run(['ip', '-json', 'link', 'show', interface_name], suppress_error=True, sudo=False)
        self.log.debug(f"get_os_interface_type() -> stdout: {result.stdout}")

        if result.exit_code:
            self.log.debug(f"get_os_interface_type() -> Interface Not Found: {interface_name}")
            return InterfaceType.UNKNOWN

        try:
            interfaces = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to decode JSON: {e}")
            return InterfaceType.UNKNOWN

        if not interfaces:
            self.log.debug(f"get_os_interface_type() -> No interfaces found for: {interface_name}")
            return InterfaceType.UNKNOWN

        interface = interfaces[0]
        self.log.debug(f"Parsed interface JSON: {interface}")

        link_type = interface.get('link_type', '')
        self.log.debug(f"Detected link type: {link_type}")

        if link_type == 'ether':
            return InterfaceType.ETHERNET
        elif link_type in ['tun', 'tap']:
            return InterfaceType.VIRTUAL
        elif link_type == 'vlan':
            return InterfaceType.VLAN
        elif link_type == 'bridge':
            return InterfaceType.BRIDGE
        elif link_type == 'loopback':
            return InterfaceType.LOOPBACK

        return InterfaceType.UNKNOWN

    def get_os_interface_type_extened(self, interface_name: InterfaceName) -> InterfaceType:
        """
        Get the type of a network interface using lshw.

        This method retrieves information about the network interface using lshw and determines its type based on the
        capabilities and configuration.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            InterfaceType: An enumeration representing the type of the network interface.
        """
        interface_info = self.get_os_interface_hardware_info(interface_name)
        
        if not interface_info:
            if_type =  self.get_os_interface_type(interface_name)
            return if_type
        
        elif interface_info.get('capabilities', {}).get('wireless'):
            return InterfaceType.WIRELESS_WIFI
        
        elif interface_info.get('capabilities', {}).get('tp') or interface_info.get('configuration', {}).get('duplex'):
            return InterfaceType.ETHERNET
        
        return self.get_os_interface_type(interface_name)

    def get_db_interface_type(self, interface_name) -> InterfaceType:
        """
        Get the interface type for a specified interface name from the database.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            InterfaceType: The type of the interface.
        """
        interface_details = self.get_interface_details()

        for if_dict in interface_details:
            if if_dict['Interfaces']['InterfaceName'] == interface_name:                
                interface_type_str = if_dict['Interfaces']['Properties']['InterfaceType']
                for interface_enum in InterfaceType:
                    if interface_type_str == interface_enum.value:
                        return interface_enum

        return InterfaceType.UNKNOWN

    def does_db_interface_exist(self, interface_name: InterfaceName) -> PredicateResult:
        """
        Determine if a network interface with the specified name exists on the DB.
        Args:
            interface_name (str): The name of the network interface to be checked.

        Returns:
            StatusResult: A boolean value indicating the existence of the specified interface in the DB.
            - True: The interface exists.
            - False: otherwise
        """        
        return self.db_lookup_interface_exists(interface_name).status

    def add_db_interface_entry(self, interface_name: InterfaceName, ifType: InterfaceType) -> StatusResult:
        """
        Add an interface entry to the database.

        Args:
            interface_name (str): The name of the interface to be added.
            ifType (InterfaceType): The type of the interface.

        Returns:
            StatusResult: STATUS_OK if the interface entry is added successfully, STATUS_NOK if there is an error.

        """
        if self.add_db_interface(interface_name, ifType):
            self.log.debug(f"Unable to add interface: {interface_name} to DB")
            return STATUS_NOK
        
        if ifType != InterfaceType.ETHERNET:
            self.update_db_ifSpeed(interface_name, None)
            self.update_db_duplex(interface_name, None)
        
        return STATUS_OK
        
    def update_interface_mac(self, interface_name: InterfaceName, mac: MacAddressText | None = None) -> StatusResult:
        """
        Update the MAC address of a network interface.
        Update the MAC address to the DB 

        This method either generates a random MAC address or uses the provided MAC address
        (if valid) and assigns it to the specified network interface.

        Args:
        
        interface_name (str): The name of the network interface to which the MAC address will be assigned.
        
        mac (str, optional): Supported MAC address formats:
        - xx:xx:xx:xx:xx:xx
        - xx-xx-xx-xx-xx-xx
        - xxxx.xxxx.xxxx
        - xxxxxxxxxxxx

        Returns:
            StatusResult: STATUS_OK if the MAC address was successfully added, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_interface_mac() -> interface_name: {interface_name} -> mac: {mac}")

        if not mac:
            new_mac = self.generate_random_mac()
            self.log.debug(f"update_interface_mac() mac-auto: {new_mac}")

        elif self.is_valid_mac_address(mac):
            stat, format_mac = self.format_mac_address(mac)
            self.log.debug(f"update_interface_mac() -> mac: {mac} -> format_mac: {format_mac}")

            if not stat:
                self.log.error(f"Unable to format MAC address: {mac}")
                return STATUS_NOK

        else:
            self.log.error(f"Invalid MAC address: {mac}")
            return STATUS_NOK

        if self.set_interface_mac(interface_name, new_mac if not mac else format_mac):
            self.log.error(f"Unable to set MAC address to interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_mac_address(interface_name, new_mac if not mac else format_mac):
            self.log.error(f"Unable to set MAC address to interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_inet(self, interface_name: InterfaceName, inet_address: InetAddressText, secondary: bool = False, negate: bool = False) -> StatusResult:
        """
        Add or remove an inet address from a network interface.
        Update interface inet DB
        
        This method either adds or removes an inet address from the specified network interface.

        Args:
            interface_name (str): The name of the network interface.
            inet_address (str): The IP address in CIDR notation (e.g., "192.168.1.1/24" for IPv4 or "2001:db8::1/64" for IPv6).
            secondary (bool, optional): If True, the method will configure the address as secondary. If False, it will configure it as the primary address (default is False).
            negate (bool): If True, the method will remove the specified IP address from the interface. If False, it will add the address.

        Returns:
            StatusResult: STATUS_OK if the IP address was successfully updated, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_interface_inet() -> interface: {interface_name} -> inet: {inet_address} -> secondary: {secondary} -> negate: {negate}")

        if negate:
            if self.del_inet_address(interface_name, inet_address):
                self.log.error(f"Unable to remove inet Address: {inet_address} from interface: {interface_name} via OS")
                return STATUS_NOK
            
        else:
            if self.set_inet_address(interface_name, inet_address, secondary):
                self.log.error(f"Unable to set inet Address: {inet_address} to interface: {interface_name} via OS")
                return STATUS_NOK
        
        if self.update_db_inet_address(interface_name, inet_address, secondary, negate):
            self.log.error(f"Unable to update inet Address: {inet_address} to interface: {interface_name} via DB")
            return STATUS_NOK
        
        return STATUS_OK

    def update_interface_duplex(self, interface_name: InterfaceName, duplex: Duplex) -> StatusResult:
        """
        Add or set the duplex mode for a network interface.

        This method allows adding or setting the duplex mode to 'auto', 'half', or 'full' for the specified interface.

        Args:
            interface_name (str): The name of the network interface to configure.
            duplex (Duplex): The duplex mode to set. Valid values are Duplex.AUTO, Duplex.HALF, or Duplex.FULL.

        Returns:
            StatusResult: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        
        if duplex == Duplex.NONE:
            
            if self.update_db_duplex(interface_name, duplex.value):
                self.log.error(f"Unable to update interface: {interface_name} to duplex: {duplex.value}")
                return STATUS_NOK
            
            return STATUS_OK            
        
        if self.set_duplex(interface_name, duplex):
            print(f"Invalid duplex mode ({duplex.value}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
        
        if self.update_db_duplex(interface_name, duplex.value):
            self.log.error(f"Unable to update interface: {interface_name} to duplex: {duplex.value}")
            return STATUS_NOK
            
        self.log.debug(f"Updated interface: {interface_name} to duplex: {duplex.value}")
        
        return STATUS_OK
    
    def update_interface_speed(self, interface_name: InterfaceName, speed: Speed) -> StatusResult:
        """
        Set the network interface speed and update it in the database.

        Args:
            interface_name (str): The name of the network interface to configure.
            speed (Speed): The desired speed setting.

        Returns:
            StatusResult: STATUS_OK if the speed configuration was successful, STATUS_NOK otherwise.
        """

        self.log.debug(f"update_interface_speed() -> interface: {interface_name} Speed: {speed}")
        
        if speed == Speed.NONE:
            if self.update_db_ifSpeed(interface_name, speed.value):
                self.log.error(f'Unable to update database speed: {speed.value} on interface: {interface_name}')
                return STATUS_NOK
            return STATUS_OK
        
        if speed == Speed.AUTO_NEGOTIATE:
            self.set_speed(interface_name, Speed.AUTO_NEGOTIATE, Speed.AUTO_NEGOTIATE)
            self.update_db_ifSpeed(interface_name, Speed.AUTO_NEGOTIATE.value)
            
        elif speed in {Speed.MBPS_10, Speed.MBPS_100, Speed.MBPS_1000, Speed.MBPS_10000}:
            self.set_speed(interface_name, speed)
            self.update_db_ifSpeed(interface_name, str(speed.value))
        
        else:
            print(f"Invalid speed value: {speed.value}")
            return STATUS_NOK
        
        return STATUS_OK
            
    def update_shutdown(self, interface_name: InterfaceName, state: State) -> StatusResult:
        """
        Set the shutdown status of a network interface.

        This method allows setting the shutdown status of the specified network interface to 'up' or 'down'.

        Args:
            interface_name (str): The name of the network interface to configure.
            state (State): The status to set. Valid values are State.UP (to bring the interface up)
                        or State.DOWN (to shut the interface down).

        Returns:
            StatusResult: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        shutdown = state != State.UP
        
        if self.update_db_shutdown_status(interface_name, shutdown):
            self.log.error(f"Unable to set interface: {interface_name} to {state.value} via db")
            return STATUS_NOK
        
        self.log.debug(f"update_shutdown() -> interface_name: {interface_name} -> State: {state} via os")
        return self.set_interface_shutdown(interface_name, state)
     
    def create_os_dummy_interface(self, interface_name:InterfaceName) -> StatusResult:
        """
        Create a dummy interface with the specified name to OS.

        Args:
            interface_name (str): The name for the dummy interface.

        Returns:
            StatusResult: STATUS_OK if the dummy interface was created successfully, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'add', 'name', interface_name , 'type', 'dummy'], suppress_error=True)
        
        if result.exit_code:
            self.log.error(f'Error creating dummy -> {interface_name}, Reason: {result.stderr}')
            return STATUS_NOK
        
        self.log.debug(f'Created {interface_name} Dummy')
        
        return STATUS_OK

    def destroy_os_dummy_interface(self, interface_name: InterfaceName) -> StatusResult:
        """
        Destroy a dummy interface with the specified name on the OS.

        Args:
            interface_name (str): The name of the dummy interface to destroy.

        Returns:
            StatusResult: STATUS_OK if the dummy interface was destroyed successfully, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'delete', interface_name, 'type', 'dummy'], suppress_error=True)

        if result.exit_code:
            self.log.error(f'Error destroying dummy -> {interface_name}, Reason: {result.stderr}')
            return STATUS_NOK

        self.log.debug(f'Destroyed {interface_name} dummy')
        return STATUS_OK
        
    def rename_interface(self, initial_interface_name: InterfaceName, 
                        alias_interface_name: InterfaceName, 
                        suppress_error: bool=True) -> StatusResult:
        """
        Rename a network interface to a specified alias name.
        
        This method renames a network interface from `initial_interface_name` to `alias_interface_name`. If the initial 
        interface does not exist, or if the renaming process fails, it logs an error unless `suppress_error` is set to `True`.
        
        Args:
            initial_interface_name (str): The current name of the network interface to be renamed.
            alias_interface_name (str): The new alias name for the network interface.
            suppress_error (bool, optional): If True, suppresses error logging when renaming fails. Defaults to True.
        
        Returns:
            StatusResult: STATUS_OK if the interface was renamed successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"rename_interface() -> if: {initial_interface_name} -> alias-if: {alias_interface_name}")
        
        # Check if the initial interface exists
        if not self.does_os_interface_exist(initial_interface_name):
            if not suppress_error:
                self.log.error(f"Interface: {initial_interface_name} does not exist")
            return STATUS_NOK        

        # Get the hardware bus info for the initial interface
        bus_info = self.get_os_interface_hardware_info(initial_interface_name)['businfo']
        
        # Attempt to rename the interface using the `ip` command
        result = self.run(['ip', 'link', 'set', initial_interface_name, 'name', alias_interface_name], suppress_error=True)
        
        # Check if the alias interface already exists in the database
        if self.db_lookup_interface_alias_exist(initial_interface_name, alias_interface_name):
            self.log.debug(f"Alias-Interface already exists: {alias_interface_name} assigned to initial-interface: {initial_interface_name}")
            return STATUS_OK
        
        # If the `ip` command failed, handle the error
        if result.exit_code:
            if not suppress_error:
                self.log.error(f"Unable to rename interface {initial_interface_name} to {alias_interface_name} in the OS")
            return STATUS_NOK
        
        # Update the database with the new alias name
        if self.update_db_rename_alias(bus_info, initial_interface_name, alias_interface_name):
            if not suppress_error:
                self.log.error(f"Unable to add initial-interface: {initial_interface_name} to alias-interface: {alias_interface_name} in the DB")
            return STATUS_NOK
        
        return STATUS_OK
       
    def set_os_rename_interface(self, reverse=False, suppress_error: bool=True) -> StatusResult:
        """
        Rename network interfaces based on database aliases.
        
        This method renames network interfaces as specified in the database. It can also reverse the renaming process
        if the `reverse` parameter is set to `True`. If an error occurs during the renaming process, it logs an error 
        message unless `suppress_error` is set to `True`.
        
        Args:
            reverse (bool, optional): If True, reverses the renaming process by swapping original and alias names. 
                                    Defaults to False.
            suppress_error (bool, optional): If True, suppresses error logging when renaming fails. Defaults to True.
        
        Returns:
            StatusResult: STATUS_OK if all interfaces were renamed successfully, STATUS_NOK otherwise.
        """
        for alias in self.get_db_interface_aliases():
            original_name = alias['InterfaceName']
            alias_name = alias['AliasInterface']

            self.log.debug(f'orig-interface: {original_name} -> new-interface: {alias_name}')

            if reverse:
                original_name, alias_name = alias_name, original_name

            if self._rename_os_interface(original_name, alias_name):
                if not suppress_error:
                    self.log.error(f"Failed to update and rename interface: {original_name} to {alias_name}")
                return STATUS_NOK

            self.log.debug(f"Interface {original_name} successfully updated and renamed to {alias_name}")

        return STATUS_OK

    def update_interface_proxy_arp(self, interface_name: InterfaceName, negate: bool = False) -> StatusResult:
        """
        Enable or disable Proxy ARP on a network interface and update the Proxy ARP configuration in the database.

        This method allows you to enable or disable Proxy ARP on the specified network interface and update the Proxy ARP
        configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            negate (bool): If True, Proxy ARP will be disabled on the interface. If False, Proxy ARP will be enabled.

        Returns:
            StatusResult: STATUS_OK if the Proxy ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        if Arp().set_os_proxy_arp(interface_name, negate):
            self.log.error(f"Unable to update proxy-arp: {not negate} on interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_proxy_arp(interface_name, (not negate)):
            self.log.error(f"Unable to update proxy-arp: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_drop_gratuitous_arp(self, interface_name: InterfaceName, negate: bool = False) -> StatusResult:
        """
        Enable or disable the dropping of gratuitous ARP packets on a network interface and update the configuration in the database.

        This method allows you to enable or disable the dropping of gratuitous ARP packets on the specified network interface
        and update the configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            negate (bool): If True, gratuitous ARP dropping will be disabled on the interface. If False, it will be enabled.

        Returns:
            StatusResult: STATUS_OK if the gratuitous ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        if Arp().set_os_drop_gratuitous_arp(interface_name, negate):
            self.log.error(f"Unable to update drop-gratuitous-arp: {not negate} on interface: {interface_name} via OS")
            return STATUS_NOK

        if self.update_db_drop_gratuitous_arp(interface_name, (not negate)):
            self.log.error(f"Unable to update drop-gratuitous-arp: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def update_interface_static_arp(self, interface_name: InterfaceName, inet: InetAddressText, mac_address: MacAddressText, encap: Encapsulate, negate: bool = False) -> StatusResult:
        """
        Enable or disable a static ARP entry for a network interface and update the static ARP configuration in the database.

        This method allows you to enable or disable a static ARP entry on the specified network interface and update the
        static ARP configuration in the database.

        Args:
            interface_name (str): The name of the network interface.
            inet (str): The IP address associated with the ARP entry.
            mac_address (str): The MAC address associated with the ARP entry.
            encap (Encapsulate): The type of encapsulation used for the ARP entry.
            negate (bool): If True, the static ARP entry will be disabled. If False, the static ARP entry will be enabled.

        Returns:
            StatusResult: STATUS_OK if the static ARP configuration was successfully updated, STATUS_NOK otherwise.
        """
        status, mac_address = self.format_mac_address(mac_address)
        
        if not status:
            self.log.error(f"Invalid ARP entry mac address: {mac_address}")
            return STATUS_NOK
        
        if not Arp().is_arp_entry_exists(inet):
            self.log.debug(f"ARP entry for {inet} already exists")
            
            if Arp().set_os_static_arp(interface_name, inet, mac_address, encap.value, not negate):
                self.log.error(f"Unable to update static ARP: {not negate} on interface: {interface_name} via OS")
                return STATUS_NOK
        
        if self.update_db_static_arp(interface_name, inet, mac_address, encap.value, negate):
            self.log.error(f"Unable to update static ARP: {not negate} on interface: {interface_name} via DB")
            return STATUS_NOK

        return STATUS_OK

    def set_nat_domain_status_1(self, interface_name:InterfaceName, nat_in_out:NATDirection, negate=False):
        
        if nat_in_out is NATDirection.INSIDE:
            if Nat().create_inside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
        else:
            if Nat().create_outside_nat(interface_name):
                self.log.error(f"Unable to add INSIDE NAT to interface: {interface_name}")
                return STATUS_NOK
            
        return STATUS_OK        

    def set_nat_domain_status_2(self, interface_name:InterfaceName, nat_pool_name:NatPoolName, nat_in_out:NATDirection, negate=False):
        if nat_in_out == NATDirection.INSIDE.value:
            self.log.debug("Configuring NAT for the inside interface")
            
            if Nat().create_inside_nat(nat_pool_name, self.ifName, negate):
                self.log.error(f"Unable to set INSIDE NAT to interface: {self.ifName} to NAT-pool {nat_pool_name}")
                return STATUS_NOK

            if self.update_db_nat_direction(self.ifName, nat_pool_name, NATDirection.INSIDE, negate):
                self.log.debug(f"Unable to update NAT Direction: {nat_in_out}")
                return STATUS_NOK
        
        elif nat_in_out == NATDirection.OUTSIDE.value:
            self.log.debug("Configuring NAT for the outside interface")
            
            if Nat().create_outside_nat(nat_pool_name, self.ifName, negate):
                self.log.error(f"Unable to set OUTSIDE NAT to interface: {self.ifName} to NAT-pool {nat_pool_name}")
                return STATUS_NOK
            
            if self.update_db_nat_direction(self.ifName, nat_pool_name, NATDirection.OUTSIDE, negate):
                self.log.debug(f"Unable to update NAT Direction: {nat_in_out}")
                return STATUS_NOK
        return STATUS_OK

    def set_nat_domain_status(self, interface_name: InterfaceName, nat_pool_name: NatPoolName, nat_in_out: NATDirection, negate=False) -> StatusResult:
        """
        Configure NAT domain status for an interface.

        Args:
            interface_name (str): The name of the interface.
            nat_pool_name (str): The name of the NAT pool.
            nat_in_out (NATDirection): The direction of NAT (INSIDE or OUTSIDE).
            negate (bool, optional): Whether to negate the NAT configuration. Default is False.

        Returns:
            StatusResult: STATUS_OK if NAT configuration is successful, STATUS_NOK if there is an error.

        """
        if nat_in_out == NATDirection.INSIDE:
            self.log.debug("Configuring NAT for the inside interface")

            if Nat().create_inside_nat(nat_pool_name, interface_name, negate):
                self.log.error(f"Unable to set INSIDE NAT to interface: {interface_name} to NAT-pool {nat_pool_name} via OS")
                return STATUS_NOK
            
        elif nat_in_out == NATDirection.OUTSIDE:
            self.log.debug("Configuring NAT for the outside interface")

            if Nat().create_outside_nat(nat_pool_name, interface_name, negate):
                self.log.error(f"Unable to set OUTSIDE NAT to interface: {interface_name} to NAT-pool {nat_pool_name} via OS")
                return STATUS_NOK

        return STATUS_OK

    def get_os_interface_hardware_info(self, interface_name: InterfaceName) -> dict:
        """
        Retrieve information about hardware network interfaces.

        Args:
            interface_name (str): The name of the network interface to retrieve information for.

        Returns:
            dict or None: A dictionary containing information about the network interface if successful,
                          None otherwise.
        """
        try:
            result = self.run(['lshw', '-c', 'network', '-json'], suppress_error=True, sudo=False)

            if result.exit_code == 0:
                output_json = json.loads(result.stdout)

                for interface in output_json:
                    if interface.get('logicalname') == interface_name:
                        return interface

                self.log.debug(f"No information found for interface: {interface_name}")
                return None
            
            else:
                self.log.debug(f"Error running lshw command. Exit code: {result.exit_code}")
                return None

        except (json.JSONDecodeError, AttributeError) as e:
            print(f"Error decoding JSON: {e}")
            return None

    def update_interface_description(self, interface_name: InterfaceName, description: str) -> StatusResult:
        """
        Update the description of a network interface in the database.

        This method allows you to update the user-defined description of a specific network interface in the database.

        Args:
            interface_name (str): The name of the network interface.
            description (str): The new description to assign to the network interface.

        Returns:
            StatusResult: STATUS_OK if the description is successfully updated, STATUS_NOK otherwise.
        """
        return self.update_db_description(interface_name, description)

    def update_interface_db_from_os(self, interface_name: InterfaceName | None = None) -> StatusResult:
        """
        Update the database with information about network interfaces found by the operating system.

        This method iterates through all network interfaces discovered by the operating system,
        checks the database to ensure that each interface is not already defined. If not defined,
        it creates an entry with basic configuration. Otherwise, it skips the interface.

        Args:
            interface_name (str, optional): The name of a specific network interface to update.

        Returns:
            StatusResult: STATUS_OK if the update process is successful, STATUS_NOK otherwise.
        """
        for if_name in self.get_os_network_interfaces():
            
            interface_exists = self.db_lookup_interface_exists(if_name).status
            if interface_name is not None and if_name != interface_name or interface_exists:
                self.log.debug(f"Skipping interface: {if_name}")
                continue
            
            if_type = self.get_os_interface_type_extened(if_name)
                       
            if if_type != InterfaceType.UNKNOWN:
                self.log.debug(f"Adding Interface: {if_name} -> if-type: {if_type.name} to DB")
                self.add_db_interface_entry(if_name, if_type)
                self.update_interface_description(if_name,f'Interface Type: {if_type.name}')
                self.update_shutdown(if_name, State.UP)

        return STATUS_OK

    def _rename_os_interface(self, initial_interface_name: InterfaceName, alias_interface_name: InterfaceName) -> StatusResult:
        """
        Rename the operating system network interface.

        This method uses the 'ip' command to rename the specified network interface.
        
        Args:
            initial_interface_name (str): The current name of the network interface.
            alias_interface_name (str): The new name to assign to the network interface.

        Returns:
            StatusResult: STATUS_OK if the renaming process is successful, STATUS_NOK otherwise.
        """
        result = self.run(['ip', 'link', 'set', initial_interface_name, 'name', alias_interface_name], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Error renaming interface: {initial_interface_name} to {alias_interface_name}")
            return STATUS_NOK

        self.log.debug(f"Interface {initial_interface_name} successfully renamed to {alias_interface_name}")
        
        return STATUS_OK

    def fetch_db_interface_names(self) -> list[str]:
        """
        Get a list of all interface names from DB.

        Returns:
            list[str]: A list containing the names of all interfaces.
        """
        return self.get_db_interface_names()
    
    def flush_interfaces(self, interface_name: InterfaceName | None = None) -> StatusResult:
        """
        Flush network interfaces, removing any configurations.

        This method iterates through the list of network interfaces and uses the 'flush_interface' method
        to remove configurations. If a specific interface name is provided, only that interface is flushed.

        Args:
            interface_name (str, optional): The name of the specific network interface to flush.

        Returns:
            StatusResult: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        if interface_name:
            self.flush_interface(interface_name)
        else:
            for if_name in self.get_db_interface_names():
                self.flush_interface(if_name)

        return STATUS_OK

    # LoopBack Operations

    def get_os_lo_labels(self) -> list[str]:
        """
        Extract labels from the loopback interface labels

        Args:
            ip_lo_json (dict): The JSON data structure for the loopback interface.

        Returns:
            list[str]: A list of labels found in the loopback interface's address information.
        """
        labels = []
        
        try:
            result = self.run(['ip', '-json', 'address', 'show', 'dev', 'lo'], suppress_error=True)
            
            if result.exit_code:
                self.log.debug(f"does_os_interface_exist() returned a non-zero exit code: {result.exit_code}")
                return []
                            
        except Exception as e:
            self.log.error(f"Exception in does_os_interface_exist: {e}")
            return []

        interfaces = json.loads(result.stdout)
        
        for interface in interfaces:
            ifname = interface.get("ifname", "")
                            
            if ifname == "lo":
                for addr_info in interface.get("addr_info", []):
                    label = addr_info.get("label", "lo")
                    labels.append(label.split(":")[-1])

        return labels

    def create_os_loopback(self, loopback_name: InterfaceName, inet_address: InetAddressText) -> StatusResult:
        """
        Creates a loopback interface with the specified name (label) and IP address on the 'lo' device.

        Args:
            loopback_name (str): The name (label) for the new loopback interface.
            inet_address (str): The IP address to assign to the loopback interface.

        Returns:
            StatusResult: STATUS_OK if the loopback interface was created successfully, otherwise STATUS_NOK.
        """
        
        if loopback_name in self.get_os_lo_labels():
            self.log.debug(f"Loopback interface {loopback_name} already exists.")
            return STATUS_NOK
        
        try:
            ip = ipaddress.ip_address(inet_address)
            if ip.version == 4:
                ip_ver_opt = 'addr'
                cidr = '/32'
            elif ip.version == 6:
                ip_ver_opt = '-6 addr'
                cidr = '/128'
            else:
                self.log.error(f'inet address is invalid: {inet_address}')
                return STATUS_NOK
            
        except ValueError:
            self.log.error(f'inet address is invalid: {inet_address}')
            return STATUS_NOK

        inet_address += cidr

        command = ['ip', ip_ver_opt, 'add', inet_address, 'label', f'lo:{loopback_name}', 'dev', 'lo']
        
        rtn = self.run(command, suppress_error=True)
        
        if rtn.exit_code != 0:
            self.log.error(f"Failed to create loopback interface {loopback_name} with address {inet_address}: {rtn.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def set_db_loopback(self, loopback_name: InterfaceName, inet_address_cidr: InetCidrText) -> StatusResult:
        """
        Sets a loopback interface in the database with the specified name and IP address in CIDR notation.

        Args:
            loopback_name (str): The name (label) for the loopback interface.
            inet_address_cidr (str): The IP address with CIDR notation to assign to the loopback interface.

        Returns:
            StatusResult: STATUS_OK if the loopback interface was set successfully, otherwise STATUS_NOK.
        """
        
        # Attempt to add the loopback interface entry to the database
        if not self.add_db_interface_entry(interface_name=loopback_name, ifType=InterfaceType.LOOPBACK):
            self.log.error(f'Unable to add Loopback interface: {loopback_name}')
            return STATUS_NOK
        
        # Attempt to update the IP address for the loopback interface in the database
        if not self.update_db_inet_address(interface_name=loopback_name, inet_address_cidr=inet_address_cidr):
            self.log.error(f'Unable to update inet address for Loopback interface: {loopback_name} with address: {inet_address_cidr}')
            # Remove the interface entry since the IP address update failed
            self.del_db_loopback(loopback_name)
            return STATUS_NOK
        
        return STATUS_OK
    
    def destroy_os_loopback(self, loopback_name: InterfaceName, inet_address: InetAddressText) -> StatusResult:
        """
        Destroys a loopback interface with the specified name (label) and IP address from the 'lo' device.

        Args:
            loopback_name (str): The name (label) for the loopback interface to be removed.
            inet_address (str): The IP address assigned to the loopback interface.

        Returns:
            StatusResult: STATUS_OK if the loopback interface was removed successfully, otherwise STATUS_NOK.
        """
        
        if loopback_name not in self.get_os_lo_labels():
            self.log.debug(f"Loopback interface {loopback_name} does not exist.")
            return STATUS_NOK
        
        try:
            ip = ipaddress.ip_address(inet_address)
            if ip.version == 4:
                ip_ver_opt = 'addr'
                cidr = '/32'
            elif ip.version == 6:
                ip_ver_opt = '-6 addr'
                cidr = '/128'
            else:
                self.log.error(f'inet address is invalid: {inet_address}')
                return STATUS_NOK
            
        except ValueError:
            self.log.error(f'inet address is invalid: {inet_address}')
            return STATUS_NOK

        inet_address += cidr

        command = ['ip', ip_ver_opt, 'del', inet_address, 'label', f'lo:{loopback_name}', 'dev', 'lo']
        
        rtn = self.run(command, suppress_error=True)
        
        if rtn.exit_code != 0:
            self.log.error(f"Failed to destroy loopback interface {loopback_name} with address {inet_address}: {rtn.stderr}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def del_db_loopback(self, loopback_name: InterfaceName) -> StatusResult:
        """
        Deletes a loopback interface from the database with the specified name.

        Args:
            loopback_name (str): The name (label) of the loopback interface to be deleted.

        Returns:
            StatusResult: STATUS_OK if the loopback interface was deleted successfully, otherwise STATUS_NOK.
        """
        
        if not self.del_db_interface(loopback_name):
            self.log.error(f'Unable to delete Loopback interface: {loopback_name}')
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_next_loopback_address(self) -> str:
        """
        Search the lo interface, retrieve a list of IPv4 addresses in the 127.x.x.x range,
        and find the next available address in that range.

        Returns:
            str: The next available 127.x.x.x address in CIDR notation.
        """
        try:
            # Get the list of addresses on the loopback interface in JSON format
            result = self.run(['ip', '-j', 'addr', 'show', 'dev', 'lo'], suppress_error=True)

            if result.exit_code != 0:
                self.log.error(f"Error retrieving IP addresses: {result.stderr}")
                return None

            data = json.loads(result.stdout)

            # Collect all 127.x.x.x addresses
            addresses = [
                ipaddress.ip_interface(f"{addr_info['local']}/{addr_info['prefixlen']}").ip
                for iface in data if iface['ifname'] == 'lo'
                for addr_info in iface.get('addr_info', [])
                if addr_info['family'] == 'inet' and ipaddress.ip_interface(f"{addr_info['local']}/{addr_info['prefixlen']}").ip.is_loopback
            ]

            # Sort addresses and find the highest one
            addresses.sort()
            last_address = addresses[-1] if addresses else ipaddress.IPv4Address('127.0.0.0')

            # Calculate the next available address
            next_address = last_address + 1
            if next_address.is_loopback:
                next_address_cidr = f"{next_address}/8"
                return next_address_cidr
            else:
                self.log.error("No more available 127.x.x.x addresses")
                return None

        except Exception as e:
            self.log.error(f"An error occurred: {e}")
            return None

    def update_interface_loopback_inet(self, loopback_name: InterfaceName, inet_address_cidr: InetCidrText | None = None, negate: bool = False) -> StatusResult:
        """
        Update or delete the inet address of a loopback interface.

        This function updates the inet address of a specified loopback interface. If the negate parameter is set to True,
        it attempts to delete the specified inet address from the loopback interface. Otherwise, it sets the specified
        inet address. If no address is provided, it attempts to auto-assign the next available inet address.

        Parameters:
        loopback_name (str): The name of the loopback interface to update.
        inet_address_cidr (str, optional): The inet address in CIDR notation to set or delete. If None, the next available
                                        address is auto-assigned. Defaults to None.
        negate (bool): If True, the inet address is deleted from the loopback interface. If False, the address is set.
                    Defaults to False.

        Returns:
        StatusResult: STATUS_OK if the operation was successful, otherwise STATUS_NOK.
        """
        self.log.debug(f"update_interface_loopback_inet() - Loopback: {loopback_name}, "
                    f"Inet: {inet_address_cidr}, Negate: {negate}")

        if negate:
            if not self.del_inet_address_loopback(loopback_name, inet_address_cidr):
                self.log.error(f"Unable to delete loopback: {loopback_name} address: {inet_address_cidr} from OS")
                return STATUS_NOK

            if not self.del_db_interface(loopback_name):
                self.log.error(f"Unable to delete loopback: {loopback_name} address: {inet_address_cidr} from DB")
                return STATUS_NOK

        else:
            if not inet_address_cidr:
                inet_address_cidr = self.get_next_loopback_address()
                if not inet_address_cidr:
                    self.log.error("Unable to get next available loopback address")
                    return STATUS_NOK

                self.log.debug(f'Auto-Assign Loopback: {loopback_name} - inet: {inet_address_cidr}')

            if self.set_inet_address_loopback(loopback_name, inet_address_cidr):
                self.log.error(f"Unable to update loopback: {loopback_name} address: {inet_address_cidr} to OS")
                return STATUS_NOK

            if self.add_db_interface(loopback_name, InterfaceType.LOOPBACK):
                self.log.error(f"Unable to update loopback: {loopback_name} to DB")
                return STATUS_NOK

        return STATUS_OK

# FILE: tests/packaging/test_interface_auto_discovery.py
from __future__ import annotations

import sys
import types
from pathlib import Path


def test_cli_entrypoint_enables_system_startup(monkeypatch) -> None:
    startup_values = []

    class FakeRouterCLI:
        def __init__(self, system_start_up: bool = False) -> None:
            startup_values.append(system_start_up)

        def run(self) -> None:
            return None

    fake_module = types.ModuleType("routershell.lib.cli.router_main_cli")
    fake_module.RouterCLI = FakeRouterCLI
    monkeypatch.setitem(sys.modules, "routershell.lib.cli.router_main_cli", fake_module)

    from routershell import cli

    assert cli.main() == 0
    assert startup_values == [True]


def test_os_interface_discovery_uses_unprivileged_ip(monkeypatch) -> None:
    from routershell.lib.network_manager.common.run_commands import RunResult
    from routershell.lib.network_manager.network_operations.interface import Interface

    commands = []
    iface = Interface()

    def fake_run(command: list[str], suppress_error: bool = False, shell: bool = False, sudo: bool = True) -> RunResult:
        commands.append((command, sudo))
        return RunResult(
            stdout=(
                "["
                '{"ifname": "lo", "link_type": "loopback"},'
                '{"ifname": "enp1s0", "link_type": "ether"},'
                '{"ifname": "wlp6s0", "link_type": "ether"}'
                "]"
            ),
            stderr="",
            exit_code=0,
            command=command,
        )

    monkeypatch.setattr(iface, "run", fake_run)
    monkeypatch.setattr(
        "routershell.lib.network_manager.network_operations.interface.os.path.isdir",
        lambda path: path.endswith("/wlp6s0/wireless"),
    )

    assert iface.get_os_network_interfaces() == ["enp1s0", "wlp6s0"]
    assert commands == [(["ip", "-json", "link", "show"], False)]


def test_blank_database_is_populated_from_os_interfaces(monkeypatch, tmp_path: Path) -> None:
    from routershell.lib.common.constants import ROUTER_SHELL_DB_FILE_ENV, STATUS_OK
    from routershell.lib.common.singleton import Singleton
    from routershell.lib.db.interface_db import InterfaceDatabase
    from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
    from routershell.lib.network_manager.common.interface import InterfaceType
    from routershell.lib.network_manager.common.phy import State
    from routershell.lib.network_manager.network_operations.interface import Interface

    monkeypatch.setenv(ROUTER_SHELL_DB_FILE_ENV, str(tmp_path / "routershell.db"))
    Singleton._instances.pop(RouterShellDB, None)
    RouterShellDB.connection = None
    RouterShellDB.connection_created = False
    InterfaceDatabase.rsdb = RouterShellDB()

    iface = Interface()
    monkeypatch.setattr(iface, "get_os_network_interfaces", lambda: ["enp1s0"])
    monkeypatch.setattr(iface, "get_os_interface_type_extened", lambda interface_name: InterfaceType.ETHERNET)

    shutdown_updates = []

    def fake_update_shutdown(interface_name: str, state: State) -> bool:
        shutdown_updates.append((interface_name, state))
        return STATUS_OK

    monkeypatch.setattr(iface, "update_shutdown", fake_update_shutdown)

    assert iface.fetch_db_interface_names() == []
    assert iface.update_interface_db_from_os() == STATUS_OK
    assert iface.fetch_db_interface_names() == ["enp1s0"]
    assert shutdown_updates == [("enp1s0", State.UP)]

    assert iface.update_interface_db_from_os() == STATUS_OK
    assert iface.fetch_db_interface_names() == ["enp1s0"]
