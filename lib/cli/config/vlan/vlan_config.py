import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.command_class_interface import CmdPrompt
from lib.common.constants import STATUS_NOK
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.network_manager.network_interfaces.vlan.vlan_interface import VlanMangement

class VlanConfig(CmdPrompt):

    def __init__(self, vlan_id: int, negate: bool=False) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=True, exec_mode=ExecMode.CONFIG_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_MGT)
        self._vlan_mgt = VlanMangement(vlan_id)
        self._vlan_id = vlan_id
        self.log.debug(f'VlanConfig Started - VlanID: {vlan_id}')
               
    def vlanconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
    
    @CmdPrompt.register_sub_commands()         
    def vlanconfig_name(self, args: List) -> bool:
        self.log.debug(f'vlanconfig_name -> {args}')
        if len(args):
            return self._vlan_mgt.set_name(args[0])
        else:
            self.print_invalid_cmd_response(args)
            return STATUS_NOK
            
    @CmdPrompt.register_sub_commands()         
    def vlanconfig_description(self, args: List) -> bool:
        self.log.debug(f'vlanconfig_description -> {args}')
        if len(args):
            return self._vlan_mgt.set_description(args)
        else:
            self.print_invalid_cmd_response(args)
            return STATUS_NOK