
import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.command_class_interface import CmdPrompt
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLGS
from lib.network_manager.common.phy import State
from lib.network_manager.network_interfaces.bridge.bridge_factory import BridgeInterface, BridgeInterfaceFactory
from lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE
from lib.network_manager.network_operations.bridge import Bridge


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

class BridgeConfig(CmdPrompt):
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
        self._bridge_name = bridge_name
        self._bridge_config_cmd : BridgeInterface = BridgeInterfaceFactory(self._bridge_name).get_bridge_interface()
               
    def bridgeconfig_help(self, args: List[str]=None) -> None:
        """Display help for all available bridge control commands.
        
        Args:
            args (List, optional): Additional arguments (not used).
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['management'])
    def bridgeconfig_inet(self, args: List[str] = None, negate: bool = False) -> bool:
        """
        Manage the management IP address of the bridge.

        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, negates the command (removes the management IP).

        Returns:
            bool: Status of the command execution.
        """
        if not args or 'management' not in args:
            print("Error: 'management' keyword is required.")
            return STATUS_NOK

        if len(args) < 2:
            print("Error: Management IP address is required.")
            return STATUS_NOK

        management_ip = args[1]

        if negate:
            management_ip = ""  # Clear the management IP if negate is True

        if self._bridge_config_cmd.set_inet_management(inet=management_ip):
            print(f"Unable to set management IP for bridge {self._bridge_name}")
            return STATUS_NOK

        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def bridgeconfig_description(self, args: List[str] = None, negate: bool = False) -> bool:
        """
        Manage the description of the bridge.

        Args:
            args (List, optional): List of arguments for the description command.
            negate (bool, optional): If True, negates the command (removes the description).

        Returns:
            bool: Status of the command execution.
        """
        description = ""

        if args:
            description = " ".join(args)
        
        if negate:
            description = ""

        if self._bridge_config_cmd.set_description(description):
            print(f"Unable to set description: {description} for bridge {self._bridge_name} ")
            return STATUS_NOK

        return STATUS_OK

    @CmdPrompt.register_sub_commands()         
    def bridgeconfig_protocol(self, args: List[str]=None, negate: bool=False) -> bool:
        """Manage bridge protocol settings.
        
        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, negates the command (removes the protocol).
        
        Returns:
            bool: Status of the command execution.
        """
        print('Not implemented yet')
        return STATUS_OK

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['enable','disable'])
    def bridgeconfig_stp(self, args: List[str] = None, negate: bool = False) -> bool:
        """
        Manage Spanning Tree Protocol (STP) settings for the bridge.
        
        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, negates the command (removes STP).
        
        Returns:
            bool: Status of the command execution.
        """
        if not args:
            print("Missing STP argument")
            return STATUS_NOK
        
        if 'disable' not in args and 'enable' not in args:
            print("Invalid STP option")
            return STATUS_NOK
        
        stp = STP_STATE.STP_ENABLE if 'enable' in args else STP_STATE.STP_DISABLE
        
        if self._bridge_config_cmd.set_stp(stp=stp):
            print(f"Unable to set STP to bridge {self._bridge_name}")
            return STATUS_NOK
        
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def bridgeconfig_shutdown(self, args: List[str] = None, negate: bool = False) -> bool:
        """
        Shutdown or bring up the bridge interface.
        
        Args:
            args (List, optional): List of arguments for the command.
            negate (bool, optional): If True, shuts down the bridge interface. If False, brings up the bridge interface. Defaults to False.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        state = State.UP if negate else State.DOWN
        
        self.log.debug(f"bridgeconfig_shutdown() -> Bridge: {self._bridge_name} -> " + 
                        f"current-state: {Bridge().get_shutdown_status_os(self._bridge_name).value} -> state: {state}")

        if self._bridge_config_cmd.set_shutdown_status(state):
            print(f"Error: unable to set bridge: {self._bridge_name}")
            return STATUS_NOK
        
        return STATUS_OK
      
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['description', 'shutdown'])
    def bridgeconfig_no(self, args: List[str]) -> bool:
        """Negate commands like description, shutdown, stp, or protocol for the bridge.
        
        Args:
            args (List): List of arguments for the command.
        
        Returns:
            bool: Status of the command execution.
        """
        self.log.debug(f"bridgeconfig_no() -> {args}")
        
        negate:bool = True
                
        if 'shutdown' in args:
            self.log.debug(f'up/down interface -> {self._bridge_name}')
            self.bridgeconfig_shutdown(None, negate)
               
        elif 'description' in args:
            self.log.debug(f"Remove protocol -> {args}")
            self.bridgeconfig_description(None, negate)        
        
        else:
            print(f'error: invalid command: {args}')
            return STATUS_NOK
        
        return STATUS_OK
