### Summary
Added clear manual VM testing documentation for creating a RouterShell VM, installing the current worktree, entering the VM shell, running RouterShell commands, and cleaning up afterward. Added a focused pytest guard so the manual shell workflow remains documented.

### Modified Files
- tools/vm/README.md
- tests/tools/test_vm_workflow.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/python -m pytest tests/tools/test_vm_workflow.py -q` -> pass, 6 passed.
- `/opt/routershell/venv/bin/python -m ruff check tests/tools/test_vm_workflow.py` -> pass, all checks passed.
- `bash -n tools/vm/*.sh` -> pass.
- `/opt/routershell/venv/bin/python -m pytest -q` -> pass, 38 passed.
- `/opt/routershell/venv/bin/python -m ruff check .` -> pass, all checks passed.

### Tests
- `pytest` -> pass, 38 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM scripts.

### Notes / Warnings
- Documentation-only workflow change; no VM was created, installed, or deleted during this task.

### Remaining TODOs / Follow-Ups
- None.

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

## Manual RouterShell Testing

Use this workflow when you want a disposable Linux host where RouterShell is
installed and ready for interactive commands.

From the RouterShell repository on the development workstation:

```bash
cd ~/Projects/RouterShell
tools/vm/multipass-create.sh
tools/vm/multipass-test-install.sh --development
tools/vm/multipass-shell.sh
```

The first command creates or reuses the `routershell-install-test` VM. The
second command copies the current worktree into the VM, installs RouterShell in
editable development mode, and verifies the install. The third command opens an
interactive shell inside the VM.

Inside the VM, run RouterShell commands against the VM instead of the
development workstation:

```bash
which routershell
routershell --help
ip link show
routershell
```

The VM contains ten simulated 1gbit interfaces named `rs1g0` through `rs1g9`.
Use those interfaces for manual discovery, configuration, and rollback testing.

Exit the VM shell when finished:

```bash
exit
```

Delete the VM:

```bash
tools/vm/multipass-destroy.sh --purge
```

Clean up RouterShell-created VMs:

```bash
tools/vm/multipass-cleanup.sh --dry-run
tools/vm/multipass-cleanup.sh --purge
```

Use `--all` to delete every Multipass instance whose name starts with
`routershell-`:

```bash
tools/vm/multipass-cleanup.sh --all --purge
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

    assert 'RS_VM_ARCHIVE="${RS_VM_ARCHIVE:-${HOME}/routershell-vm-test.tar.gz}"' in common_script
    assert '--exclude=".env"' in common_script
    assert '--exclude=".routershell"' in common_script
    assert 'RS_VM_VIRTUAL_INTERFACES="${RS_VM_VIRTUAL_INTERFACES:-10}"' in common_script
    assert 'RS_VM_VIRTUAL_INTERFACE_PREFIX="${RS_VM_VIRTUAL_INTERFACE_PREFIX:-rs1g}"' in common_script
    assert 'RS_VM_VIRTUAL_INTERFACE_RATE="${RS_VM_VIRTUAL_INTERFACE_RATE:-1gbit}"' in common_script
    assert 'mkdir -p "$(dirname "${RS_VM_ARCHIVE}")"' in common_script
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
    assert "ROUTERSHELL_INSTALL_VM_TOOLS=false" in test_install_script
    assert "source '${RS_VM_REPO_DIR}/.env'" in test_install_script
    assert "source /etc/routershell/routershell.env" in test_install_script
    assert "Interface().get_os_network_interfaces()" in test_install_script
    assert "Missing RouterShell VM interfaces" in test_install_script


def test_vm_cleanup_is_scoped_to_routershell_instances() -> None:
    cleanup_script = (VM_TOOLS / "multipass-cleanup.sh").read_text()

    assert "multipass list --format csv" in cleanup_script
    assert "$1 ~ /^routershell-/" in cleanup_script
    assert '--dry-run' in cleanup_script
    assert "multipass delete" in cleanup_script
    assert "multipass purge" in cleanup_script


def test_vm_readme_documents_manual_shell_workflow() -> None:
    vm_readme = (VM_TOOLS / "README.md").read_text()

    assert "## Manual RouterShell Testing" in vm_readme
    assert "tools/vm/multipass-create.sh" in vm_readme
    assert "tools/vm/multipass-test-install.sh --development" in vm_readme
    assert "tools/vm/multipass-shell.sh" in vm_readme
    assert "routershell" in vm_readme
    assert "rs1g0" in vm_readme
    assert "rs1g9" in vm_readme
