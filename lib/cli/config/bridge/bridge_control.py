
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
        """Initialize BridgeConfigError with a specific error message.
        
        Args:
            message (str): The error message to be displayed.
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """String representation of the BridgeConfigError.
        
        Returns:
            str: A string describing the error.
        """
        return f'BridgeConfigError: {self.message}'

class BridgeControl(CmdPrompt, Bridge):
    """BridgeControl class for managing network bridges via command-line interface."""

    def __init__(self, bridge_name: str) -> None:
        """Initialize the BridgeControl class.
        
        Args:
            bridge_name (str): The name of the bridge to be managed.
        """
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        Bridge().__init__()

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONTROL)
        self.bridge_name = bridge_name

        if self.add_bridge_global(bridge_name):
            self.log.error("Unable to add (%s) to DB", bridge_name)
               
    def bridgecontrol_help(self, args: List=None) -> None:
        """Display help for all available bridge control commands.
        
        Args:
            args (List, optional): Additional arguments (not used).
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands()         
    def bridgecontrol_protocol(self, args: List=None, negate: bool=False) -> bool:
        """Manage bridge protocol settings.
        
        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, negates the command (removes the protocol).
        
        Returns:
            bool: Status of the command execution.
        """
        print('Not implemented yet')
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def bridgecontrol_stp(self, args: List=None, negate: bool=False) -> bool:
        """Manage Spanning Tree Protocol (STP) settings for the bridge.
        
        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, negates the command (removes STP).
        
        Returns:
            bool: Status of the command execution.
        """
        print('Not implemented yet')
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def bridgecontrol_shutdown(self, args: List=None, negate: bool=False) -> bool:
        """Shutdown or bring up the bridge interface.
        
        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, brings up the bridge interface instead of shutting it down.
        
        Returns:
            bool: Status of the command execution.
        """
        
        self.log.debug("bridgecontrol_shutdown() -> Bridge: %s -> negate: %s", self.bridge_name, negate)
        state = State.DOWN
        if negate:
            state = State.UP
        if self.set_interface_shutdown(self.bridge_name, state):
            print(f'Error: unable to set bridge: {self.bridge_name}')
            return STATUS_NOK
        return STATUS_OK
      
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'stp', 'protocol'])
    def bridgecontrol_no(self, args: List) -> bool:
        """Negate commands like shutdown, stp, or protocol for the bridge.
        
        Args:
            args (List): List of arguments for the command.
        
        Returns:
            bool: Status of the command execution.
        """
        self.log.debug("ifconfig_no() -> Line -> %s", args)

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug("up/down interface -> %s", self.bridge_name)
            self.bridgecontrol_shutdown(None, negate=True)
        
        elif start_cmd == 'stp':
            self.log.debug("Remove stp -> (%s)", args)
            self.bridgecontrol_stp(args[1:], negate=True)

        elif start_cmd == 'protocol':
            self.log.debug("Remove protocol -> (%s)", args)
            self.bridgecontrol_protocol(args[1:], negate=True)
        
        else:
            print(f'error: invalid command: {args}')
            return STATUS_NOK
        
        return STATUS_OK
