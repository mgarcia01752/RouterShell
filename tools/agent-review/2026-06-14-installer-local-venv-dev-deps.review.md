### Summary
Updated the installer so repo-local environment installs use the project `.venv`, install RouterShell editable with development dependencies, and restore sudo-created local build metadata ownership. Installer tests now cover local `.venv` selection, dev dependency installation, production/global runtime installs, and pre/post ownership repair for generated `src/*.egg-info` metadata.

### Modified Files
- install/install.sh
- tests/install/test_install_env.py

### Commands Executed And Results
- `/opt/routershell/venv/bin/python -m pytest tests/install/test_install_env.py -q` -> pass, 13 passed.
- `/opt/routershell/venv/bin/python -m ruff check tests/install/test_install_env.py` -> pass, all checks passed.
- `bash -n install/install.sh install/uninstall.sh` -> pass.
- `sudo -n chown -R "$(id -u):$(id -g)" src/routershell.egg-info` -> failed, sudo password required in this environment.
- `/opt/routershell/venv/bin/python -m pytest -q` -> pass, 47 passed.
- `/opt/routershell/venv/bin/python -m ruff check .` -> pass, all checks passed.
- `bash -n tools/vm/*.sh install/install.sh install/uninstall.sh` -> pass.

### Tests
- `pytest` -> pass, 47 passed.
- `ruff` -> pass, all checks passed.
- `bash -n` -> pass for VM scripts, install script, and uninstall script.

### Notes / Warnings
- `src/routershell.egg-info` is currently root-owned from the earlier sudo install; this environment could not repair it because sudo requires a password.
- The updated installer repairs existing local `src/*.egg-info` ownership before and after editable install when `SUDO_UID` and `SUDO_GID` are available.
- `pyproject.toml` remains modified from the earlier failed release bump and is intentionally not included in this review bundle.

### Remaining TODOs / Follow-Ups
- Run `sudo chown -R "$(id -u):$(id -g)" src/routershell.egg-info` once locally, or rerun the updated local installer, before retrying `.venv/bin/python -m build`.

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

restore_local_project_ownership() {
  local egg_info_dir

  if [[ "${VENV_DIR}" != "${LOCAL_VENV_DIR}" ]]; then
    return
  fi

  if [[ -z "${SUDO_UID:-}" || -z "${SUDO_GID:-}" ]]; then
    return
  fi

  chown -R "${SUDO_UID}:${SUDO_GID}" "${VENV_DIR}"

  for egg_info_dir in "${PROJECT_ROOT}"/src/*.egg-info; do
    [[ -e "${egg_info_dir}" ]] || continue
    chown -R "${SUDO_UID}:${SUDO_GID}" "${egg_info_dir}"
  done
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
  restore_local_project_ownership

  if [[ "${install_dev_dependencies}" == "true" ]]; then
    "${VENV_DIR}/bin/python" -m pip install -e "${PROJECT_ROOT}[dev]"
  else
    "${VENV_DIR}/bin/python" -m pip install "${PROJECT_ROOT}"
  fi

  restore_local_project_ownership
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
