import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.router_shell_db import RouterShellDatabaseConnector as RSDB, UpdateResult, InsertResult
from lib.network_manager.bridge import BridgeProtocol

class BridgeDatabase():
    
    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)   
    
    def bridge_exists(cls, bridge_name:str) -> bool:
        return STATUS_OK
        
    def add_bridge(cls, bridge_name) -> bool:
        return STATUS_OK
    
    def insert_protocol(cls, bridge_name: str, br_protocol:BridgeProtocol) -> bool:
        return STATUS_OK

    def add_interface(cls, bridge_name:str, interface_name:str) -> bool:
        return STATUS_OK
    
    def get_bridge_summary(cls, bridge_name:str=None) -> bool:
        '''bridge_name:str=None means give whole summary'''
        return STATUS_OK
    
    def remove_interface(cls, bridge_name:str, interface_name):
        return STATUS_OK
    
    def get_interfaces(cls, bridge_name:str) -> list:
        pass
    