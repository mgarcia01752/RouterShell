
import logging
from typing import List

from lib.cli.base.exec_priv_mode import ExecMode

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.interface import Interface


class IfConfigError(Exception):
    """Custom exception for IfConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'IfConfigError: {self.message}'

class IfConfig(CmdPrompt, Interface):

    def __init__(self, ifName: str, ifType: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().IF_CONFIG)
               
    def ifconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(sub_cmds=['sub-command'])         
    def ifconfig_cmd(self, args: List=None) -> None:
        self.log.debug(f'test_cmd -> {args}')
        return STATUS_OK
        
    @CmdPrompt.register_sub_commands() 
    def ifconfig_description(self, line:str, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_mac(self, args:str) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_ipv6(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()        
    def ifconfig_ip(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_duplex(self, args) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_speed(self, args) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_bridge(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_shutdown(self, args=None, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_switchport(self, args=None, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_wireless(self, args=None, negate:bool=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_no(self, line):
        return STATUS_OK