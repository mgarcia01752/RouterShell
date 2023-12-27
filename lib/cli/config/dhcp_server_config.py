import argparse
import logging

import cmd2

from lib.network_manager.dhcp_server import DHCPServer, DhcpPoolFactory

from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.router_prompt import RouterPrompt

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.cli.common.cmd2_global import Cmd2GlobalSettings as cgs

from lib.common.common import STATUS_NOK, STATUS_OK
from lib.network_services.dhcp.common.dhcp_common import DHCPOptionLookup, DHCPVersion
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DHCPv6Modes

class DHCPServerConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt):
    
    GLOBAL_CONFIG_MODE = 'global'
    PROMPT_CMD_ALIAS = 'dhcp'    
    
    def __init__(self, dhcp_pool_name: str, negate=False):
        self.dhcp_pool_name = dhcp_pool_name
        self.negate = negate
        
        super().__init__()        
        GlobalUserCommand.__init__(self)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_SERVER_CONFIG)
        self.debug = cgs.DEBUG_GLOBAL
        
        self.log.debug(f"DHCPServerConfig({dhcp_pool_name}) -> negate: {negate}")
        
        prompt_ext = ""
        if self.isGlobalMode() :
            prompt_ext = f'-{dhcp_pool_name}'
        else:
            self.log.debug(f"DHCPServerConfig() -> Not in DHCP Global Config Mode")
        
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, f'{self.PROMPT_CMD_ALIAS}{prompt_ext}')
        self.prompt = self.set_prompt()
        
        self.dhcp_pool_factory = DhcpPoolFactory(dhcp_pool_name)
                
    def isGlobalMode(self) -> bool:
        return self.dhcp_pool_name == self.GLOBAL_CONFIG_MODE
    
    def do_subnet(self, args: str):
        '''
        Configure a subnet with the specified IP address and subnet mask.

        Args:
            args (str): The arguments for the 'subnet' command, which should include an IP address and a subnet mask.

        Example ULA IPv4 | IPv6 :
            subnet 192.168.1.0/24 | fd00:1::/64
        '''
        self.log.debug(f"do_subnet() -> args: {args} -> negate: {self.negate}")

        parser = argparse.ArgumentParser(
            description="Configure a DHCP server subnet",
            epilog="Use 'subnet <inet-subnet>/<CIDR>' to set the subnet."
        )

        # Define the arguments directly without subcommands
        parser.add_argument("inet_subnet_cidr", help="The IP address/mask of the subnet")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        inet_subnet_cidr = args.inet_subnet_cidr
        self.log.debug(f"Configuring subnet with INET Subnet: {inet_subnet_cidr}")
        self.dhcp_pool_factory.add_pool_subnet(inet_subnet_cidr)
        
    def do_pool(self, args: str):
        '''
        Configure an IP pool with the specified start and end IP addresses and subnet mask.

        Args:
            args (str): The arguments for the 'pools' command, which should include the start IP address, end IP address, and subnet mask.

        Example:
            pools 192.168.1.10 192.168.1.20 255.255.255.0
        '''
        self.log.debug(f"do_pool() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure an IP pool for the DHCP server",
            epilog="Use 'pools <ip-address-start> <ip-address-end> <ip-subnet-mask>' to set the pool."
        )

        # Define the arguments directly without subcommands
        parser.add_argument("inet_start", help="The starting IP address of the pool")
        parser.add_argument("inet_end", help="The ending IP address of the pool")
        parser.add_argument("inet_subnet_cidr", help="The subnet mask for the pool")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        # Access the parsed arguments directly
        inet_start = args.inet_start
        inet_end = args.inet_end
        inet_subnet_cidr = args.inet_subnet_cidr

        # Handle the 'pools' command logic here
        self.log.debug(f"Configuring IP pool with start IP: {inet_start}, end IP: {inet_end}, and subnet mask: {inet_subnet_cidr}")
        self.dhcp_pool_factory.add_inet_pool_range(inet_start, inet_end, inet_subnet_cidr)
        
    def do_reservations(self, args: str):
        '''
        Configure a reservation for a client with the specified MAC address, IP address, and optional hostname.

        Args:
            args (str): The arguments for the 'reservations' command, which should include the MAC address, IP address, and optional hostname.

        Example:
            reservations hw-address 00:11:22:33:44:55 ip-address 192.168.1.10 hostname client1
        '''
        self.log.debug(f"do_reservations() -> args: {args}")

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
        self.log.debug(f"Configuring reservation for client with {mac_or_duid}: {client_identifier}, IP address: {ip_address}, and hostname: {hostname}")
        self.dhcp_pool_factory.add_reservation(client_identifier, ip_address)

    def do_option(self, args:str, negate=False):
        '''args: dhcp_option dhcp_value'''
        
        self.log.debug(f"do_option() -> args: {args} -> negate:{negate}")
        
        args_parts = args.strip().split()
        
        if len(args_parts) == 2:
            
            dhcp_option, dhcp_value = args_parts
            if self.dhcp_pool_factory.get_subnet_inet_version() == DHCPVersion.DHCP_V4:
                if not DHCPOptionLookup().get_dhcpv4_option_code(dhcp_option):
                    print(f"Invalid IPv4 DHCP option: {dhcp_option}")
                    return 
            else:
                if not DHCPOptionLookup().get_dhcpv6_option_code(dhcp_option):
                    print(f"Invalid IPv6 DHCP option: {dhcp_option}")
                    return 
        else:                     
            print(f"Invalid DHCP option: {dhcp_option}")   
        
        if self.isGlobalMode():
            self.log.debug(f"Adding DHCP option to global configuration: {args}")

        self.dhcp_pool_factory.add_option(dhcp_option, dhcp_value)

    def do_mode(self, args:str, negate=False):
        '''
        Set the DHCPv6 Mode.

        Args:
            args (List[str]): List of arguments.
            negate (bool): Whether to negate the mode.

        Example:
            Use 'mode <[slaac | ra-only | ra-names | ra-stateless | ra-advrouter | off-link]>'
            to set the DHCPv6 mode.
        '''

        self.log.debug(f"do_mode() -> args: {args}")

        parser = argparse.ArgumentParser(
            description="Set the DHCPv6 Mode",
            epilog="Example: Use 'mode <[slaac | ra-only | ra-names | ra-stateless | ra-advrouter | off-link]>' to set the DHCPv6 mode."
        )

        # Define the argument directly without subcommands
        parser.add_argument('mode', choices=['ra-only', 'slaac', 'ra-names', 'ra-stateless', 'ra-advrouter', 'off-link'],
                            help='Set the DHCPv6 mode.')

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return     

        if self.dhcp_pool_factory.get_subnet_inet_version() == DHCPVersion.DHCP_V4:
            print('DHCP mode is reserved for a DHCPv6 subnet')
            return

        self.dhcp_pool_factory.add_dhcp_mode(DHCPv6Modes.get_key(args.mode))


    def do_commit(self) -> bool:
        return STATUS_OK
    