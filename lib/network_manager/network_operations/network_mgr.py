import ipaddress
import json
import logging
import subprocess
from typing import List
from tabulate import tabulate

from lib.network_manager.common.inet import InetServiceLayer
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.common.constants import STATUS_NOK, STATUS_OK

class InterfaceNotFoundError(Exception):
    """
    Exception raised when a network interface is not found.
    """

    def __init__(self, message="Network interface not found"):
        self.message = message
        super().__init__(self.message)


class NetworkManager(InetServiceLayer):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().NETWORK_MANAGER)
    
    def net_mgr_interface_exist(self, interface_name) -> bool:
        """
        Check if a network interface with the given name exists on the system.

        This method uses the 'ip link' command to list all network interfaces on
        the system and checks if the specified interface name exists in the output.

        Args:
            interface_name (str): The name of the network interface to check.

        Returns:
            bool: A status indicating whether the interface is valid or not.
            - 'True': If the interface exists.
            - 'False': If the interface does not exist or an error occurred.
        """
        command = ['ip', 'link', 'show', interface_name]

        try:
            # Run the 'ip link' command using self.run()
            result = self.run(command)

            # Check the exit code to determine the status
            if result.exit_code == 0:
                return True
            else:
                return False
        except Exception as e:
            # Handle any errors that occurred during the command execution
            print(f"Error: {e}")
            return 'STATUS_NOK'

    def flush_interface(self, interface_name: str) -> bool:
        """
        Flush the configuration of a specific network interface.

        This method uses the 'ip addr flush' command to remove all configurations from the specified network interface.

        Args:
            interface_name (str): The name of the network interface to flush.

        Returns:
            bool: STATUS_OK if the flush process is successful, STATUS_NOK otherwise.
        """
        self.log.debug(f"flush_interface() -> interface_name: {interface_name}")

        if not self.net_mgr_interface_exist(interface_name):
            return STATUS_NOK

        if self.run(['ip', 'addr', 'flush', 'dev', f"{interface_name}"], suppress_error=True):
            self.log.debug(f'Unable to flush interface: {interface_name}')
            return STATUS_NOK

        return STATUS_OK

    def get_vlan_interfaces(self) -> List[str]:
        return []
    
    def get_interfaces(self, args=None):
        """
        Display information about network interfaces.

        This method uses the 'ip' command from the 'iproute2' tool to list and display information
        about network interfaces. It formats the output using the 'tabulate' library.

        Args:
            args (str, optional): Additional arguments (not used). Default is None.

        Returns:
            None
        """
        try:
            # Run the 'ip' command and capture the output
            output = self.run(['ip', 'addr', 'show'])

            # Split the output into interface sections
            interface_sections = output.stdout.strip().split('\n\n')

            # Initialize the data list for tabulation
            data = []

            for section in interface_sections:
                lines = section.strip().split('\n')
                interface_name = lines[0].split(':')[1].strip()

                inet_addresses = []
                inet6_addresses = []
                ether_address = ""
                state = ""

                for line in lines:
                    if 'inet ' in line:
                        inet_parts = line.strip().split()
                        subnet_cidr = str(ipaddress.IPv4Network(f'{inet_parts[1]}/{inet_parts[3]}', strict=False).prefixlen)
                        inet_addresses.append(inet_parts[1] + '/' + subnet_cidr)
                    elif 'inet6 ' in line:
                        inet6_parts = line.strip().split()
                        inet6_addresses.append(inet6_parts[1] + '/' + inet6_parts[3])
                    elif 'link/ether ' in line:
                        ether_parts = line.strip().split()
                        ether_address = ether_parts[1]

                flags = lines[1].strip()
                state = "UP" if "UP" in flags else "DOWN"

                inet_address = '\n'.join(inet_addresses)
                inet6_address = '\n'.join(inet6_addresses)

                data.append([interface_name, inet_address, inet6_address, ether_address, state])

            # Display the interface information as a table
            headers = ['Interface', 'inet', 'inet6', 'ether', 'State']
            print(tabulate(data, headers, tablefmt='simple'))

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return True

    def show_interfaces(self, args=None):
        # Run the 'ip -json addr show' command and capture its output
        result = self.run(['ip', '-json', 'addr', 'show'])

        # Check if the command was successful
        if result.exit_code != 0:
            print("Error executing 'ip -json addr show'.")
            return

        # Parse the JSON output
        json_data = result.stdout

        # Parse the JSON data into a list of network interfaces
        interface_data = json.loads(json_data)

        # Prepare data for tabulation
        table_data = []

        if isinstance(interface_data, list):
            for info in interface_data:
                interface_name = info.get("ifname", "")
                inet = ""
                inet6 = ""
                ether = info.get("address", "")
                flags = info.get("flags", [])
                state = "UP" if 'UP' in flags else "DOWN"

                for addr_info in info.get("addr_info", []):
                    if addr_info["family"] == "inet":
                        inet = f"{addr_info['local']}/{addr_info['prefixlen']}"
                    elif addr_info["family"] == "inet6":
                        if inet6:
                            inet6 += "\n"
                        inet6 += f"{addr_info['local']}/{addr_info['prefixlen']}"

                table_data.append([interface_name, inet, inet6, ether, state])
        else:
            interface_name = interface_data.get("ifname", "")
            inet = ""
            inet6 = ""
            ether = interface_data.get("address", "")
            flags = interface_data.get("flags", [])
            state = "UP" if 'UP' in flags else "DOWN"

            for addr_info in interface_data.get("addr_info", []):
                if addr_info["family"] == "inet":
                    inet = f"{addr_info['local']}/{addr_info['prefixlen']}"
                elif addr_info["family"] == "inet6":
                    if inet6:
                        inet6 += "\n"
                    inet6 += f"{addr_info['local']}/{addr_info['prefixlen']}"

            table_data.append([interface_name, inet, inet6, ether, state])

        # Define headers
        headers = ["Interface", "inet", "inet6", "ether", "State"]

        # Display the table using tabulate
        table = tabulate(table_data, headers, tablefmt="simple")

        print(table)

    def detect_network_hardware(self, args=None):
        """
        Detect and display information about network hardware on the system.

        This function runs the 'lshw -c network' command using sudo to gather information about
        network hardware on the system. It extracts relevant information for each network interface,
        such as logical name, bus info, serial number, capacity, and type (Ethernet or Wireless).
        The gathered information is displayed in a tabular format.

        Note:
            - The function requires administrative privileges to execute the 'lshw' command.
            - The 'lshw' command should be available on the system.

        Returns:
            None
        """
        interface_info = []

        try:
            # Run the 'lshw -c network' command and capture the output
            network_info = self.run(['lshw', '-c', 'network'], text=True)

            # Split the output into sections for each network interface
            sections = network_info.stdout.split('*-network')

            for section in sections[1:]:
                lines = section.strip().split('\n')

                # Initialize a dictionary to store information for this interface
                interface_data = {
                    'Logical Name': "N/A",
                    'Bus Info': "N/A",
                    'Serial': "N/A",
                    'Capacity': "N/A",
                    'Type': 'Unknown'
                }

                # Parse the lines for relevant information
                for line in lines:
                    if "bus info:" in line:
                        interface_data['Bus Info'] = line.split("bus info:")[1].strip()
                    elif "logical name:" in line:
                        interface_data['Logical Name'] = line.split("logical name:")[1].strip()
                    elif "serial:" in line:
                        interface_data['Serial'] = line.split("serial:")[1].strip()
                    elif "configuration:" in line:
                        configuration = line.split("configuration:")[1].strip()
                        if "pci@" in interface_data['Bus Info'] and "wireless" in configuration.lower():
                            interface_data['Type'] = "Wireless"
                    elif "capacity:" in line:
                        interface_data['Capacity'] = line.split("capacity:")[1].strip()

                # Determine the interface type based on bus info
                if "usb@" in interface_data['Bus Info']:
                    interface_data['Type'] = "USB-Ethernet"
                elif "pci@" in interface_data['Bus Info'] and "Wireless" not in interface_data['Type']:
                    interface_data['Type'] = "PCI-Ethernet"

                # Append the interface information to the list
                interface_info.append(interface_data)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
        # Display the interface information in a tabular format
        headers = ['Logical Name', 'Bus Info', 'Serial', 'Capacity', 'Type']
        table_data = [[
            interface['Logical Name'],
            interface['Bus Info'],
            interface['Serial'],
            interface['Capacity'],
            interface['Type']
        ] for interface in interface_info]

        print(tabulate(table_data, headers, tablefmt='simple'))