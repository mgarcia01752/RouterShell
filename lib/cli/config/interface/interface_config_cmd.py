import logging
from typing import List
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.interface.interface_config import InterfaceConfig
from lib.common.common import Common
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.interface import Interface
from lib.network_manager.network_interface_factory import CreateLoopBackNetInterface, NetInterface, NetInterfaceFactory

class InterfaceConfigCmdError(Exception):
    """Custom exception for InterfaceConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'InterfaceConfigCmdError: {self.message}'
   
class InterfaceConfigCmd(ConfigurePrompt):
    def __init__(self, interface_name:List[str]):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().INTERFACE_CONFIG_CMD)
        interface_name = interface_name[0]
        self.log.debug(f'InterfaceConfigCmd() -> Interface: {interface_name}')
        
        ''' Supported InterfaceType()
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
        '''
        
        if Interface().db_lookup_interface_exists(interface_name):
            net_if = NetInterfaceFactory(interface_name).getNetInterface()            
        else:
            raise InterfaceConfigCmdError(f'Invalid interface: {interface_name}')
                
        super().__init__(sub_cmd_name=net_if.get_ifType().value)
        
        self.register_top_lvl_cmds(InterfaceConfig(net_interface=net_if))

    def intro(self) -> str:
        return f'Starting Interface Configuration'
                    
    def help(self):
        pass
