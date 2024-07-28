from abc import ABC

from lib.common.constants import STATUS_OK


class BridgeGroup(ABC):
    def __init__(self, interface_name:str):
        self._interface_name = interface_name
        pass
        
    def set_bridge_group(self, bridge_group:str) -> bool:
        return STATUS_OK
    
    def del_bridge_group(self, bridge_group:str) -> bool:
        return STATUS_OK
    