import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_interface_factory import NetInterface

class LoopbackConfig(CmdPrompt):

    def __init__(self, net_interface: NetInterface) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().LOOPBACK_CONFIG)
        self.log.setLevel(logging.INFO)
        
        self.net_interface = net_interface
        self.log.debug(f'Loopback: {net_interface.get_interface_name()}')
               
    def loopbackconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands()         
    def loopbackconfig_description(self, args: List=None) -> bool:
        self.log.debug(f'loopbackconfig_description -> {args}')
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])         
    def loopbackconfig_ip(self, args: List=None, negate: bool=False) -> bool:
        self.log.debug(f'loopbackconfig_ip -> {args}')
        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])         
    def loopbackconfig_ipv6(self, args: List=None, negate: bool=False) -> bool:
        self.log.debug(f'loopbackconfig_ipv6 -> {args}')
        return STATUS_OK

    @CmdPrompt.register_sub_commands()         
    def loopbackconfig_shutdown(self, args: List=None, negate: bool=False) -> bool:
        self.log.debug(f'loopbackconfig_shutdown -> {args}')
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(append_nested_sub_cmds=['ip', 'ipv6', 'shutdown'])         
    def loopbackconfig_no(self, args: List=None) -> bool:
        self.log.debug(f'loopbackconfig_no -> {args}')
        
        if 'ip' in args:
            self.loopbackconfig_ip(args, negate=True)
        elif 'ipv6' in args:
            self.loopbackconfig_ipv6(args, negate=True)
        elif 'shutdown' in args:
            self.loopbackconfig_shutdown(args, negate=True)
        else:
            print(f"Invalid argument: {args}")
        
        return STATUS_OK    