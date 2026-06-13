### Summary
Added centralized RouterShell logging configuration using standard Python logging with rotating file support and environment overrides. Wired the runtime entry points to configure logging before starting CLI workflows, removed hardcoded logging setup from the deeper CLI module, documented runtime logging, and added focused tests.

### Modified Files
- README.md
- install/README.md
- src/routershell/logging_config.py
- src/routershell/cli.py
- src/routershell/lib/cli/router_main_cli.py
- tests/packaging/test_logging_config.py

### Commands Executed And Results
- `python3 -m pytest tests/packaging/test_logging_config.py` → fail; system Python has no pytest module.
- `python3 -m ruff check src/routershell/logging_config.py src/routershell/cli.py src/routershell/lib/cli/router_main_cli.py tests/packaging/test_logging_config.py` → fail; system Python has no ruff module.
- `/opt/routershell/venv/bin/python -m pytest tests/packaging/test_logging_config.py` → pass; 5 tests passed.
- `/opt/routershell/venv/bin/ruff check src/routershell/logging_config.py src/routershell/cli.py src/routershell/lib/cli/router_main_cli.py tests/packaging/test_logging_config.py` → pass; all checks passed after import/whitespace cleanup.
- `/opt/routershell/venv/bin/python -m pytest` → pass; 9 tests passed.
- `/opt/routershell/venv/bin/ruff check .` → pass; all checks passed.

### Tests
- `/opt/routershell/venv/bin/python -m pytest` → pass; 9 tests passed.
- `/opt/routershell/venv/bin/ruff check .` → pass; all checks passed.

### Notes / Warnings
- Validation used `/opt/routershell/venv` because system Python did not have pytest or ruff installed.
- Existing `RouterShellLoggerSettings` remains in place for compatibility with current `self.log.setLevel(...)` calls.

### Remaining TODOs / Follow-Ups
- Migrate classes from `self.log` to `self.logger` in a later mechanical cleanup.
- Retire `RouterShellLoggerSettings` after per-component level calls are removed.

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
`/var/lib/routershell/baseline` before making install changes.

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
developer validation, not production hosts.

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

# FILE: src/routershell/logging_config.py

"""Central logging configuration for RouterShell."""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path

DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = Path("/tmp/log/routershell.log")
DEFAULT_LOG_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_LOG_BACKUP_COUNT = 5

LOG_LEVEL_ENV = "ROUTERSHELL_LOG_LEVEL"
LOG_FILE_ENV = "ROUTERSHELL_LOG_FILE"
LOG_CONSOLE_ENV = "ROUTERSHELL_LOG_CONSOLE"
LOG_FILE_ENABLED_ENV = "ROUTERSHELL_LOG_FILE_ENABLED"

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}
_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


class RouterShellLogging:
    """Configure and retrieve RouterShell loggers."""

    @staticmethod
    def configure(
        level: str = DEFAULT_LOG_LEVEL,
        log_file: str | Path = DEFAULT_LOG_FILE,
        console: bool = True,
        file_logging: bool = True,
    ) -> None:
        """Configure root logging for RouterShell runtime processes.

        Environment variables override the passed values:
        `ROUTERSHELL_LOG_LEVEL`, `ROUTERSHELL_LOG_FILE`,
        `ROUTERSHELL_LOG_CONSOLE`, and `ROUTERSHELL_LOG_FILE_ENABLED`.
        File logging uses a rotating handler and is skipped when the target
        directory cannot be created or written.
        """
        resolved_level = RouterShellLogging._resolve_level(os.getenv(LOG_LEVEL_ENV, level))
        resolved_file = Path(os.getenv(LOG_FILE_ENV, str(log_file)))
        resolved_console = RouterShellLogging._resolve_bool(os.getenv(LOG_CONSOLE_ENV), console)
        resolved_file_logging = RouterShellLogging._resolve_bool(os.getenv(LOG_FILE_ENABLED_ENV), file_logging)

        handlers = {}
        root_handlers = []

        if resolved_console:
            handlers["console"] = {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": resolved_level,
            }
            root_handlers.append("console")

        if resolved_file_logging and RouterShellLogging._can_write_log_file(resolved_file):
            handlers["file"] = {
                "backupCount": DEFAULT_LOG_BACKUP_COUNT,
                "class": "logging.handlers.RotatingFileHandler",
                "encoding": "utf-8",
                "filename": str(resolved_file),
                "formatter": "default",
                "level": resolved_level,
                "maxBytes": DEFAULT_LOG_MAX_BYTES,
            }
            root_handlers.append("file")

        if not root_handlers:
            handlers["null"] = {
                "class": "logging.NullHandler",
                "level": resolved_level,
            }
            root_handlers.append("null")

        logging.config.dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    },
                },
                "handlers": handlers,
                "root": {
                    "handlers": root_handlers,
                    "level": resolved_level,
                },
            }
        )

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Return a named logger using RouterShell's logging configuration."""
        return logging.getLogger(name)

    @staticmethod
    def _resolve_level(level: str) -> int:
        return _LEVELS.get(level.strip().upper(), _LEVELS[DEFAULT_LOG_LEVEL])

    @staticmethod
    def _resolve_bool(value: str | None, default: bool) -> bool:
        if value is None:
            return default

        normalized = value.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
        return default

    @staticmethod
    def _can_write_log_file(log_file: Path) -> bool:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with log_file.open("a", encoding="utf-8"):
                return True
        except OSError:
            return False


def configure_logging(
    level: str = DEFAULT_LOG_LEVEL,
    log_file: str | Path = DEFAULT_LOG_FILE,
    console: bool = True,
    file_logging: bool = True,
) -> None:
    """Configure RouterShell logging with standard runtime defaults."""
    RouterShellLogging.configure(
        level=level,
        log_file=log_file,
        console=console,
        file_logging=file_logging,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a RouterShell logger by name."""
    return RouterShellLogging.get_logger(name)

# FILE: src/routershell/cli.py

"""Console entry points for RouterShell."""

from __future__ import annotations

from routershell.logging_config import configure_logging


def main() -> int:
    """Run the RouterShell interactive CLI."""
    configure_logging()

    from routershell.lib.cli.router_main_cli import RouterCLI

    RouterCLI().run()
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
from routershell.lib.cli.common.router_prompt import RouterPrompt
from routershell.lib.cli.config.config import Configure
from routershell.lib.cli.show.show import Show
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
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

    def run(self):
        print(self.intro)
        self.start()

# FILE: tests/packaging/test_logging_config.py

"""Tests for RouterShell logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from routershell.logging_config import (
    LOG_CONSOLE_ENV,
    LOG_FILE_ENABLED_ENV,
    LOG_FILE_ENV,
    LOG_LEVEL_ENV,
    configure_logging,
    get_logger,
)


def test_configure_logging_uses_rotating_file_handler(tmp_path, monkeypatch) -> None:
    """Default file logging should use a bounded rotating file handler."""
    log_file = tmp_path / "routershell.log"
    monkeypatch.setenv(LOG_FILE_ENV, str(log_file))
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()

    handlers = logging.getLogger().handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], RotatingFileHandler)

    logger = get_logger("routershell.test")
    logger.info("hello from test")

    assert log_file.exists()
    assert "hello from test" in log_file.read_text(encoding="utf-8")


def test_configure_logging_honors_env_level(tmp_path, monkeypatch) -> None:
    """The log level environment variable should control the root logger."""
    monkeypatch.setenv(LOG_FILE_ENV, str(tmp_path / "routershell.log"))
    monkeypatch.setenv(LOG_LEVEL_ENV, "DEBUG")
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()

    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_ignores_invalid_env_level(tmp_path, monkeypatch) -> None:
    """Invalid log levels should fall back to the default INFO level."""
    monkeypatch.setenv(LOG_FILE_ENV, str(tmp_path / "routershell.log"))
    monkeypatch.setenv(LOG_LEVEL_ENV, "LOUD")
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()

    assert logging.getLogger().level == logging.INFO


def test_configure_logging_is_idempotent(tmp_path, monkeypatch) -> None:
    """Repeated configuration should replace handlers instead of duplicating them."""
    monkeypatch.setenv(LOG_FILE_ENV, str(tmp_path / "routershell.log"))
    monkeypatch.setenv(LOG_CONSOLE_ENV, "false")

    configure_logging()
    configure_logging()

    assert len(logging.getLogger().handlers) == 1


def test_configure_logging_can_disable_file_logging(monkeypatch) -> None:
    """RouterShell should support console-only logging."""
    monkeypatch.setenv(LOG_FILE_ENABLED_ENV, "false")
    monkeypatch.setenv(LOG_CONSOLE_ENV, "true")

    configure_logging()

    handlers = logging.getLogger().handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
    assert not isinstance(handlers[0], RotatingFileHandler)
