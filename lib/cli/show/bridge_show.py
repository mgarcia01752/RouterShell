import json
import logging
from typing import Any, Dict, List

from tabulate import tabulate

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.network_operations.bridge import Bridge

class BridgeShow(RunCommand):
    """Command set for showing Bridge-Show-Command"""

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg

    def bridge(self, arg=None):
        Bridge().get_bridge()

    def show_bridge_group_interface_table(self) -> bool:
        
        json_data = self.run(['ip', '-json', 'addr'])
        
        if json_data.exit_code:
            self.log.error(f"Failed to get bridge group interface table: {json_data.stderr}")
            return STATUS_NOK
        
        try:
            network_data: List[Dict[str, Any]] = json.loads(json_data.stdout)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON data: {e}")
            exit()        
        
        bridge_group_interfacess: List[Dict[str, str]] = []

        for item in network_data:
            # Check if the item has a 'master' key
            if 'master' in item:
                bridge_name = item['master']
                # Collect INET addresses
                inet_addresses = [
                    f"{info['local']}/{info['prefixlen']}"
                    for info in item.get('addr_info', [])
                    if info['family'] == 'inet'
                ]
                bridge_group_interfacess.append({
                    'Bridge Name': bridge_name,
                    'Interface': item['ifname'],
                    'INET Address': '\n'.join(inet_addresses)
                })
                    
        print(tabulate(bridge_group_interfacess, headers='keys', tablefmt='simple'))
        
        return STATUS_OK

    def show_bridges(self, args=None):
        # Run the 'ip -json link show type bridge' command and capture its output
        result = self.run(['ip', '-json', 'link', 'show', 'type', 'bridge'])

        # Check if the command was successful
        if result.exit_code != 0:
            print("Error executing 'ip -json link show type bridge'.")
            return

        # Parse the JSON output
        json_data = result.stdout

        # Parse the JSON data into a list of bridge interfaces
        bridge_data = json.loads(json_data)

        # Prepare data for tabulation
        table_data = []

        # Check if bridge_data is a list
        if isinstance(bridge_data, list):
            for info in bridge_data:
                bridge_name = info.get("ifname", "")
                ether = info.get("address", "")
                flags = info.get("flags", [])
                state = "UP" if "UP" in flags else "DOWN"

                table_data.append([bridge_name, ether, state])
        else:
            bridge_name = bridge_data.get("ifname", "")
            ether = bridge_data.get("address", "")
            flags = bridge_data.get("flags", [])
            state = "UP" if "UP" in flags else "DOWN"

            table_data.append([bridge_name, ether, state])

        # Define headers
        headers = ["Bridge Name", "ether", "State"]

        # Display the table using tabulate
        table = tabulate(table_data, headers, tablefmt="simple")

        print(table)

    def show_bridges_new(self):
        """
        Get a formatted table of bridge information using the tabulate library.

        Returns:
            str: A formatted table as a string.
        """

        def parse_ip_addr():
            result = self.run(['ip', '-j', 'addr', 'show'])
            if result.exit_code:
                self.log("Unable to get IP addresses")
                return []
            return json.loads(result.stdout)

        def parse_ip_link():
            result = self.run(['ip', '-j', 'link', 'show', 'type', 'bridge'])
            if result.exit_code:
                self.log("Unable to get bridge links")
                return []
            return json.loads(result.stdout)

        def get_ip_for_interface(interface):
            ip_data = parse_ip_addr()
            ipv4, ipv6 = None, None
            for iface in ip_data:
                if iface['ifname'] == interface:
                    for addr in iface.get('addr_info', []):
                        if addr['family'] == 'inet':
                            ipv4 = addr['local']
                        elif addr['family'] == 'inet6':
                            ipv6 = addr['local']
            return ipv4, ipv6

        bridges = parse_ip_link()
        bridge_data = []

        for bridge in bridges:
            bridge_ifname = bridge['ifname']
            bridge_mac = bridge['address']
            bridge_state = bridge['operstate']
            
            ipv4, ipv6 = get_ip_for_interface(bridge_ifname)
            
            interfaces = self.run(['bridge', '-j', 'link', 'show', 'dev', bridge_ifname])
            if interfaces.exit_code:
                self.log(f"Unable to get interfaces for bridge {bridge_ifname}")
                interface_names = []
            else:
                interface_data = json.loads(interfaces.stdout)
                interface_names = [iface['ifname'] for iface in interface_data]

            bridge_data.append({
                'Bridge': bridge_ifname,
                'Mac': bridge_mac,
                'IPv4': ipv4,
                'IPv6': ipv6,
                'State': bridge_state,
                'Interfaces': ", ".join(interface_names)
            })

        headers = ['Bridge', 'Mac', 'IPv4', 'IPv6', 'State', 'Interfaces']

        print(tabulate(bridge_data, headers=headers, tablefmt='simple'))
        
        
