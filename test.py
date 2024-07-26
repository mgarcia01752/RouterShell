#!/usr/bin/env python3


import logging
from typing import List, Dict
from tabulate import tabulate
import re

class DHCPClientLogParser:
    
    @staticmethod
    def parse_log_line(line: str) -> Dict[str, str]:
        """
        Parses a single log line into its components.

        Args:
            line (str): The log line to parse.

        Returns:
            dict: A dictionary with the parsed components.
        """
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

class DHCPClientShow:
    """Command set for showing DHCPClient-Show-Command"""

    def __init__(self, args=None):
        self.log = logging.getLogger(self.__class__.__name__)
        self.args = args
    
    def flow_log(self) -> List[str]:
        """
        Retrieve DHCP client flow logs related to IPv4 address assignment from the system journal.

        Returns:
            List[str]: A list of DHCP client flow log entries related to IPv4 address assignment.
        """
        # Placeholder for actual log retrieval logic
        return [
            "Jul 26 15:14:21 Router daemon.info dnsmasq-dhcp[573]: DHCPDISCOVER(eth4) 192.168.100.90 94:c6:91:15:14:3e",
            "Jul 26 15:14:21 Router daemon.info dnsmasq-dhcp[573]: DHCPOFFER(eth4) 192.168.100.90 94:c6:91:15:14:3e",
            "Jul 26 15:14:21 Router daemon.info dnsmasq-dhcp[573]: DHCPREQUEST(eth4) 192.168.100.90 94:c6:91:15:14:3e",
            "Jul 26 15:14:21 Router daemon.info dnsmasq-dhcp[573]: DHCPACK(eth4) 192.168.100.90 94:c6:91:15:14:3e"
        ]

    def show_parsed_logs(self):
        """
        Parses the DHCP client flow logs and prints them in a tabulated format.
        """
        logs = self.flow_log()
        parsed_logs = [DHCPClientLogParser.parse_log_line(line) for line in logs]
        
        # Filtering out empty dictionaries
        parsed_logs = [log for log in parsed_logs if log]
        
        if parsed_logs:
            # Ensure all dictionaries have the same keys
            headers = list(parsed_logs[0].keys())
            print("Headers:", headers)  # Debugging statement
            print("Parsed Logs:", parsed_logs)  # Debugging statement
            
            # Convert to list of lists if needed
            data = [list(log.values()) for log in parsed_logs]
            table = tabulate(data, headers=headers, tablefmt='pretty')
            print(table)
        else:
            print("No valid log entries found.")

# Example usage:
dhcp_client_show = DHCPClientShow()
dhcp_client_show.show_parsed_logs()

