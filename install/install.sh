#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT="${ROUTERSHELL_INSTALL_ROOT:-/opt/routershell}"
BIN_DIR="${ROUTERSHELL_BIN_DIR:-/usr/local/bin}"
VENV_DIR="${INSTALL_ROOT}/venv"
SKIP_OS_PACKAGES="false"
SKIP_PYTHON_PACKAGE="false"
DEVELOPMENT_INSTALL="false"

usage() {
  cat <<'EOF'
Install RouterShell on a general-purpose Linux host.

Usage:
  install.sh [--install-root PATH] [--bin-dir PATH] [--development] [--skip-os-packages] [--skip-python-package]

Options:
  --install-root       Runtime install root. Default: /opt/routershell
  --bin-dir            Directory for command launchers. Default: /usr/local/bin
  --development        Install RouterShell editable with development dependencies.
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
  load_os_release
  reject_embedded_targets
  detect_package_manager

  log "Detected ${OS_NAME} with package manager: ${PACKAGE_MANAGER}"

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
