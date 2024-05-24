import logging
from typing import List
from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.base.global_cmd_op import Global
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.interface.ifconfig import IfConfig
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class InterfaceConfigError(Exception):
    """Custom exception for InterfaceConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'InterfaceConfigError: {self.message}'
   

class InterfaceConfig(ConfigurePrompt, IfConfig):
    def __init__(self, ifName: str, ifType:str=None):
        """
        Initialize the InterfaceConfig class.

        Args:
            interface_name (str): The name of the interface to configure.

        Raises:
            InterfaceConfigError: If the interface_name is empty.
        """
        super().__init__(sub_cmd_name='if')

        if not ifName:
            raise InterfaceConfigError("InterfaceConfig interface_name cannot be empty.")

        self.ifName = ifName
        IfConfig().__init__(ifName=ifName)
        
        self.register_top_lvl_cmds(IfConfig())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().INTERFACE_CONFIG)
    
    def intro(self) -> str:
        return f'Starting Interface Configuration'
                    
    def help(self):
        pass
