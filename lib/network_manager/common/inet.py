import ipaddress
import json
import logging
from typing import List

from lib.network_manager.common.mac import MacServiceLayer
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunResult
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class InetServiceLayer(MacServiceLayer):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().INET)
                    
    def is_valid_ipv4(self, inet_address: str) -> bool:
        """
        Check if an IPv4 address is valid.

        Args:
            inet_address (str): The IPv4 address as a string.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        
        self.log.debug(f"is_valid_ipv4() -> Inet Address: ({inet_address})")
        
        try:
            ipaddress.IPv4Address(inet_address)
            self.log.debug(f"is_valid_ipv4() -> Inet Address: ({inet_address}) is Good")
            return True
        except ipaddress.AddressValueError:
            self.log.error(f"is_valid_ipv4() -> Inet Address: ({inet_address}) is Bad")
            return False

    def is_valid_ipv6(self, inet6_address: str, include_prefix=True) -> bool:
        """
        Check if an IPv6 address is valid.

        Args:
            inet6_address (str): The IPv6 address as a string.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        try:
            parts = inet6_address.split('/')
            self.log.debug(f"is_valid_ipv6() -> inet6: ({parts}) -> include-prefix({include_prefix})")
            if len(parts) != 2:
                return False

            address, prefix_length = parts[0], int(parts[1])
            ipaddress.IPv6Network(address)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    def is_ip_assigned_to_interface(self, ip_address, interface):
        """
        Check if an IP address is assigned to a specific network interface on a Linux system.

        Args:
            ip_address (str): The IP address to check.
            interface (str): The network interface to check.

        Returns:
            bool: True if the IP address is assigned to the interface, False otherwise.
        """
        command = ['ip', 'addr', 'show', interface]
        result = self.run(command)

        lines = result.stdout.split('\n')
        for line in lines:
            if ip_address in line:
                return True
        return False

    def is_valid_inet_address(self, ip_address: str) -> bool:
        """
        Check if a string is a valid IP address.

        Args:
            ip_address (str): The IP address to validate.

        Returns:
            bool: True if the input is a valid IP address, False otherwise.
        """
        try:
            ip = ipaddress.ip_address(ip_address)
            return True
        except ValueError:
            return False

    def set_ipv4_default_gateway(self, interface: str, inet_address: str) -> RunResult:
        """
        Set the default IPv4 gateway on an interface.

        Args:
            interface (str): The network interface.
            inet_address (str): The IPv4 gateway address as a string.

        Returns:
            str: Status code, either STATUS_OK or STATUS_NOK.
        """
        if not self.is_valid_ipv4(inet_address):
            logging.error(f"Invalid IPv4 gateway address: {inet_address}")
            return STATUS_NOK
        
        cmd = ["ip", "route", "add", "default", "via", inet_address, "dev", interface]
        return self.run(cmd)
     
    def set_ipv6_default_gateway(self, interface: str, inet6_address: str) -> RunResult:
        """
        Set the default IPv6 gateway on an interface.

        Args:
            interface (str): The network interface.
            inet6_address (str): The IPv6 gateway address as a string.

        Returns:
            str: Status code, either STATUS_OK or STATUS_NOK.
        """
        if not self.is_valid_ipv6(inet6_address):
            logging.error(f"Invalid IPv6 gateway address: {inet6_address}")
            return STATUS_NOK
        
        cmd = ["ip", "-6", "route", "add", "default", "via", inet6_address, "dev", interface]
        return self.run(cmd)

    def is_valid_network_interface(self, interface: str) -> bool:
        """
        Check if a string is a valid network interface name.

        Args:
            interface (str): The network interface name.

        Returns:
            bool: True if the input is a valid network interface name, False otherwise.
        """
        # Add your network interface validation logic here
        return True  # Replace with actual validation logic

    def get_interface_ip_addresses(self, interface_name, ip_version=None):
        """
        Get IP addresses of a network interface using iproute2 --json option.

        Args:
            interface_name (str): The name of the network interface.
            ip_version (str, optional): IP version to filter (None for both IPv4 and IPv6,
                                        'ipv4' for IPv4 only, 'ipv6' for IPv6 only).

        Returns:
            list: List of IP addresses associated with the interface.
        """
        # Run the ip command with --json option
        output = self.run(['ip', '--json', 'addr', 'show', interface_name])
        
        if output.exit_code:
            self.log.error(f"Unable to obtain ip addresses from interface: {interface_name}")
            return []

        # Parse the JSON output
        ip_info = json.loads(output.stdout)

        # Extract IP addresses based on the specified IP version
        addresses = []
        for addr_info in ip_info[0]['addr_info']:
            ip_addr = addr_info['local']
            if ip_version is None or (ip_version == 'ipv4' and ':' not in ip_addr) or (ip_version == 'ipv6' and ':' in ip_addr):
                addresses.append(ip_addr)

        return addresses

    def set_inet_address(self, interface_name: str, inet_address_cidr: str, secondary: bool = False) -> bool:
        """
        Set an IP address on an interface.

        Args:
            interface_name (str): The network interface.
            inet_address_cidr (str): The IP address to set as a string in CIDR notation, including the label.
            secondary (bool, optional): Set as a secondary address. Defaults to False.

        Returns:
            bool: True for success, STATUS_NOK for failure.
        """
        self.log.debug(f"set_inet_address() - Interface: {interface_name} -> inet: {inet_address_cidr} -> secondary: {secondary}")

        if not interface_name:
            self.log.error("set_inet_address() -> Interface not defined")
            return STATUS_NOK

        try:
            ip = ipaddress.ip_interface(inet_address_cidr)
            
            # Check if the IP address is a network or broadcast address
            if ip.ip == ip.network.network_address or ip.ip == ip.network.broadcast_address:
                self.log.debug(f"Invalid IP address: {inet_address_cidr}, it's a network or broadcast address")
                return STATUS_NOK
            
        except ValueError as e:
            self.log.debug(f"Invalid IP address: {inet_address_cidr}, Error: {e}")
            return STATUS_NOK

        if self.is_ip_assigned_to_interface(inet_address_cidr, interface_name):
            self.log.debug(f"IP: {inet_address_cidr} already assigned to Interface: {interface_name}, must be deleted before re-assigning")
            return STATUS_NOK

        cmd = ["ip", "addr", "add", f"{inet_address_cidr}", "dev", interface_name]

        if secondary:
            cmd += ["label", f"{interface_name}:secondary"]
        
        self.log.debug(f"set_inet_address() -> cmd: {cmd}")
                
        result = self.run(cmd)
        if result.exit_code:
            self.log.error(f"Unable to add inet: {inet_address_cidr} to interface: {interface_name} -> status: {result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK 

    def del_inet_address(self, interface: str, ip_address: str) -> bool:
        """
        Remove an IP address from a network interface.

        Args:
            interface (str): The name of the network interface.
            ip_address (str): The IP address to remove.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """
        if not self.is_valid_network_interface(interface):
            self.log.debug(f"Invalid network interface: {interface}")
            return STATUS_NOK

        if not self.is_valid_inet_address(ip_address):
            self.log.debug(f"Invalid IP address: {ip_address}")
            return STATUS_NOK

        self.log.debug(f"Removing IP address {ip_address} from interface {interface}")

        result = self.run(["sudo", "ip", "addr", "del", ip_address, "dev", interface])

        if result.exit_code:
            self.log.debug(f"Unable to remove IP address {ip_address} from Interface {interface}")
            return STATUS_NOK

        self.log.debug(f"Removed IP address {ip_address} from interface {interface}")
        return STATUS_OK
