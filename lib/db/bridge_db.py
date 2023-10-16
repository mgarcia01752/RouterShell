import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.router_shell_db import RouterShellDatabaseConnector as RSDB, UpdateResult, InsertResult
from lib.network_manager.bridge import BridgeProtocol

class BridgeDatabase():
    
    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        if not cls.rsdb:
            cls.log.info(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()   
    
    def bridge_exists(cls, bridge_name: str) -> bool:
        """
        Check if a bridge with the given name exists in the database.

        Args:
            cls: The class reference.
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        cls.log.info(f"bridge_exists() -> BridgeName: {bridge_name}")

        if not cls.rsdb.get_bridge_id(bridge_name):
            cls.log.info(f"bridge_exists() -> Bridge {bridge_name} does not exist")
            return False

        return True

    def add_bridge(cls, bridge_name:str) -> bool:
        cls.log.info(f"add_bridge() -> BridgeName: {bridge_name}")
        
        if cls.bridge_exists(bridge_name):
            cls.log.info(f"Unable to add bridge {bridge_name}, bridge already exists")
            return STATUS_NOK
        
        rsp = cls.rsdb.insert_bridge(bridge_name)
        
        if rsp.status:
            cls.log.error(f"Unable to add bridge: {bridge_name} Error: {rsp.result}")
            return STATUS_NOK
        
        return STATUS_OK
    
    def insert_protocol(cls, bridge_name: str, br_protocol:BridgeProtocol) -> bool:
        cls.log.info(f"insert_protocol() -> BridgeName: {bridge_name}")
        
        if not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to add protocol to bridge {bridge_name}, bridge does not exists")
            return STATUS_NOK
        
        return STATUS_OK

    def add_interface(cls, bridge_name:str, interface_name:str) -> bool:
        cls.log.info(f"add_interface() -> BridgeName: {bridge_name}")

        if not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to add interface {interface_name} to bridge {bridge_name}, bridge does not exists")
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_bridge_summary(cls, bridge_name: str = None) -> bool:
        cls.log.info(f"get_bridge_summary() -> BridgeName: {bridge_name}")
        
        if bridge_name is not None and not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to add protocol to bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def remove_interface(cls, bridge_name:str, interface_name):
        cls.log.info(f"bridge_exists() -> BridgeName: {bridge_name}")
        
        if not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to remove interface {interface_name} to bridge {bridge_name} does not exists")
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_interfaces(cls, bridge_name:str) -> list:
        cls.log.info(f"bridge_exists() -> BridgeName: {bridge_name}")
        pass
    