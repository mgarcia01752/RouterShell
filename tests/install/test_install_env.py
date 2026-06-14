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


def test_local_runtime_install_restores_generated_metadata_ownership(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    venv_dir = project_root / ".venv"
    egg_info_dir = project_root / "src" / "routershell.egg-info"
    command_log = tmp_path / "commands.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    egg_info_dir.mkdir(parents=True)
    python3 = bin_dir / "python3"
    python3.write_text(
        "#!/usr/bin/env bash\n"
        f"printf 'python3 %s\\n' \"$*\" >> {command_log}\n"
        "if [[ \"$1 $2\" == '-m venv' ]]; then\n"
        "  mkdir -p \"$3/bin\"\n"
        "  cat > \"$3/bin/python\" <<'PYEOF'\n"
        "#!/usr/bin/env bash\n"
        f"printf 'venv-python %s\\n' \"$*\" >> {command_log}\n"
        "PYEOF\n"
        "  chmod +x \"$3/bin/python\"\n"
        "fi\n"
    )
    python3.chmod(0o755)

    script = f"""
export ROUTERSHELL_INSTALL_SH_NO_MAIN=true
export PATH={bin_dir}:$PATH
export SUDO_UID=1000
export SUDO_GID=1000
source install/install.sh
PROJECT_ROOT={project_root}
LOCAL_ENV_FILE="${{PROJECT_ROOT}}/.env"
LOCAL_VENV_DIR="${{PROJECT_ROOT}}/.venv"
ACTIVE_ENV_FILE="${{LOCAL_ENV_FILE}}"
VENV_DIR="${{LOCAL_VENV_DIR}}"
DEVELOPMENT_INSTALL=false
chown() {{
  printf 'chown %s\\n' "$*" >> {command_log}
}}
install_runtime_package
"""

    _run_bash(script)
    log_text = command_log.read_text()

    assert log_text.count(f"chown -R 1000:1000 {venv_dir}") == 2
    assert log_text.count(f"chown -R 1000:1000 {egg_info_dir}") == 2


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
