import ipaddress

class IPUtilities:
    
    @staticmethod
    def is_ip_in_range(ip_and_subnet: str, ip_address_start: str, ip_address_end: str, subnet_of_ip_start_ip_end: str) -> bool:
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

    @staticmethod
    def convert_ip_mask_to_ip_prefix(ip_address, prefix_length):
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

