#!/usr/bin/env python3
import re

class DHCPClientLogParser:
    
    @staticmethod
    def parse_log_line(line: str) -> dict:
        """
        Parses a single log line into its components.

        Args:
            line (str): The log line to parse.

        Returns:
            dict: A dictionary with the parsed components.
        """
        # Example log line:
        # Jul 26 14:48:41 Router daemon.info dnsmasq-dhcp[573]: DHCPDISCOVER(eth4) 192.168.100.90 94:c6:91:15:14:3e
        regex = (r"(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+"
                 r"(?P<host>\w+).*"
                 r"(?P<dhcp>DHCPDISCOVER|DHCPOFFER|DHCPREQUEST|DHCPACK)"
                 r"\((?P<interface>\w+)\)\s+"
                 r"(?P<ip_address>\d+\.\d+\.\d+\.\d+)?\s*"
                 r"(?P<mac_address>[0-9a-f:]{17})")
                
        match = re.match(regex, line)
        
        if match:
            return match.groupdict()
        
        return {}

# Example usage:
log_line = "Jul 26 14:48:41 Router daemon.info dnsmasq-dhcp[573]: DHCPDISCOVER(eth4) 192.168.100.90 94:c6:91:15:14:3e"
parser = DHCPClientLogParser()
parsed_line = parser.parse_log_line(log_line)
print(parsed_line)
