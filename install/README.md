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
Development mode also installs GitHub CLI (`gh`) so failed GitHub Actions logs
can be inspected from the development workstation.
On apt/snapd systems, development mode also installs Multipass so the
`tools/vm/` installer test workflow can create disposable RouterShell test VMs.
Production installs do not install GitHub CLI or Multipass.

Skip development GitHub CLI installation when needed:

```bash
sudo ROUTERSHELL_INSTALL_GITHUB_CLI=false ./install/install.sh --development
```

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
