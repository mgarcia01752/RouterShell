from abc import ABC
import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_operations.vlan import Vlan

class VlanSwitchport(ABC):
    def __init__(self, interface_name:str):
        self.log = logging.getLogger(self.__class__.__name__)        
        self._interface_name = interface_name
        
    def set_interface_to_vlan(self, vlan_name:str) -> bool:
        
        vlan_id = Vlan().get_vlan_id_from_vlan_name(vlan_name)
        if vlan_id == Vlan.INVALID_VLAN_ID:
            self.log.error(f"Vlan {vlan_name} does not exist")
            return STATUS_NOK
        
        Vlan().add_interface_to_vlan(self._interface_name, vlan_id)
        return STATUS_OK
    
    def del_interface_from_vlan(self, vlan_name:str) -> bool:
        
        vlan_id = Vlan().get_vlan_id_from_vlan_name(vlan_name)
        if vlan_id == Vlan.INVALID_VLAN_ID:
            self.log.error(f"Vlan {vlan_name} does not exist")
            return STATUS_NOK
        
        Vlan().delete_interface_from_vlan(self._interface_name, vlan_id)
                
        return STATUS_OK
    
    
        