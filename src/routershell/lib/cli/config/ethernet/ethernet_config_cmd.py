import logging

from routershell.lib.cli.config.configure_prompt import ConfigurePrompt
from routershell.lib.cli.config.ethernet.ethernet_config import EthernetConfig
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory
from routershell.lib.network_manager.network_operations.interface import Interface


class EthernetConfigCmdError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'EthernetConfigCmdError: {self.message}'
   
class EthernetConfigCmd(ConfigurePrompt):
    def __init__(self, eth_name:list[str]):
        super().__init__(sub_cmd_name=InterfaceType.ETHERNET.value) 
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().ETHERNET_CONFIG_CMD)
        eth_name = eth_name[0]
        self.log.debug(f'EthernetConfigCmd() -> Interface: {eth_name}')

        if Interface().db_lookup_interface_exists(eth_name):
            eth_if = NetInterfaceFactory(eth_name, InterfaceType.ETHERNET).getNetInterface(interface_name=eth_name)            
        else:
            raise EthernetConfigCmdError(f'Invalid interface: {eth_name}')
                
        self.register_top_lvl_cmds(EthernetConfig(eth_interface_obj=eth_if))

    def intro(self) -> str:
        return 'Starting Ethernet Configuration'
                    
    def help(self):
        pass
