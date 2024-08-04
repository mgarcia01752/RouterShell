

from lib.common.constants import STATUS_OK
from lib.network_manager.network_operations.vlan import Vlan

class VlanFactoryException(Exception):
    pass    

class VlanFactory:
    def __init__(self, vlan_id:int):
        
        if not Vlan.is_vlan_id_valid(vlan_id):
            #raise exception
            pass 
            
        self._vlan_id = vlan_id
    
    def set_vlan_name(self, vlan_name:str) -> bool:
        return STATUS_OK
    
    def update_vlan_description(self, description:str) -> bool:
        return STATUS_OK