import logging
import json
import cmd2

from tabulate import tabulate

from lib.cli.global.global_operation import GlobalUserCommand
from lib.common.router_prompt import ExecMode, RouterPrompt
from lib.network_manager.phy import State
from lib.common.constants import *

from lib.network_manager.bridge import Bridge
class InvalidBridge(Exception):
    def __init__(self, message):
        super().__init__(message)

class BridgeConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Bridge):
    """Command set for configuring Bridge-Config-Configuration"""

    PROMPT_CMD_ALIAS = "br"
    
    def __init__(self, bridge_ifName: str):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Bridge.__init__(self)
        
        self.log.debug(f"__init__() -> Bridge: {bridge_ifName}")
        if not (self.does_bridge_exist(bridge_ifName, suppress_error=True)):
            self.log.debug(f"__init__() -> Bridge: {bridge_ifName} -> DOES NOT EXISTS, ADDING to DB")
            if self.add_bridge_global(bridge_ifName):
                self.log.error(f"Unable to add ({bridge_ifName}) to DB")
                return STATUS_NOK
                        
        self.bridge_ifName = bridge_ifName
        self.prompt = self.set_prompt()
             
    def do_protocol(self, args=None):
        return 
    
    def do_shutdown(self, args=None, negate=False) -> bool:
        """
        Change the state of a network interface.

        :param args: Additional arguments (optional).
        :param negate: If True, set the state to UP; otherwise, set it to DOWN.
        :return: True if the interface state was successfully changed, False otherwise.
        """
        self.log.debug(f"do_shutdown() -> Bridge: {self.bridge_ifName} -> negate: {negate}")
        
        state = State.DOWN
        
        if negate:
            state = State.UP
        
        return Bridge().set_interface_state(self.bridge_ifName, state)
        
    def complete_no(self, text, line, begidx, endidx):
        completions = ['shutdown', 'name', 'protocol']
        return [comp for comp in completions if comp.startswith(text)]
          
    def do_no(self, line):    
        self.log.debug(f"do_no() -> Line -> {line}")
        
        parts = line.strip().split()
        start_cmd = parts[0]
        
        self.log.debug(f"do_no() -> Start-CMD -> {start_cmd}")        
        
        if start_cmd == 'shutdown':
            self.log.debug(f"Enable interface -> {self.bridge_ifName}")
            self.do_shutdown(None, negate=True)
    