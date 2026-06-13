# RouterShell VM Install Testing

This directory contains a Multipass-based workflow for testing the generic
RouterShell Linux installer away from the development workstation.

This is a development workflow. It is not part of the production RouterShell
install process.

The VM workflow is for general-purpose Linux install testing only. BusyBox,
OpenWrt, Buildroot, Yocto/Poky images, and embedded router targets remain out
of scope until they have a dedicated install design.

## Prerequisites

- Multipass installed on the development workstation. On apt/snapd systems,
  `sudo ./install/install.sh --development` installs Multipass automatically.
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

The host-side archive defaults to `$HOME/routershell-vm-test.tar.gz` so the
Multipass snap can read it during transfer. Override it with `RS_VM_ARCHIVE`
when needed.

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

The VM test disables nested Multipass installation inside the guest while still
testing RouterShell's editable development install path.

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
excluding `.git`, `.env`, `.routershell`, `.venv`, caches, and build outputs.
It transfers the archive into the VM, extracts it under `/tmp/RouterShell`,
runs the generic installer in production mode by default, and verifies:

- `/usr/local/bin/routershell` exists and is executable.
- `/usr/local/bin/routershell-factory-reset` exists and is executable.
- `/opt/routershell/venv/bin/python` exists and is executable.
- `/var/lib/routershell/baseline/manifest.json` exists.
- The VM has the configured virtual network interfaces.
- The installed Python environment can import `routershell`, verify console
  entry functions, read the package version, and discover the virtual network
  interfaces.

The test intentionally does not start the interactive RouterShell CLI.
