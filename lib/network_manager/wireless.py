import logging

from lib.network_manager.network_manager import NetworkManager

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

from lib.common.constants import STATUS_OK, STATUS_NOK


class Wireless(NetworkManager):
    """Command set for showing Wireless-Commands"""

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIRELESS)
        
    def set_ssid(self, ssid:str) -> bool:
        return STATUS_OK