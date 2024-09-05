from enum import Enum
import ipaddress
import json
import logging
from typing import List, Optional, Tuple

from lib.network_manager.common.mac import MacServiceLayer
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunResult
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

class InetVersion(Enum):
    IPv4 = 4
    IPv6 = 6
    UNKNOWN = 0

class InetServiceLayer(MacServiceLayer):
    """
    A class for configuring network settings using iproute2.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().INET)
                    
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

    def get_interface_ip_addresses(self, interface_name, ip_version=None) -> List:
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
    
    def set_inet_address_loopback(self, loopback_name: str, inet_address_cidr: str) -> bool:
        """
        Set an internet address (IPv4 or IPv6) on a loopback interface. 
        Appending to the local loopback (lo) interface 

        Args:
            loopback_name (str): The name of the loopback interface.
            inet_address_cidr (str): The CIDR notation of the IP address to assign.

        Returns:
            bool: STATUS_OK if the address was successfully set, STATUS_NOK otherwise.
        """
        self.log.debug(f"set_inet_address_loopback() - Loopback: {loopback_name} -> inet: {inet_address_cidr}")

        if not loopback_name:
            self.log.error("set_inet_address_loopback() -> Loopback not defined")
            return STATUS_NOK

        try:
            ip_interface = ipaddress.ip_interface(inet_address_cidr)
            ip_version = ip_interface.version
            
        except ValueError:
            self.log.error(f"set_inet_address_loopback() -> Invalid IP address: {inet_address_cidr}")
            return STATUS_NOK

        lo_name = f'lo:{loopback_name}'
        cmd = ['ip', 'addr', 'add', inet_address_cidr, 'label', lo_name, 'dev', 'lo']

        if ip_version == 6:
            cmd.insert(1, '-6')
            
        self.log.debug(f'set_inet_address_loopback() -> {cmd}')
        out = self.run(cmd)

        if out.exit_code:
            self.log.error(f"set_inet_address_loopback() -> Unable to set inet address: "
                           f"{inet_address_cidr} on loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        return STATUS_OK

    def del_inet_address_loopback(self, loopback_name: str, inet_address_cidr: str) -> bool:
        """
        Delete an internet address (IPv4 or IPv6) from a loopback interface.

        Args:
            loopback_name (str): The name of the loopback interface.
            inet_address_cidr (str): The CIDR notation of the IP address to remove.

        Returns:
            bool: STATUS_OK if the address was successfully removed, STATUS_NOK otherwise.
        """
        self.log.debug(f"del_inet_address_loopback() - Loopback: {loopback_name} -> inet: {inet_address_cidr}")

        if not loopback_name:
            self.log.error("del_inet_address_loopback() -> Loopback not defined")
            return STATUS_NOK

        try:
            ip_interface = ipaddress.ip_interface(inet_address_cidr)
            ip_version = ip_interface.version
            
        except ValueError:
            self.log.error(f"del_inet_address_loopback() -> Invalid IP address: {inet_address_cidr}")
            return STATUS_NOK

        lo_name = f'lo:{loopback_name}'
        cmd = ['ip', 'addr', 'del', inet_address_cidr, 'label', lo_name, 'dev', 'lo']

        if ip_version == 6:
            cmd.insert(1, '-6')

        self.log.info(f'del_inet_address_loopback() -> {cmd}')
        out = self.run(cmd)

        if out.exit_code:
            self.log.error(f"del_inet_address_loopback() -> Unable to delete inet address: "
                        f"{inet_address_cidr} from loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        return STATUS_OK
    
    def update_inet_address_loopback(self, loopback_name: str, old_inet_address_cidr: str, new_inet_address_cidr: str) -> bool:
        """
        # TODO Need to test, not sure if this works
        
        Update (overwrite) an internet address (IPv4 or IPv6) on a loopback interface.

        Args:
            loopback_name (str): The name of the loopback interface.
            old_inet_address_cidr (str): The CIDR notation of the current IP address to be replaced.
            new_inet_address_cidr (str): The CIDR notation of the new IP address to assign.

        Returns:
            bool: STATUS_OK if the address was successfully updated, STATUS_NOK otherwise.
        """
        self.log.debug(f"update_inet_address_loopback() - Loopback: {loopback_name} -> "
                    f"Old Inet: {old_inet_address_cidr}, New Inet: {new_inet_address_cidr}")

        if not loopback_name:
            self.log.error("update_inet_address_loopback() -> Loopback not defined")
            return STATUS_NOK

        try:
            old_ip_interface = ipaddress.ip_interface(old_inet_address_cidr)
            new_ip_interface = ipaddress.ip_interface(new_inet_address_cidr)
            old_ip_version = old_ip_interface.version
            new_ip_version = new_ip_interface.version

        except ValueError as e:
            self.log.error(f"update_inet_address_loopback() -> Invalid IP address: {e}")
            return STATUS_NOK

        # Delete old IP address
        lo_name = f'lo:{loopback_name}'
        del_cmd = ['ip', 'addr', 'del', old_inet_address_cidr, 'label', lo_name, 'dev', 'lo']
        if old_ip_version == 6:
            del_cmd.insert(1, '-6')
        
        self.log.info(f'update_inet_address_loopback() - Deleting old address -> {del_cmd}')
        out = self.run(del_cmd)
        
        if out.exit_code:
            self.log.error(f"update_inet_address_loopback() -> Unable to delete old inet address: "
                        f"{old_inet_address_cidr} from loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        # Add new IP address
        add_cmd = ['ip', 'addr', 'add', new_inet_address_cidr, 'label', lo_name, 'dev', 'lo']
        if new_ip_version == 6:
            add_cmd.insert(1, '-6')

        self.log.info(f'update_inet_address_loopback() - Adding new address -> {add_cmd}')
        out = self.run(add_cmd)

        if out.exit_code:
            self.log.error(f"update_inet_address_loopback() -> Unable to set new inet address: "
                        f"{new_inet_address_cidr} on loopback: {loopback_name}, Reason: {out.stderr}")
            return STATUS_NOK

        return STATUS_OK

        
    def set_inet_address(self, interface_name: str, inet_address_cidr: str, secondary: bool = False) -> bool:
        """
        Set an IP address on an interface via OS.

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
            
            # TODO: ip route has a 15 character length label limit, need to add check
            if secondary:
                cmd += ["label", f"{interface_name}:sec"]
            
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

    def is_ip_range_within_subnet(self, subnet_cidr: str, ip_range_start: str, ip_range_end: str, ip_range_subnet: str) -> bool:
        """
        Check if an IP range is within a given subnet.

        Args:
            subnet_cidr (str): The subnet in CIDR notation (e.g., "192.168.1.0/24" or "2001:db8::/64").
            ip_range_start (str): The start IP address of the range.
            ip_range_end (str): The end IP address of the range.
            ip_range_subnet (str): The subnet mask for the IP range.

        Returns:
            bool: True if the IP range is within the subnet, False otherwise.
        """
        
        try:
            network = ipaddress.ip_network(subnet_cidr, strict=False)
            ip_start = ipaddress.ip_address(ip_range_start)
            ip_end = ipaddress.ip_address(ip_range_end)
            subnet_mask = ipaddress.ip_network(ip_range_subnet, strict=False).netmask

            return network.network_address <= ip_start and network.broadcast_address >= ip_end and subnet_mask == network.netmask

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
            return network.version in {4, 6}
        except (ipaddress.AddressValueError, ValueError):
            return False


    def get_inet_subnet_inet_version(self, inet_subnet_cidr: str) -> InetVersion:
        """
        Determine the IP version (IPv4 or IPv6) based on the CIDR notation of an IP subnet.

        Args:
            inet_subnet_cidr (str): The CIDR notation for the IP subnet (e.g., "192.168.0.0/24" for IPv4 or "2001:db8::/32" for IPv6).

        Returns:
            InetVersion: An InetVersion enum representing the IP version (IPv4, IPv6, or UNKNOWN).

        Raises:
            ValueError: If the input is not a valid CIDR notation.

        """
        try:
            network = ipaddress.IPv4Network(inet_subnet_cidr, strict=False)
            return InetVersion.IPv4

        except ValueError:
            try:
                network = ipaddress.IPv6Network(inet_subnet_cidr, strict=False)
                return InetVersion.IPv6
            except ValueError:
                return InetVersion.UNKNOWN

    @staticmethod
    def validate_subnet_format(subnet: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the format of an IPv4 or IPv6 subnet.

        Args:
            subnet (str): The subnet in CIDR notation.

        Returns:
            tuple: (bool, Optional[str]) where the first element is True if valid, otherwise False.
                The second element is an error message or None if valid.

        Example:
            subnet = "172.16.0.0/24"
            subnet = "fd00:1::/64"
        """
        try:
            ipaddress.ip_network(subnet)
            return True, None
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def validate_inet_ranges(subnet_cidr: str, pool_start: str, pool_end: str) -> bool:
        """
        Validate if the specified IP address range in the DHCP pool falls within both the subnet and the pool subnet.

        This method checks if the IP address range specified in the DHCP pool falls within the given subnet and considers
        the pool subnet as well. It iterates over subnets within the pool range subnet using 
        `ipaddress.summarize_address_range` and checks if any part of the pool range overlaps with the specified subnet.

        Args:
            subnet_cidr (str): The subnet CIDR of the DHCP pool.
            pool_start (str): The starting IP address of the DHCP pool.
            pool_end (str): The ending IP address of the DHCP pool.

        Returns:
            bool: True if the DHCP pool range is valid within both the subnet and the pool subnet, False otherwise.
        """
        try:
            subnet = ipaddress.ip_network(subnet_cidr)
            pool_start_address = ipaddress.ip_address(pool_start)
            pool_end_address = ipaddress.ip_address(pool_end)

            for subnet_segment in ipaddress.summarize_address_range(pool_start_address, pool_end_address):
                if not subnet.overlaps(subnet_segment):
                    return False

            return True
        
        except ValueError as e:
            return False

    @staticmethod
    def validate_inet_range(subnet_cidr: str, inet: str) -> bool:
        """
        Validate if the specified IP address falls within the given subnet.

        This method checks if the provided IP address falls within the specified subnet. It uses the `ipaddress` module
        to validate the IP address format and then checks if the IP address is within the given subnet.

        Args:
            subnet_cidr (str): The subnet CIDR to validate against.
            inet (str): The IP address to be validated.

        Returns:
            bool: True if the provided IP address is within the specified subnet, False otherwise.
        """
        try:
            subnet = ipaddress.ip_network(subnet_cidr)
            inet_address = ipaddress.ip_address(inet)

            # Check if the IP address is within the subnet
            return inet_address in subnet
            
        except ValueError as e:
            # Log or handle the specific error message
            return False

