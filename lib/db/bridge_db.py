import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB, Result

from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS

class BridgeDatabase():
    
    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().BRIDGE_DB)
        
        '''CMD2 DEBUG LOGGING'''
        cls.debug = CGS().DEBUG_BRIDGE_DB
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
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
        cls.log.debug(f"bridge_exists() -> Bridge: {bridge_name}")

        return cls.rsdb.bridge_exists(bridge_name).status

    def add_bridge(cls, bridge_name: str, bridge_protocol:str=None, stp_status:bool=True) -> Result:
        """
        Add a new bridge to the database.

        Args:
            cls: The class reference.
            bridge_name (str): The name of the bridge to add.

        Returns:
            InsertResult: An instance of the InsertResult class with status, row_id, and result attributes.
        """
        cls.log.debug(f"add_bridge() -> BridgeName: {bridge_name}")

        if cls.bridge_exists(bridge_name):
            cls.log.debug(f"Unable to add bridge {bridge_name}, bridge already exists")
            return Result(STATUS_NOK, -1, "Bridge already exists")

        rsp = cls.rsdb.insert_bridge(bridge_name, bridge_protocol)

        if rsp.status:
            cls.log.error(f"Unable to add bridge: {bridge_name} Error: {rsp.result}")
            return Result(STATUS_NOK, -1, rsp.result)

        return Result(STATUS_OK, rsp.row_id, "Bridge added successfully")

    def del_bridge(cls, bridge_name:str):
        cls.log.debug(f"del_bridge() -> BridgeName: {bridge_name}")
        
        if cls.rsdb.delete_bridge_entry(bridge_name):
            cls.log.error(f"Unable to delete Bridge: {bridge_name}")
            return STATUS_NOK
        return STATUS_OK
        
    def insert_protocol(cls, bridge_name: str, br_protocol:str) -> bool:
        cls.log.debug(f"insert_protocol() -> BridgeName: {bridge_name}")
        
        if not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to add protocol to bridge {bridge_name}, bridge does not exists")
            return STATUS_NOK
        
        return STATUS_OK

    def add_interface(cls, bridge_name:str, interface_name:str) -> bool:
        cls.log.debug(f"add_interface() -> BridgeName: {bridge_name}")

        if not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to add interface {interface_name} to bridge {bridge_name}, bridge does not exists")
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_bridge_summary(cls, bridge_name: str = None) -> bool:
        cls.log.debug(f"get_bridge_summary() -> BridgeName: {bridge_name}")
        
        if bridge_name is not None and not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to add protocol to bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def remove_interface(cls, bridge_name:str, interface_name):
        cls.log.debug(f"bridge_exists() -> BridgeName: {bridge_name}")
        
        if not cls.bridge_exists(bridge_name):
            cls.log.error(f"Unable to remove interface {interface_name} to bridge {bridge_name} does not exists")
            return STATUS_NOK
        
        return STATUS_OK
    
    def get_interfaces(cls, bridge_name:str) -> list:
        cls.log.debug(f"bridge_exists() -> BridgeName: {bridge_name}")
        pass
    