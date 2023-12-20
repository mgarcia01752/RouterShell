from enum import Enum
import logging

from lib.common.common import Common
from lib.network_manager.common.phy import PhyServiceLayer
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK

class InterfaceLayerFoundError(Exception):

    def __init__(self, message="Interface Layer error"):
        self.message = message
        super().__init__(self.message)

class InterfaceType(Enum):
    DEFAULT = 'if' 
    PHYSICAL = 'phy'
    ETHERNET = 'eth'
    VLAN = 'vlan'
    LOOPBACK = 'loopback'
    VIRTUAL = 'vir'
    BRIDGE = 'br'
    WIRELESS_WIFI = 'wifi'
    WIRELESS_CELL = 'cell'
    UNKNOWN = 'UNKNOWN'

class InterfaceLayer(PhyServiceLayer):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().INTERFACE)
        
    def get_interface_type(self, interface_name:str) -> InterfaceType:
        return InterfaceType.ETHERNET
        