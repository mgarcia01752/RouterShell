
from abc import ABC
import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.phy import State
from lib.network_manager.network_operations.dhcp.client.dhcp_client import DHCPClient
from lib.network_manager.network_operations.dhcp.common.dhcp_common import DHCPStackVersion
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

class DHCPInterfaceClient(ABC):
    def __init__(self, interface_name:str):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_INTERFACE_CLIENT)
        self._interface_name = interface_name

    def update_interface_dhcp_client(self, dhcp_stack_ver: DHCPStackVersion, dhcp_client_state: State) -> bool:
        """
        Update the DHCP configuration for a network interface via OS.
        Update the DHCP configuration for a network interface via DB.
        
        Args:
            interface_name (str): The name of the network interface.
            dhcp_stack_ver (DHCPStackVersion): The DHCP version (DHCP_V4 or DHCP_V6).
            dhcp_client_state (State): If DOWN, disable DHCP; if UP, enable DHCP.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.

        """
        try:
            dhcp_client = DHCPClient(self._interface_name, dhcp_stack_ver)
            self.log.debug(f"Updated DHCP client configuration for interface: {self._interface_name} via OS")
        
        except Exception as e:
            self.log.critical(f"Failed to update DHCP client configuration for interface: {self._interface_name} via OS: {e}")
            return STATUS_NOK
        
        if dhcp_client_state == State.DOWN:
            if dhcp_client.stop():
                self.log.error(f"Failed to stop client on interface: {self._interface_name} OS update error.")
                return STATUS_NOK
        
        else:                                            
            if dhcp_client.start():
                self.log.error(f"Failed to start {dhcp_stack_ver.value} client on interface: {self._interface_name} OS update error.")
                return STATUS_NOK

        return STATUS_OK

         