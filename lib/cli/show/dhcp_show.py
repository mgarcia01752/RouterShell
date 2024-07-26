import logging
from typing import List
from tabulate import tabulate
from lib.common.common import Common
from lib.common.constants import STATUS_OK
from lib.network_manager.network_operations.dhcp.client.dhcp_client import DHCPClient
from lib.network_manager.network_operations.dhcp.server.dhcp_server import DhcpServerManager

class DHCPClientShow():
    """Command set for showing DHCPClient-Show-Command"""

    def __init__(self, args=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.args = args
    
    def flow_log(self) -> List[str]:
        """
        Retrieve DHCP client flow logs related to IPv4 address assignment from the system journal.

        Returns:
            List[str]: A list of DHCP client flow log entries related to IPv4 address assignment.
        """
        for line in DHCPClient.get_flow_log():
            print(line)    

class DHCPServerShow():
    """Command set for showing DHCPServer-Show-Command"""

    def __init__(self, args=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.args = args
    
    def leases(self):
        """
        Display DHCP leases using tabulate.
        """

        # Assuming DhcpServerManager().get_all_leases() returns a list of lease dictionaries
        leases = DhcpServerManager().get_leases()

        # Extract lease information for tabulation
        table_data = [(lease['hostname'], lease['ip_address'], lease['mac_address'], Common().convert_timestamp(int(lease['expires']))) for lease in leases]

        # Define table headers
        headers = ['Hostname', 'IP Address', 'MAC Address', 'Expiry Time']

        # Use tabulate to format the data as a table
        formatted_table = tabulate(table_data, headers, tablefmt="simple")

        # Print the formatted table
        print(formatted_table)

    def status(self) -> str:
        """
        Get the status of the DHCP server.

        Returns:
            str: The status of the DHCP server. Possible values are 'Active' or 'Not Active'.
        """
        if DhcpServerManager().status() == STATUS_OK:
            return 'Active'
        else:
            return 'Not Active'

    def dhcp_lease_log(self) -> List[str]:
        """
        Get the DHCP-related log entries from the system journal.

        Returns:
            List[str]: A list of DHCP-related log entries.
        """
        for line in DhcpServerManager().lease_log():
            print(line)

    def dhcp_server_log(self) -> List[str]:
        """
        Get the DHCP-related log entries from the system journal.

        Returns:
            List[str]: A list of DHCP-related log entries.
        """
        for line in DhcpServerManager().server_log():
            print(line)
    
    