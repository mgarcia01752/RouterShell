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
