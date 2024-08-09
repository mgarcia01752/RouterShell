import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.interface import InterfaceType
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.db.sqlite_db.router_shell_db import RouterShellDB as DB, Result


class VlanDatabase():
    
    rsdb = DB()
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_DB)   
    
    def add_vlan_id(self, vlan_id: int) -> bool:
        """
        Add a VLAN ID to the database using the rsdb method.

        Args:
            vlan_id (int): The VLAN ID to be added.

        Returns:
            bool: STATUS_OK if the VLAN ID was successfully added or already exists,
                  STATUS_NOK if there was an error adding the VLAN ID.
        """
        
        if not self.rsdb.vlan_id_exists(vlan_id).status:
            self.log.debug(f'VlanID: {vlan_id}, does not exists, adding Vlan to DB')
            return self.rsdb.insert_vlan_id(vlan_id).status
        
        self.log.debug(f'VlanID: {vlan_id} already exisit, no need to add')
        
        return STATUS_OK

    def add_vlan(self, vlan_id: int, vlan_name: str, description: str = None) -> Result:
        """
        Add a new VLAN to the database.

        Args:
            vlan_id (int): The unique ID of the VLAN.
            vlan_name (str): The name of the VLAN.
            description (str, optional): A description of the VLAN.

        Returns:
            Result: A Result object representing the outcome of the operation.
                - If the operation is successful, the Result object will have 'status' set to STATUS_OK
                  and 'row_id' containing the unique identifier of the inserted VLAN.
                - If there is an error or if the VLAN already exists, the Result object will have 'status' set to STATUS_NOK,
                  'row_id' set to None, and 'reason' providing additional information.
        """
        return self.rsdb.insert_vlan(vlan_id, vlan_name, description)

    def update_vlan_description(self, vlan_id: int, vlan_description: str) -> bool:
        """
        Update the description of a VLAN by its ID.

        Args:
            vlan_id (int): The unique ID of the VLAN.
            vlan_description (str): The new description for the VLAN.

        Returns:
            bool: True if the update is successful, False otherwise.

        Example:
        You can use the update_vlan_description class method to update the description of a VLAN.
        For example:
        ```
        success = YourClass.update_vlan_description(10, 'New VLAN Description')
        
        if success:
            print("VLAN description updated successfully.")
        else:
            print("Failed to update VLAN description.")
        ```
        """
        return self.rsdb.update_vlan_description_by_vlan_id(vlan_id, vlan_description).status

    def vlan_exists(self, vlan_id: int) -> bool:
        """
        Check if a VLAN with the given ID exists in the database.

        Args:
            self: The class reference.
            vlan_id (int): The unique ID of the VLAN to check.

        Returns:
            bool: True if a VLAN with the given ID exists, False otherwise.
        """
        return self.rsdb.vlan_id_exists(vlan_id).status

    def get_vlan_name_by_vlan_id(self, vlan_id: int) -> Result:
        """
        Get the name of a VLAN by its ID.

        Args:
            vlan_id (int): The unique ID of the VLAN.

        Returns:
            Result: A Result object representing the outcome of the operation.
            - If the operation is successful, the Result object will have 'status' set to STATUS_OK,
                  'row_id' set to the unique identifier of the VLAN, and 'result' containing the VLAN name.
            - If there is an error or if the VLAN with the provided ID does not exist, the Result object will have
                  'status' set to STATUS_NOK, 'row_id' set to None, and 'reason' providing additional information.

        """
        return self.rsdb.select_vlan_name_by_vlan_id(vlan_id)

    def update_vlan_name_via_vlanID(self, vlan_id: int, vlan_name: str) -> Result:
        """
        Update the name of a VLAN by its ID.

        Args:
            self: The class reference.
            vlan_id (int): The unique ID of the VLAN to update.
          self  vlan_name (str): The new name for the VLAN.

        Returns:
            bool: (STATUS_OK) if the update is successful, (STATUS_NOK) if it fails.
        """        
        return self.rsdb.update_vlan_name_by_vlan_id(vlan_id, vlan_name)

    def add_ports_to_vlan(self, vlan_id: int, ports_to_add: list):
        # Add ports to a VLAN
        vlan_interface_id = self.get_vlan_interface_id(vlan_id)
        if vlan_interface_id:
            for port in ports_to_add:
                self.insert_vlan_interface_mapping(vlan_interface_id, port)

    def delete_interface_from_vlan(self, vlan_id: int, port_to_delete: int):
        # Delete an interface (port) from a VLAN
        vlan_interface_id = self.get_vlan_interface_id(vlan_id)
        if vlan_interface_id:
            self.delete_vlan_interface_mapping(vlan_interface_id, port_to_delete)

    def add_interface_to_vlan(self, vlan_id: int, interface_name: str) -> bool:
        """
        Add a VLAN to a specific interface type in the database.

        Args:
            vlan_id (int): The unique identifier of the VLAN.
            interface_name (str): The name of the interface or bridge group.

        Returns:
            bool: STATUS_OK if the VLAN was successfully added to the specified interface type, STATUS_NOK otherwise.
        """
        
        interface_type = self.rsdb.select_interface_type(interface_name)
        
        self.log.debug(f"add_vlan_to_interface_type({vlan_id} -> {interface_name}) -> Interface-Type: {interface_type}")
        
        try:
            
            if interface_type == InterfaceType.BRIDGE:
                result = self.rsdb.insert_vlan_interface(vlan_id, bridge_group_name=interface_name)
            else:
                result = self.rsdb.insert_vlan_interface(vlan_id, interface_name=interface_name)

            return result.status

        except Exception as e:
            self.log.error("add_vlan_to_interface_type() -> Error adding VLAN to interface type: %s", e)
            return STATUS_NOK

    def get_vlan_id_from_vlan_name(self, vlan_name: str) -> int:
        """
        Retrieves the VLAN ID associated with a given VLAN name.

        Args:
            vlan_name (str): The name of the VLAN.

        Returns:
            int: The VLAN ID if found, otherwise returns Vlan.INVALID_VLAN_ID.

        """
        from lib.network_manager.network_operations.vlan import Vlan
        result = self.rsdb.select_vlan_id_by_vlan_name(vlan_name)

        if result.status == STATUS_OK and result.result:
            return result.result.get('VlanID', Vlan.INVALID_VLAN_ID)
        else:
            self.log.debug(f"Unable to retrieve VLAN ID for VLAN name: {vlan_name}")
            return Vlan.INVALID_VLAN_ID
