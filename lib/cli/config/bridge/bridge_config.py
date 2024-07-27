
import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.phy import State
from lib.network_manager.network_operations.bridge.bridge import Bridge

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

class BridgeConfig(CmdPrompt, Bridge):
    """BridgeConfig class for managing network bridges via command-line interface."""

    def __init__(self, bridge_name: str, negate:bool=False) -> None:
        """Initialize the BridgeConfig class.
        
        Args:
            bridge_name (str): The name of the bridge to be managed.
        """
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        Bridge().__init__()

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG)
        self.bridge_name = bridge_name

        if self.add_bridge_global(bridge_name):
            self.log.error("Unable to add (%s) to DB", bridge_name)
               
    def bridgeconfig_help(self, args: List=None) -> None:
        """Display help for all available bridge control commands.
        
        Args:
            args (List, optional): Additional arguments (not used).
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands()         
    def bridgeconfig_protocol(self, args: List=None, negate: bool=False) -> bool:
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
    def bridgeconfig_stp(self, args: List=None, negate: bool=False) -> bool:
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
    def bridgeconfig_shutdown(self, args: List = None, negate: bool = False) -> bool:
        """
        Shutdown or bring up the bridge interface.
        
        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, shuts down the bridge interface. If False, brings up the bridge interface. Defaults to False.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        
        self.log.info(f"bridgeconfig_shutdown() -> Bridge: {self.bridge_name} -> current-state: {Bridge().get_bridge_state(self.bridge_name).value} -> negate: {negate}")

        state = State.UP if negate else State.DOWN

        if self.shutdown_cmd(self.bridge_name, state):
            print(f"Error: unable to set bridge: {self.bridge_name}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def bridgeconfig_ip(self, args: List[str], negate: bool = False) -> bool:
        
        return STATUS_OK
        
      
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'stp', 'protocol'])
    def bridgeconfig_no(self, args: List) -> bool:
        """Negate commands like shutdown, stp, or protocol for the bridge.
        
        Args:
            args (List): List of arguments for the command.
        
        Returns:
            bool: Status of the command execution.
        """
        self.log.info(f"bridgeconfig_no() -> {args}")
        
        negate:bool = True
                
        if 'shutdown' in args:
            self.log.debug("up/down interface -> %s", self.bridge_name)
            self.bridgeconfig_shutdown(None, negate)
        
        elif 'stp' in args:
            self.log.debug(f"Remove stp -> {args}")
            self.bridgeconfig_stp(args[1:], negate)

        elif 'protocol' in args:
            self.log.debug(f"Remove protocol -> {args}")
            self.bridgeconfig_protocol(args[1:], negate)
        
        else:
            print(f'error: invalid command: {args}')
            return STATUS_NOK
        
        return STATUS_OK
