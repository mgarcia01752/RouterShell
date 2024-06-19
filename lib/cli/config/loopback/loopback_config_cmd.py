import logging
from typing import List
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.loopback.loopback_config import LoopbackConfig
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.network_interfaces.create_loopback_net_interface import CreateLoopBackNetInterface

class LoopbackConfigCmdError(Exception):
    """Custom exception for LoopbackConfigCmd errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'LoopbackConfigError: {self.message}'
   
class LoopbackConfigCmd(ConfigurePrompt):

    def __init__(self, loopback_name:List[str] = None):
        super().__init__(sub_cmd_name=InterfaceType.LOOPBACK.value)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().LOOPBACK_CONFIG_CMD)
        self.log.info(f'LoopbackConfigCmd() -> Starting LoopbackConfig -> {loopback_name}')
        loopback_name = loopback_name[0]

        #Loopbacks are dynamically created except for the initial linux local loopback: lo
        lio = CreateLoopBackNetInterface(loopback_name).getLoopbackInterface(loopback_name)
        self.register_top_lvl_cmds(LoopbackConfig(loopback_interface_obj=lio))  
        
    def intro(self) -> str:
        return f'Starting Loopback Config....'
                    
    def help(self):
        pass
