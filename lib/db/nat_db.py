import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB, Result

from lib.cli.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.cli.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.nat import *


class NatDB:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().NAT_DB)
        
        '''CMD2 DEBUG LOGGING'''
        cls.debug = CGS().DEBUG_NAT_DB
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()  

    def pool_name_exists(cls, pool_name: str) -> bool:
        """
        Check if a NAT pool with the given name exists in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to check for existence.

        Returns:
            bool: True if a NAT pool with the specified name exists, False otherwise.

        This method queries the NAT database to determine whether a NAT pool with the
        provided name exists.

        Args:
            - pool_name (str): The name of the NAT pool to check for existence.

        Returns:
            - bool: True if a NAT pool with the specified name exists, False otherwise.

        """
        cls.log.debug(f"pool_name_exists() Pool-Name: {pool_name}")
        return cls.rsdb.global_nat_pool_name_exists(pool_name).status
       
    def insert_global_pool_name(cls, pool_name: str) -> bool:
        """
        Create a new global NAT pool configuration in the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to create.

        Returns:
            bool: True if the NAT pool is created successfully, False otherwise.

        This method allows you to create a new global NAT pool configuration in the NAT database.

        Args:
            - pool_name (str): The name of the NAT pool to create.

        Returns:
            - bool: STATUS_OK if the NAT pool is created successfully, STATUS_NOK if there was an error during creation.
        """
        try:
            # Check if the NAT pool already exists
            if cls.pool_name_exists(pool_name):
                cls.log.debug(f"insert_global_pool_name() Check -> '{pool_name}' already exists.")
                cls.log.error(f"Global NAT pool '{pool_name}' already exists.")
                return STATUS_NOK

            # Create the NAT pool
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

    def delete_global_pool_name(cls, pool_name: str) -> bool:
        """
        Delete a global NAT pool configuration from the NAT database.

        Args:
            pool_name (str): The name of the NAT pool to be deleted.

        Returns:
            bool: True if the NAT pool is deleted successfully, False otherwise.
        """
        try:
            # Check if the NAT pool exists before attempting to delete it
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

    def get_global_pool_names(cls) -> list:
        """
        Retrieve a list of global NAT pool names from the NAT database.

        Returns:
            list: A list of NAT pool names.
        """
        try:
            # Retrieve the list of NAT pool names from the database
            pool_names = cls.rsdb.get_global_nat_pool_names()

            cls.log.debug("Retrieved global NAT pool names: %s", pool_names)
            return pool_names

        except Exception as e:
            cls.log.error(f"An error occurred while retrieving global NAT pool names: {e}")
            return []

    def add_inside_interface(cls, pool_name: str, interface_name: str) -> bool:
        """
        Add an inside interface to a NAT pool configuration.

        Args:
            pool_name (str): The name of the NAT pool.
            interface_name (str): The name of the inside interface to add.

        Returns:
            bool: True if the inside interface is added successfully, False otherwise.
        """
        try:
            # Check if the NAT pool exists
            if not cls.rsdb.pool_name_exists(pool_name):
                cls.log.error(f"Global NAT pool '{pool_name}' does not exist.")
                return False

            # Retrieve the NAT pool ID based on its name
            pool_id_result = cls.rsdb.get_global_nat_row_id(pool_name)

            if not pool_id_result.status:
                cls.log.error(f"Failed to retrieve NAT pool ID for '{pool_name}': {pool_id_result.result}")
                return False

            pool_id = pool_id_result.row_id

            # Check if the inside interface exists
            if not cls.interface_exists(interface_name):
                cls.log.error(f"Inside interface '{interface_name}' does not exist.")
                return False

            # Retrieve the inside interface ID based on its name
            interface_id_result = cls.rsdb.get_interface_id(interface_name)

            if not interface_id_result.status:
                cls.log.error(f"Failed to retrieve interface ID for '{interface_name}': {interface_id_result.result}")
                return False

            interface_id = interface_id_result.row_id

            # Check if the inside interface is already associated with the NAT pool
            if cls.rsdb.inside_interface_exists(pool_id, interface_id):
                cls.log.error(f"Inside interface '{interface_name}' is already associated with '{pool_name}'.")
                return False

            # Add the inside interface to the NAT pool
            result = cls.rsdb.insert_interface_nat_direction(interface_name, pool_name, NATDirection.INSIDE)

            if result.status == STATUS_OK:
                cls.log.debug(f"Added inside interface '{interface_name}' to '{pool_name}'.")
                return True
            else:
                cls.log.error(f"Failed to add inside interface '{interface_name}' to '{pool_name}': {result.result}")
                return False

        except Exception as e:
            cls.log.error(f"An error occurred while adding inside interface to '{pool_name}': {e}")
            return False

    def delete_inside_interface(cls, pool_name: str, interface_name: str) -> bool:
        pass
    
    def add_outside_interface(cls, pool_name: str, interface_name: str) -> bool:
        pass
                    
    def delete_outside_interface(cls, pool_name: str, interface_name: str) -> str:
        pass
    