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
SYSTEM_ENV_FILE={system_env}
DEVELOPMENT_INSTALL=true
ENV_SCOPE=auto
select_env_file
create_env_file
printf '%s\\n' "${{ACTIVE_ENV_FILE}}"
"""

    result = _run_bash(script)
    local_env = project_root / ".env"

    assert result.stdout.strip().endswith(str(local_env))
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
SYSTEM_ENV_FILE={system_env}
STATE_DIR={tmp_path}/state
DEVELOPMENT_INSTALL=false
ENV_SCOPE=auto
select_env_file
create_env_file
printf '%s\\n' "${{ACTIVE_ENV_FILE}}"
"""

    result = _run_bash(script)

    assert result.stdout.strip().endswith(str(system_env))
    assert system_env.exists()
    assert "ROUTERSHELL_LOG_FILE" in system_env.read_text()
    assert f'ROUTERSHELL_DB_FILE="{tmp_path}/state/routershell.db"' in system_env.read_text()
    assert not (project_root / ".env").exists()


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
