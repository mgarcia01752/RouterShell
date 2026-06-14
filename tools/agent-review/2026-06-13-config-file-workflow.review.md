### Summary
Added a basic RouterShell configuration-file workflow using `routershell --config-file <path>`. The console and module entry points now share argument parsing, RouterCLI can feed a command file through the existing prompt processor, and docs/tests cover the workflow and missing-file failure.

### Modified Files
- README.md
- install/README.md
- src/routershell/__main__.py
- src/routershell/cli.py
- src/routershell/lib/cli/router_main_cli.py
- tests/packaging/test_interface_auto_discovery.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/python -m pytest tests/packaging/test_interface_auto_discovery.py tests/packaging/test_entry_points.py -q` -> pass, 7 passed.
- `/opt/routershell/venv/bin/python -m ruff check src/routershell/cli.py src/routershell/__main__.py src/routershell/lib/cli/router_main_cli.py tests/packaging/test_interface_auto_discovery.py` -> pass, all checks passed.
- `/opt/routershell/venv/bin/python -m pytest -q` -> pass, 42 passed.
- `/opt/routershell/venv/bin/python -m ruff check .` -> pass, all checks passed.
- `bash -n tools/vm/*.sh install/install.sh install/uninstall.sh` -> pass.

### Tests
- `pytest` -> pass, 42 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM scripts, install script, and uninstall script.

### Notes / Warnings
- The initial workflow supports non-interactive file application through `--config-file`; arbitrary interactive `copy file <path> running-config` is still a future enhancement.

### Remaining TODOs / Follow-Ups
- Consider adding an interactive `copy file <path> running-config` command after the basic workflow is exercised.

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
On apt/snapd systems, development mode also installs Multipass so the
`tools/vm/` installer test workflow can create disposable RouterShell test VMs.
Production installs do not install Multipass.

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

# FILE: src/routershell/__main__.py
"""Module execution for RouterShell."""

from __future__ import annotations

from routershell import cli


def main() -> int:
    """Run RouterShell from ``python -m routershell``."""
    return cli.main()


if __name__ == "__main__":
    raise SystemExit(main())

# FILE: src/routershell/cli.py
"""Console entry points for RouterShell."""

from __future__ import annotations

import argparse
from pathlib import Path

from routershell.lib.common.constants import STATUS_NOK
from routershell.lib.common.types import CommandArgs
from routershell.logging_config import configure_logging


def main(argv: CommandArgs | None = None) -> int:
    """Run the RouterShell interactive CLI."""
    parser = argparse.ArgumentParser(description="Run RouterShell.")
    parser.add_argument(
        "--config-file",
        type=Path,
        help="Load RouterShell commands from a configuration file and exit.",
    )
    parser.add_argument(
        "-f",
        "--factory-reset",
        action="store_true",
        help="Run the factory reset workflow.",
    )
    args = parser.parse_args(argv)

    if args.factory_reset:
        return factory_reset()

    if args.config_file and not args.config_file.is_file():
        parser.error(f"configuration file not found: {args.config_file}")

    configure_logging()

    from routershell.lib.cli.router_main_cli import RouterCLI

    router_cli = RouterCLI(system_start_up=True)
    if args.config_file:
        if router_cli.run(config_file=args.config_file) == STATUS_NOK:
            return 1
    else:
        router_cli.run()

    return 0


def factory_reset() -> int:
    """Run the RouterShell factory reset workflow."""
    configure_logging()

    from routershell.lib.system.system_start_up import SystemFactoryReset

    SystemFactoryReset()
    return 0

# FILE: src/routershell/lib/cli/router_main_cli.py
import logging

from routershell.lib.cli.base.clear_mode import ClearMode
from routershell.lib.cli.base.copy import Copy
from routershell.lib.cli.base.global_cmd_op import Global
from routershell.lib.cli.common.router_prompt import PromptFeeder, RouterPrompt
from routershell.lib.cli.config.config import Configure
from routershell.lib.cli.show.show import Show
from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import FilePath, StatusResult
from routershell.lib.system.system_call import SystemCall
from routershell.lib.system.system_start_up import SystemStartUp


class RouterCLI(RouterPrompt):
    """
    RouterCLI is a command-line interface class for managing and interacting with network routers.

    This class inherits from RouterPrompt and initializes the router system with optional startup procedures.

    Attributes:
        system_start_up (bool): Determines if the system startup procedures should be executed upon initialization.

    Methods:
        __init__(system_start_up=True):
            Initializes the RouterCLI instance and optionally performs system startup procedures.
    """

    def __init__(self, system_start_up=False):
        """
        Initializes the RouterCLI instance.

        Args:
            system_start_up (bool): If True, performs system startup procedures by calling SystemStartUp().
                Defaults to True.

        Inherited Methods:
            RouterPrompt.__init__(): Initializes the parent RouterPrompt class.

        Example:
            # Create a RouterCLI instance with system startup procedures
            router_cli = RouterCLI(system_start_up=True)

            # Create a RouterCLI instance without system startup procedures
            router_cli = RouterCLI(system_start_up=False)
        """
        super().__init__()

        if system_start_up:
            SystemStartUp()

        RouterPrompt.__init__(self)

        self.register_top_lvl_cmds(Global())
        self.register_top_lvl_cmds(ClearMode())
        self.register_top_lvl_cmds(Configure())
        self.register_top_lvl_cmds(Copy())
        self.register_top_lvl_cmds(Show())

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ROUTERCLI)

        self.intro_message()

    def intro_message(self):
        banner_motd = SystemCall().get_banner()
        self.intro = f"\n{banner_motd}\n" if banner_motd else "Welcome to the Router CLI!\n"

    def run(self, config_file: FilePath | None = None) -> StatusResult:
        """
        Start RouterShell interactively or apply a command file.

        Args:
            config_file (FilePath | None): Optional file containing RouterShell
                commands to process through the same command path used by
                pasted interactive commands. When provided, RouterShell exits
                after the file is processed.

        Returns:
            StatusResult: STATUS_OK when the CLI session or file processing
            completes successfully.
        """
        print(self.intro)
        if config_file:
            prompt_feeder = PromptFeeder(PromptFeeder.process_file(config_file))
            return self.start(prompt_feeder)

        self.start()
        return STATUS_OK

# FILE: tests/packaging/test_interface_auto_discovery.py
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest


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

    assert cli.main([]) == 0
    assert startup_values == [True]


def test_cli_entrypoint_loads_config_file(monkeypatch, tmp_path: Path) -> None:
    startup_values = []
    config_files = []
    config_file = tmp_path / "lab-router.cfg"
    config_file.write_text("enable\nshow running-config\n")

    class FakeRouterCLI:
        def __init__(self, system_start_up: bool = False) -> None:
            startup_values.append(system_start_up)

        def run(self, config_file: Path | None = None) -> None:
            config_files.append(config_file)

    fake_module = types.ModuleType("routershell.lib.cli.router_main_cli")
    fake_module.RouterCLI = FakeRouterCLI
    monkeypatch.setitem(sys.modules, "routershell.lib.cli.router_main_cli", fake_module)

    from routershell import cli

    assert cli.main(["--config-file", str(config_file)]) == 0
    assert startup_values == [True]
    assert config_files == [config_file]


def test_cli_entrypoint_rejects_missing_config_file(monkeypatch, tmp_path: Path) -> None:
    startup_values = []
    missing_config_file = tmp_path / "missing.cfg"

    class FakeRouterCLI:
        def __init__(self, system_start_up: bool = False) -> None:
            startup_values.append(system_start_up)

    fake_module = types.ModuleType("routershell.lib.cli.router_main_cli")
    fake_module.RouterCLI = FakeRouterCLI
    monkeypatch.setitem(sys.modules, "routershell.lib.cli.router_main_cli", fake_module)

    from routershell import cli

    with pytest.raises(SystemExit) as error:
        cli.main(["--config-file", str(missing_config_file)])

    assert error.value.code == 2
    assert startup_values == []


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
