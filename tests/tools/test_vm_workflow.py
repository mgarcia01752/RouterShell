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
