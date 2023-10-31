import logging
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK

class DHCPServerDatabase:
    """
    A class for interacting with the DHCP server database.
    """

    rsdb = RSDB()

    def __init__(self):
        """
        Initialize the DHCPServerDatabase class.

        This constructor sets up the class logger and connects to the RouterShell database if not already connected.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_SERVER_DB)

        if not self.rsdb:
            self.log.debug("Connecting to RouterShell Database")
            self.rsdb = RSDB()

    def dhcp_pool_name_exists_db(self, dhcp_pool_name: str) -> bool:
        """
        Check if a DHCP pool name exists in the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name to check.

        Returns:
            bool: True if the DHCP pool name exists, False otherwise.
        """
        return self.rsdb.dhcp_pool_name_exist(dhcp_pool_name).status

    def add_dhcp_pool_subnet_db(self, dhcp_pool_name: str, inet_subnet_cidr: str) -> bool:
        """
        Add a DHCP pool subnet to the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name.
            inet_subnet_cidr (str): The subnet CIDR to add to the pool.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return self.rsdb.insert_dhcp_pool_subnet(dhcp_pool_name, inet_subnet_cidr).status

    def add_dhcp_subnet_inet_address_range_db(self, inet_subnet_cidr: str, inet_address_start: str, inet_address_end: str, inet_address_subnet_cidr: str) -> bool:
        """
        Add an address range to a DHCP subnet in the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add the address range to.
            inet_address_start (str): The start address of the range.
            inet_address_end (str): The end address of the range.
            inet_address_subnet_cidr (str): The subnet CIDR of the address range.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return self.insert_dhcp_subnet_inet_address_range(inet_subnet_cidr, inet_address_start, inet_address_end, inet_address_subnet_cidr).status

    def add_dhcp_subnet_reservation_db(self, inet_subnet_cidr: str, hw_address: str, inet_address: str) -> bool:
        """
        Add a DHCP subnet reservation to the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add the reservation to.
            hw_address (str): The hardware address of the reservation.
            inet_address (str): The reserved IP address.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return self.rsdb.insert_dhcp_subnet_reservation(inet_subnet_cidr, hw_address, inet_address).status

    def add_dhcp_subnet_option_db(self, inet_subnet_cidr: str, dhcp_option: str, option_value: str) -> bool:
        """
        Add a DHCP subnet option to the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to add the option to.
            dhcp_option (str): The DHCP option to add.
            option_value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return self.rsdb.insert_dhcp_subnet_option(inet_subnet_cidr, dhcp_option, option_value).status

    def add_dhcp_subnet_reservation_option_db(self, inet_subnet_cidr: str, hw_address: str, dhcp_option: str, option_value: str) -> bool:
        """
        Add a DHCP subnet reservation option to the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR of the reservation.
            hw_address (str): The hardware address of the reservation.
            dhcp_option (str): The DHCP option to add.
            option_value (str): The value of the DHCP option.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return self.rsdb.insert_dhcp_subnet_reservation_option(inet_subnet_cidr, hw_address, dhcp_option, option_value).status

    def update_dhcp_pool_name_interface(self, dhcp_pool_name: str, interface_name: str) -> bool:
        """
        Update the interface associated with a DHCP pool in the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name.
            interface_name (str): The new interface name.

        Returns:
            bool:  if the operation was successful, STATUS_NOK otherwise.
        """
        return self.rsdb.update_dhcp_pool_name_interface(dhcp_pool_name, interface_name).status
