import logging
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_services.dhcp.common.dhcp_common import DHCPVersion

class DHCPClientDatabase:
    rsdb = RSDB()
    log = logging.getLogger(__name__)

    def __init__(self):
        """
        Initializes the DHCPClientDatabase instance and sets up logging.
        """
        self.log.setLevel(RSLGS().INTERFACE_DB)

    @classmethod
    def add_db_dhcp_client(
        cls, interface_name: str, dhcp_version: DHCPVersion) -> bool:
        """
        Adds a DHCP client entry to the database for a specified interface.

        Args:
            interface_name (str): The name of the network interface to update.
            dhcp_version (DHCPVersion): The version of the DHCP stack to add.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return cls.rsdb.insert_interface_dhcp_client(interface_name, dhcp_version.value)

    @classmethod
    def update_db_dhcp_client(
        cls, interface_name: str, dhcp_version: DHCPVersion) -> bool:
        """
        Updates the DHCP client entry in the database for a specified interface.

        Args:
            interface_name (str): The name of the network interface to update.
            dhcp_version (DHCPVersion): The version of the DHCP stack to set.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return cls.rsdb.update_interface_dhcp_client(interface_name, dhcp_version.value).status

    @classmethod
    def remove_db_dhcp_client(
        cls, interface_name: str, dhcp_version: DHCPVersion) -> bool:
        """
        Removes a DHCP client entry from the database for a specified interface.

        Args:
            interface_name (str): The name of the network interface to update.
            dhcp_version (DHCPVersion): The version of the DHCP stack to remove.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return cls.rsdb.remove_interface_dhcp_client(interface_name, dhcp_version.value).status
