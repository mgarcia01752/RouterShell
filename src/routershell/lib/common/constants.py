import os
from enum import Enum, auto
from pathlib import Path

from routershell.lib.common.types import InterfaceName, StatusResult

STATUS_OK = StatusResult(False)
STATUS_NOK = StatusResult(True)

ROUTER_CONFIG_DIR = 'config'
ROUTER_CONFIG = os.path.join(ROUTER_CONFIG_DIR, 'startup-config.cfg')

ROUTERSHELL_STATE_DIR = Path("/var/lib/routershell")
ROUTERSHELL_RUNTIME_LOG_DIR = Path("/tmp/log")
ROUTERSHELL_DEFAULT_LOG_FILE = ROUTERSHELL_RUNTIME_LOG_DIR / "routershell.log"
ROUTERSHELL_COMMAND_LOG_FILE = ROUTERSHELL_RUNTIME_LOG_DIR / "routershell-command.log"
ROUTERSHELL_SYSCTL_LOG_FILE = ROUTERSHELL_RUNTIME_LOG_DIR / "sysctl.log"

SYSTEMD_RUNTIME_DIR = Path("/run/systemd/system")
SYSV_INIT_DIR = Path("/etc/init")
ETC_HOSTNAME_FILE = Path("/etc/hostname")
SYSV_MESSAGES_LOG_FILE = Path("/var/log/messages")
SYSV_BOOT_LOG_FILE = Path("/var/log/boot")

DNSMASQ_CONFIG_DIR = Path("/etc/dnsmasq.d")
DNSMASQ_LEASE_FILE_PATH = Path("/var/lib/misc/dnsmasq.leases")
HOSTAPD_CONF_DIR = Path("/etc/hostapd")
HOSTAPD_CONF_FILE = "hostapd.conf"
TELNET_SYSV_CONFIG_FILE = Path("/etc/xinetd.d/telnet")

PROC_SYS_NET_IPV4_CONF_DIR = Path("/proc/sys/net/ipv4/conf")

ROUTER_SHELL_DB = 'routershell.db'
ROUTER_SHELL_DB_FILE_ENV = 'ROUTERSHELL_DB_FILE'
ROUTER_SHELL_PROJECT_ROOT_ENV = 'ROUTERSHELL_PROJECT_ROOT'
ROUTER_SHELL_SQL_STARTUP = 'db_schema.sql'


def proc_ipv4_conf_path(interface_name: InterfaceName, setting_name: str) -> Path:
    return PROC_SYS_NET_IPV4_CONF_DIR / interface_name / setting_name

class Status(Enum):
    ENABLE = auto()
    DISABLE = auto()
