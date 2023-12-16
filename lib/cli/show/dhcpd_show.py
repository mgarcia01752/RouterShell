import logging
from tabulate import tabulate
from lib.common.common import Common

from lib.network_manager.dhcp_server import DhcpServerManager

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
        leases = DhcpServerManager().get_all_leases()

        # Extract lease information for tabulation
        table_data = [(lease['hostname'], lease['ip_address'], lease['mac_address'], Common().convert_timestamp(int(lease['expires']))) for lease in leases]

        # Define table headers
        headers = ['Hostname', 'IP Address', 'MAC Address', 'Expiry Time']

        # Use tabulate to format the data as a table
        formatted_table = tabulate(table_data, headers, tablefmt="simple")

        # Print the formatted table
        print(formatted_table)

        
    def status(self):
        pass
    
    def config(self, interface_name:str):
        pass
    
    