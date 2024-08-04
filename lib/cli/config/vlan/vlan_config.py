import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.command_class_interface import CmdPrompt
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.network_manager.network_operations.vlan import Vlan

class VlanConfig(CmdPrompt):

    def __init__(self, vlan_id: int) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_CONFIG)
        self._vlan_id = vlan_id
        self._vlan_obj = Vlan()
               
    def vlanconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
    
    @CmdPrompt.register_sub_commands()         
    def vlanconfig_name(self, args: List=None) -> None:
        self.log.debug(f'vlanconfig_name -> {args}')
        return STATUS_OK
    
     @CmdPrompt.register_sub_commands()         
    def vlanconfig_description(self, args: List=None) -> None:
        self.log.debug(f'vlanconfig_description -> {args}')
        return STATUS_OK