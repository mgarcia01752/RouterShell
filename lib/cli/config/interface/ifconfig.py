
import logging
from typing import List

from lib.cli.base.exec_priv_mode import ExecMode

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.interface import Interface

class IfConfig(CmdPrompt,Interface):

    def __init__(self, args: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().TEST_DEFAULT)
               
    def ifconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        pass
    
    @CmdPrompt.register_sub_commands(sub_cmds=['sub-command'])         
    def ifconfig_cmd(self, args: List=None) -> None:
        self.log.debug(f'test_cmd -> {args}')
        pass
        
    @CmdPrompt.register_sub_commands() 
    def ifconfig_description(self, line:str, negate=False):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_mac(self, args:str):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_ipv6(self, args, negate=False):
        pass
    
    @CmdPrompt.register_sub_commands()        
    def ifconfig_ip(self, args, negate=False):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_duplex(self, args):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_speed(self, args):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_bridge(self, args, negate=False):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_shutdown(self, args=None, negate=False):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_switchport(self, args=None, negate=False):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_wireless(self, args=None, negate:bool=False):
        pass
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_no(self, line):
        pass