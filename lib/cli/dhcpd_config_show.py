import argparse
import ipaddress
import json
import logging

import cmd2

from lib.db.dhcp_db import DHCPDatabase, DhcpOptionsLUT, DHCPDatabaseFactory
from lib.cli.exec_priv_mode import ExecMode
from lib.cli.global_operation import GlobalUserCommand
from lib.cli.router_prompt import RouterPrompt

from lib.common.common import STATUS_NOK, STATUS_OK

class DHCPServerConfig(cmd2.Cmd,
                       GlobalUserCommand,
                       RouterPrompt):
    
    GLOBAL_CONFIG_MODE = 'global'
    PROMPT_CMD_ALIAS = 'dhcp'    
    
    def __init__(self, dhcp_pool_name: str, negate=False):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        GlobalUserCommand.__init__(self)
        
        self.log.info(f"DHCPServerConfig({dhcp_pool_name}) -> negate: {negate}")
        
        ''' DO NOT MODIFY THIS LINE'''
        self.dhcp_pool_obj = None        
        self.dhcp_pool_name = dhcp_pool_name
        self.negate = negate
        ''' DO NOT MODIFY THIS LINE'''
        
        prompt_ext = ""
        if self.isGlobalMode() :
            prompt_ext = f'-{dhcp_pool_name}'
        else:
            self.log.info(f"DHCPServerConfig() -> Not in DHCP Global Config Mode")
        
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, f'{self.PROMPT_CMD_ALIAS}{prompt_ext}')
        self.prompt = self.set_prompt()
                
        if not DHCPDatabase().pool_name_exists(self.dhcp_pool_name):
            self.log.info(f"DHCP-Pool:({self.dhcp_pool_name}) does not exist -> Creating DHCP-POOL: {self.dhcp_pool_name}")

        
    def isGlobalMode(self) -> bool:
        return self.dhcp_pool_name == self.GLOBAL_CONFIG_MODE
    
    def do_subnet(self, args: str):
        '''
        Configure a subnet with the specified IP address and subnet mask.

        Args:
            args (str): The arguments for the 'subnet' command, which should include an IP address and a subnet mask.

        Example:
            subnet 192.168.1.0/24
        '''
        self.log.info(f"do_subnet() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure a DHCP server subnet",
            epilog="Use 'subnet <ip-address> <subnet-mask>' to set the subnet."
        )

        # Define the arguments directly without subcommands
        parser.add_argument("ip_address_mask", help="The IP address/mask of the subnet")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        ip_address_mask = args.ip_address_mask
        self.log.info(f"Configuring subnet with IP Subnet: {ip_address_mask}")
        self.dhcp_pool_Fact = DHCPDatabaseFactory(self.dhcp_pool_name, ip_address_mask, self.negate)

        
    def do_pools(self, args: str):
        '''
        Configure an IP pool with the specified start and end IP addresses and subnet mask.

        Args:
            args (str): The arguments for the 'pools' command, which should include the start IP address, end IP address, and subnet mask.

        Example:
            pools 192.168.1.10 192.168.1.20 255.255.255.0
        '''
        self.log.info(f"do_pools() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure an IP pool for the DHCP server",
            epilog="Use 'pools <ip-address-start> <ip-address-end> <ip-subnet-mask>' to set the pool."
        )

        # Define the arguments directly without subcommands
        parser.add_argument("ip_start", help="The starting IP address of the pool")
        parser.add_argument("ip_end", help="The ending IP address of the pool")
        parser.add_argument("subnet_mask", help="The subnet mask for the pool")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        # Access the parsed arguments directly
        ip_start = args.ip_start
        ip_end = args.ip_end
        subnet_mask = args.subnet_mask

        # Handle the 'pools' command logic here
        self.log.info(f"Configuring IP pool with start IP: {ip_start}, end IP: {ip_end}, and subnet mask: {subnet_mask}")
        # Implement your logic for configuring the IP pool using the parsed arguments

    def do_reservations(self, args: str):
        '''
        Configure a reservation for a client with the specified MAC address, IP address, and optional hostname.

        Args:
            args (str): The arguments for the 'reservations' command, which should include the MAC address, IP address, and optional hostname.

        Example:
            reservations hw-address 00:11:22:33:44:55 ip-address 192.168.1.10 hostname client1
        '''
        self.log.info(f"do_reservations() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure a reservation for a DHCP client",
            epilog="Use 'reservations [hw-address | duid] <mac-address> ip-address <ip-address> [hostname <string>]' to set a reservation."
        )

        # Define the arguments and options
        parser.add_argument("mac_or_duid", choices=["hw-address", "duid"], 
                            help="Specify 'hw-address' or 'duid' to identify the client")
        parser.add_argument("client_identifier", 
                            help="The MAC address or DUID of the client")
        parser.add_argument("ip_identifier", 
                            help="Specify 'ip-address' to set the client's IP address")
        parser.add_argument("ip_address", 
                            help="The reserved IP address for the client")
        parser.add_argument("hostname", nargs="?", 
                            help="An optional hostname for the client")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        # Access the parsed arguments and options
        mac_or_duid = args.mac_or_duid
        client_identifier = args.client_identifier
        ip_identifier = args.ip_identifier
        ip_address = args.ip_address
        hostname = args.hostname

        # Handle the 'reservations' command logic here
        self.log.info(f"Configuring reservation for client with {mac_or_duid}: {client_identifier}, IP address: {ip_address}, and hostname: {hostname}")
        # Implement your logic for configuring the reservation using the parsed arguments

    def do_option(self, args:str, negate=False):
        '''args: dhcp_option dhcp_value'''
        
        self.log.info(f"do_option() -> args: {args} -> negate:{negate}")
        
        args_parts = args.strip().split()
        
        if len(args_parts) == 2:
            dhcp_option, dhcp_value = args_parts
            if not DhcpOptionsLUT().dhcp_option_exists(dhcp_option):
                print(f"Invalid DHCP option: {dhcp_option}")
                return STATUS_NOK

        if self.isGlobalMode():
            self.log.info(f"Adding DHCP option to global configuration: {args}")
            DHCPDatabase().update_global_config(dhcp_option, dhcp_value)
    
    def do_tell(self, args):
        print(f"{DHCPDatabase().get_copy_dhcp_pool()}")
        print(f"{DHCPDatabase().get_copy_kea_dhcpv4_config()}")

    def do_commit(self):
        pass
    
class DHCPServerShow():
    """Command set for showing DHCPServer-Show-Command"""

    def __init__(self, args=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.args = args