import logging
from typing import List

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.sqlite_db.router_shell_db import RouterShellDB as DB, Result
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS

class NatDB:

    rsdb = DB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().NAT_DB)
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = DB()  

    def pool_name_exists(cls, pool_name: str) -> bool:
        """
        Check if a NAT pool with the given name exists in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to check for existence.

        Returns:
            bool: True if a NAT pool with the specified name exists, False otherwise.

        """
        cls.log.debug(f"pool_name_exists() Pool-Name: {pool_name}")
        return cls.rsdb.global_nat_pool_name_exists(pool_name).status
       
    def insert_global_nat_pool_name(cls, pool_name: str) -> bool:
        """
        Create a new global NAT pool configuration in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to create.

        Returns:
            bool: True if the NAT pool is created successfully, False otherwise.

        """
        try:
            if cls.pool_name_exists(pool_name):
                cls.log.debug(f"insert_global_pool_name() Check -> '{pool_name}' already exists.")
                cls.log.error(f"Global NAT pool '{pool_name}' already exists.")
                return STATUS_NOK

            result = cls.rsdb.insert_global_nat_pool(pool_name)

            if result.status == STATUS_OK:
                cls.log.debug(f"insert_global_pool_name() -> Created global NAT pool: {pool_name}")
                return STATUS_OK
            else:
                cls.log.error(f"Failed to create global NAT pool: {pool_name}")
                return STATUS_NOK

        except Exception as e:
            cls.log.error(f"An error occurred while creating global NAT pool: {e}")
            return STATUS_NOK

    def delete_global_nat_pool_name(cls, pool_name: str) -> bool:
        """
        Delete a global NAT pool configuration from the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to be deleted.

        Returns:
            bool: True if the NAT pool is deleted successfully, False otherwise.
        """
        try:
            if not cls.pool_name_exists(pool_name):
                cls.log.error(f"Global NAT pool '{pool_name}' does not exist.")
                return STATUS_NOK

            result = cls.rsdb.delete_global_nat_pool_name(pool_name)

            if result.status == STATUS_OK:
                cls.log.debug(f"Deleted global NAT pool: {pool_name}")
                return STATUS_OK
            else:
                cls.log.error(f"Failed to delete global NAT pool: {pool_name}")
                return STATUS_NOK

        except Exception as e:
            cls.log.error(f"An error occurred while deleting global NAT pool: {e}")
            return STATUS_NOK

    def get_global_nat_pool_names(cls) -> list:
        """
        Retrieve a list of global NAT pool names from the NAT database.

        Returns:
            list: A list of NAT pool names.
        """
        try:
            pool_names = cls.rsdb.select_global_nat_pool_names()

            cls.log.debug("Retrieved global NAT pool names: %s", pool_names)
            return pool_names

        except Exception as e:
            cls.log.error(f"An error occurred while retrieving global NAT pool names: {e}")
            return []

    def is_interface_direction_in_nat_pool(cls, interface_name: str, nat_pool_name: str, direction: str) -> Result:
        """
        Check if the specified interface is associated with the given NAT pool and direction.

        Args:
            interface_name (str): The name of the interface to check.
            nat_pool_name (str): The name of the NAT pool to check.
            direction (str): The direction to check (inside or outside).

        Returns:
            Result: A Result object with the following fields:
            - status (bool): True if the interface is found in the specified NAT pool and direction, False otherwise.
            - row_id (int): The row ID of the found entry, or 0 if not found.

        Raises:
            sqlite3.Error: If there is an error with the database query.

        """
        cls.log.debug(f"is_interface_direction_in_nat_pool({interface_name} -> {nat_pool_name} -> {direction})")
        return cls.rsdb.select_nat_interface_direction(interface_name, nat_pool_name, direction)

    def get_interface_direction_in_nat_pool_list(cls, nat_pool_name: str, direction: str) -> List[Result]:
        """
        Get list of interfaces is associated with the given NAT pool and direction.

        Args:
            nat_pool_name (str): The name of the NAT pool to check.
            direction (str): The direction to check (inside or outside).

        Returns List:
            Result: A Result object with the following fields:
            - status (bool): True if the interface is found in the specified NAT pool and direction, False otherwise.
            - row_id (int): The row ID of the found entry, or 0 if not found.

        Raises:
            sqlite3.Error: If there is an error with the database query.

        """
        cls.log.debug(f"get_interface_direction_in_nat_pool_list({nat_pool_name} -> {direction})")
        
        return cls.rsdb.select_nat_interface_direction_list(nat_pool_name, direction)

    def add_inside_interface(cls, nat_pool_name: str, interface_name: str) -> bool:
        """
        Add an inside interface to a NAT pool configuration.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the inside interface to add.

        Returns:
            bool: STATUS_OK if the inside interface is added successfully, STATUS_NOK otherwise.
        """
        from lib.network_manager.network_operations.nat import NATDirection
        
        cls.log.debug(f"add_inside_interface({nat_pool_name}, {interface_name})")
        
        try:
            pool_id_result = cls.rsdb.global_nat_pool_name_exists(nat_pool_name)

            if not pool_id_result.status:
                cls.log.error(f"Failed to retrieve NAT pool ID for '{nat_pool_name}': {pool_id_result.reason}")
                return STATUS_NOK

            if not cls.rsdb.interface_exists(interface_name):
                cls.log.error(f"Inside interface '{interface_name}' does not exist.")
                return STATUS_NOK

            if cls.rsdb.inside_interface_exists(nat_pool_name, interface_name).status:
                cls.log.error(f"Inside interface '{interface_name}' is already associated with '{nat_pool_name}'.")
                return STATUS_NOK

            result = cls.rsdb.insert_interface_nat_direction(interface_name, nat_pool_name, NATDirection.INSIDE.value)

            if result.status:
                cls.log.error(f"Failed to add inside interface '{interface_name}' to '{nat_pool_name}': {result.reason}")
                return STATUS_NOK
            else:
                cls.log.debug(f"Inserted inside interface '{interface_name}' to '{nat_pool_name}'.")
                return STATUS_OK

        except Exception as e:
            cls.log.error(f"An error occurred while adding inside interface to '{nat_pool_name}': {e}")
            return STATUS_NOK

    def delete_inside_interface(cls, pool_name: str, interface_name: str) -> bool:
        pass
    
    def add_outside_interface(cls, nat_pool_name: str, interface_name: str) -> bool:
        """
        Add an outside interface to a NAT pool configuration DB.

        Args:
            nat_pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the outside interface to add.

        Returns:
            bool: STATUS_OK if the outside interface is added successfully, STATUS_NOK otherwise.
        """
        from lib.network_manager.network_operations.nat import NATDirection
        
        cls.log.debug(f"add_outside_interface({nat_pool_name}, {interface_name})")
        
        try:
            pool_id_result = cls.rsdb.global_nat_pool_name_exists(nat_pool_name)
            
            if not pool_id_result.status:
                cls.log.error(f"Failed to retrieve NAT pool ID for '{nat_pool_name}': {pool_id_result.reason}")
                return STATUS_NOK
                        
            result = cls.rsdb.insert_interface_nat_direction(interface_name, nat_pool_name, NATDirection.OUTSIDE.value)

            if result.status:
                cls.log.error(f"Failed to insert outside interface '{interface_name}' to '{nat_pool_name}': {result.reason}")
                return STATUS_NOK
            else:
                cls.log.debug(f"Inserted outside interface '{interface_name}' to '{nat_pool_name}'.")
                return STATUS_OK

        except Exception as e:
            cls.log.error(f"An error occurred while inserting outside interface to '{nat_pool_name}': {e}")
            return STATUS_NOK
                    
    def delete_outside_interface(cls, pool_name: str, interface_name: str) -> str:
        pass
    