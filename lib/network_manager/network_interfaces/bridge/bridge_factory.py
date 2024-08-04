import logging
from typing import List
from lib.common.constants import STATUS_OK, STATUS_NOK
from lib.network_manager.common.phy import State
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.network_manager.network_interfaces.bridge.bridge_interface import BridgeInterface

class BridgeInterfaceFactory:
    """
    Factory class for creating and managing bridge interface commands.

    Attributes:
        _bridge_config_command_list (List['BridgeInterface']): A list that holds the bridge configuration commands 
        for different bridges. This list is used to store and manage the configuration commands for bridges 
        created by the factory.
        
    Methods:
        __init__(bridge_name: str):
            Initializes the BridgeConfigFactory with the given bridge name and sets up logging.
        
        get_bridge_interface() -> 'BridgeInterface':
            Creates a new BridgeInterface object for the current bridge and adds it to the list of commands.
            Returns the newly created BridgeInterface object.
    """
    
    _bridge_interface_list: List[BridgeInterface] = []
    
    def __init__(self, bridge_name: str):
        """
        Initializes the BridgeConfigFactory with the given bridge name and sets up logging.

        Args:
            bridge_name (str): The name of the bridge for which configuration commands will be created.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().BRIDGE_INTERFACE_FACTORY)        
        self._bridge_name = bridge_name
    
    def destroy_bridge(self) -> bool:
        """
        Destroy the bridge associated with the current object.

        This method iterates through the list of bridge configuration commands and 
        destroys the bridge if it matches the current bridge name.

        Returns:
            bool: STATUS_OK if the bridge was successfully destroyed, STATUS_NOK otherwise.
        """
        if BridgeInterfaceFactory._bridge_interface_list:
            for bcc in BridgeInterfaceFactory._bridge_interface_list:
                if self._bridge_name == bcc.get_bridge_name():
                    if bcc.destroy_bridge():
                        self.log.debug(f'Failed to destroy bridge {bcc.get_bridge_name()}')
                        return STATUS_NOK
                    else:
                        self.log.debug(f'Destroyed bridge {bcc.get_bridge_name()}')
                        return STATUS_OK
        return STATUS_NOK

    def get_bridge_interface(self) -> 'BridgeInterface':
        """
        Creates a new BridgeInterface object for the current bridge and adds it to the list of commands.

        This method initializes a new BridgeInterface object with the bridge name and appends it to 
        the class-level list of bridge configuration commands.

        Returns:
            BridgeInterface: The newly created BridgeInterface object.
        """
        bcc = BridgeInterface(self._bridge_name)
        BridgeInterfaceFactory._bridge_interface_list.append(bcc)

        if not bcc.does_bridge_exist() and not bcc.create_bridge():
            self.log.debug(f"Bridge {self._bridge_name} created successfully.")
            
        return bcc
    
    def set_shutdown_status_all_bridges(self, shutdown_state: State) -> bool:
        """
        Sets the shutdown status for all bridges managed by the system using the BridgeInterface class.

        This method performs the following actions:
        1. Iterates over each bridge configuration command in the singleton list.
        2. Applies the specified shutdown status to each bridge.
        3. Logs the result of the operation.

        Args:
            shutdown_state (State): The desired shutdown status to set for all bridges. 
                This should be an instance of the `State` enum, such as `State.UP` or `State.DOWN`.

        Returns:
            bool: STATUS_OK if the shutdown status was successfully set for all bridges, STATUS_NOK otherwise.
        """
        if not BridgeInterfaceFactory._bridge_interface_list:
            self.log.error("No BridgeInterface Found")
            return STATUS_NOK
        
        success = STATUS_OK

        for bcc in BridgeInterfaceFactory._bridge_interface_list:
            if not bcc.set_shutdown_status(shutdown_state):
                self.log.error(f"Failed to set bridge {bcc._bridge_name} to {shutdown_state}")
                success = STATUS_NOK

        return success
