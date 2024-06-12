import ipaddress
import random
import re
import socket
import os
import datetime
import subprocess
import logging
from datetime import datetime 

from lib.common.constants import *

class Common():
    '''Commonly used Static Methods'''

    def __init__(self) -> None:
        self.log = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def getHostName() -> str:
        try:
            # Get the hostname of the computer
            hostname = socket.gethostname()
            return hostname
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    @staticmethod
    def get_reboot_command() -> str:
        ''''''
        # Check if the /etc/init directory exists (indicating SysV init)
        if os.path.exists('/etc/init'):
            return 'sudo init 6'  # Use SysV init reboot command

        # Check if the /run/systemd/system directory exists (indicating systemd)
        if os.path.exists('/run/systemd/system'):
            return 'sudo systemctl reboot'  # Use systemd reboot command

        # Default to 'sudo reboot' if neither init system is found
        return 'sudo reboot'
    
    @staticmethod
    def get_shutdown_command() -> str:

        # Check if the /etc/init directory exists (indicating SysV init)
        if os.path.exists('/etc/init'):
            return 'sudo init 0'  # Use SysV init reboot command

        # Check if the /run/systemd/system directory exists (indicating systemd)
        if os.path.exists('/run/systemd/system'):
            return 'sudo systemctl shutdown'  # Use systemd reboot command

        # Default to 'sudo shutdown' if neither init system is found
        return 'sudo shutdown'
    
    @staticmethod
    def getclock(line) -> str:
        ''''''
        # Split the line to extract the format argument (if provided)
        args = line.split()
        if args:
            format_argument = args[0]
        else:
            format_argument = None

        # Get the current date and time
        current_time = datetime.datetime.now()

        # Determine the format based on the argument (or use a default format)
        if format_argument:
            try:
                formatted_time = current_time.strftime(format_argument)
                print(formatted_time)
            except ValueError:
                print("Invalid format argument.")
        else:
            # Default format if no argument is provided
            formatted_time = current_time.strftime("%H:%M:%S.%f PST %a %b %d %Y")
            print(formatted_time)
    
    @staticmethod        
    def get_network_hardware(self) -> list:
        ''''''
        ifName_info = []

        try:
            # Run the 'lshw -c network' command and capture the output
            network_info = subprocess.check_output(['sudo', 'lshw', '-c', 'network'], text=True)

            # Split the output into sections for each network interface
            sections = network_info.split('*-network')

            for section in sections[1:]:
                lines = section.strip().split('\n')

                # Initialize a dictionary to store information for this interface
                ifName_data = {
                    'Logical Name': "N/A",
                    'Bus Info': "N/A",
                    'Serial': "N/A",
                    'Capacity': "N/A",
                    'Type': 'Unknown'
                }

                # Parse the lines for relevant information
                for line in lines:
                    if "bus info:" in line:
                        ifName_data['Bus Info'] = line.split("bus info:")[1].strip()
                    elif "logical name:" in line:
                        ifName_data['Logical Name'] = line.split("logical name:")[1].strip()
                    elif "serial:" in line:
                        ifName_data['Serial'] = line.split("serial:")[1].strip()
                    elif "configuration:" in line:
                        configuration = line.split("configuration:")[1].strip()
                        if "pci@" in ifName_data['Bus Info'] and "wireless" in configuration.lower():
                            ifName_data['Type'] = "Wireless"
                    elif "capacity:" in line:
                        ifName_data['Capacity'] = line.split("capacity:")[1].strip()

                # Determine the interface type based on bus info
                if "usb@" in ifName_data['Bus Info']:
                    ifName_data['Type'] = "USB-Ethernet"
                elif "pci@" in ifName_data['Bus Info'] and "Wireless" not in ifName_data['Type']:
                    ifName_data['Type'] = "PCI-Ethernet"

                # Append the interface information to the list
                ifName_info.append(ifName_data)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return ifName_info
    
    @staticmethod
    def is_valid_interface(self, ifName):
        
        try:
            # Use subprocess to run the 'ifconfig -a' command
            output = subprocess.check_output(['ifconfig', '-a'], text=True)

            # Check if the interface_name appears in the output
            if ifName in output:
                return STATUS_OK
            
            return STATUS_NOK
        except subprocess.CalledProcessError:
            return STATUS_NOK
    
    @staticmethod
    def generate_random_mac_address(self):
        '''Generate a random Mac Address that is not a Multicast'''
        # The first byte should be an even number (locally administered)
        first_byte = random.randint(0, 127) * 2

        # Generate the remaining 5 bytes randomly
        random_bytes = [random.randint(0, 255) for _ in range(5)]

        # Combine the bytes into a MAC address string
        mac_address = "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(
            first_byte, *random_bytes
        )

        return mac_address
 
    @staticmethod
    def is_valid_ip(ip_str: str) -> bool:
        '''Check both IPv4 and IPv6 is properly formatted'''
        try:
            ipaddress.IPv4Address(ip_str)  # Check if it's a valid IPv4 address
            return STATUS_OK
        except ipaddress.AddressValueError:
            try:
                ipaddress.IPv6Address(ip_str)  # Check if it's a valid IPv6 address
                return STATUS_OK
            except ipaddress.AddressValueError:
                return STATUS_NOK
    
    @staticmethod    
    def flatten_list(simple_list):
        return [item for item in simple_list]
    
    @staticmethod
    def convert_timestamp(timestamp:int):
        """
        Convert Unix timestamp to human-readable date and time.
        """
        if timestamp:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return "N/A" 

    @staticmethod
    def is_valid_hostname(hostname: str) -> bool:
        """
        Check if a hostname is valid based on DNS standards.

        Args:
            hostname (str): The hostname to be validated.

        Returns:
            bool: True if the hostname is valid, False otherwise.
        """
        if not hostname or len(hostname) > 255:
            return False

        # Check if the hostname contains only valid characters
        if not re.match("^[a-zA-Z0-9.-]+$", hostname):
            return False

        # Check if the hostname does not start or end with a hyphen
        if hostname.startswith("-") or hostname.endswith("-"):
            return False

        # Check if there are no consecutive periods (..)
        if ".." in hostname:
            return False

        return True
    
    @staticmethod
    def get_env(var_name: str) -> str:
        """
        Get the value of an environment variable.
        
        Args:
            var_name (str): The name of the environment variable.
        
        Returns:
            str: The value of the environment variable, or None if it is not found.
        """
        return os.environ.get(var_name)


