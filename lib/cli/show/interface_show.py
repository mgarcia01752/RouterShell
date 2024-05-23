import json
import logging

from tabulate import tabulate
from lib.network_manager.interface import Interface
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class InterfaceShow(Interface):
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().IF_SHOW)
        self.arg = arg
    
    def show_interface_statistics(self, interface_name=None):
        if interface_name:
            command = ["ip", "-json", "-s", "link", "show", interface_name]
        else:
            command = ["ip", "-json", "-s", "link", "show"]

        result = self.run(command)
                    
        interface_data = result.stdout

        parsed_data = json.loads(interface_data)

        headers = ["Interface Name", "MAC Address", "Tx Bytes", "Tx Packets", "Rx Bytes", "Rx Packets", "Rx Errors", "Rx Drops"]

        rows = []
        for entry in parsed_data:
            interface_name = entry["ifname"]
            mac_address = entry["address"]
            tx_bytes = entry["stats64"]["tx"]["bytes"]
            tx_packets = entry["stats64"]["tx"]["packets"]
            rx_bytes = entry["stats64"]["rx"]["bytes"]
            rx_packets = entry["stats64"]["rx"]["packets"]
            rx_errors = entry["stats64"]["rx"]["errors"]
            rx_drops = entry["stats64"]["rx"]["dropped"]            

            rows.append([interface_name, mac_address, tx_bytes, tx_packets, rx_bytes, rx_packets, rx_errors, rx_drops])

        table = tabulate(rows, headers=headers, tablefmt="simple")

        print(table)

    def show_ip_interface_brief(self):
        """
        Display a brief summary of IP interfaces.

        This function retrieves IP interface information using the `get_ip_addr_info` method and
        displays it in a tabular format. It includes interface name, MAC address, IP addresses
        (both IPv4 and IPv6), operational state, and protocol.

        If no IP address is assigned to an interface, it is marked as "unassigned."

        The output is printed to the console.

        Args:
            None

        Returns:
            None
        """
        ip_info_json = self.get_ip_addr_info()
        
        table = []
        for interface in ip_info_json:
            interface_name = interface["ifname"]
            mac = interface.get("address", "N/A")
            inet_addresses = []
            inet6_addresses = []
            for addr_info in interface["addr_info"]:
                if addr_info["family"] == "inet":
                    address = addr_info["local"]
                    if self.is_secondary_address(interface, address):
                        address += " (s)"
                    inet_addresses.append(address)
                elif addr_info["family"] == "inet6":
                    inet6_addresses.append(addr_info["local"])

            inet_str = "\n".join(inet_addresses) if inet_addresses else "unassigned"
            inet6_str = "\n".join(inet6_addresses) if inet6_addresses else "unassigned"

            state = interface.get("operstate", "N/A")
            protocol = interface.get("link_type", "N/A")

            table.append([interface_name, mac, inet_str, inet6_str, state, protocol])

        headers = ["Interface", "mac", "inet", "inet6", "state", "protocol"]
        print(tabulate(table, headers, tablefmt="simple"))

