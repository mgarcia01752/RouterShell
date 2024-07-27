import logging
from typing import Optional
from lib.common.constants import STATUS_OK, STATUS_NOK
from lib.network_manager.network_operations.bridge.bridge import STP_STATE, Bridge, BridgeProtocol, State
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS

class BridgeConfigFactory:
    def __init__(self, bridge_name: str):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG_FACTORY)        
        self.bridge_name = bridge_name

class BridgeConfigCommands:
    def __init__(self, bridge_name: str):
        """
        Initialize the BridgeConfigCommands instance.

        Args:
            bridge_name (str): The name of the bridge to configure.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG_COMMANDS)
        self.bridge_name = bridge_name
    
    def does_bridge_exist(self) -> bool:
        """
        Check if the specified bridge exists.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        if not Bridge().does_bridge_exist(self.bridge_name):
            self.log.debug(f'does_bridge_exist() -> {self.bridge_name} does not exist')
            return False         
        return True
    
    def create_bridge_interface(self) -> bool:
        """
        Create a bridge interface if it does not already exist.

        Returns:
            bool: STATUS_OK if the bridge was successfully created or already exists, STATUS_NOK otherwise.
        """
        if not self.does_bridge_exist():
            if Bridge().add_bridge(self.bridge_name):
                self.log.debug(f'create_bridge_interface() -> Bridge {self.bridge_name} successfully created')
                return STATUS_OK
            
            else:
                self.log.error(f'create_bridge_interface() -> Failed to create bridge {self.bridge_name}')
                return STATUS_NOK
        
        self.log.debug(f'create_bridge_interface() -> Bridge {self.bridge_name} already exists')
        return STATUS_OK
    
    def set_management_inet(self, inet: str) -> bool:
        """
        Set the IPv4 or IPv6 address for the bridge.

        Args:
            inet (str): The IP address to set.

        Returns:
            bool: STATUS_OK if the IP address was successfully set, STATUS_NOK otherwise.
        """
        if self.does_bridge_exist():
            current_inet = Bridge().get_inet(self.bridge_name)
            if current_inet != inet:
                if Bridge().update_bridge(bridge_name=self.bridge_name, management_inet=inet):
                    self.log.debug(f'set_inet() -> Inet address {inet} set for bridge {self.bridge_name}')
                    return STATUS_OK
                else:
                    self.log.error(f'set_inet() -> Failed to set inet address {inet} for bridge {self.bridge_name}')
                    return STATUS_NOK
            self.log.debug(f'set_inet() -> Inet address {inet} is already set for bridge {self.bridge_name}')
        return STATUS_OK
    
    def set_shutdown_status(self, negate: bool) -> bool:
        """
        Set the shutdown status of the bridge.

        Args:
            negate (bool): If True, sets the bridge to DOWN state, otherwise UP state.

        Returns:
            bool: STATUS_OK if the shutdown status was successfully set, STATUS_NOK otherwise.
        """
        if self.does_bridge_exist():
            new_status = State.DOWN if negate else State.UP
            current_status = Bridge().get_bridge_shutdown_status_os(self.bridge_name)
            if current_status != new_status:
                if Bridge().update_bridge(bridge_name=self.bridge_name, shutdown_status=new_status):
                    self.log.debug(f'set_shutdown_status() -> Shutdown status {new_status} set for bridge {self.bridge_name}')
                    return STATUS_OK
                else:
                    self.log.error(f'set_shutdown_status() -> Failed to set shutdown status {new_status} for bridge {self.bridge_name}')
                    return STATUS_NOK
            self.log.debug(f'set_shutdown_status() -> Shutdown status {new_status} is already set for bridge {self.bridge_name}')
        return STATUS_OK
    
    def set_stp(self, stp: STP_STATE) -> bool:
        """
        Set the Spanning Tree Protocol (STP) state for the bridge.

        Args:
            stp (STP_STATE): The STP state to set.

        Returns:
            bool: STATUS_OK if the STP state was successfully set, STATUS_NOK otherwise.
        """
        if self.does_bridge_exist():
            current_stp = Bridge().get_bridge_stp_status_os(self.bridge_name)
            if current_stp != stp:
                if Bridge().update_bridge(bridge_name=self.bridge_name, stp_status=stp):
                    self.log.debug(f'set_stp() -> STP status {stp} set for bridge {self.bridge_name}')
                    return STATUS_OK
                else:
                    self.log.error(f'set_stp() -> Failed to set STP status {stp} for bridge {self.bridge_name}')
                    return STATUS_NOK
            self.log.debug(f'set_stp() -> STP status {stp} is already set for bridge {self.bridge_name}')
        return STATUS_OK
    
    def set_bridge_protocol(self, protocol: BridgeProtocol) -> bool:
        """
        Set the bridge protocol for the bridge.

        Args:
            protocol (BridgeProtocol): The bridge protocol to set.

        Returns:
            bool: STATUS_OK if the bridge protocol was successfully set, STATUS_NOK otherwise.
        """
        if self.does_bridge_exist():

            if Bridge().update_bridge(bridge_name=self.bridge_name, protocol=protocol):
                self.log.debug(f'set_bridge_protocol() -> Bridge protocol {protocol} set for bridge {self.bridge_name}')
                return STATUS_OK
            else:
                self.log.error(f'set_bridge_protocol() -> Failed to set bridge protocol {protocol} for bridge {self.bridge_name}')
                return STATUS_NOK
        
        self.log.debug(f'set_bridge_protocol() -> Bridge protocol {protocol} is already set for bridge {self.bridge_name}')
        return STATUS_OK
    
    def set_description(self, description: Optional[str]) -> bool:
        """
        Set a description for the bridge.

        Args:
            description (Optional[str]): The description to set. If None, the description will be cleared.

        Returns:
            bool: STATUS_OK if the description was successfully set, STATUS_NOK otherwise.
        """
        if self.does_bridge_exist():

            if Bridge().update_bridge(bridge_name=self.bridge_name, description=description):
                self.log.debug(f'set_description() -> Description "{description}" set for bridge {self.bridge_name}')
                return STATUS_OK
            else:
                self.log.error(f'set_description() -> Failed to set description "{description}" for bridge {self.bridge_name}')
                return STATUS_NOK

        self.log.debug(f'set_description() -> Description "{description}" is already set for bridge {self.bridge_name}')
        return STATUS_OK
