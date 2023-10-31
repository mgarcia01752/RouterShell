import ipaddress
import json
import logging

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

    def is_secondary_address(self, interface, address):
        """
        Check if an IP address is a secondary address on the given interface.

        Args:
            interface (dict): The interface information in JSON format.
            address (str): The IP address to check.

        Returns:
            bool: True if the address is a secondary address, False otherwise.
        """
        for addr_info in interface["addr_info"]:
            if addr_info["family"] in ["inet", "inet6"] and addr_info["local"] == address:
                if "label" in addr_info and "secondary" in addr_info["label"]:
                    return True
        return False

    def get_ip_addr_info(self, interface_name: str = None) -> list:
        """
        Get IP address information for network interfaces.

        Args:
            interface_name (str, optional): If provided, fetch IP information for the specified network interface.

        Returns:
            list: A list of dictionaries containing IP address information for network interfaces.
        """
        cmd = ["ip", "--json", "addr", "show"]
        if interface_name:
            cmd.extend(['dev', interface_name])

        ip_addr_raw_json = self.run(cmd)
        
        if ip_addr_raw_json.exit_code:
            self.log.error(f"Error getting ip address info: cmd -> {cmd} error: {ip_addr_raw_json.stderr}")
            return []
        
        try:
            ip_addr_json_obj = json.loads(ip_addr_raw_json.stdout)
            return ip_addr_json_obj
        
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
 
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

    def is_ip_assigned_to_interface(self, ip_address, interface) -> bool:
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

    def get_interface_ip_addresses(self, interface_name, ip_version=None) -> list:
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
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """
        self.log.debug(f"set_inet_address() - Interface: {interface_name} -> inet: {inet_address_cidr} -> secondary: {secondary}")

        if not interface_name:
            self.log.error("set_inet_address() -> Interface not defined")
            return STATUS_NOK

        try:
            ip = ipaddress.ip_interface(inet_address_cidr)
            
            if ip.ip == ip.network.network_address or ip.ip == ip.network.broadcast_address:
                self.log.error(f"Invalid IP address: {inet_address_cidr}, it's a network or broadcast address")
                return STATUS_NOK
            
        except ValueError as e:
            self.log.error(f"Invalid IP address: {inet_address_cidr}, Error: {e}")
            return STATUS_NOK

        if self.is_ip_assigned_to_interface(inet_address_cidr, interface_name):
            self.log.debug(f"Skipping...Inet: {inet_address_cidr} already assigned to Interface: {interface_name}")
        else:
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

    def is_ip_in_range(self, ip_and_subnet: str, ip_address_start: str, ip_address_end: str, subnet_of_ip_start_ip_end: str) -> bool:
        """
        Check if an IP address is within a specified range considering a given subnet.

        Args:
            ip_and_subnet (str): The IP address and subnet in CIDR notation (e.g., "192.168.1.10/24" or "2001:0db8::1/64").
            ip_address_start (str): The start IP address of the range.
            ip_address_end (str): The end IP address of the range.
            subnet_of_ip_start_ip_end (str): The subnet for the start and end IP addresses.

        Returns:
            bool: True if the IP address is in the specified range, False otherwise.
        """
        try:
            ip_and_subnet = ipaddress.ip_network(ip_and_subnet, strict=False)
            start_ip = ipaddress.ip_network(ip_address_start + "/" + subnet_of_ip_start_ip_end, strict=False)
            end_ip = ipaddress.ip_network(ip_address_end + "/" + subnet_of_ip_start_ip_end, strict=False)
            return start_ip <= ip_and_subnet <= end_ip
        except (ipaddress.AddressValueError, ValueError):
            return False

    def convert_ip_mask_to_cidr(ip_address:str, prefix_length:IndentationError) -> str:
        """
        Convert an IP address and prefix length into a formatted IP address with CIDR notation.

        Args:
            ip_address (str): The IP address, either IPv4 or IPv6.
            prefix_length (int): The prefix length (subnet mask) for the IP address.

        Returns:
            str: A formatted IP address in CIDR notation (e.g., "192.168.1.0/24" or "2001:0db8::/64").
            Returns None if the input is not a valid IP address or prefix length.
        """
        try:
            # Check if the input IP address is IPv4 or IPv6
            if ':' in ip_address:
                # IPv6 address
                ip_network = ipaddress.IPv6Network(f"{ip_address}/{prefix_length}", strict=False)
                formatted_ip = str(ip_network.network_address)
                formatted_prefix = ip_network.prefixlen
            else:
                # IPv4 address
                ip_network = ipaddress.IPv4Network(f"{ip_address}/{prefix_length}", strict=False)
                formatted_ip = str(ip_network.network_address)
                formatted_prefix = ip_network.prefixlen

            return f"{formatted_ip}/{formatted_prefix}"
        except (ipaddress.AddressValueError, ValueError):
            return None

    def is_valid_inet_subnet(self, inet_subnet_cidr: str) -> bool:
        """
        Check if the given string is a valid IPv4 or IPv6 subnet in CIDR notation.

        Args:
            inet_subnet_cidr (str): The CIDR notation to check for validity.

        Returns:
            bool: True if the CIDR notation is a valid IPv4 or IPv6 subnet, False otherwise.

        Note:
        This function uses the `ipaddress` module to verify the validity of the CIDR notation.
        If the notation is valid and corresponds to either an IPv4 or IPv6 network, it returns True.
        If the notation is invalid or not recognized as IPv4 or IPv6, it returns False.
        """
        try:
            network = ipaddress.ip_network(inet_subnet_cidr, strict=False)

            if network.version == 4 or network.version == 6:
                return True
            else:
                return False
            
        except (ipaddress.AddressValueError, ValueError):
            
            return False


