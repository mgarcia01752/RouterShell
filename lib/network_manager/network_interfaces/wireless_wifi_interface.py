import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
from lib.network_manager.network_interfaces.network_interface import NetworkInterface

class WirelessWifiInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class WirelessWifiInterface(NetworkInterface):

    def __init__(self, ethernet_name: str):
        super().__init__(interface_name=ethernet_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIRELESS_WIFI_INTERFACE)        
            