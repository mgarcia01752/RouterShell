import logging
from typing import List
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.ethernet.ethernet_config import EthernetConfig
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory
from lib.network_manager.network_operations.interface import Interface

class EthernetConfigCmdError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'EthernetConfigCmdError: {self.message}'
   
class EthernetConfigCmd(ConfigurePrompt):
    def __init__(self, ethernet_name:List[str]):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ETHERNET_CONFIG_CMD)
        ethernet_name = ethernet_name[0]
        self.log.debug(f'EthernetConfigCmd() -> Interface: {ethernet_name}')
        
        if Interface().db_lookup_interface_exists(ethernet_name):
            net_if = NetInterfaceFactory(ethernet_name, InterfaceType.ETHERNET).getNetInterface()            
        else:
            raise EthernetConfigCmdError(f'Invalid interface: {ethernet_name}')
                
        super().__init__(sub_cmd_name=net_if.get_ifType().value)
        
        self.register_top_lvl_cmds(EthernetConfig(net_interface=net_if))

    def intro(self) -> str:
        return f'Starting Ethernet Configuration'
                    
    def help(self):
        pass
