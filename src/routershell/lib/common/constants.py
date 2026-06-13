import os
from enum import Enum, auto

from routershell.lib.common.types import StatusResult

STATUS_OK = StatusResult(False)
STATUS_NOK = StatusResult(True)

ROUTER_CONFIG_DIR = 'config'
ROUTER_CONFIG = os.path.join(ROUTER_CONFIG_DIR, 'startup-config.cfg')

DNSMASQ_LEASE_FILE_PATH = "/var/lib/misc/dnsmasq.leases"

HOSTAPD_CONF_DIR = "/etc/hostapd"
HOSTAPD_CONF_FILE="hostapd.conf"

ROUTER_SHELL_DB = 'routershell.db'
ROUTER_SHELL_DB_FILE_ENV = 'ROUTERSHELL_DB_FILE'
ROUTER_SHELL_PROJECT_ROOT_ENV = 'ROUTERSHELL_PROJECT_ROOT'
ROUTER_SHELL_SQL_STARTUP = 'db_schema.sql'

class Status(Enum):
    ENABLE = auto()
    DISABLE = auto()
