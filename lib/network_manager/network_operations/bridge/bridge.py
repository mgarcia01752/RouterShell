import json
import logging
from typing import List, Optional

from lib.db.bridge_db import BridgeDatabase 
from lib.network_manager.common.phy import State
from lib.common.common import STATUS_NOK, STATUS_OK

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.network_operations.bridge.bridge_settings import STP_STATE, BridgeProtocol

class Bridge(RunCommand, BridgeDatabase):

    def __init__(self):
        super().__init__()
        BridgeDatabase().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE)
        
    def get_bridge_list_os(self) -> List[str]:
        """
        Get a list of bridge names from OS

        Returns:
            List[str]: A list of bridge names.
        """
        result = self.run(['ip', '-j', 'link', 'show', 'type', 'bridge'])

        if result.exit_code:
            self.log.error("Unable to get bridge list")
            return []

        try:
            bridge_links = json.loads(result.stdout)
            bridge_names = [link['ifname'] for link in bridge_links]
            return bridge_names
        
        except json.JSONDecodeError as e:
            self.log.debug(f"Failed to parse JSON: {e}")
            return []
        
        except KeyError as e:
            self.log.debug(f"Unexpected data format: {e}")
            return []

    def add_bridge(self, bridge_name: str) -> bool:
        """
        Add a bridge to the system and database. The method checks if the bridge exists in the OS and the database,
        and performs appropriate actions based on its presence.

        Args:
            bridge_name (str): The name of the bridge to be added.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self._does_bridge_exist_os(bridge_name):
            if not self.does_bridge_exists_db(bridge_name):
                self.log.warn(f'Bridge {bridge_name} not in DB, adding to DB')
                if self.add_bridge_db(bridge_name):
                    self.log.error(f'Failed to add bridge: {bridge_name} to DB')
                    return STATUS_NOK
                return STATUS_OK
            
            self.log.debug(f"Bridge {bridge_name} already exists in DB")
            return STATUS_NOK
        
        # If bridge does not exist in the OS, it might still exist in the DB, so handle this case
        if self.does_bridge_exists_db(bridge_name):
            self.log.debug(f"Bridge {bridge_name} already exists in DB - Deleting and re-adding")
            if self.del_bridge_db(bridge_name):
                self.log.debug(f"Failed to delete existing bridge {bridge_name} from DB")
                return STATUS_NOK
        
        if self.add_bridge_db(bridge_name):
            self.log.error(f"Failed to add bridge {bridge_name} to DB")
            return STATUS_NOK
        
        return STATUS_OK

    def update_bridge(self, bridge_name: str, 
                    protocol: Optional[BridgeProtocol] = None, 
                    stp_status: Optional[STP_STATE] = None,
                    management_inet: Optional[str] = None,
                    shutdown_status: Optional[State] = None) -> bool:
        """
        Update the bridge configuration both on the operating system and in the database.

        This method performs the following actions:
        1. Updates the bridge on the operating system.
        2. Updates the bridge in the database with the new configuration.

        Args:
            bridge_name (str): The name of the bridge to update.
            protocol (Optional[BridgeProtocol]): The new protocol for the bridge. Defaults to None.
            stp_status (Optional[STP_STATE]): The new STP status for the bridge. Defaults to None.
            management_inet (Optional[str]): The management IP address for the bridge. Defaults to None.
            shutdown_status (Optional[State]): The new shutdown status for the bridge. Defaults to None.

        Returns:
            bool: True if both OS and DB updates were successful, False otherwise.
        """
        # Update the bridge on the operating system
        if not self._update_bridge_via_os(bridge_name, protocol, stp_status, management_inet, shutdown_status):
            self.log.error(f"Failed to update bridge {bridge_name} on OS")
            return STATUS_NOK

        # Update the bridge in the database
        if not self.update_bridge_db(bridge_name, protocol, stp_status, management_inet, shutdown_status):
            self.log.error(f"Failed to update bridge {bridge_name} in DB")
            return STATUS_NOK

        self.log.debug(f"Bridge {bridge_name} successfully updated in both OS and DB")
        return STATUS_OK

    def del_bridge(self, bridge_name: str) -> bool:
        """
        Delete a bridge from the operating system and the database.

        This method performs the following actions:
        1. Attempts to delete the bridge from the operating system using `_del_bridge_via_os`.
        2. If successful, proceeds to delete the bridge from the database using `del_bridge_db`.
        3. Returns `STATUS_OK` if both operations are successful, or `STATUS_NOK` if any operation fails.

        Args:
            bridge_name (str): The name of the bridge to delete.

        Returns:
            bool: `STATUS_OK` if the bridge was successfully deleted from both the OS and the DB,
                `STATUS_NOK` otherwise.
        """
        if not self._del_bridge_via_os(bridge_name):
            self.log.error('Unable to delete bridge via OS')
            return STATUS_NOK
        
        if not self.del_bridge_db(bridge_name):
            self.log.error(f"Failed to delete bridge {bridge_name} from DB")
            return STATUS_NOK
        
        return STATUS_OK
    
    def does_bridge_exist(self, bridge_name: str) -> bool:
        """
        Check if a bridge exists both on the operating system and in the database.

        This method performs the following checks:
        1. Verifies if the bridge exists on the operating system.
        2. Checks if the bridge also exists in the database.

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists on the operating system and does not exist in the database, 
                indicating that it needs to be added to the database. False otherwise.
        """
        if not self._does_bridge_exist_os(bridge_name):
            self.log.debug(f'Bridge {bridge_name} does not exist on OS')
            return False

        if self.does_bridge_exists_db(bridge_name):
            self.log.debug(f'Bridge {bridge_name} exists in DB, but does not exist on OS')
            return False

        return True
    
    def _does_bridge_exist_os(self, bridge_name:str, suppress_error=False) -> bool:
        """
        Check if a bridge with the given name exists via iproute.
        Will also remove bridge name in db if the interface is not available

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        self.log.debug(f"does_bridge_exist_os() -> Checking bridge name exists: {bridge_name}")
        
        output = self.run(['ip', 'link', 'show', 'dev', bridge_name], suppress_error=True)
        
        if output.exit_code:
            self.log.debug(f"does_bridge_exist_os() -> Bridge does NOT exist: {bridge_name} - exit-code: {output.exit_code}")
            return False
            
        self.log.debug(f"does_bridge_exist_os(exit-code({output.exit_code})) -> Bridge does exist: {bridge_name}")
        
        return True

    def _del_bridge_via_os(self, bridge_name: str) -> bool:
        """
        Delete a bridge from the operating system. If there are any interfaces linked to the bridge,
        they will be unlinked before the bridge is deleted.

        This method first checks if the bridge exists on the OS. If it does, it will also ensure that
        all interfaces linked to the bridge are unlinked before attempting to delete the bridge itself.

        Args:
            bridge_name (str): The name of the bridge to delete.

        Returns:
            bool: True if the bridge was successfully deleted from the OS, False otherwise.
        """
        if not self._does_bridge_exist_os(bridge_name):
            self.log.debug(f"Bridge {bridge_name} does not exist on OS. No deletion performed.")
            return STATUS_NOK

        # Find and unlink any interfaces associated with the bridge
        linked_interfaces = self._get_linked_interfaces(bridge_name)
        
        if linked_interfaces:
            self.log.debug(f"Unlinking interfaces {linked_interfaces} from bridge {bridge_name}.")
            for iface in linked_interfaces:
                result = self.run(['ip', 'link', 'set', iface, 'nomaster', '-json'])
                if result.exit_code != 0:
                    self.log.error(f"Failed to unlink interface {iface} from bridge {bridge_name}: {result.stderr.strip()}")
                    return STATUS_NOK
        
        # Now delete the bridge
        result = self.run(['ip', 'link', 'delete', bridge_name, '-json'])
        
        if result.exit_code:
            self.log.debug(f"Bridge {bridge_name} successfully deleted from OS")
            return STATUS_OK
        else:
            self.log.error(f"Failed to delete bridge {bridge_name} from OS: {result.stderr.strip()}")
            return STATUS_NOK

    def _get_linked_interfaces(self, bridge_name: str) -> List[str]:
        """
        Retrieve a list of interfaces linked to the given bridge using JSON output for parsing.

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            List[str]: A list of interface names that are linked to the bridge.
        """
        result = self.run(['bridge', 'link', 'show', bridge_name, '-json'])
        
        if result.exit_code:
            self.log.error(f"Failed to retrieve linked interfaces for bridge {bridge_name}: {result.stderr.strip()}")
            return []

        try:
            data = json.loads(result.stdout)
            interfaces = [entry['ifname'] for entry in data if 'ifname' in entry]
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to parse JSON for bridge {bridge_name}: {e}")
            return []

        return interfaces

    def _update_bridge_via_os(self, bridge_name: str, 
                            protocol: Optional[BridgeProtocol] = None, 
                            stp_status: Optional[STP_STATE] = None,
                            management_inet: Optional[str] = None,
                            shutdown_status: Optional[State] = None) -> bool:
        """
        Update a bridge on the operating system with the specified parameters.

        This method updates the bridge's protocol, STP status, management IP address, 
        and shutdown status on the operating system.

        Args:
            bridge_name (str): The name of the bridge to update.
            protocol (Optional[BridgeProtocol]): The new protocol for the bridge. Defaults to None.
            stp_status (Optional[STP_STATE]): The new STP status for the bridge. Defaults to None.
            management_inet (Optional[str]): The management IP address for the bridge. Defaults to None.
            shutdown_status (Optional[State]): The new shutdown status for the bridge. Defaults to None.

        Returns:
            bool: True if the bridge was successfully updated, False otherwise.
        """
        if not self._does_bridge_exist_os(bridge_name):
            self.log.debug(f"Bridge {bridge_name} does not exist on OS. No update performed.")
            return STATUS_NOK

        # Initialize command list
        cmd = ['ip', 'link', 'set', bridge_name]

        if protocol:
            # Example: Set protocol; modify as per actual command syntax
            cmd.extend(['bridge', 'protocol', protocol.name])
        
        if stp_status:
            # Example: Set STP status; modify as per actual command syntax
            stp_command = 'enable' if stp_status == STP_STATE.STP_ENABLE else 'disable'
            cmd.extend(['bridge', 'stp', stp_command])

        if management_inet:
            # Example: Set management IP address; modify as per actual command syntax
            cmd.extend(['addr', 'add', management_inet, 'dev', bridge_name])
        
        if shutdown_status:
            shutdown_command = 'down' if shutdown_status == State.DOWN else 'up'
            cmd.extend(['net', 'link', shutdown_command])

        result = self.run(cmd)

        if result.exit_code == 0:
            self.log.debug(f"Bridge {bridge_name} successfully updated on OS")
            return STATUS_OK
        else:
            self.log.error(f"Failed to update bridge {bridge_name} on OS: {result.stderr.strip()}")
            return STATUS_NOK


            

                