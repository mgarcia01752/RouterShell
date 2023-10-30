import ipaddress
import json
import logging

from typing import Optional

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.db.dhcp_server_db import DHCPServerDatabase
from lib.network_manager.network_manager import NetworkManager

class InvalidDhcpServer(Exception):
    def __init__(self, message):
        super().__init__(message)

class DHCPServer(NetworkManager, DHCPServerDatabase):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().INTERFACE)
        self.arg = arg