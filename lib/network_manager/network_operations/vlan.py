import json
import logging
from typing import Optional

from lib.db.sqlite_db.router_shell_db import Result
from lib.db.vlan_db import VlanDatabase

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.common.phy import State
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.network_operations.bridge import Bridge

class Vlan(RunCommand):

    VLAN_PREFIX_ID = "Vlan"
    INVALID_VLAN_ID:int = 0
    VLAN_DEFAULT_START:int = 1
    VLAN_MAX_ID:int = 4096
    
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN)

    @staticmethod
    def is_vlan_id_range_valid(vlan_id: int) -> bool:
        """
        Check if a given VLAN ID is within the valid range.

        Args:
            vlan_id (int): The VLAN ID to be checked.

        Returns:
            bool: True if the VLAN ID is within the valid range, False otherwise.
        """
        return vlan_id >= Vlan.VLAN_DEFAULT_START and vlan_id <= Vlan.VLAN_MAX_ID

    def add_vlan_id(self, vlan_id: int) -> bool:
        """
        Add a VLAN ID to the database using the VLANDatabase method.

        Args:
            vlan_id (int): The VLAN ID to be added.

        Returns:
            bool: STATUS_OK if the VLAN ID was successfully added, STATUS_NOK otherwise.
        """
        return VlanDatabase().add_vlan_id(vlan_id)

    def does_vlan_id_exist_db(self, vlan_id: int) -> bool:
        """
        Check if a given VLAN ID exists in the database.

        Args:
            vlan_id (int): The VLAN ID to be checked.

        Returns:
            bool: True if the VLAN ID exists in the database, False otherwise.
        """
        return VlanDatabase().vlan_exists(vlan_id)

    def does_vlan_name_exist(vlan_name: str) -> bool:
        """
        Checks if a VLAN with the given name exists.

        Args:
            vlan_name (str): The name of the VLAN to check.

        Returns:
            bool: True if the vlan name exists, False otherwise.
        """
        if VlanDatabase().get_vlan_id_from_vlan_name(vlan_name) == Vlan.INVALID_VLAN_ID:
            return False
        return True

    def update_vlan_name(self, vlan_id: int, vlan_name: str) -> bool:
        """
        Update the name of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_name (str): The new name for the VLAN.

        Note:
        - This method calls the `update_vlan_name` method of `VLANDatabase` to update the VLAN's name in the database.
        """
        self.log.debug(f"update_vlan_name() -> VlanID: {vlan_id} -> VlanName: {vlan_name}")
        
        return VlanDatabase().update_vlan_name_via_vlanID(vlan_id, vlan_name).status

    def update_vlan_description(self, vlan_id: int, vlan_description: str) -> bool:
        """
        Update the description of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_description (str): The new description for the VLAN.

        Note:
        - This method calls the `update_vlan_description_by_vlan_id` method of `VLANDatabase` to update the VLAN's description in the database.
        """
        return VlanDatabase().update_vlan_description(vlan_id, vlan_description)

    def add_vlan_to_interface_os(self, vlan_id: int, interface_name: str) -> bool:

        result = self.run(["ip", "-j", "link", "show", "type", "vlan"])
        
        if result.exit_code:
            self.log.error("Failed to fetch existing VLAN interfaces.")
            return STATUS_NOK

        try:
            existing_vlans = json.loads(result.stdout)
            vlan_interface_name = f"{interface_name}.{vlan_id}"
            
            for vlan in existing_vlans:
                if vlan_interface_name in vlan['ifname']:
                    print(f"VLAN interface {vlan_interface_name} already exists.")
                    return STATUS_NOK

        except json.JSONDecodeError:
            self.log.error("Failed to parse JSON output for existing VLAN interfaces.")
            return STATUS_NOK

        result = self.run(["ip", "link", "add", "link", interface_name, "name", vlan_interface_name, "type", "vlan", "id", str(vlan_id)])
        
        if result.exit_code:
            self.log.error(f"Unable to create VLAN: {vlan_id}, error: {result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_bridge_by_vlan_id(self, bridge_name: str, vlan_id: int) -> str:
        """
        Add a bridge to a VLAN.

        Args:
            bridge_name (str): The name of the bridge to be added to the VLAN.
            vlan_id (int): The VLAN ID to which the bridge should be added.

        Returns:
            str: A status code indicating the outcome of the operation.
                - If the bridge does not exist, returns STATUS_NOK.
                - If the interface cannot be added to the VLAN, returns STATUS_NOK.
                - If the operation is successful, returns STATUS_OK.

        """
        if Bridge().does_bridge_exist(bridge_name):
            self.log.debug(f"Bridge does not exist: {bridge_name}")
            return STATUS_NOK
        
        if self.add_interface_by_vlan_id(bridge_name, vlan_id):
            self.log.debug(f"Unable to add bridge: {bridge_name} to VLAN: {vlan_id}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_interface_by_vlan_id(self, interface_name: str, vlan_id: int) -> bool:
        """
        Add an interface to a VLAN.

        Args:
            interface_name (str): The name of the network interface.
            vlan_id (int): The VLAN ID to assign to the VLAN.

        Returns:
            bool: A status indicating the result of the operation:
            - 'STATUS_OK' if the interface was successfully added to the VLAN.
            - 'STATUS_NOK' if the operation failed due to invalid parameters or other issues.
        """
        if not Vlan.is_vlan_id_range_valid(vlan_id):
            self.log.debug(f"add_interface_by_vlan_id({interface_name}) Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_db(vlan_id):
            self.log.debug(f"add_interface_by_vlan_id({interface_name}) Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        if self.add_interface_to_vlan_os(vlan_id, interface_name):
            self.log.error(f'Unable to add interface {interface_name} to vlan-id: {vlan_id} -> vlan-id: {vlan_id} to OS')
            return STATUS_NOK
        
        if VlanDatabase().add_interface_to_vlan(vlan_id, interface_name):
            self.log.error(f'Unable to add interface {interface_name} to vlan-id: {vlan_id} -> vlan-id: {vlan_id} to DB')
            return STATUS_NOK
        
        return STATUS_OK

    def add_interface_to_vlan_os(self, vlan_id: int, interface_name: str) -> bool:
        """
        Add an interface to a VLAN on the operating system.

        Args:
            vlan_id (int): The VLAN ID to add the interface to.
            interface_name (str): The name of the interface to be added to the VLAN.

        Returns:
            bool: STATUS_OK if the interface was successfully added to the VLAN, otherwise STATUS_NOK.

        Logs:
            Logs a debug message if the interface could not be added to the VLAN via the OS.
        """
        if not isinstance(vlan_id, int):
            self.log.error(f"Invalid type for vlan_id: {type(vlan_id)}. Expected int.")
            return STATUS_NOK
        
        if not isinstance(interface_name, str):
            self.log.error(f"Invalid type for interface_name: {type(interface_name)}. Expected str.")
            return STATUS_NOK
        
        vlan_name = f'{interface_name}.{vlan_id}'
        result = self.run(['ip', 'link', 'add', 'link', interface_name, 'name', vlan_name, 'type', 'vlan', 'id', str(vlan_id)])

        if result.exit_code:
            self.log.debug(f"Unable to add VlanID {vlan_id} to interface: {interface_name} via OS, error: {result.stderr}")
            return STATUS_NOK

        return STATUS_OK

    def delete_interface_from_vlan(self, interface_name: str, vlan_id: int) -> bool:
        return STATUS_OK

    def get_vlan_name_from_vlan_id(self, vlan_id: int) -> Optional[str]:
        """
        Retrieves the VLAN name corresponding to a given VLAN ID.
        
        Args:
            vlan_id (int): The ID of the VLAN.
        
        Returns:
            Optional[str]: The name of the VLAN if found, Vlan.INVALID_VLAN_ID otherwise.
        """
        result: Result = VlanDatabase().get_vlan_name_by_vlan_id(vlan_id)
        
        if result.status:
            self.log.error(f"Unable to retrieve VLAN name from VLAN ID: {vlan_id}")
            return Vlan.INVALID_VLAN_ID
        
        return result.result.get('VlanName')
    
    def get_vlan_id_from_vlan_name(self, vlan_name:str) -> int:
        """
        Retrieves the VLAN ID associated with a given VLAN name.

        Args:
            vlan_name (str): The name of the VLAN.

        Returns:
            int: The VLAN ID if found, otherwise returns Vlan.INVALID_VLAN_ID.
        """     
        return VlanDatabase().get_vlan_id_from_vlan_name(vlan_name)
    
    def set_vlan_state(self, vlan_id: int, state: State) -> bool:
        """
        Sets the state of all interfaces associated with a specific VLAN.
        """
        try:
            # Convert state to lowercase string ('up' or 'down')
            status = state.value.lower()

            # Retrieve the list of all network interfaces in JSON format
            result = self.run(['ip', '-json', 'link', 'show'])

            if result.exit_code != 0:
                self.log.error(f"Failed to retrieve interface information: {result.stderr}")
                return STATUS_NOK

            try:
                interfaces_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                self.log.error(f"Error decoding JSON output: {str(e)}")
                return STATUS_NOK

            success = STATUS_OK

            # Loop through the interfaces and set the state for the ones matching the VLAN ID
            for interface in interfaces_data:
                if interface.get('ifname', '').endswith(f'.{vlan_id}'):
                    # Set the state (up or down) of the VLAN interface
                    set_result = self.run(['ip', 'link', 'set', 'dev', interface['ifname'], status])
                    if set_result.exit_code != 0:
                        self.log.error(f"Failed to set interface {interface['ifname']} to {status}: {set_result.stderr}")
                        success = STATUS_NOK

            return success

        except Exception as e:
            self.log.error(f"Unexpected error setting VLAN state: {str(e)}")
            return STATUS_NOK

        
            
    
            