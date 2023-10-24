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
    
    def set_inet_address(self,
                        interface: str, 
                        inet_address: str, 
                        inet_cidr: str, 
                        secondary: bool = False) -> bool:
        """
        Set an IPv4 address on an interface.

        Args:
            interface (str): The network interface.
            inet_address (str): The IPv4 address to set as a string in CIDR notation, including the label.
            inet_cidr (str): The IPv4 subnet in CIDR notation.
            secondary (bool, optional): Set as a secondary address. Defaults to False.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """
        
        if self.is_ip_assigned_to_interface(inet_address, interface):
            self.log.debug(f"Ip: {inet_address} already assigned to Interface: {interface}")
            return STATUS_NOK
                
        if not self.is_valid_ipv4(inet_cidr):
            self.log.error(f"Invalid IPv4 subnet: {inet_cidr}")
            return STATUS_NOK

        cmd = ["ip", "addr", "add", f"{inet_address}/{inet_cidr}", "dev", interface]
        
        if secondary:
            cmd += ["label", f"{interface}:secondary"]
            
        self.log.debug(f"set_inet_address() -> cmd: {cmd}")
        
        return STATUS_NOK if self.run(cmd).exit_code else STATUS_OK

    def del_ip_address(self, interface: str, ip_address: str) -> bool:
        """
        Delete an IP address from a network interface.

        Args:
            interface (str): The name of the network interface.
            ip_address (str): The IPv4 address to delete.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """
        self.log.debug(f"Deleting IP address {ip_address} from interface {interface}")

        result = self.run(["sudo", "ip", "addr", "del", ip_address, "dev", interface])

        if result.exit_code:
            self.log.debug(f"Unable to delete IP address {ip_address} from Interface {interface}")
            return STATUS_NOK

        self.log.debug(f"Deleted IP address {ip_address} from interface {interface}")
        return STATUS_OK

    def set_ipv4_default_gateway(self,
                                 interface: str, inet_address: str) -> RunResult:
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
    
    def set_inet6_address(self,
                          interface: str, 
                          inet6_address: str,
                          secondary: bool = False) -> RunResult:
        """
        Set an IPv6 address on an interface.

        Args:
            interface (str): The network interface.
            inet6_address (str): The IPv6 address to set as a string.
            inet6_subnet (ipaddress.IPv6Network): The IPv6 subnet.
            secondary (bool, optional): Set as secondary address. Defaults to False.

        Returns:
            str: Status code, either STATUS_OK or STATUS_NOK.
        """
        if not self.is_valid_ipv6(inet6_address):
            logging.error(f"Invalid IPv6 address: {inet6_address}")
            return STATUS_NOK
        
        cmd = ["ip", "-6", "addr", "add"]
        if secondary:
            cmd += ["secondary"]
        cmd += [f"{inet6_address}", "dev", interface]
        return self.run(cmd)
   
    def del_inet6_address(self,
                          interface: str, 
                          inet6_address: str,
                          secondary: bool = False) -> RunResult:
        """
        Delete an IPv6 address on an interface.

        Args:
            interface (str): The network interface.
            inet6_address (str): The IPv6 address to set as a string.
            inet6_subnet (ipaddress.IPv6Network): The IPv6 subnet.
            secondary (bool, optional): Set as secondary address. Defaults to False.

        Returns:
            str: Status code, either STATUS_OK or STATUS_NOK.
        """
        if not self.is_valid_ipv6(inet6_address):
            logging.error(f"Invalid IPv6 address: {inet6_address}")
            return STATUS_NOK
        
        cmd = ["ip", "addr", "del"]
        if secondary:
            cmd += ["secondary"]
        cmd += [f"{inet6_address}", "dev", interface]
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

    def get_interface_ip_addresses(self, ifName, ip_version=None):
        """
        Get IP addresses of a network interface using iproute2 --json option.

        Args:
            ifName (str): The name of the network interface.
            ip_version (str, optional): IP version to filter (None for both IPv4 and IPv6,
                                        'ipv4' for IPv4 only, 'ipv6' for IPv6 only).

        Returns:
            list: List of IP addresses associated with the interface.
        """
        # Run the ip command with --json option
        output = self.run(['ip', '--json', 'addr', 'show', ifName])
        
        if output.exit_code:
            self.log.error(f"Unable to obtain ip addresses from interface: {ifName}")
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
