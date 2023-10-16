import logging
from typing import Optional
from click import Tuple

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.router_shell_db import InsertResult, RouterShellDatabaseConnector as RSDB


class VLANDatabase(RSDB):
    
    def __init__(cls):
        super().__init__()
        cls.log = logging.getLogger(cls.__class__.__name__)   
    
    def add_vlan(cls, vlan_id: int, vlan_name: str, description: str = None) -> InsertResult:
        """
        Add a VLAN to the database.

        Args:
            cls: The class reference.
            vlan_id (int): The unique ID of the VLAN.
            vlan_name (str): The name of the VLAN.
            description (str, optional): Description of the VLAN.

        Returns:
            tuple: A tuple containing two values:
                - int: Status indicator (STATUS_NOK or STATUS_OK).
                - int: The row ID of the inserted VLAN if successful, or -1 if unsuccessful.

        Note:
            STATUS_NOK and STATUS_OK are constants used to indicate the status of the operation.
        """
        # Check if the VLAN already exists
        if cls.vlan_exists(vlan_id):
            cls.log.error(f"Unable to add, VLAN already exists: {vlan_id}. Delete VLAN and re-add")
            return STATUS_NOK, -1

        # Insert the VLAN into the database
        row_id = cls.insert_vlan(vlan_id, vlan_name, description)

        if row_id > 0:
            return InsertResult(STATUS_OK, row_id)
        else:
            cls.log.error("Failed to insert VLAN into the database")
            return InsertResult(STATUS_NOK, -1)

    def update_vlan_description(cls, vlan_id: int, vlan_description: str) -> bool:
        """
        Update the description of a VLAN by its ID.

        Args:
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_description (str): The new description for the VLAN.

        Returns:
            bool: (STATUS_OK) if the update is successful, (STATUS_NOK) if it fails.
        """
        return cls.update_vlan_description_by_vlan_id(vlan_id, vlan_description)
        
    def vlan_exists(cls, vlan_id: int) -> bool:
        """
        Check if a VLAN with the given ID exists in the database.

        Args:
            cls: The class reference.
            vlan_id (int): The unique ID of the VLAN to check.

        Returns:
            bool: True if a VLAN with the given ID exists, False otherwise.
        """
        return cls.get_vlan_id(vlan_id) is not None

    def get_vlan_name(cls, vlan_id: int) -> InsertResult:
        """
        Retrieve the name of a VLAN by its ID.

        Args:
            cls: The class reference.
            vlan_id (int): The unique ID of the VLAN for which to retrieve the name.

        Returns:
            tuple: A tuple containing two values:
                - int: Status indicator (STATUS_NOK or STATUS_OK).
                - str or None: The name of the VLAN with the given ID if found, or None if it doesn't exist.
        """
        vlan_name = cls.get_vlan_name_by_id(vlan_id)
        if vlan_name is not None:
            return InsertResult(STATUS_OK, vlan_name)
        else:
            cls.log.error(f"VLAN with ID {vlan_id} not found.")
            return InsertResult(STATUS_NOK, None)

    def update_vlan_name(cls, vlan_id: int, vlan_name: str) -> bool:
        """
        Update the name of a VLAN by its ID.

        Args:
            cls: The class reference.
            vlan_id (int): The unique ID of the VLAN to update.
            vlan_name (str): The new name for the VLAN.

        Returns:
            bool: (STATUS_OK) if the update is successful, (STATUS_NOK) if it fails.
        """
        if cls.update_vlan_name_by_id(vlan_id, vlan_name):
            cls.log.info(f"Name of VLAN {vlan_id} updated successfully.")
            return STATUS_OK
        else:
            cls.log.error(f"Failed to update the name of VLAN {vlan_id}.")
            return STATUS_NOK
    
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
