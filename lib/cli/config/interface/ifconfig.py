
import logging
from typing import List

from lib.cli.base.exec_priv_mode import ExecMode

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.phy import State
from lib.network_manager.interface import Interface


class IfConfigError(Exception):
    """Custom exception for IfConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'IfConfigError: {self.message}'

class IfConfig(CmdPrompt, Interface):

    def __init__(self, ifName: str=None, ifType: str=None) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().IF_CONFIG)
        
        self.ifName = ifName
               
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
        """
        This function is used to change the state of an interface to either UP or DOWN.

        Args:
            self: The instance of the class containing this method.
            args (list): A list of arguments. If the list contains only the string 'no', the interface
                        state will be set to DOWN; otherwise, it will be set to UP.

        Returns:
            str: A message indicating the result of the interface state change.
        """
        ifState = State.DOWN
        
        if negate:
            ifState = State.UP

        self.log.debug(f'ifconfig_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.update_shutdown(self.ifName, ifState)
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_switchport(self, args=None, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_wireless(self, args=None, negate:bool=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(sub_cmds=['shutdown'])    
    def ifconfig_no(self, args: List):
        
        self.log.debug(f"ifconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self.ifName}")
            self.ifconfig_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({args})")
            self.ifconfig_bridge(args[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({args})")
            self.ifconfig_ip(args[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({args})")
            self.ifconfig_ipv6(args[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({args})")
            self.ifconfig_switchport(args[1:], negate=True)
        
        elif start_cmd == 'description':
            self.log.debug(f"Remove description -> ({args})")
            self.ifconfig_description(args[1:], negate=True)
        
        else:
            print(f"No negate option for {start_cmd}")
        
        return STATUS_OK