import json
import logging
from typing import List, Optional

from lib.db.bridge_db import BridgeDatabase 
from lib.network_manager.common.phy import State
from lib.common.common import STATUS_NOK, STATUS_OK

from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
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

    def add_bridge(self, bridge_name: str, fix_os_db_inconsistency: bool = False) -> bool:
        """
        Adds a bridge to both the operating system (OS) and the database (DB).

        If the bridge already exists in either the OS or the DB, it checks for inconsistencies 
        and can optionally fix them based on the `fix_os_db_inconsistency` flag.

        Args:
            bridge_name (str): The name of the bridge to add.
            fix_os_db_inconsistency (bool): Flag to indicate if inconsistencies between 
                                            the OS and DB should be fixed.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        if self._does_bridge_exist_os(bridge_name):
            return self._handle_bridge_os_db_inconsistencies(bridge_name, fix_os_db_inconsistency, os_exists=True)
        
        elif self.does_bridge_exists_db(bridge_name):
            return self._handle_bridge_os_db_inconsistencies(bridge_name, fix_os_db_inconsistency, os_exists=False)
        
        else:
            self.log.debug(f"Adding bridge {bridge_name} to both OS and DB")
            if self._add_bridge_os(bridge_name):
                self.log.error(f'Unable to add bridge {bridge_name} to OS')
                return STATUS_NOK
            if self.add_bridge_db(bridge_name):
                self.log.error(f'Unable to add bridge {bridge_name} to DB')
                return STATUS_NOK                
        
        return STATUS_OK

    def update_bridge(self, bridge_name: str, 
                        protocol: Optional[BridgeProtocol] = None, 
                        stp_status: Optional[STP_STATE] = None,
                        management_inet: Optional[str] = None,
                        description: Optional[str] = None,
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
            description (Optional[str]): The new description for the bridge. Defaults to None.
            shutdown_status (Optional[State]): The new shutdown status for the bridge. Defaults to None.

        Returns:
            bool: STATUS_OK if both OS and DB updates were successful, STATUS_NOK otherwise.
        """
        # Update the bridge on the operating system
        if self._update_bridge_via_os(bridge_name, protocol, stp_status, management_inet, shutdown_status):
            self.log.error(f"Failed to update bridge {bridge_name} on OS")
            return STATUS_NOK

        # Update the bridge in the database
        update_result = self.update_bridge_db(
            bridge_name=bridge_name,
            protocol=protocol,
            stp_status=stp_status,
            management_inet=management_inet,
            description=description,
            shutdown_status=shutdown_status
        )
        
        if update_result:
            self.log.error(
                f"Failed to update bridge {bridge_name} in DB with parameters: "
                f"protocol={protocol}, stp_status={stp_status}, "
                f"management_inet={management_inet}, description={description}, "
                f"shutdown_status={shutdown_status}"
            )
            return STATUS_NOK

        self.log.debug(f"Bridge {bridge_name} successfully updated in both OS and DB")
        return STATUS_OK

    def get_bridge_shutdown_status_os(self, bridge_name: str) -> State:
        """
        Retrieve the shutdown status of a bridge from the operating system.

        Args:
            bridge_name (str): The name of the bridge to query.

        Returns:
            State: The shutdown status of the bridge (UP, DOWN, UNKNOWN).
        """
        # Execute the command and capture the output
        result = self.run(['ip', '-j', 'link', 'show', bridge_name])
        
        if result.exit_code != 0:
            self.log.error(f"Failed to get status for bridge {bridge_name}: {result.stderr}")
            return State.UNKNOWN

        # Parse the JSON output
        try:
            bridges = json.loads(result.stdout)
            for bridge in bridges:
                if bridge.get('ifname') == bridge_name:
                    # Check the 'operstate' field for status
                    operstate = bridge.get('operstate')
                    if operstate == 'down':
                        return State.DOWN
                    elif operstate == 'up':
                        return State.UP
                    else:
                        return State.UNKNOWN
        except json.JSONDecodeError as e:
            self.log.error(f"Failed to parse JSON output for bridge {bridge_name}: {e}")
            return State.UNKNOWN

        return State.UNKNOWN

    def get_bridge_stp_status_os(self, bridge_name: str) -> STP_STATE:
        """
        Retrieve the STP status of a bridge from the operating system.

        Args:
            bridge_name (str): The name of the bridge to query.

        Returns:
            STP_STATE: The STP status of the bridge (STP_DISABLE or STP_ENABLE).
        """
        # Execute the command and capture the output
        result = self.run(['bridge', 'stp', 'show', bridge_name, '-json'])

        if result.exit_code != 0:
            self.log.error(f"Failed to get STP status for bridge {bridge_name}: {result.stderr}")
            return STP_STATE.STP_DISABLE  # Default to STP_DISABLE if there's an error

        # Parse the output to determine the STP status
        output = result.stdout
        try:
            # Assuming output is a JSON string and we need to parse it
            import json
            status_info = json.loads(output)

            # Check if 'stp_state' field is present and determine the status
            stp_state = status_info.get('stp_state', None)
            if stp_state == 'enabled':
                return STP_STATE.STP_ENABLE
            elif stp_state == 'disabled':
                return STP_STATE.STP_DISABLE
            else:
                return STP_STATE.STP_DISABLE  # Default to STP_DISABLE if state is unknown
        except (json.JSONDecodeError, KeyError) as e:
            self.log.error(f"Error parsing STP status for bridge {bridge_name}: {e}")
            return STP_STATE.STP_DISABLE

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
            self.log.info(f'Bridge {bridge_name} does not exist on OS')
            
            if self.does_bridge_exists_db(bridge_name):
                self.log.warn(f'Bridge {bridge_name} does exists in DB, but not in OS')            
            
            return False
        
        if not self.does_bridge_exists_db(bridge_name):
            self.log.info(f'Bridge {bridge_name} does not exists in DB, but does in OS')
            return False

        self.log.info(f'Bridge {bridge_name} does exists in both OS and DB')
        
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
        self.log.debug(f"_does_bridge_exist_os() -> Checking bridge name exists: {bridge_name}")
        
        output = self.run(['ip', 'link', 'show', 'dev', bridge_name], suppress_error=True)
        
        if output.exit_code:
            self.log.debug(f"_does_bridge_exist_os(return:{False}) -> Bridge does NOT exist: {bridge_name} - iproute: exit-code: {output.exit_code}")
            return False
            
        self.log.debug(f"_does_bridge_exist_os(exit-code({output.exit_code})) -> Bridge does exist: {bridge_name}")
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
            bool: STATUS_OK if the bridge was successfully deleted from the OS, STATUS_NOK otherwise.
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
        result = self.run(['ip', 'link', 'delete', bridge_name, 'type', 'bridge'])
        
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

        if protocol is None and stp_status is None and management_inet is None and shutdown_status is None:
            self.log.info('_update_bridge_via_os() - All Arguments None - no action needed')
            return STATUS_OK
        
        # Initialize command list
        cmd = []

        if protocol:
            # Example: Set protocol; modify as per actual command syntax
            # cmd.append(['ip', 'link', 'set', 'dev', bridge_name, 'type', 'bridge', 'stp', str(protocol.value)])
            self.log.debug(f'Bridge Protocol is not supported with iproute')
            cmd.append([])
            
        if stp_status:
            # Set STP status using the `bridge` command
            stp_command = '1' if stp_status == STP_STATE.STP_ENABLE else '0'
            cmd.append(['ip', 'link', 'set', 'dev', bridge_name, 'type','bridge', 'stp_state', stp_command])

        if management_inet:
            # Example: Set management IP address; modify as per actual command syntax
            cmd.append(['ip', 'addr', 'add', management_inet, 'dev', bridge_name])
        
        if shutdown_status:
            shutdown_command = 'down' if shutdown_status == State.DOWN else 'up'
            cmd.append(['ip', 'link', 'set', 'dev', bridge_name, shutdown_command])

        for command in cmd:
            self.log.info(f'_update_bridge_via_os() -> cmd: {" ".join(command)}')
            result = self.run(command)
            
            if result.exit_code != 0:            
                self.log.error(f"Failed to update bridge {bridge_name} on OS: {result.stderr.strip()}")
                return STATUS_NOK

        self.log.debug(f"Bridge {bridge_name} successfully updated on OS")
        return STATUS_OK
  
    def _handle_bridge_os_db_inconsistencies(self, bridge_name: str, fix_os_db_inconsistency: bool, os_exists: bool) -> bool:
        """
        Handles inconsistencies between the operating system (OS) and the database (DB) for a bridge.

        Args:
            bridge_name (str): The name of the bridge.
            fix_os_db_inconsistency (bool): Flag to indicate if inconsistencies should be fixed.
            os_exists (bool): Flag indicating if the bridge exists in the OS.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        if os_exists:
            self.log.debug(f"Bridge {bridge_name} already exists in the OS")
            if not self.does_bridge_exists_db(bridge_name):
                self.log.debug(f"Bridge {bridge_name} does not exist in the database")
                self.log.critical(f'Inconsistency between the OS and DB: bridge {bridge_name} not found in the DB but found in the OS')

                if fix_os_db_inconsistency:
                    self.log.debug(f"Fixing the DB to match the OS")
                    if self.add_bridge_db(bridge_name):
                        return STATUS_OK
                    return STATUS_NOK
                return STATUS_NOK
        else:
            self.log.debug(f"Bridge {bridge_name} does not exist in the OS but exists in the database")

            if fix_os_db_inconsistency:
                self.log.debug(f"Fixing the OS to match the DB")
                if self.del_bridge_db(bridge_name):
                    if self._add_bridge_os(bridge_name):
                        self.add_bridge_db(bridge_name)
                        return STATUS_OK
                return STATUS_NOK
            return STATUS_NOK

    def _add_bridge_os(self, bridge_name: str) -> bool:
        """
        Create a bridge with Spanning Tree Protocol (STP) enabled.

        Args:
            bridge_name (str): The name of the bridge to create.

        Returns:
            bool: STATUS_OK if the bridge is created with STP enabled successfully, STATUS_NOK if creation fails.
        """
        self.log.debug(f"_add_bridge_os() -> Adding bridge: {bridge_name} to OS")
        
        result = self.run(['ip', 'link', 'add', 'name', bridge_name, 'type', 'bridge'])
        
        if result.exit_code:
            self.log.warning(f"Bridge {bridge_name} cannot be created - exit-code: {result.exit_code}")
            return STATUS_NOK

        self.log.debug(f"_add_bridge_os() -> Added bridge: {bridge_name} to OS")
        return STATUS_OK
                       