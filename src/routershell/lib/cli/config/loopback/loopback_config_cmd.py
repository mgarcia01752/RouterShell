import logging

from routershell.lib.cli.config.configure_prompt import ConfigurePrompt
from routershell.lib.cli.config.loopback.loopback_config import LoopbackConfig
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.network_manager.common.interface import InterfaceType
from routershell.lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory


class LoopbackConfigCmdError(Exception):
    """Custom exception for LoopbackConfigCmd errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'LoopbackConfigError: {self.message}'
   
class LoopbackConfigCmd(ConfigurePrompt):

    def __init__(self, loopback_name:list[str] = None):
        super().__init__(sub_cmd_name=InterfaceType.LOOPBACK.value)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().LOOPBACK_CONFIG_CMD)
        self.log.debug(f'LoopbackConfigCmd() -> Starting LoopbackConfig -> {loopback_name}')
        loopback_name = loopback_name[0]
        
        lio = NetInterfaceFactory(loopback_name, InterfaceType.LOOPBACK).getNetInterface(loopback_name)
        self.register_top_lvl_cmds(LoopbackConfig(loopback_interface_obj=lio))  
        
    def intro(self) -> str:
        return 'Starting Loopback Config....'
                    
    def help(self):
        pass
