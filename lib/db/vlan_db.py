import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB, Result

class VLANDatabase():
    
    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)   
    
    def add_vlan(cls, vlan_id: int, vlan_name: str, description: str = None) -> Result:
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

        Example:
        You can use the add_vlan class method to add a new VLAN to the database.
        For example:
        ```
        result = YourClass.add_vlan(10, 'VLAN_10', 'Example VLAN')
        
        if result.status == STATUS_OK:
            print(f"VLAN added successfully with ID: {result.row_id}")
        else:
            print(f"Failed to add VLAN: {result.reason}")
        ```
        """
        return cls.rsdb.insert_vlan(vlan_id, vlan_name, description)

    def update_vlan_description(cls, vlan_id: int, vlan_description: str) -> bool:
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
        return cls.rsdb.update_vlan_description_by_vlan_id(vlan_id, vlan_description).status

    def vlan_exists(cls, vlan_id: int) -> bool:
        """
        Check if a VLAN with the given ID exists in the database.

        Args:
            cls: The class reference.
            vlan_id (int): The unique ID of the VLAN to check.

        Returns:
            bool: True if a VLAN with the given ID exists, False otherwise.
        """
        return cls.rsdb.vlan_id_exists(vlan_id).status

    def get_vlan_name(cls, vlan_id: int) -> Result:
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

        Example:
        You can use the get_vlan_name class method to retrieve the name of a VLAN by its ID.
        For example:
        ```
        result = YourClass.get_vlan_name(10)
        
        if result.status == STATUS_OK:
            vlan_name = result.result['VlanName']
            print(f"VLAN name: {vlan_name}")
        else:
            print(f"Failed to retrieve VLAN name: {result.reason}")
        ```
        """
        return cls.rsdb.select_vlan_name_by_vlan_id(vlan_id)

        
    def update_vlan_name_via_vlanID(cls, vlan_id: int, vlan_name: str) -> Result:
        """
        Update the name of a VLAN by its ID.

        Args:
            cls: The class reference.
            vlan_id (int): The unique ID of the VLAN to update.
          cls  vlan_name (str): The new name for the VLAN.

        Returns:
            bool: (STATUS_OK) if the update is successful, (STATUS_NOK) if it fails.
        """
        
        if cls.rsdb.update_vlan_name_by_vlan_id(vlan_id, vlan_name).status == STATUS_OK:
            cls.log.info(f"update_vlan_name_via_vlanID() -> Vlan-Name: {vlan_name} updated successfully.")
            return Result(STATUS_OK, vlan_name)
        else:
            cls.log.error(f"update_vlan_name_via_vlanID() -> Failed to update the name: {vlan_name} of VLAN {vlan_id}.")
            return Result(STATUS_NOK, vlan_name)
    
    def add_ports_to_vlan(cls, vlan_id: int, ports_to_add: list):
        # Add ports to a VLAN
        vlan_interface_id = cls.get_vlan_interface_id(vlan_id)
        if vlan_interface_id:
            for port in ports_to_add:
                cls.insert_vlan_interface_mapping(vlan_interface_id, port)

    def delete_interface_from_vlan(cls, vlan_id: int, port_to_delete: int):
        # Delete an interface (port) from a VLAN
        vlan_interface_id = cls.get_vlan_interface_id(vlan_id)
        if vlan_interface_id:
            cls.delete_vlan_interface_mapping(vlan_interface_id, port_to_delete)
