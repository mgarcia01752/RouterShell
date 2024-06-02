
import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.config.interface.interface_config import InterfaceConfig
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.interface import Interface
from lib.system.system_config import SystemConfig

class ConfigCmd(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CONFIGURE_CMD)
               
    def configcmd_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_network_interfaces())         
    def configcmd_interface(self, args: List=None) -> bool:
        self.log.debug(f'configcmd_interface -> {args}')
        InterfaceConfig(ifName=args[0]).start()        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()
    def configcmd_hostname(self, args: List=None) -> bool:

        self.log.debug(f"configcmd_hostname() -> args: {args}")

        if SystemConfig().set_hostname(args[0]):
            print(f"Error: Failed to set the hostname: {args[0]}.")
            return STATUS_NOK
                
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['if', 'if-alias'])
    def configcmd_rename(self, args: List) -> bool:

        if len(args) != 4:
            print('missing arguments') 
        
        self.log.debug(f"configcmd_rename() -> args: {args}")

        if args[0] == 'if':
            self.log.debug(f"configcmd_rename() -> if")
            
            if len(args) == 4:
                self.log.debug(f"configcmd_rename() -> args-parts: {args}")
                Interface().rename_interface(args[1], args[3])

            else:
                print(f"Invalid command: rename {args}")
                
        return STATUS_OK
   