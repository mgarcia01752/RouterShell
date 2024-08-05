import logging
from typing import List, Optional
from lib.network_manager.network_operations.vlan import Vlan
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS

class VlanMangementException(Exception):
    def __init__(self, message):
        super().__init__(message)

class VlanMangement:

    def __init__(self, vlan_id: int):
        """
        Initialize the VlanMangement with a VLAN ID.

        Args:
            vlan_id (int): The VLAN ID to be managed.

        Raises:
            VlanMangementException: If unable to add the VLAN ID to the database.
        """
        self._vlan_id = vlan_id
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_CONFIG_CMD)

        if Vlan().add_vlan_id(vlan_id):
            self.log.error(f'Unable to insert/select VlanID: {vlan_id} to DB')
            raise VlanMangementException(f"Unable to add VlanID: {vlan_id} to DB")
        
        if Vlan().update_vlan_name(vlan_id, f'Vlan{vlan_id}'):
            self.log.error(f'Unable to update VlanID: {vlan_id} -> name: Vlan{vlan_id} to DB')
        
        self.log.debug(f'VlanMangement() Started - VlanID: {vlan_id}')
    
    def get_vlan_id(self) -> int:
        """
        Get the VLAN ID managed by the factory.

        Returns:
            int: The VLAN ID.
        """
        return self._vlan_id
    
    def set_name(self, vlan_name: str) -> bool:
        """
        Set the name for the VLAN.

        Args:
            vlan_name (str): The name to be set for the VLAN.

        Returns:
            bool: True if the VLAN name was successfully updated, False otherwise.

        Raises:
            ValueError: If the vlan_name is None.
        """
        if vlan_name is None:
            raise ValueError("VLAN name cannot be None")
        
        return Vlan().update_vlan_name(self._vlan_id, vlan_name)

    def set_description(self, description: Optional[List[str]] = None) -> bool:
        """
        Set the description for the VLAN.

        Args:
            description (Optional[List[str]]): The description to be set for the VLAN. If None, it will be set as an empty string.
                                            If a list is provided, it will be joined into a single string with spaces.

        Returns:
            bool: True if the VLAN description was successfully updated, False otherwise.
        """
        if description is None:
            description_str = ""
        else:
            description_str = " ".join(description)

        return Vlan().update_vlan_description(self._vlan_id, description_str)


