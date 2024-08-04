import logging
from typing import Optional
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.phy import State
from lib.network_manager.network_interfaces.bridge.bridge_protocols import STP_STATE, BridgeProtocol
from lib.network_manager.network_operations.bridge import Bridge
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS


class BridgeInterface:
    def __init__(self, bridge_name: str, defaults_at_create:bool=True):
        """
        Initialize the BridgeInterface instance.

        Args:
            bridge_name (str): The name of the bridge to configure.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().BRIDGE_INTERFACE)
        self._bridge_name = bridge_name
        self._defaults_at_create = defaults_at_create
    
    def get_bridge_name(self):
        """
        Retrieve the name of the current bridge.

        This method returns the bridge name stored in the instance's _bridge_name attribute.

        Returns:
            str: The name of the bridge.
        """
        return self._bridge_name

    def does_bridge_exist(self) -> bool:
        """
        Check if the specified bridge exists.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        if not Bridge().does_bridge_exist(self._bridge_name):
            self.log.debug(f'does_bridge_exist() -> {self._bridge_name} does not exist')
            return False         
        return True
    
    def create_bridge(self) -> bool:
        """
        Create a bridge interface if it does not already exist.

        Returns:
            bool: STATUS_OK if the bridge was successfully created or already exists, STATUS_NOK otherwise.
        """        
        if self.does_bridge_exist():
            self.log.error(f'Can not create bridge: {self._bridge_name}, already exists')
            return STATUS_NOK
            
        if Bridge().add_bridge(self.get_bridge_name()):
            self.log.error(f'create_bridge(return {STATUS_NOK}) -> Failed to create Bridge {self.get_bridge_name()}')
            return STATUS_NOK
        
        if self._defaults_at_create:
            if Bridge().update_bridge(self._bridge_name, 
                                        BridgeProtocol.IEEE_802_1S,
                                        STP_STATE.STP_ENABLE, 
                                        shutdown_status=State.DOWN):
                self.log.error(f'create_bridge(return {STATUS_NOK}) -> Failed to configure Bridge {self._bridge_name} with IEEE 802.1S and STP enabled')
                return STATUS_NOK
        
        self.log.debug(f'create_bridge(return {STATUS_NOK}) -> successfully created bridge {self.get_bridge_name()}')
        return STATUS_OK
    
    def destroy_bridge(self):
        """
        Destroy the current bridge by calling the del_bridge method of the Bridge class.

        This method retrieves the bridge name of the current instance and 
        deletes the bridge using the del_bridge method from the Bridge class.
        """
        return Bridge().del_bridge(self.get_bridge_name())

    def set_inet_management(self, inet: str) -> bool:
        """
        Set the IPv4 or IPv6 address for the bridge.

        Args:
            inet (str): The IP address to set.

        Returns:
            bool: STATUS_OK if the IP address was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set management inet {inet} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK
        
        if Bridge().update_bridge(bridge_name=self._bridge_name, management_inet=inet):
            self.log.debug(f'set_inet_management() -> Failed to set inet address {inet} to bridge {self._bridge_name}')
            return STATUS_NOK

        self.log.debug(f'set_inet_management() -> Inet address {inet} is set to bridge {self._bridge_name}')
        return STATUS_OK
    
    def set_shutdown_status(self, state: State) -> bool:
        """
        Set the shutdown status for a specified bridge.

        This method checks if the bridge exists. If it does, it compares the current shutdown status 
        with the desired new status. If they differ, it updates the bridge's shutdown status. 

        Parameters:
            state (State): The desired shutdown status to set for the bridge. 
                        It can be State.UP, State.DOWN, or State.UNKNOWN.

        Returns:
            bool: STATUS_OK (True) if the shutdown status was successfully set or if it was already set to the desired status.
                STATUS_NOK (False) if there was an error setting the shutdown status.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set {state} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK
        
        if Bridge().update_bridge(bridge_name=self._bridge_name, shutdown_status=state):
            self.log.debug(f'set_shutdown_status() -> Failed shutdown status {state} set for bridge {self._bridge_name}')
            return STATUS_NOK

        self.log.debug(f'set_shutdown_status() -> Shutdown status {state} is set to bridge {self._bridge_name}')
        return STATUS_OK

    def set_stp(self, stp: STP_STATE) -> bool:
        """
        Set the Spanning Tree Protocol (STP) state for the bridge.

        Args:
            stp (STP_STATE): The STP state to set.

        Returns:
            bool: STATUS_OK if the STP state was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set stp {stp} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK
           
        if Bridge().update_bridge(bridge_name=self._bridge_name, stp_status=stp):
            self.log.debug(f'set_stp() -> Failed to set STP status {stp} to bridge {self._bridge_name}')
            return STATUS_NOK
        
        self.log.debug(f'set_stp() -> STP status {stp} is set for bridge {self._bridge_name}')
        
        return STATUS_OK
    
    def set_bridge_protocol(self, protocol: BridgeProtocol) -> bool:
        """
        Set the bridge protocol for the bridge.

        Args:
            protocol (BridgeProtocol): The bridge protocol to set.

        Returns:
            bool: STATUS_OK if the bridge protocol was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set protocol {protocol} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK

        if Bridge().update_bridge(bridge_name=self._bridge_name, protocol=protocol):
            self.log.error(f'set_bridge_protocol() -> Failed to set description "{protocol}" to bridge {self._bridge_name}')
            return STATUS_NOK
            
        self.log.debug(f'set_bridge_protocol() -> Bridge protocol {protocol} is already set for bridge {self._bridge_name}')
        return STATUS_OK
    
    def set_description(self, description: Optional[str]) -> bool:
        """
        Set a description for the bridge.

        Args:
            description (Optional[str]): The description to set. If None, the description will be cleared.

        Returns:
            bool: STATUS_OK if the description was successfully set, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            self.log.error(f'Unable to set description {description} to bridge: {self._bridge_name} does not exists')
            return STATUS_NOK

        if Bridge().update_bridge(bridge_name=self._bridge_name, description=description):
            self.log.error(f'set_description() -> Failed to set description "{description}" to bridge {self._bridge_name}')
            return STATUS_NOK
            
        self.log.debug(f'set_description() -> Description "{description}" set to bridge {self._bridge_name}')
        
        return STATUS_OK
