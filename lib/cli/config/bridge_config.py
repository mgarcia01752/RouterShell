import logging
import cmd2

from tabulate import tabulate
from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

from lib.cli.common.router_prompt import ExecMode, RouterPrompt
from lib.network_manager.network_manager import InterfaceType
from lib.network_manager.common.phy import State
from lib.common.constants import *

from lib.network_manager.bridge import Bridge
class InvalidBridge(Exception):
    def __init__(self, message):
        super().__init__(message)

class BridgeConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Bridge):
    """Command set for configuring Bridge-Config-Configuration"""

    PROMPT_CMD_ALIAS = InterfaceType.BRIDGE.value
    
    def __init__(self, bridge_name: str):
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug(f"__init__() -> Bridge: {bridge_name}")
        self.log.setLevel(RSLGS().BRIDGE_CONFIG)
        self.debug = CGS().DEBUG_BRIDGE_CONFIG
        
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Bridge.__init__(self)
        
        self.bridge_ifName = bridge_name
        
        if self.add_bridge_global(bridge_name):
            self.log.debug(f"Unable to add ({bridge_name}) to DB")
                        
        self.prompt = self.set_prompt()
             
    def do_protocol(self, args=None):
        return 
    
    def do_shutdown(self, args=None, negate=False) -> bool:
        """
        Change the state of a network interface.

        :param args: Additional arguments (optional).
        :param negate: If True, set the state to UP; otherwise, set it to DOWN.
        :return: STATUS_OK if the interface state was successfully changed, STATUS_OK otherwise.
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
    