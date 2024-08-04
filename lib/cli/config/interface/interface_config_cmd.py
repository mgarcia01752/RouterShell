import logging
from typing import List
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.interface.interface_config import InterfaceConfig
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory
from lib.network_manager.network_operations.interface import Interface

class InterfaceConfigCmdError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'InterfaceConfigCmdError: {self.message}'
   
class InterfaceConfigCmd(ConfigurePrompt):
    def __init__(self, interface_name:List[str]):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ETHERNET_CONFIG_CMD)
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
            net_if = NetInterfaceFactory(interface_name).getNetInterface(interface_name=interface_name)            
        else:
            raise InterfaceConfigCmdError(f'Invalid interface: {interface_name}')
                
        super().__init__(sub_cmd_name=net_if.get_ifType().value)
        
        self.register_top_lvl_cmds(InterfaceConfig(net_interface=net_if))

    def intro(self) -> str:
        return f'Starting Interface Configuration'
                    
    def help(self):
        pass
