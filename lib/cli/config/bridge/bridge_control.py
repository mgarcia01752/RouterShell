import argparse
import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.bridge import Bridge
from lib.network_manager.common.phy import State

class BridgeConfigError(Exception):
    """Custom exception for BridgeConfigError errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'BridgeConfigError: {self.message}'

class BridgeControl(CmdPrompt):

    def __init__(self, bridge_name: str) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)

        self.network_bridge = Bridge()

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONTROL)

        self.bridge_name = bridge_name

        if self.network_bridge.add_bridge_global(bridge_name):
            self.log.error(f"Unable to add ({bridge_name}) to DB")
               
    def bridgecontrol_help(self, args: List=None) -> None:
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands()         
    def bridgecontrol_protocol(self, args: List=None, negate: bool=False) -> bool:
        print('Not implemented yet')
        return STATUS_OK

    @CmdPrompt.register_sub_commands()         
    def bridgecontrol_stp(self, args: List=None, negate: bool=False) -> bool:
        print('Not implemented yet')
        return STATUS_OK

    @CmdPrompt.register_sub_commands()         
    def bridgecontrol_shutdown(self, args: List=None, negate: bool=False) -> bool:
        self.log.debug(f"bridgecontrol_shutdown() -> Bridge: {self.bridge_name} -> negate: {negate}")
        
        state = State.DOWN
        
        if negate:
            state = State.UP
        
        if self.network_bridge.set_interface_shutdown(self.bridge_name, state):
            print(f'Error: unable to set bridge: {self.bridge_name}')
            return STATUS_NOK
        
        return STATUS_OK
      
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'stp', 'protocol'])    
    def bridgecontrol_no(self, args: List) -> bool:
        
        self.log.debug(f"ifconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self.ifName}")
            self.ifconfig_shutdown(None, negate=True)
        
        elif start_cmd == 'stp':
            self.log.debug(f"Remove stp -> ({args})")
            self.bridgecontrol_stp(args[1:], negate=True)

        elif start_cmd == 'protocol':
            self.log.debug(f"Remove protocol -> ({args})")
            self.bridgecontrol_protocol(args[1:], negate=True)