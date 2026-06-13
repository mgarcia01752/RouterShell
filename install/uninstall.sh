#!/usr/bin/env bash
set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
INSTALL_ROOT="${ROUTERSHELL_INSTALL_ROOT:-/opt/routershell}"
BIN_DIR="${ROUTERSHELL_BIN_DIR:-/usr/local/bin}"
REMOVE_RUNTIME_LOGS="false"

usage() {
  cat <<'EOF'
Uninstall RouterShell from a general-purpose Linux host.

Usage:
  uninstall.sh [--install-root PATH] [--bin-dir PATH] [--remove-runtime-logs]

Options:
  --install-root        Runtime install root. Default: /opt/routershell
  --bin-dir             Directory containing command launchers. Default: /usr/local/bin
  --remove-runtime-logs Remove /tmp/log RouterShell runtime logs.
  -h, --help            Show this help.

This script removes RouterShell's runtime virtual environment and launchers.
It does not remove shared operating-system packages such as Python, iproute,
dnsmasq, hostapd, or lshw.
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
      shift
      ;;
    --bin-dir)
      shift
      [[ -n "${1:-}" ]] || die "--bin-dir requires a path."
      BIN_DIR="$1"
      shift
      ;;
    --remove-runtime-logs)
      REMOVE_RUNTIME_LOGS="true"
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
    die "Run this uninstaller as root, for example: sudo ./install/uninstall.sh"
  fi
}

guard_install_root() {
  case "${INSTALL_ROOT}" in
    /|/opt|/usr|/usr/local|/home|/root)
      die "Refusing to remove broad install root: ${INSTALL_ROOT}"
      ;;
  esac
}

remove_launchers() {
  rm -f "${BIN_DIR}/routershell" "${BIN_DIR}/routershell-factory-reset"
}

remove_runtime() {
  guard_install_root
  rm -rf "${INSTALL_ROOT}"
}

remove_runtime_logs() {
  if [[ "${REMOVE_RUNTIME_LOGS}" != "true" ]]; then
    return
  fi

  rm -f /tmp/log/routershell.log /tmp/log/routershell-command.log
}

main() {
  require_root
  remove_launchers
  remove_runtime
  remove_runtime_logs
  log "RouterShell uninstall complete."
}

main
