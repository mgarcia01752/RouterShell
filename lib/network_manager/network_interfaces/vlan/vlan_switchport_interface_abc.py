from abc import ABC
import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_operations.vlan import Vlan

class VlanSwitchport(ABC):
    """
    Abstract base class for managing VLAN switchport operations.
    
    Attributes:
        _interface_name (str): Name of the network interface.
        log (logging.Logger): Logger for the class.
    """
    
    def __init__(self, interface_name: str):
        """
        Initializes the VlanSwitchport with a given interface name.
        
        Args:
            interface_name (str): The name of the network interface.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self._interface_name = interface_name
        
    def set_interface_to_vlan(self, vlan_id: int) -> bool:
        """
        Assigns the interface to a specified VLAN.
        
        Args:
            vlan_id (int): The VlanID.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """        
        return Vlan().add_interface_by_vlan_id(self._interface_name, vlan_id)
    
    def del_interface_from_vlan(self, vlan_if: int) -> bool:
        """
        Removes the interface from a specified VLAN.
        
        Args:
            vlan_name (str): The name of the VLAN.
        
        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        print('Not Implemented yet')
        return STATUS_OK
