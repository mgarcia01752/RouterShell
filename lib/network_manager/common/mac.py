import logging
import random
import re

from typing import Tuple
from tabulate import tabulate 
from lib.network_manager.common.interface import InterfaceLayer
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.common.constants import STATUS_NOK, STATUS_OK

class MacServiceLayerFoundError(Exception):
    """
    Exception raised when a network interface is not found.
    """

    def __init__(self, message="Mac Service error"):
        self.message = message
        super().__init__(self.message)

class MacServiceLayer(InterfaceLayer):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().MAC)
        
    def set_interface_mac(self, interface_name: str, mac_address: str) -> bool:
        """
        Set the MAC address of a network interface via os.

        Args:
            interface_name (str): The name of the network interface to update.
            mac_address (str): The new MAC address to set for the network interface.
            
        Returns:
            bool: STATUS_OK if the MAC address was successfully updated, STATUS_NOK otherwise.

        Note:
            - This method requires administrative privileges to update the MAC address.
            - The 'ifName' parameter is optional, and if not provided, the method will not perform any actions.
            - It checks if the MAC address is in a valid format and returns STATUS_NOK if not.
        """
        
        if not interface_name:
            self.log.error(f"update_if_mac_address() No Interface Defined -> mac {mac_address} -> ifName: {interface_name}")
            MacServiceLayerFoundError("No Interface Defined")
            return STATUS_NOK
            
        self.log.debug(f"update_if_mac_address() -> mac {mac_address} -> ifName: {interface_name}")
        
        if not self.is_valid_mac_address(mac_address):
            self.log.debug(f"update_if_mac_address() -> Error -> mac {mac_address} -> ifName: {interface_name}")
            MacServiceLayerFoundError(f"Mac Address is not valid: {mac_address}")
            return STATUS_NOK
            
        self.log.debug(f"update_if_mac_address() -> ifName: {interface_name} -> mac: {mac_address}")
        try:
            self.run(["ip", "link", "set", "dev", interface_name, "down"])
            self.run(["ip", "link", "set", "dev", interface_name, "address", mac_address])
            self.run(["ip", "link", "set", "dev", interface_name, "up"])

            self.log.debug(f"Changed MAC address of {interface_name} to {mac_address}")
            return STATUS_OK
        
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return STATUS_NOK

    def is_valid_mac_address(self, mac: str) -> bool:
        """
        Check if a given MAC address is valid.

        Args:
            mac (str): The MAC address to be validated.

        Supported MAC address formats:
        - xxxxxxxxxxxx: Twelve characters with no delimiters.
        - xx:xx:xx:xx:xx:xx: Six pairs of two characters separated by colons.
        - xx-xx-xx-xx-xx-xx: Six pairs of two characters separated by hyphens.
        - xxxx.xxxx.xxxx: Three groups of four characters separated by dots.

        Returns:
            bool: True if the MAC address is valid, False otherwise.
        """
        # Define regular expression patterns for supported MAC address formats
        patterns = [
            r'^[0-9A-Fa-f]{12}$',
            r'^[0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}$',
            r'^[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}-[0-9A-Fa-f]{2}$',
            r'^[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}$'
        ]

        # Check if the MAC address matches any of the patterns
        for pattern in patterns:
            if re.match(pattern, mac):
                return True

        return False

    def format_mac_address(self, mac_address: str) -> Tuple[bool, str]:
        """
        Normalize and format a MAC address into the standard format (xx:xx:xx:xx:xx:xx).

        Args:
            mac_address (str): The MAC address in various formats.

        Supported MAC address formats:
        - xxxxxxxxxxxx: Twelve alphanumeric characters with no delimiters.
        - xxxx.xxxx.xxxx: Twelve alphanumeric characters separated by dots.
        - xx:xx:xx:xx:xx:xx: Six pairs of two alphanumeric characters separated by colons or hyphens.
        - xx-xx-xx-xx-xx-xx: Six pairs of two alphanumeric characters separated by hyphens.

        Returns:
        tuple: A tuple containing:
            - bool: True if the MAC address was successfully formatted, False otherwise.
            - str: The formatted MAC address in the standard format (xx:xx:xx:xx:xx:xx) if successful,
                or None if the input MAC address is not recognized.

        """
        # Remove any non-alphanumeric characters from the input
        mac_address = re.sub(r'[^0-9a-fA-F]', '', mac_address)

        # Check if the MAC address is already in the standard format
        if len(mac_address) == 12:
            formatted_mac = ':'.join([mac_address[i:i+2] for i in range(0, 12, 2)])
            return True, formatted_mac

        # Check if the MAC address is in the xxxx.xxxx.xxxx format
        if len(mac_address) == 14:
            formatted_mac = ':'.join([mac_address[i:i+4] for i in range(0, 14, 4)])
            return True, formatted_mac

        # Check if the MAC address is in the xx:xx:xx:xx:xx:xx format
        if len(mac_address) == 17 and (mac_address.count(':') == 5 or mac_address.count('-') == 5):
            formatted_mac = ':'.join(mac_address.split(':'))
            return True, formatted_mac

        # Check if the MAC address is in the xx-xx-xx-xx-xx-xx format
        if len(mac_address) == 17 and mac_address.count('-') == 5:
            formatted_mac = ':'.join(mac_address.split('-'))
            return True, formatted_mac

        # If none of the recognized formats, return None
        return False, None

    def generate_random_mac(self, address_type='UA') -> str:
        """
        Generate a random MAC address with the specified address type.

        Args:
            address_type (str): The type of MAC address to generate. Possible values:
            - 'UA' for Universally Administered (default).
            - 'LA' for Locally Administered.
            - 'MC' for Multicast.
            - 'SA' for Universally Administered but with the second least significant bit set (Stallion MAC).

        Returns:
            str: A randomly generated MAC address in the specified address type range, formatted as 'xx:xx:xx:xx:xx:xx'.
        """
        if address_type == 'UA':
            # UA MAC address: The first byte should start with '02' to indicate UA MAC address
            mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
        elif address_type == 'LA':
            # LA MAC address: The first byte should start with '02' to indicate LA MAC address
            mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
            # Set the second least significant bit to indicate LA
            mac[0] |= 0x02
        elif address_type == 'MC':
            # Multicast MAC address: The first byte should start with '01' to indicate multicast MAC address
            mac = [0x01] + [random.randint(0x00, 0xFF) for _ in range(5)]
        elif address_type == 'SA':
            # Stallion MAC address: The first byte should start with '02' to indicate UA MAC address
            mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
            # Set the second least significant bit to indicate SA
            mac[0] |= 0x02
        else:
            raise ValueError("Invalid address_type. Use 'UA', 'LA', 'MC', or 'SA'.")

        return ':'.join(map(lambda x: format(x, '02x'), mac))
    
    def get_arp(self, args=None):
        try:
            
            self.log.debug(f"get_arp()")
            
            # Run the 'ip neighbor show' command and capture the output
            output = self.run(['ip', 'neighbor', 'show'])

            self.log.debug(f"get_arp() stderr: ({output.stderr}) -> exit_code: ({output.exit_code }) -> stdout: \n{output.stdout}")
            
            if output.exit_code == 0:
                
                arp_lines = output.stdout.strip().split('\n')

                arp_table = [line.split() for line in arp_lines]

                headers = ["IP Address", "Device", "Interface", "Type", "MAC Address", "State"]
                
                table = tabulate(arp_table, headers=headers, tablefmt='plain', colalign=("left", "left", "left", "left", "left"))

                print(table)
            else:
                print(f"Error executing 'ip neighbor show' command: {output.stderr}")
        except Exception as e:
            print(f"Error: {e}")

    def is_valid_duid_ll(self, duid):
        """
        Validate if the provided string is a valid DUID-LL (Link-layer address) in DHCPv6.

        Args:
            duid (str): The DHCP Unique Identifier to be validated.

        Returns:
            bool: True if the provided string is a valid DUID-LL, False otherwise.
        """
        duid_ll_pattern = re.compile(r'^00:01:[0-9a-fA-F:]+$')
        return bool(duid_ll_pattern.match(duid))
