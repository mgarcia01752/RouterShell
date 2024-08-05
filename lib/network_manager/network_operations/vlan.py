import json
import logging

from lib.db.vlan_db import VLANDatabase

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.network_operations.bridge import Bridge

class Vlan(RunCommand):

    VLAN_PREFIX_ID = "Vlan"
    VLAN_DEFAULT_START:int = 1
    VLAN_MAX_ID:int = 4096
    
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN)

    @staticmethod
    def is_vlan_id_valid(vlan_id: int) -> bool:
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
        return VLANDatabase().add_vlan_id(vlan_id)

    def does_vlan_id_exist_db(self, vlan_id: int) -> bool:
        """
        Check if a given VLAN ID exists in the database.

        Args:
            vlan_id (int): The VLAN ID to be checked.

        Returns:
            bool: True if the VLAN ID exists in the database, False otherwise.
        """
        return VLANDatabase().vlan_exists(vlan_id)
    
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
        
        return VLANDatabase().update_vlan_name_via_vlanID(vlan_id, vlan_name).status

    def update_vlan_description(self, vlan_id: int, vlan_description: str) -> bool:
        """
        Update the description of a VLAN in the database.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_description (str): The new description for the VLAN.

        Note:
        - This method calls the `update_vlan_description_by_vlan_id` method of `VLANDatabase` to update the VLAN's description in the database.
        """
        return VLANDatabase().update_vlan_description(vlan_id, vlan_description)

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

    def add_bridge_to_vlan(self, bridge_name: str, vlan_id: int) -> str:
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
        
        if self.add_interface_to_vlan(bridge_name, vlan_id):
            self.log.debug(f"Unable to add bridge: {bridge_name} to VLAN: {vlan_id}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_interface_to_vlan(self, interface_name: str, vlan_id: int, interface_type:InterfaceType) -> bool:
        """
        Add an interface to a VLAN.

        Args:
            interface_name (str): The name of the network interface.
            vlan_id (int): The VLAN ID to assign to the VLAN.
            interface_type (InterfaceType):

        Returns:
            str: A status indicating the result of the operation:
            - 'STATUS_OK' if the interface was successfully added to the VLAN.
            - 'STATUS_NOK' if the operation failed due to invalid parameters or other issues.
        """
        if Vlan.is_vlan_id_valid():
            self.log.debug(f"add_interface_to_vlan({interface_type.name}) Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_db(vlan_id):
            self.log.debug(f"add_interface_to_vlan({interface_type.name}) Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        db_result = VLANDatabase().get_vlan_name(vlan_id)

        if db_result.status:
            self.log.error(f"Unable to obtain vlan-name from vlan-id: {vlan_id}")
            return STATUS_NOK

        vlan_name = db_result.result.get('VlanName')

        if vlan_name is None:
            self.log.error(f"VLAN name not found for vlan-id: {vlan_id}")
            return STATUS_NOK

        self.add_interface_to_vlan_os(vlan_id, vlan_name, interface_name)
        
        return VLANDatabase().add_vlan_to_interface_type(vlan_id, interface_name, interface_type)

    def add_interface_to_vlan_os(self, vlan_id: int, vlan_name:str, interface_name:str) -> bool:
        
        result = self.run(['ip', 'link', 'add', 'link', interface_name, 'name', vlan_name , 'type', 'vlan', 'id', str(vlan_id)], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Unable to add VLAN {vlan_name} to interface: {interface_name} via OS")
            return STATUS_NOK

        return STATUS_OK

    def del_interface_to_vlan(self, vlan_id: int) -> bool:
        """
        Delete an interface from a VLAN.

        Args:
            ifName (str): The name of the network interface.
            vlan_id (int): The VLAN ID to assign to the VLAN.

        Returns:
            str: A status indicating the result of the operation:
                - STATUS_OK if the interface was successfully added to the VLAN.
                - STATUS_NOK if the operation failed due to invalid parameters or other issues.
        """
        if not Vlan.is_vlan_id_valid():
            self.log.debug(f"del_interface_to_vlan() Error: Invalid VLAN ID: {vlan_id}")
            return STATUS_NOK

        if not self.does_vlan_id_exist_db(vlan_id):
            self.log.debug(f"del_interface_to_vlan() Error: VLAN ID {vlan_id} already exists.")
            return STATUS_NOK
        
        db_result = VLANDatabase().get_vlan_name(vlan_id)

        if not db_result.status:
            self.log.error(f"Unable to obtain vlan-name from vlan-id: {vlan_id}")
            return STATUS_NOK

        vlan_name = db_result.result.get('VlanName')

        if vlan_name is None:
            self.log.error(f"VLAN name not found for vlan-id: {vlan_id}")
            return STATUS_NOK
        
        result = self.run(['ip', 'link', 'delete', 'dev', vlan_name], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Unable to del VLAN {vlan_name}")
            self.log.error(f"Error: {result.stderr}")
            return STATUS_NOK

        return STATUS_OK
    