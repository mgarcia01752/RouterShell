import argparse
import cmd2
import logging
from lib.common.inet_ultils import IPUtilities as IPUltils

from lib.network_manager.interface import Interface, InterfaceType
from lib.network_manager.phy import Duplex, Speed, State
from lib.network_manager.arp import Arp, Encapsulate

from lib.cli.base.global_operation import GlobalUserCommand
from lib.common.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.bridge import Bridge
from lib.network_manager.nat import NATDirection, Nat

from lib.db.interface_db import InterfaceConfigDB as IFCDB

from lib.common.constants import *

from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS

class InvalidInterface(Exception):
    def __init__(self, message):
        super().__init__(message)

class InterfaceConfig(cmd2.Cmd, 
                      GlobalUserCommand, 
                      RouterPrompt, 
                      Interface):
    
    bridge_name=""
    
    def __init__(self, ifName: str, ifType:str=None):
        super().__init__()
            
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().IF_CONFIG)
        self.debug = CGS().DEBUG_IF_CONFIG
        
        GlobalUserCommand.__init__(self)
        Interface.__init__(self)
        
        self.log.debug(f"InterfaceConfig() -> ({ifName})")
        
        if ifType in [member.value for member in InterfaceType]:
            self.PROMPT_CMD_ALIAS = ifType
            self.log.debug(f"Interface Type is {ifType} - Type-> {InterfaceType.LOOPBACK.value}")
            
            '''Concatenate for Vlan + loopback (Assuming at this point)'''
            ifName = ifType + ifName
            
            if ifType == InterfaceType.LOOPBACK.value:
                self.log.debug(f"Creating {ifName} if it does not exists....")
                
                #Create interface if it does not exists
                if not self.does_interface_exist(ifName):
                    self.log.debug(f"Creating Loopback {ifName}")
                    if self.create_loopback(ifName):
                        return STATUS_NOK
                    else:
                        self.log.debug(f"Adding Loopback to DB")
                        IFCDB().add_interface(ifName, ifType)
                else:
                    self.log.debug(f"Not Creating Loopback {ifName}")
        else:
            self.PROMPT_CMD_ALIAS = InterfaceType.DEFAULT.value
        
        if not self.does_interface_exist(ifName):
            print(f"Interface {ifName} does not exists.")
            RouterPrompt.__init__(self, ExecMode.CONFIG_MODE)
            self.do_end()
        else:
            RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
            '''
                TODO:   Need a way to auto detect or verify the interface type
                        Right now, all interfaces are ethernet, except loopback
            '''
            
            if IFCDB().add_interface(ifName, InterfaceType.ETHERNET.value):
                self.log.debug(f"Unable to add interface: {ifName} to DB")
                return STATUS_NOK
            
        self.ifName = ifName
        self.prompt = self.set_prompt()
        self.log.debug(f"InterfaceConfig() - ifType: {ifType} -> ifName: {ifName}")
        
    def do_help(self, args=None):
        print("mac\t\t\t\tmac address")
        print("ip\t\t\t\tip")
        print("ipv6\t\t\t\tipv6")
        print("duplex\t\t\t\tduplex")
        print("speed\t\t\t\tspeed")
        
    def _exit_init(self):
        '''Exit for __init__()'''
        return False
            
    def complete_mac(self, text, line, begidx, endidx):
        completions = ['address', 'auto']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_mac(self, args):
        # Split the input arguments to separate the command and the MAC address
        parts = args.strip().split()

        self.log.debug(f"do_mac() -> Parts: {parts}")
        
        if len(parts) == 1 and parts[0] == "auto":
            new_mac = self.generate_random_mac()
            self.log.debug(f"do_mac() -> auto -> {new_mac}")
            
            if not self.update_if_mac_address(self.ifName, new_mac):
                
                IFCDB().update_mac_address(self.ifName,new_mac)
                IFCDB().add_line_to_interface(self.ifName, f"mac auto")
                
        elif len(parts) == 2 and parts[0] == "address":
            mac = parts[1]
            self.log.debug(f"do_mac() -> address -> {mac}")
            
            if self.is_valid_mac_address(mac) == STATUS_OK:
                _, format_mac = self.format_mac_address(mac)
                
                self.log.debug(f"do_mac() -> mac: {mac} -> format_mac: {format_mac}")
                self.update_if_mac_address(self.ifName, format_mac)
                IFCDB().update_mac_address(self.ifName,format_mac)
                IFCDB().add_line_to_interface(self.ifName, f"mac address f{format_mac}")
            else:
                print(f"Invalid MAC address: {mac}")
        else:
            print("Usage: mac [auto | <MAC_ADDRESS>]")
        
    def complete_ipv6(self, text, line, begidx, endidx):
        completions = ['address', 'dhcp']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_ipv6(self, args, negate=False):
 
        parser = argparse.ArgumentParser(
            description="Configure IPv6 settings on the interface",
            epilog="Cisco-style suboptions:\n"
                "  address <IPv6 Address>/<Mask>               Set static IPv6 address.\n"
                "  dhcp                                        Configure DHCP client.\n"
                "  <suboption> --help                          Get help for specific suboptions."
        )
        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for 'ip address' command
        address_parser = subparsers.add_parser(
            "address",
            help="Set a static IP address on the interface (e.g., 'ipv6 address fd00:1234:5678:abcd::1/64')."
        )
        address_parser.add_argument("ipv6_address_mask", help="IPv6 address and mask to configure.")

        # Subparser for 'ip dhcp' command
        dhcp_parser = subparsers.add_parser(
            "dhcp",
            help="Configure DHCP client on the interface (e.g., 'ipv6 dhcp')."
        )

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == "address":
            ipv6_address_mask = args.ipv6_address_mask
            
            self.log.debug(f"Configuring static IPv6 Address on Interface ({self.ifName}) -> Inet: ({ipv6_address_mask})")
            
            if not self.is_valid_ipv6(ipv6_address_mask):
                raise InvalidInterface(f"Invalid Inet Address ({ipv6_address_mask})")
            
            if negate:
                result = self.del_inet6_address(self.ifName, ipv6_address_mask)
                if result.exit_code:
                    self.log.debug(f"Unable to del IPv6 Address: {ipv6_address_mask} from interface: {self.ifName}")  
            else:    
                result = self.set_inet6_address(self.ifName, ipv6_address_mask)
                if result.exit_code:
                    self.log.debug(f"Unable to add IPv6 Address: {ipv6_address_mask} to interface: {self.ifName}")  
            
        elif args.subcommand == "dhcp":
            print(f"Configuring DHCPv6 client on Interface {self.ifName}")
            # Implement the logic to configure DHCP client here.       

    def complete_ip(self, text, line, begidx, endidx):
        completions = ['address', 'proxy-arp', 'drop-gratuitous-arp', 'static-arp']
        completions.extend(['nat', 'inside', 'outside', 'pool'])
        
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_ip(self, args, negate=False):
        """
        Configure IP settings on the interface.

        Args:
            args (str): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Available suboptions:
        - `address <IPv4 Address> <IPv4 Subnet Mask>`: Set a static IP address.
        - `proxy-arp`: Enable proxy ARP.
        - `drop-gratuitous-arp`: Enable drop gratuitous ARP.
        - `static-arp <inet> <mac> [arpa]`: Add/Del static ARP entry.
        - `nat pool <nat-pool-name>`: Configure NAT pool name. 
        - `nat [inside|outside]`: Configure NAT address pool for inside or outside interface.

        Use `<suboption> --help` to get help for specific suboptions.
        """                   
        parser = argparse.ArgumentParser(
            description="Configure IP settings on the interface and NAT.",
            epilog="Available suboptions:\n"
                    "   address <IPv4 Address> <IPv4 Subnet Mask>           Set static IP address.\n"
                    "   proxy-arp                                           Enable proxy ARP.\n"
                    "   drop-gratuitous-arp                                 Enable drop-gratuitous-ARP.\n"
                    "   static-arp <inet> <mac> [arpa]                      Add/Del static ARP entry.\n"
                    "   nat pool <pool-name>                                Configure NAP pool name.\n"   
                    "   nat pool <pool-name> [inside|outside] acl <acl-id>  Configure NAT for inside or outside interface."
                    "\n"
                    "Use <suboption> --help to get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        address_parser = subparsers.add_parser( "address",
            help="Set a static IP address on the interface (e.g., 'ip address 192.168.1.1 255.255.255.0')."
        )
        address_parser.add_argument("ipv4_address", 
                                    help="IPv4 address to configure.")
        address_parser.add_argument("subnet_mask", 
                                    help="IPv4 subnet mask to configure.")

        subparsers.add_parser("proxy-arp",
            help="Set proxy-arp on the interface 'ip proxy-arp')."
        )
        
        subparsers.add_parser("drop-gratuitous-arp",
            help="Set drop-gratuitous-arp on the interface 'ip drop-gratuitous-arp')."
        )

        static_arp_parser = subparsers.add_parser("static-arp",
            help="Set static-arp on the interface 'ip static-arp <IPv4 Address> <Mac Address> [Encapsulation Type arpa]')."
        )
        static_arp_parser.add_argument("ipv4_addr_arp",         
                                       help="IPv4 address for arp entry.")
        static_arp_parser.add_argument("mac_addr_arp",          
                                       help="Mac address for arp entry.")
        static_arp_parser.add_argument("encap_arp", nargs='?',  
                                       help="Ecapsulation type [arpa].")     
          
        nat_in_out_parser = subparsers.add_parser("nat",
            help="Configure Network Address Translation (NAT) for inside or outside interfaces."
        )
        
        nat_in_out_parser.add_argument("pool_option",
            nargs='?',
            choices=["pool"],
            help="Specify 'pool' followed by the NAT pool name when configuring NAT."
        )

        nat_in_out_parser.add_argument("pool_name",
            nargs='?',
            help="Specify the NAT pool name when configuring NAT."
        )

        nat_in_out_parser.add_argument("nat_direction_pool",
            choices=['inside', 'outside'],
            help="Specify 'inside' for configuring NAT on the internal interface or 'outside' for the external interface."
        )

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == "address":
            ipv4_address = args.ipv4_address
            subnet_mask = args.subnet_mask
            
            self.log.debug(f"Configuring static IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address}) Mask:({subnet_mask})")
            
            if not self.is_valid_ipv4(ipv4_address):
                raise InvalidInterface(f"Invalid Inet Address ({ipv4_address})")
            
            if not self.is_valid_ipv4(subnet_mask):
                raise InvalidInterface(f"Invalid Inet Subnet ({ipv4_address})")
            
            if negate:
                self.del_inet_address(self.ifName, ipv4_address, subnet_mask)
                
                ip_prefix = IPUltils().convert_ip_mask_to_ip_prefix(ipv4_address, subnet_mask)
                
                if ip_prefix:
                    IFCDB().update_ip_address(self.ifName, ip_prefix)
                    IFCDB().add_line_to_interface(self.ifName, f"no ip {args.subcommand} {ipv4_address} {subnet_mask}")
                else:
                    self.log.fatal("Unable to add IP address to DB")
            else:
                self.set_inet_address(self.ifName, ipv4_address, subnet_mask)
                IFCDB().add_line_to_interface(self.ifName, f"ip {args.subcommand} {ipv4_address} {subnet_mask}")
            
        elif args.subcommand == "proxy-arp":
            self.log.debug(f"Set proxy-arp on Interface {self.ifName}")
            if negate:
                Arp().set_proxy_arp(self.ifName, not negate)
                IFCDB.update_proxy_arp(self.ifName, True)
                IFCDB.add_line_to_interface(self.ifName, f"no {args.subcommand}") 
            else:
                Arp().set_proxy_arp(self.ifName, negate)
                IFCDB.update_proxy_arp(self.ifName, False)
                IFCDB().add_line_to_interface(self.ifName, f"{args.subcommand}")
                
        elif args.subcommand == "drop-gratuitous-arp":
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            if negate:
                Arp().set_drop_gratuitous_arp(self.ifName, not negate)
                IFCDB().update_drop_gratuitous_arp(self.ifName, True)
                IFCDB().add_line_to_interface(self.ifName, f"no {args.subcommand}")
            else:
                Arp().set_drop_gratuitous_arp(self.ifName, negate)
                IFCDB().update_drop_gratuitous_arp(self.ifName, False)
                IFCDB().add_line_to_interface(self.ifName, f"{args.subcommand}")

        elif args.subcommand == "static-arp":
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args.ipv4_addr_arp
            mac_addr_arp = args.mac_addr_arp
            nat_direction = args.nat_direction_pool
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            if negate:
                Arp().set_static_arp(ipv4_addr_arp, mac_addr_arp, 
                                     self.ifName, encap_arp, add_arp_entry=False)
                IFCDB().update_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, encap_arp, negate)
                IFCDB().add_line_to_interface(self.ifName, f"no ip {args.subcommand} {ipv4_addr_arp} {mac_addr_arp}")
            
            else:
                Arp().set_static_arp(ipv4_addr_arp, mac_addr_arp, 
                                     self.ifName, encap_arp, add_arp_entry=True)
                IFCDB().update_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, encap_arp, not negate)
                IFCDB().add_line_to_interface(self.ifName, f"ip {args.subcommand} {ipv4_addr_arp} {mac_addr_arp}")

        elif args.subcommand == "nat":
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            pool_name = args.pool_name
            
            self.log.info(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction} -> Pool: {pool_name}")

            if nat_direction == NATDirection.INSIDE.value:
                self.log.info("Configuring NAT for the inside interface")
                
                if Nat().create_inside_nat(pool_name, self.ifName, negate):
                    self.log.error(f"Unable to set INSIDE NAT to interface: {self.ifName} to NAT-pool {pool_name}")
                    return STATUS_NOK

                if IFCDB().update_nat_direction(self.ifName, pool_name, NATDirection.INSIDE, negate):
                    self.log.debug(f"Unable to update NAT Direction: {nat_direction}")
                    return STATUS_NOK
                else:
                    IFCDB().add_line_to_interface(self.ifName, f"ip {args.subcommand} {nat_direction} pool {pool_name}")
                  
            elif nat_direction == NATDirection.OUTSIDE.value:
                self.log.info("Configuring NAT for the outside interface")
                
                if Nat().create_outside_nat(pool_name, self.ifName, negate):
                    self.log.error(f"Unable to set OUTSIDE NAT to interface: {self.ifName} to NAT-pool {pool_name}")
                    return STATUS_NOK
                
                if IFCDB().update_nat_direction(self.ifName, pool_name, NATDirection.OUTSIDE, negate):
                    self.log.debug(f"Unable to update NAT Direction: {nat_direction}")
                    return STATUS_NOK
                else:
                    IFCDB().add_line_to_interface(self.ifName, f"ip {args.subcommand} {nat_direction} pool {pool_name}")                
            else:
                self.log.error(f"Invalid NAT type: {args.nat_type}, Use '{NATDirection.INSIDE.value}' or '{NATDirection.OUTSIDE.value}'")

    def do_duplex(self, args):
        '''
        Set the duplex mode of a network interface.
        Usage: duplex <auto | half | full>
        '''
        if not args:
            print("Usage: duplex <auto | half | full>")
            return

        duplex_values = {d.value: d for d in Duplex}
        args = args.lower()

        self.log.debug(f"do_duplex() -> ARGS: {args}")    
        self.log.debug(f"do_duplex() -> duplex_modes: {duplex_values}")    
        
        if args in duplex_values:
            duplex = duplex_values[args]
            self.set_duplex(self.ifName, duplex)
            
            if IFCDB.update_duplex_status(self.ifName, duplex):
                self.log.debug(f"Unable to update duplex: {duplex}")
                return STATUS_NOK    
            
            IFCDB().add_line_to_interface(self.ifName, f"duplex {duplex}")
            
        else:
            print("Invalid duplex mode. Use 'auto', 'half', or 'full'.")

    def do_speed(self, args):
        '''
        Set the speed of a network interface.
        Usage: speed <10 | 100 | 1000 | 10000 | auto>
        '''
        if not args:
            print("Usage: speed <10 | 100 | 1000 | 10000 | auto>")
            return

        self.log.debug(f"do_speed() -> ARGS: {args}")
        
        speed_values = {str(s.value): s for s in Speed}
        args = args.lower()

        if args == "auto":
            self.set_ifSpeed(self.ifName, Speed.MBPS_10, Speed.AUTO_NEGOTIATE)
            
        elif args in speed_values:
            speed = speed_values[args]
            self.set_ifSpeed(self.ifName, speed)
            # TODO IFCDB().add_line_to_interface(self.ifName, f"speed {speed}")
        else:
            print("Invalid speed value. Use '10', '100', '1000', '10000', or 'auto'.")

    def complete_bridge(self, text, line, begidx, endidx):
        completions = ['group']
        return [comp for comp in completions if comp.startswith(text)]

    def do_bridge_group(self, args, negate=False):
        """
        Apply a bridge configuration to the interface.

        Args:
            args (str): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Debugging information:
            - This method logs debugging information with the provided arguments.

        Suboptions:
            - group <id>: Set the bridge group identifier.
            - <suboption> --help: Get help for specific suboptions.
        """        
        self.log.debug(f"do_bridge_group() -> ARGS: ({args}) -> Negate: ({negate})")
        
        # Split the arguments to obtain the bridge name
        bridge_name = args.strip().split()[0] if args else None

        if bridge_name:
            self.log.debug(f"do_bridge_group() -> Adding to Bridge {bridge_name}")
            if not negate:
                Bridge().add_interface_cmd(self.ifName, bridge_name)
                InterfaceConfigDB.add_line_to_interface(self.ifName, f"bridge group {self.ifName} {bridge_name}")
            else:
                Bridge().del_interface_cmd(self.ifName)
        
    def do_bridge(self, args, negate=False):
        """
        Apply a bridge configuration to the interface.

        Args:
            args (str): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Debugging information:
            - This method logs debugging information with the provided arguments.

        Suboptions:
            - group <id>: Set the bridge group identifier.
            - <suboption> --help: Get help for specific suboptions.
        """        
        self.log.debug(f"do_bridge() -> ARGS: ({args}) -> Negate: ({negate}))")
        
        parser = argparse.ArgumentParser(
            description="Apply bridge to interface",
            epilog="Suboptions:\n"
                "  group <id>                                   Set static IPv6 address.\n"
                "  <suboption> --help                           Get help for specific suboptions."
        )
         
        subparsers = parser.add_subparsers(dest="subcommand")
        bridge_parser = subparsers.add_parser(
            "group",
            help="Set the bridge group ID"
        )
        
        bridge_parser.add_argument("bridge_group_id", help="Bridge Group")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == 'group':
            if negate:
                self.log.debug(f"do_bridge().group -> Deleting Bridge {args.bridge_group_id}")
                Bridge().del_interface_cmd(self.ifName, args.bridge_group_id)
            else:
                self.log.debug(f"do_bridge().group -> Adding Bridge: {args.bridge_group_id} to Interface: {self.ifName}")
                Bridge().add_interface_cmd(self.ifName, args.bridge_group_id)
                InterfaceConfigDB.add_line_to_interface(self.ifName, f"bridge {args.subcommand} {self.ifName}")
        
        return 
    
    def do_shutdown(self, args=None, negate=False):
        """
        This function is used to change the state of an interface to either UP or DOWN.

        Args:
            self: The instance of the class containing this method.
            args (list): A list of arguments. If the list contains only the string 'no', the interface
                        state will be set to DOWN; otherwise, it will be set to UP.

        Returns:
            str: A message indicating the result of the interface state change.
        """
        ifState = State.DOWN
        
        if negate:
            ifState = State.UP
            shutdown_stat = f"no shutdown"
        else:
            shutdown_stat = f"shutdown"
        
        IFCDB().add_line_to_interface(self.ifName, f"{shutdown_stat}")
        
        return self.set_interface_state(self.ifName, ifState)

    def complete_switchport(self, text, line, begidx, endidx):
        completions = ['access', 'mode']
        return [comp for comp in completions if comp.startswith(text)]
 
    def do_switchport(self, args=None, negate=False):
        """
        Configure switchport settings.

        Args:
            args (str, optional): Command arguments. Defaults to None.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Debugging information:
            - This method logs debugging information with the provided arguments.

        Subcommands:
            - mode access: Configure the switchport in access mode.
            - access vlan <id>: Set the access VLAN identifier.
            - <suboption> --help: Get help for specific subcommands and suboptions.
        """
        self.log.debug(f" switchport() -> {args}")

        parser = argparse.ArgumentParser(
            description="Configure switchport.",
            epilog="Available subcommands:\n"
                "  mode access\n"
                "  access vlan <id>\n"
                "  <suboption> --help     Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for 'mode' subcommand
        mode_parser = subparsers.add_parser(
            "mode",
            help="Set switchport mode (access or trunk)"
        )

        mode_parser.add_argument(
            "mode_type",
            choices=["access", "trunk"],
            help="Select switchport mode (access or trunk)"
        )

        access_parser = subparsers.add_parser(
            "access",
            help="Configure access mode settings"
        )

        vlan_parser = access_parser.add_subparsers(dest="access_subcommand")

        vlan_parser.add_parser(
            "vlan",
            help="Set the access VLAN ID"
        ).add_argument(
            "vlan_id",
            type=int,
            help="Set the access VLAN ID"
        )

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == "mode":
            if args.mode_type == "access":
                self.log.debug("Setting switchport mode to access")
            elif args.mode_type == "trunk":
                self.log.debug("Setting switchport mode to trunk")
            InterfaceConfigDB.add_line_to_interface(self.ifName, f"switchport {args.subcommand} {args.mode_type}")
        
        elif args.subcommand == "access":
            if args.access_subcommand == "vlan":
                vlan_id = args.vlan_id
                if negate:
                    self.log.debug(f"Deleting access mode with VLAN ID {vlan_id} to interface: {self.ifName}")
                    self.del_vlan(vlan_id)
                    InterfaceConfigDB.add_line_to_interface(self.ifName, f"no switchport {args.subcommand} {args.access_subcommand} {vlan_id}")
                else:
                    self.log.debug(f"Setting access mode with VLAN ID {vlan_id} to interface: {self.ifName}")
                    self.set_vlan(self.ifName, vlan_id)
                    InterfaceConfigDB.add_line_to_interface(self.ifName, f"switchport {args.subcommand} {args.access_subcommand} {vlan_id}") 
            else:
                self.log.error(f"Unknown subcommand under 'access': {args.access_subcommand}")
        else:
            self.log.debug(f"Unknown subcommand: {args.subcommand}")

    def complete_no(self, text, line, begidx, endidx):
        completions = ['shutdown', 'bridge', 'group', 'ip', 'ipv6', 'address']
        return [comp for comp in completions if comp.startswith(text)]
        
    def do_no(self, line):
        """
        Negate or remove a previously configured setting or command.

        Args:
            line (str): The command or setting to negate or remove.

        Debugging Information:
            - This method logs debugging information about the actions performed.

        Supported Commands:
            - shutdown: Enable the interface (opposite of 'shutdown' command).
            - bridge <args>: Remove a bridge configuration.
            - ip <args>: Remove an IP configuration.
            - ipv6 <args>: Remove an IPv6 configuration.
            - switchport <args>: Remove switchport settings.

        Example:
            To remove a previously configured setting:
                no setting_name

        Note:
            This command is used to negate or remove a previously configured setting or command.
        """
        self.log.debug(f"do_no() -> Line -> {line}")
        
        parts = line.strip().split()
        start_cmd = parts[0]
        
        self.log.debug(f"do_no() -> Start-CMD -> {start_cmd}")
        
        if start_cmd == 'shutdown':
            self.log.debug(f"Enable interface -> {self.ifName}")
            self.do_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({line})")
            self.do_bridge(parts[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({line})")
            self.do_ip(parts[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({line})")
            self.do_ipv6(parts[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({line})")
            self.do_switchport(parts[1:], negate=True)
       
    def create_default_interface_config(self) -> bool:
        '''
        Default configuration 
        interface <physical_interface>
            duplex auto
            speed auto
            shutdown     
        '''
        self.do_speed(Speed.AUTO_NEGOTIATE.value)
        self.do_duplex(Duplex.AUTO.value)
        self.do_shutdown(False)
