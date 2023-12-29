STATUS_OK = False
STATUS_NOK = True

import os

ROUTER_CONFIG_DIR = 'config'
ROUTER_CONFIG = os.path.join(ROUTER_CONFIG_DIR, 'startup-config.cfg')

DNSMASQ_LEASE_FILE_PATH = "/var/lib/misc/dnsmasq.leases"

HOSTAPD_CONF_DIR = "/etc/hostapd"
HOSTAPD_CONF_FILE="hostapd.conf"

ROUTER_SHELL_DB = 'routershell.db'
ROUTER_SHELL_SQL_STARTUP = 'db_schema.sql'

