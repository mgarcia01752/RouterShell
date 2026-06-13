#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT="${ROUTERSHELL_INSTALL_ROOT:-/opt/routershell}"
BIN_DIR="${ROUTERSHELL_BIN_DIR:-/usr/local/bin}"
STATE_DIR="${ROUTERSHELL_STATE_DIR:-/var/lib/routershell}"
BASELINE_DIR="${STATE_DIR}/baseline"
VENV_DIR="${INSTALL_ROOT}/venv"
SKIP_OS_PACKAGES="false"
SKIP_PYTHON_PACKAGE="false"
DEVELOPMENT_INSTALL="false"
SKIP_SNAPSHOT="false"
FORCE_SNAPSHOT="false"
SNAPSHOT_ONLY="false"

usage() {
  cat <<'EOF'
Install RouterShell on a general-purpose Linux host.

Usage:
  install.sh [--install-root PATH] [--bin-dir PATH] [--development] [--snapshot-only] [--force-snapshot] [--no-snapshot] [--skip-os-packages] [--skip-python-package]

Options:
  --install-root       Runtime install root. Default: /opt/routershell
  --bin-dir            Directory for command launchers. Default: /usr/local/bin
  --development        Install RouterShell editable with development dependencies.
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
exec "${VENV_DIR}/bin/routershell" "\$@"
EOF

  cat > "${BIN_DIR}/routershell-factory-reset" <<EOF
#!/usr/bin/env bash
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

  warn_port_53_owner
  prepare_runtime_dirs

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

main
