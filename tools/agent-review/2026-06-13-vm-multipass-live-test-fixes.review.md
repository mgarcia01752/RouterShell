### Summary
Live Multipass testing exposed snap confinement and local-state leakage issues in the VM workflow. The VM archive now uses a snap-readable host path, excludes local `.env` and `.routershell` runtime state, loads the VM env before direct verification imports, and skips nested Multipass installation inside the guest development install.

### Modified Files
- install/install.sh
- tools/vm/multipass-common.sh
- tools/vm/multipass-test-install.sh
- tools/vm/README.md
- tests/install/test_install_env.py
- tests/tools/test_vm_workflow.py

### Commands Executed And Results
- `tools/vm/multipass-test-install.sh --development` → initially failed because Multipass snap could not read `/tmp/routershell-vm-test.tar.gz`
- `tools/vm/multipass-test-install.sh --development` → then failed because Multipass snap could not read hidden `$HOME/.cache/...` archive path
- `tools/vm/multipass-test-install.sh --development` → then stalled installing nested Multipass inside the guest; process was stopped and skip support was added
- `tools/vm/multipass-test-install.sh --development` → then failed because archived host `.env` pointed the VM DB path at `/home/dev01/Projects/RouterShell`
- `tools/vm/multipass-test-install.sh --development` → pass, VM install and interface discovery verification completed cleanly
- `/opt/routershell/venv/bin/python -m pytest tests/install/test_install_env.py tests/tools/test_vm_workflow.py -q` → pass, 13 passed
- `/opt/routershell/venv/bin/python -m pytest -q` → pass, 36 passed
- `/opt/routershell/venv/bin/python -m ruff check .` → pass
- `bash -n install/install.sh tools/vm/multipass-common.sh tools/vm/multipass-create.sh tools/vm/multipass-test-install.sh` → pass

### Tests
- `pytest` → pass, 36 passed
- `ruff` → pass, all checks passed
- Live Multipass VM install test → pass with `tools/vm/multipass-test-install.sh --development`

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

install_runtime_package() {
  install -d -m 0755 "${INSTALL_ROOT}"
  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/python" -m pip install --upgrade pip

  if [[ "${DEVELOPMENT_INSTALL}" == "true" ]]; then
    "${VENV_DIR}/bin/python" -m pip install -e "${PROJECT_ROOT}[dev]"
  else
    "${VENV_DIR}/bin/python" -m pip install "${PROJECT_ROOT}"
  fi
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
    if [[ "${DEVELOPMENT_INSTALL}" == "true" ]]; then
      log "Installing RouterShell in development mode."
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

# FILE: tools/vm/multipass-common.sh
#!/usr/bin/env bash
set -euo pipefail

RS_VM_NAME="${RS_VM_NAME:-routershell-install-test}"
RS_VM_IMAGE="${RS_VM_IMAGE:-24.04}"
RS_VM_CPUS="${RS_VM_CPUS:-2}"
RS_VM_MEMORY="${RS_VM_MEMORY:-2G}"
RS_VM_DISK="${RS_VM_DISK:-12G}"
RS_VM_ARCHIVE="${RS_VM_ARCHIVE:-${HOME}/routershell-vm-test.tar.gz}"
RS_VM_REPO_DIR="${RS_VM_REPO_DIR:-/tmp/RouterShell}"
RS_VM_VIRTUAL_INTERFACES="${RS_VM_VIRTUAL_INTERFACES:-10}"
RS_VM_VIRTUAL_INTERFACE_PREFIX="${RS_VM_VIRTUAL_INTERFACE_PREFIX:-rs1g}"
RS_VM_VIRTUAL_INTERFACE_RATE="${RS_VM_VIRTUAL_INTERFACE_RATE:-1gbit}"

rs_vm_log() {
  echo "[rs-vm] $*"
}

rs_vm_die() {
  echo "[rs-vm] ERROR: $*" >&2
  exit 1
}

rs_vm_require_multipass() {
  if ! command -v multipass >/dev/null 2>&1; then
    rs_vm_die "multipass is required. Install Multipass before running VM tests."
  fi
}

rs_vm_repo_root() {
  git rev-parse --show-toplevel
}

rs_vm_exists() {
  multipass info "${RS_VM_NAME}" >/dev/null 2>&1
}

rs_vm_require_exists() {
  if ! rs_vm_exists; then
    rs_vm_die "VM '${RS_VM_NAME}' does not exist. Run tools/vm/multipass-create.sh first."
  fi
}

rs_vm_create_archive() {
  local repo_root
  repo_root="$(rs_vm_repo_root)"

  rs_vm_log "Creating repository archive: ${RS_VM_ARCHIVE}"
  mkdir -p "$(dirname "${RS_VM_ARCHIVE}")"
  tar \
    --exclude=".git" \
    --exclude=".env" \
    --exclude=".routershell" \
    --exclude=".venv" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="build" \
    --exclude="dist" \
    -czf "${RS_VM_ARCHIVE}" \
    -C "${repo_root}/.." \
    "$(basename "${repo_root}")"
}

rs_vm_validate_virtual_interface_count() {
  if [[ ! "${RS_VM_VIRTUAL_INTERFACES}" =~ ^[0-9]+$ ]]; then
    rs_vm_die "RS_VM_VIRTUAL_INTERFACES must be a non-negative integer."
  fi
}

rs_vm_configure_virtual_interfaces() {
  rs_vm_validate_virtual_interface_count

  if [[ "${RS_VM_VIRTUAL_INTERFACES}" == "0" ]]; then
    rs_vm_log "Skipping virtual network interface setup."
    return 0
  fi

  rs_vm_log "Configuring ${RS_VM_VIRTUAL_INTERFACES} virtual ${RS_VM_VIRTUAL_INTERFACE_RATE} interfaces."
  multipass exec "${RS_VM_NAME}" -- sudo bash -s -- \
    "${RS_VM_VIRTUAL_INTERFACE_PREFIX}" \
    "${RS_VM_VIRTUAL_INTERFACES}" \
    "${RS_VM_VIRTUAL_INTERFACE_RATE}" <<'EOF'
set -euo pipefail

prefix="$1"
count="$2"
rate="$3"

modprobe dummy >/dev/null 2>&1 || true

for index in $(seq 0 $((count - 1))); do
  interface_name="${prefix}${index}"

  if ! ip link show dev "${interface_name}" >/dev/null 2>&1; then
    ip link add name "${interface_name}" type dummy
  fi

  ip link set dev "${interface_name}" mtu 1500
  ip link set dev "${interface_name}" up
  tc qdisc replace dev "${interface_name}" root tbf rate "${rate}" burst 128kb latency 50ms >/dev/null 2>&1 || true
done
EOF
}

rs_vm_verify_virtual_interfaces() {
  rs_vm_validate_virtual_interface_count

  if [[ "${RS_VM_VIRTUAL_INTERFACES}" == "0" ]]; then
    return 0
  fi

  rs_vm_log "Verifying virtual network interfaces."
  multipass exec "${RS_VM_NAME}" -- bash -s -- \
    "${RS_VM_VIRTUAL_INTERFACE_PREFIX}" \
    "${RS_VM_VIRTUAL_INTERFACES}" <<'EOF'
set -euo pipefail

prefix="$1"
count="$2"

for index in $(seq 0 $((count - 1))); do
  ip link show dev "${prefix}${index}" >/dev/null
done
EOF
}

# FILE: tools/vm/multipass-test-install.sh
#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/multipass-common.sh"

SKIP_OS_PACKAGES="${SKIP_OS_PACKAGES:-false}"
DEVELOPMENT_INSTALL="${DEVELOPMENT_INSTALL:-false}"

usage() {
  cat <<'EOF'
Copy the current RouterShell worktree into the Multipass VM and test install it.

Usage:
  multipass-test-install.sh [--development] [--skip-os-packages]

Environment:
  RS_VM_NAME                       VM name. Default: routershell-install-test
  RS_VM_REPO_DIR                   Path inside VM. Default: /tmp/RouterShell
  RS_VM_VIRTUAL_INTERFACES         Virtual interface count. Default: 10
  RS_VM_VIRTUAL_INTERFACE_PREFIX   Interface name prefix. Default: rs1g

By default, the VM test runs the production runtime install path. Use
--development to test editable install mode with development dependencies.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-os-packages)
      SKIP_OS_PACKAGES="true"
      shift
      ;;
    --development)
      DEVELOPMENT_INSTALL="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      rs_vm_die "Unknown argument: $1"
      ;;
  esac
done

rs_vm_require_multipass
rs_vm_require_exists
rs_vm_configure_virtual_interfaces
rs_vm_verify_virtual_interfaces
rs_vm_create_archive

rs_vm_log "Copying archive into VM."
multipass transfer "${RS_VM_ARCHIVE}" "${RS_VM_NAME}:/tmp/routershell-vm-test.tar.gz"

rs_vm_log "Refreshing VM test workspace."
multipass exec "${RS_VM_NAME}" -- bash -lc "rm -rf '${RS_VM_REPO_DIR}' && tar -xzf /tmp/routershell-vm-test.tar.gz -C /tmp"

install_cmd="sudo '${RS_VM_REPO_DIR}/install/install.sh'"
if [[ "${DEVELOPMENT_INSTALL}" == "true" ]]; then
  install_cmd="sudo ROUTERSHELL_INSTALL_VM_TOOLS=false '${RS_VM_REPO_DIR}/install/install.sh' --development"
fi

if [[ "${SKIP_OS_PACKAGES}" == "true" ]]; then
  install_cmd="${install_cmd} --skip-os-packages"
fi

rs_vm_log "Running RouterShell installer inside VM."
multipass exec "${RS_VM_NAME}" -- bash -lc "${install_cmd}"

rs_vm_log "Verifying RouterShell runtime install."
multipass exec "${RS_VM_NAME}" -- bash -lc "
  set -euo pipefail
  test -x /usr/local/bin/routershell
  test -x /usr/local/bin/routershell-factory-reset
  test -x /opt/routershell/venv/bin/python
  sudo test -f /var/lib/routershell/baseline/manifest.json
  set -a
  if [[ -r '${RS_VM_REPO_DIR}/.env' ]]; then
    source '${RS_VM_REPO_DIR}/.env'
  elif [[ -r /etc/routershell/routershell.env ]]; then
    source /etc/routershell/routershell.env
  fi
  set +a
  /opt/routershell/venv/bin/python - <<'PY'
import routershell
from routershell import cli
from routershell.lib.network_manager.network_operations.interface import Interface

assert callable(cli.main)
assert callable(cli.factory_reset)
expected = [f'${RS_VM_VIRTUAL_INTERFACE_PREFIX}{index}' for index in range(${RS_VM_VIRTUAL_INTERFACES})]
interfaces = Interface().get_os_network_interfaces()
missing = [interface for interface in expected if interface not in interfaces]
assert not missing, f'Missing RouterShell VM interfaces: {missing}'
print(f'RouterShell import OK: {routershell.__version__}')
PY
"

rs_vm_log "Install test passed."

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
