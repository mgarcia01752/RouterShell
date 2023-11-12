import logging
from typing import Dict, List

from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK

class DHCPServerDatabase:
    """
    A class for interacting with the DHCP server database.
    """
    def __init__(self):
        """
        Initialize the DHCPServerDatabase class.

        This constructor sets up the class logger and connects to the RouterShell database if not already connected.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_SERVER_DB)

    def dhcp_pool_name_exists_db(self, dhcp_pool_name: str) -> bool:
        """
        Check if a DHCP pool name exists in the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name to check.

        Returns:
            bool: True if the DHCP pool name exists, False otherwise.
        """
        return RSDB().dhcp_pool_name_exist(dhcp_pool_name).status
    
    def dhcp_pool_subnet_exist_db(self, inet_subnet_cidr: str) -> bool:
        """
        Check if a DHCP pool subnet with the given subnet CIDR exists in the database.

        Args:
            inet_subnet_cidr (str): The subnet CIDR to check for existence.

        Returns:
            bool: True if the DHCP pool subnet exists, False otherwise.
        """
        return RSDB().dhcp_pool_subnet_exist(inet_subnet_cidr).status

    def get_dhcp_pool_subnet_name_db(self, dhcp_pool_name: str) -> str:
        """
        Retrieve the DHCP pool subnet from the RouterShell database using the provided DHCP pool name.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            str or None: The DHCP pool subnet information retrieved from the RouterShell database, or None if no match is found.
        """        
        result = RSDB().select_dhcp_pool_subnet_via_dhcp_pool_name(dhcp_pool_name)
        if not result.status:
            return result.result['InetSubnet']
        else:
            return None

    def add_dhcp_pool_name_db(self, dhcp_pool_name: str) -> bool:
        """
        Add a DHCP pool name to the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to add.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return RSDB().insert_dhcp_pool_name(dhcp_pool_name).status

    def add_dhcp_pool_subnet_db(self, dhcp_pool_name: str, inet_subnet_cidr: str) -> bool:
        """
        Add a DHCP pool subnet to the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name.
            inet_subnet_cidr (str): The subnet CIDR to add to the pool.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return RSDB().insert_dhcp_pool_subnet(dhcp_pool_name, inet_subnet_cidr).status

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
        return RSDB().insert_dhcp_subnet_inet_address_range(inet_subnet_cidr, 
                                                          inet_address_start, 
                                                          inet_address_end, 
                                                          inet_address_subnet_cidr).status

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
        return RSDB().insert_dhcp_subnet_reservation(inet_subnet_cidr, hw_address, inet_address).status

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
        return RSDB().insert_dhcp_subnet_option(inet_subnet_cidr, dhcp_option, option_value).status

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
        return RSDB().insert_dhcp_subnet_reservation_option(inet_subnet_cidr, hw_address, dhcp_option, option_value).status

    def update_dhcp_pool_name_interface(self, dhcp_pool_name: str, interface_name: str) -> bool:
        """
        Update the interface associated with a DHCP pool in the database.

        Args:
            dhcp_pool_name (str): The DHCP pool name.
            interface_name (str): The new interface name.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        return RSDB().update_dhcp_pool_name_interface(dhcp_pool_name, interface_name).status


    '''
                                DHCP-DNSMasq - Configuration Building
    '''

    def get_global_options(self) -> List[List]:
        return []

    def get_dhcp_poll_interfaces_db(self, dhcp_pool_name: str) -> List[Dict]:
        """
        Retrieve the interfaces associated with a DHCP pool name from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool.

        Returns:
            List[Dict]: A list of dictionaries, each representing an interface with the 'interface_name' field,
            or an empty list if none are found.
        """
        sql_result = RSDB().select_dhcp_pool_interfaces(dhcp_pool_name)
                
        results = []

        for result in sql_result:
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'interface_name': result_data['interface_name'],
                }
                results.append(entry)

        return results

    def get_dhcp_pool_inet_range_db(self, dhcp_pool_name: str) -> List[Dict]:
        """
        Retrieve the DHCP pool's internet range information from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to query.

        Returns:
            List[Dict]: A list of dictionaries containing internet range information.
                Each dictionary has the following keys:
                - 'inet_start' (str): The start of the internet range.
                - 'inet_end' (str): The end of the internet range.
                - 'inet_subnet' (str): The subnet of the internet range.
        """
        sql_result = RSDB().select_dhcp_pool_inet_range(dhcp_pool_name)
        results = []

        for result in sql_result:
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'inet_start': result_data['inet_start'],
                    'inet_end': result_data['inet_end'],
                    'inet_subnet': result_data['inet_subnet'],
                }
                results.append(entry)

        return results

    def get_dhcp_pool_reservation_db(self, dhcp_pool_name: str) -> List[Dict]:
        """
        Retrieve the DHCP pool's reservation information from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to query.

        Returns:
            List[Dict]: A list of dictionaries containing reservation information.
                Each dictionary has the following keys:
                - 'mac_address' (str): The MAC address of the reserved device.
                - 'inet_address' (str): The internet address reserved for the device.
        """
        sql_result = RSDB().select_dhcp_pool_reservation(dhcp_pool_name)
        results = []

        for result in sql_result:
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'mac_address': result_data['mac_address'],
                    'inet_address': result_data['inet_address'],
                }
                results.append(entry)

        return results

    def get_dhcp_pool_options_db(self, dhcp_pool_name: str) -> List[Dict]:
        """
        Retrieve the DHCP pool's options information from the database.

        Args:
            dhcp_pool_name (str): The name of the DHCP pool to query.

        Returns:
            List[Dict]: A list of dictionaries containing DHCP options information.
                Each dictionary has the following keys:
                - 'option' (str): The DHCP option.
                - 'value' (str): The value associated with the option.
        """
        sql_result = RSDB().select_dhcp_pool_options(dhcp_pool_name)
        results = []
        
        for result in sql_result:
            self.log.debug(f"get_dhcp_pool_options_db({dhcp_pool_name}) -> SQL-RESULT: {result.result}")
            if result.status == STATUS_OK:
                result_data = result.result
                entry = {
                    'option': result_data['option'],
                    'value': result_data['value'],
                }
                results.append(entry)

        return results

    