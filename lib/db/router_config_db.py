import logging
from itertools import count
from typing import Dict, List, Tuple

from lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.interface import InterfaceType

class RouterConfigurationDatabase:

    rsdb = DB()
    counter = count(start=1)
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLS().ROUTER_CONFIG_DB)
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = DB()
            
    def get_interface_name_list(cls, interface_type: InterfaceType = InterfaceType.UNKNOWN) -> List[str]:
        """
        Get a list of interface names based on the specified interface type.

        Args:
            interface_type (InterfaceType): The type of interface to filter by.

        Returns:
            List[str]: A list of interface names.
        """
        interface_list = []

        if interface_type == InterfaceType.UNKNOWN:
            interface_result_list = cls.rsdb.select_interfaces()
        else:
            interface_result_list = cls.rsdb.select_interfaces_by_interface_type(interface_type)

        for interface in interface_result_list:
            cls.log.debug(f"get_interface_name_list() -> {interface}")
            if interface.status == STATUS_OK:
                interface_names = interface.result.get('InterfaceName')

                # Ensure interface_names is a list, even if it contains a single value
                if isinstance(interface_names, str):
                    interface_list.append(interface_names)
                elif isinstance(interface_names, list):
                    interface_list.extend(interface_names)

        return interface_list
    
    def get_interface_configuration(cls, interface_name: str) -> Tuple[bool, dict]:
        """
        Get the configuration for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            Tuple[bool, dict]: A tuple containing a boolean indicating the status and a dictionary with the interface configuration.
        """
        if_result = cls.rsdb.select_interface_configuration(interface_name)
        
        cls.log.debug(f'Interface-Base-Config: {if_result}')
        
        return if_result.status, if_result.result

    def get_interface_dhcp_client_configuration(cls, interface_name: str) -> Tuple[bool, List[dict]]:
        """
        Retrieve DHCP client configuration information associated with a specific interface.

        Parameters:
            interface_name (str): The name of the interface for which to retrieve DHCP client configuration information.

        Returns:
            Tuple[bool, List[dict]]: A tuple containing a boolean indicating the success of the operation (True for success, False for failure)
                and a list of dictionaries representing the DHCP client configuration information.
                Each dictionary contains the DHCP client version information.

        Example:
            - (STATUS_OK, [{'DhcpClientVersion': 'ip dhcp-client'}, {'DhcpClientVersion': 'ipv6 dhcp-client '}])
            - (STATUS_NOK, [])  # In case of an error
        """
        sql_result = cls.rsdb.select_interface_dhcp_client_configuration(interface_name)

        if any(result.status for result in sql_result):
            error_messages = [result.reason for result in sql_result if result.status]
            cls.log.debug(f"Error retrieving interface {interface_name} DHCP client status. Skipping. Error messages: {', '.join(error_messages)}")
            return STATUS_NOK, []

        dhcp_config_list = [result.result for result in sql_result]

        return STATUS_OK, dhcp_config_list
        
    def get_interface_ip_address_configuration(cls, interface_name: str) -> Tuple[bool, List[dict]]:
        """
        Retrieve IP address configuration for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            Tuple[bool, List[dict]]: 
                A tuple containing a boolean indicating the success of the operation
                    and a list of dictionaries with IP address configuration data.
                If the operation is successful, the boolean will be True, and the list
                    will contain dictionaries with IP address details.
                If there is an error, the boolean will be False, and the list will be empty.
        """
        if_ip_result = cls.rsdb.select_interface_ip_address_configuration(interface_name)

        # Check if any errors occurred during the retrieval
        if any(result.status for result in if_ip_result):
            error_messages = [result.reason for result in if_ip_result if result.status]
            cls.log.debug(f"Error retrieving IP address configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        ip_config_list = [result.result for result in if_ip_result]

        return STATUS_OK, ip_config_list

    def get_interface_dhcp_server_polices(cls, interface_name: str) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Retrieve DHCP server policies for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            Tuple[bool, List[Dict[str, str]]]: 
                A tuple containing a boolean indicating the success of the operation
                    and a list of dictionaries with DHCP server policies data.
                If the operation is successful, the boolean will be True, and the list
                    will contain dictionaries with DHCP server policy details.
                If there is an error, the boolean will be False, and the list will be empty.
        """
        if_dhcp_serv_policy_result = cls.rsdb.select_interface_ip_dhcp_server_policies(interface_name)

        if any(result.status for result in if_dhcp_serv_policy_result):
            error_messages = [result.reason for result in if_dhcp_serv_policy_result if result.status]
            cls.log.debug(f"Error retrieving DHCP server policies, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        dhcp_server_policies = [result.result for result in if_dhcp_serv_policy_result]

        return STATUS_OK, dhcp_server_policies

    def get_interface_ip_static_arp_configuration(cls, interface_name: str) -> Tuple[bool, List[dict]]:
        """
        Retrieve IP static ARP configuration for a specific interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            Tuple[bool, List[dict]]: A tuple containing a boolean indicating the success of the operation
                                    and a list of dictionaries with IP static ARP configuration data.
                                    If the operation is successful, the boolean will be True, and the list
                                    will contain dictionaries with IP static ARP details.
                                    If there is an error, the boolean will be False, and the list will be empty.
        """
        if_static_arp_result = cls.rsdb.select_interface_ip_static_arp_configuration(interface_name)

        # Check if any errors occurred during the retrieval
        if any(result.status for result in if_static_arp_result):
            error_messages = [result.reason for result in if_static_arp_result if result.status]
            cls.log.debug(f"Error retrieving IP static ARP configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        static_arp_config_list = [result.result for result in if_static_arp_result]

        return STATUS_OK, static_arp_config_list

    def get_interface_wifi_configuration(cls, interface_name: str) -> Tuple[bool, List[dict]]:
        """
        Get the wireless wifi configuration for a specified interface.

        Args:
            interface_name (str): The name of the interface.

        Returns:
            Tuple[bool, List[dict]]: A tuple containing a boolean status and a list of dictionaries
            representing the wireless wifi configuration for the given interface.
        """
        wifi_config_result = cls.rsdb.select_interface_wifi_configuration(interface_name)

        # Extract data from the result list and build the list of dictionaries
        wifi_config_list = [result.result for result in wifi_config_result]

        cls.log.debug(f"WiFi Interface Config: {wifi_config_list}")

        return STATUS_OK, wifi_config_list
     
    def get_interface_rename_configuration(cls) -> Tuple[bool, List[Dict]]:
        """
        Retrieve data from the 'RenameInterface' table.

        Returns:
            Tuple[bool, List[Dict]]:
            - A tuple containing a boolean indicating the success of the operation
                    and a list of dictionaries with data from the 'RenameInterface' table.
            - If the operation is successful, the boolean will be True, and the list will contain dictionaries
                    with 'InitialInterface' and 'AliasInterface' values.
            - If there is an error, the boolean will be False, and the list will be empty.
        """
        cls.log.debug('get_interface_rename_configuration()')

        rename_list = []

        rename_result = cls.rsdb.select_global_interface_rename_configuration()

        # Check if any errors occurred during the retrieval
        if any(result.status for result in rename_result):
            error_messages = [result.reason for result in rename_result if result.status]
            cls.log.debug(f"Error retrieving rename-interface-line, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        for result in rename_result:
            rename_list.append(result.result)

        return STATUS_OK, rename_list

    def get_bridge_configuration(cls) -> Tuple[bool, List[Dict]]:
        """
        Retrieve bridge configuration data.

        Returns:
            Tuple[bool, List[Dict]]:
            - A tuple containing a boolean indicating the success of the operation
              and a list of dictionaries with bridge configuration data.
            - If the operation is successful, the boolean will be True, and the list will contain dictionaries
              with 'BridgeName', 'Protocol', 'StpStatus', and 'Shutdown' keys.
            - If there is an error, the boolean will be False, and the list will be empty.
        """
        cls.log.debug('get_bridge_configuration()')

        bridge_config_list = []

        bridge_result = cls.rsdb.select_global_bridge_configuration()

        # Check if any errors occurred during the retrieval
        if any(result.status for result in bridge_result):
            error_messages = [result.reason for result in bridge_result if result.status]
            cls.log.debug(f"Error retrieving bridge configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        for result in bridge_result:
            bridge_config_list.append(result.result)

        return STATUS_OK, bridge_config_list

    def get_vlan_configuration(cls) -> Tuple[bool, List[Dict]]:
        """
        Retrieve VLAN configuration data.

        Returns:
            Tuple[bool, List[Dict]]:CONFIG_MODE
            - A tuple containing a boolean indicating the success of the operation
              and a list of dictionaries with VLAN configuration data.
            - If the operation is successful, the boolean will be True, and the list will contain dictionaries
              with 'VlanID', 'VlanDescription', and 'VlanName' keys.
            - If there is an error, the boolean will be False, and the list will be empty.
        """
        cls.log.debug('get_vlan_configuration()')

        vlan_config_list = []

        vlan_result = cls.rsdb.select_global_vlan_configuration()

        # Check if any errors occurred during the retrieval
        if any(result.status for result in vlan_result):
            error_messages = [result.reason for result in vlan_result if result.status]
            cls.log.debug(f"Error retrieving VLAN configuration, skipping: {', '.join(error_messages)}")
            return STATUS_NOK, []

        # Extract data from the result list and build the list of dictionaries
        for result in vlan_result:
            vlan_config_list.append(result.result)

        return STATUS_OK, vlan_config_list

    def get_nat_configuration(cls) -> Tuple[bool, List[Dict]]:
        """
        Get the NAT configurations.

        Returns:
        Tuple[bool, List[Dict]]: A tuple containing a boolean indicating success and a list of NAT configurations as dictionaries.
        """
        cls.log.debug('get_nat_configuration()')

        nat_config_list = []

        nat_result = cls.rsdb.select_global_nat_configuration()

        if all(result.status == STATUS_OK for result in nat_result):
            nat_config_list = [result.result for result in nat_result]
            cls.log.debug(f"Retrieved NAT configurations: {nat_config_list}")
            return STATUS_OK, nat_config_list

        else:
            cls.log.error("Failed to retrieve NAT configurations.")
            return STATUS_NOK, []

    def get_dhcp_server_configuration(cls) -> Tuple[bool, List[Dict]]:
        """
        Retrieve global DHCP server configuration data, including pool details, reservations, and subnet options.

        Returns:
            Tuple[bool, List[Dict]]: A tuple containing a boolean status and a list of dictionaries representing DHCP server configuration data.
            - The boolean status is STATUS_OK if the retrieval is successful, and STATUS_NOK otherwise.
            - The list includes dictionaries for each type of data, making it easy to distinguish between pool details,
              reservations, and subnet options.

        Note:
        - The returned list includes dictionaries for each type of data, providing a structured format for the DHCP server configuration.
        - If the retrieval is unsuccessful, the method returns a tuple with a status of STATUS_NOK and an empty list.
        """
        dhcp_server_config_result = cls.rsdb.select_global_dhcp_server_configuration()
        config_data = []

        if all(result.status == STATUS_OK for result in dhcp_server_config_result):
            
            for dsc_result in dhcp_server_config_result:
                
                #config line -> dhcp pool-name <dhcp-pool-name> -> index 2
                dhcp_pool_name_index = 2
                pool_name = dsc_result.result.get('DhcpServerPoolName').split()[dhcp_pool_name_index]
                
                combined_data = dsc_result.result

                dhcp_server_pool_results = cls.rsdb.select_global_dhcp_server_pool(pool_name)
                for data in dhcp_server_pool_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})

                dhcp_server_reservation_results = cls.rsdb.select_global_dhcp_server_reservation_pool(pool_name)
                for data in dhcp_server_reservation_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})

                dhcp_server_option_subnet_results = cls.rsdb.select_global_dhcp_server_subnet_option_pool(pool_name)
                for data in dhcp_server_option_subnet_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})

                dhcp_server_option_results = cls.rsdb.select_global_dhcpv6_server_options(pool_name)
                for data in dhcp_server_option_results:
                    for key, value in data.result.items():
                        combined_data.update({f"{key}-{str(next(cls.counter))}": value})                
                
                config_data.append(combined_data)

        else:
            return STATUS_NOK, config_data
        
        return STATUS_OK, config_data

    def get_banner(cls) -> Tuple[bool, Dict]:
        """
        Retrieve the banner Message of the Day (Motd) from the database.

        Args:
            cls: The RouterShellDB class.

        Returns:
            Tuple[bool, Dict]: A tuple containing a boolean indicating the operation's success or failure,
            and a dictionary with the banner Motd if found.

        """
        result = cls.rsdb.select_banner_motd()

        if result.status:
            cls.log.debug("Banner not found in the database.")
            return STATUS_NOK, {}
        
        return STATUS_OK, result.result

    def get_wifi_policy_configuration(cls) -> Tuple[bool, Dict]:
        """
        Retrieves WiFi policy configuration data including global policy information and associated security policies.

        Returns:
        - Tuple[bool, Dict]: A tuple containing a boolean status and a dictionary with WiFi policy configuration data.

        """
        wifi_policy_result = cls.rsdb.select_wifi_policies()
        config_data = {}

        if all(result.status == STATUS_OK for result in wifi_policy_result):
            
            for wp_result in wifi_policy_result:
                wifi_policy = wp_result.result.get('WifiPolicyName')

                wp_config = cls.rsdb.select_global_wireless_wifi_policy(wifi_policy)
                temp_config = wp_config.result

                wifi_sec_policy_list = cls.rsdb.select_global_wireless_wifi_security_policy(wifi_policy)
                wifi_sec_policy_data = []

                for wifi_sec_policy_item in wifi_sec_policy_list:
                    ssid = wifi_sec_policy_item.get('Ssid')
                    passphrase = wifi_sec_policy_item.get('WpaPassPhrase')
                    version = wifi_sec_policy_item.get('WpaVersion')

                    wifi_sec_policy_data.append({
                        'Ssid': ssid,
                        'Passphrase': passphrase,
                        'Version': version
                    })

                temp_config['WifiSecurityPolicy'] = wifi_sec_policy_data

                config_data[wifi_policy] = temp_config

        cls.log.debug(f'{config_data}')

        return STATUS_OK if config_data else STATUS_NOK, config_data
