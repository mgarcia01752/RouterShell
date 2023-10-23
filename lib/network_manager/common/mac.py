import logging
import random
import re

from typing import List

from tabulate import tabulate 

from lib.common.common import Common
from lib.network_manager.common.phy import PhyServiceLayer
from lib.common.constants import *

class MacServiceLayerFoundError(Exception):
    """
    Exception raised when a network interface is not found.
    """

    def __init__(self, message="Mac Service error"):
        self.message = message
        super().__init__(self.message)

class MacServiceLayer(PhyServiceLayer):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        
    def update_if_mac_address(self, ifName: str, mac_address: str) -> bool:
        """
        Update the MAC address of a network interface.

        Args:
            ifName (str, optional): The name of the network interface to update. Defaults to None.
            mac_address (str): The new MAC address to set for the network interface.
            
        Returns:
            bool: STATUS_OK if the MAC address was successfully updated, STATUS_NOK otherwise.

        Example:
            You can use this method to update the MAC address of a network interface, such as 'eth0', to a new MAC address.
            For instance, you might want to change the MAC address to '00:11:22:33:44:55'.

        Usage:
            status = update_if_mac_address('00:11:22:33:44:55', 'eth0')
            if status == STATUS_OK:
                print(f"MAC address of 'eth0' updated successfully.")
            else:
                print(f"Failed to update MAC address of 'eth0'.")

        Note:
            - This method requires administrative privileges to update the MAC address.
            - The 'ifName' parameter is optional, and if not provided, the method will not perform any actions.
            - It checks if the MAC address is in a valid format and returns STATUS_NOK if not.
        """
        
        if not ifName:
            self.log.error(f"update_if_mac_address() No Interface Defined -> mac {mac_address} -> ifName: {ifName}")
            MacServiceLayerFoundError("No Interface Defined")
            return STATUS_NOK
            
        self.log.debug(f"update_if_mac_address() -> mac {mac_address} -> ifName: {ifName}")
        
        if self.is_valid_mac_address(mac_address):
            self.log.debug(f"update_if_mac_address() -> Error -> mac {mac_address} -> ifName: {ifName}")
            MacServiceLayerFoundError(f"Mac Address is not valid: {mac_address}")
            return STATUS_NOK
            
        self.log.debug(f"update_if_mac_address() -> ifName: {ifName} -> mac: {mac_address}")
        try:
            self.run(["ip", "link", "set", "dev", ifName, "down"])
            self.run(["ip", "link", "set", "dev", ifName, "address", mac_address])
            self.run(["ip", "link", "set", "dev", ifName, "up"])

            self.log.debug(f"Changed MAC address of {ifName} to {mac_address}")
            return STATUS_OK
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return STATUS_NOK

            
    def is_valid_mac_address(self, mac: str) -> bool:
        """
        Check if a given MAC address is valid.

        Args:
            mac (str): The MAC address to be validated.

        Returns:
            str: STATUS_OK if the MAC address is valid, STATUS_NOK otherwise.
        """
        patterns = [
            r'^([0-9A-Fa-f]{12})$',                         # xxxxxxxxxxxx
            r'^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$',     # xx:xx:xx:xx:xx:xx
            r'^([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$'        # xxxx.xxxx.xxxx
        ]

        # Check if the MAC address matches any of the patterns
        for pattern in patterns:
            if re.match(pattern, mac):
                return STATUS_OK

        return STATUS_NOK

    def format_mac_address(self, mac_address: str):
        """
        Normalize and format a MAC address into the standard format (xx:xx:xx:xx:xx:xx).

        Args:
            mac_address (str): The MAC address in various formats.

        Returns:
            tuple: A tuple containing:
                - int: STATUS_OK if the MAC address was successfully formatted, STATUS_NOK otherwise.
                - str: The formatted MAC address in the standard format (xx:xx:xx:xx:xx:xx).

        Notes:
            This function removes non-alphanumeric characters from the input MAC address and
            converts it into the standard format (xx:xx:xx:xx:xx:xx) if possible. It recognizes
            the following input formats:
            - xxxxxxxxxxxx (12 characters)
            - xxxx.xxxx.xxxx (14 characters)
            - xx:xx:xx:xx:xx:xx (17 characters with colons)
            If the input MAC address does not match any recognized format, STATUS_NOK is returned.

        Examples:
            >>> format_mac_address("001122334455")
            (0, '00:11:22:33:44:55')
            >>> format_mac_address("12:34:56:78:90:AB")
            (0, '12:34:56:78:90:ab')
            >>> format_mac_address("12.3456.7890.ABCD")
            (0, '12:34:56:78:90:ab')
            >>> format_mac_address("1234.5678.abcd")
            (1, {})

        """
        # Remove any non-alphanumeric characters from the input
        mac_address = re.sub(r'[^0-9a-fA-F]', '', mac_address)

        # Check if the MAC address is already in the standard format
        if len(mac_address) == 12:
            formatted_mac = ':'.join([mac_address[i:i+2] for i in range(0, 12, 2)])
            return STATUS_OK, formatted_mac

        # Check if the MAC address is in the xxxx.xxxx.xxxx format
        if len(mac_address) == 14:
            formatted_mac = ':'.join([mac_address[i:i+4] for i in range(0, 14, 4)])
            return STATUS_OK, formatted_mac

        # Check if the MAC address is in the xx:xx:xx:xx:xx:xx format
        if len(mac_address) == 17 and mac_address.count(':') == 5:
            return STATUS_OK, mac_address  # Already in the standard format

        # If none of the recognized formats, return STATUS_NOK
        return STATUS_NOK, None
    
    def generate_random_mac(self):
        # The first byte should start with '02' to indicate UA MAC address
        mac = [0x02] + [random.randint(0x00, 0xFF) for _ in range(5)]
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