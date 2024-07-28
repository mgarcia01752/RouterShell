import logging
from typing import Optional

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
from lib.network_manager.common.phy import State
from lib.network_manager.network_operations.bridge.bridge_settings import STP_STATE, BridgeProtocol


class BridgeDatabase():
    
    rsdb = DB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().BRIDGE_DB)
                
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = DB()   
    
    def does_bridge_exists_db(cls, bridge_name: str) -> bool:
        """
        Check if a bridge with the given name exists in the database.

        Args:
            cls: The class reference.
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
    
        status = cls.rsdb.bridge_exist_db(bridge_name).status
        cls.log.debug(f"does_bridge_exists_db() -> Bridge: {bridge_name} - status: {status}")
        return status

    def add_bridge_db(cls, bridge_name: str) -> bool:
        """
        Add a new bridge to the database.
        
        Args:
            bridge_name (str): The name of the bridge to be added.

        Returns:
            bool: STATUS_OK if the bridge was successfully added or updated, STATUS_NOK otherwise.
        """
        cls.log.debug(f"add_bridge_db() -> BridgeName: {bridge_name}")

        if cls.rsdb.insert_interface_bridge(bridge_name).status:
            cls.log.debug(f"Bridge {bridge_name} FAILED add to DB")
        
        return cls.rsdb.update_bridge(bridge_name=bridge_name).status
        
    def del_bridge_db(cls, bridge_name: str) -> bool:
        """
        Delete a bridge by its name from the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to delete.

        Returns:
            bool: STATUS_OK if the bridge is deleted successfully, STATUS_NOK if deletion fails.
        """
        cls.log.debug(f"del_bridge() -> BridgeName: {bridge_name}")

        if cls.rsdb.delete_interface_bridge(bridge_name).status:
            cls.log.error(f"Unable to delete Bridge: {bridge_name}")
            return STATUS_NOK
        return STATUS_OK

    def insert_protocol_db(cls, bridge_name: str, br_protocol: str) -> bool:
        """
        Insert a protocol for a bridge in the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to add a protocol to.
            br_protocol (str): The protocol to add to the bridge.

        Returns:
            bool: STATUS_OK if the protocol is added successfully, STATUS_NOK otherwise.
        """
        cls.log.debug(f"insert_protocol() -> BridgeName: {bridge_name}")

        if not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to add protocol to bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def add_interface(cls, bridge_name: str, interface_name: str) -> bool:
        """
        Add an interface to a bridge in the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to add the interface to.
            interface_name (str): The name of the interface to add to the bridge.

        Returns:
            bool: STATUS_OK if the interface is added successfully, STATUS_NOK if the bridge does not exist.
        """
        cls.log.debug(f"add_interface() -> BridgeName: {bridge_name}")

        if not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to add interface {interface_name} to bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def get_bridge_summary(cls, bridge_name: str = None) -> bool:
        """
        Get a summary of a bridge in the firewall configuration.

        Args:
            bridge_name (str, optional): The name of the bridge to get a summary of. Defaults to None.

        Returns:
            bool: STATUS_OK (False) if the summary is retrieved successfully or if bridge_name is None,
            STATUS_NOK (True) if bridge_name is provided but the bridge does not exist.
        """
        cls.log.debug(f"get_bridge_summary() -> BridgeName: {bridge_name}")

        if bridge_name is not None and not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to get summary for bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def remove_interface(cls, bridge_name: str, interface_name: str) -> bool:
        """
        Remove an interface from a bridge in the firewall configuration.

        Args:
            bridge_name (str): The name of the bridge to remove the interface from.
            interface_name (str): The name of the interface to remove from the bridge.

        Returns:
            bool: STATUS_OK (False) if the interface is removed successfully, STATUS_NOK (True) if the bridge does not exist.
        """
        cls.log.debug(f"remove_interface() -> BridgeName: {bridge_name}")

        if not cls.does_bridge_exists_db(bridge_name):
            cls.log.error(f"Unable to remove interface {interface_name} from bridge {bridge_name}, bridge does not exist")
            return STATUS_NOK

        return STATUS_OK

    def get_interfaces(cls, bridge_name:str) -> list:
        cls.log.debug(f"bridge_exists() -> BridgeName: {bridge_name}")
        pass

    def update_interface_bridge_group(cls, interface_name: str, bridge_group: str, negate: bool = False) -> bool:
        """
        Update the bridge group for an interface.

        Args:
            interface_name (str): The name of the interface to update.
            bridge_group (str): The name of the bridge group to assign or remove.
            negate (bool optional): If True, remove the interface from the bridge group. 
                                    If False, assign the interface to the bridge group.

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        if negate:
            result = cls.rsdb.delete_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Removed interface '{interface_name}' from bridge group '{bridge_group}'")
        else:
            result = cls.rsdb.insert_interface_bridge_group(interface_name, bridge_group)
            cls.log.debug(f"Assigned interface '{interface_name}' to bridge group '{bridge_group}'")

        return STATUS_OK if result.status == STATUS_OK else STATUS_NOK
    
    def update_bridge_db(cls, bridge_name: str, 
                        protocol: Optional[BridgeProtocol] = None, 
                        stp_status: Optional[STP_STATE] = None,
                        management_inet: Optional[str] = None,
                        description: Optional[str] = None,
                        shutdown_status: Optional[State] = None) -> bool:
        """
        Update an existing bridge in the Bridges, Interfaces, and InterfaceIpAddress tables.

        Args:
            bridge_name (str): The name of the bridge to update.
            protocol (Optional[BridgeProtocol]): The new protocol for the bridge (if changing).
            stp_status (Optional[STP_STATE]): The new STP status (if changing).
            management_inet (Optional[str]): The management IP address for the bridge (if changing).
            description (Optional[str]): The new description for the bridge interface (if changing).
            shutdown_status (Optional[bool]): The new shutdown status for the bridge interface (if changing).

        Returns:
            bool: STATUS_OK if the update was successful, STATUS_NOK otherwise.
        """
        result = cls.rsdb.update_bridge(
            bridge_name=bridge_name,
            protocol=protocol,
            stp_status=stp_status,
            management_inet=management_inet,
            description=description,
            shutdown_status=shutdown_status
        )
        
        cls.log.debug(f"update_bridge_db() -> BridgeName: {bridge_name}, Result: {result.reason}, Status: {result.status}")

        return result.status

