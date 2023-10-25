import argparse
import cmd2
import logging
from lib.common.inet_ultils import IPUtilities as IPUltils

from lib.network_manager.interface import Interface, InterfaceType
from lib.network_manager.common.phy import Duplex, Speed, State
from lib.network_manager.arp import Arp, Encapsulate

from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.bridge import Bridge
from lib.network_manager.nat import NATDirection, Nat

from lib.db.interface_db import InterfaceDatabase as IFCDB

from lib.common.constants import *

from lib.cli.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

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
                        return None
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
            if IFCDB().add_interface(ifName, InterfaceType.ETHERNET):
                self.log.debug(f"Unable to add interface: {ifName} to DB")
            
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
                IFCDB().update_mac_address_db(self.ifName,new_mac)
                IFCDB().add_line_to_interface(f"mac auto")
                
        elif len(parts) == 2 and parts[0] == "address":
            mac = parts[1]
            self.log.debug(f"do_mac() -> address -> {mac}")
            
            if self.is_valid_mac_address(mac) == STATUS_OK:
                _, format_mac = self.format_mac_address(mac)
                
                self.log.debug(f"do_mac() -> mac: {mac} -> format_mac: {format_mac}")
                self.update_if_mac_address(self.ifName, format_mac)
                IFCDB().update_mac_address_db(self.ifName,format_mac)
                IFCDB().add_line_to_interface(f"mac address f{format_mac}")
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
        completions = ['address', 'secondary']
        completions.extend(['proxy-arp', 'drop-gratuitous-arp', 'static-arp'])
        completions.extend(['nat', 'inside', 'outside', 'pool'])
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_ip(self, args, negate=False):
        """
        Configure IP settings on the interface.

        Args:
            args (str): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Available suboptions:
        - `address <IP Address>/<CIDR> [secondary]`     : Set a static IP address.
        - `proxy-arp`                                   : Enable proxy ARP.
        - `drop-gratuitous-arp`                         : Enable drop gratuitous ARP.
        - `static-arp <inet> <mac> [arpa]`              : Add/Del static ARP entry.
        - `nat [inside|outside] pool <nat-pool-name>`   : Configure NAT address pool for inside or outside interface.

        Use `<suboption> --help` to get help for specific suboptions.
        """                   
        parser = argparse.ArgumentParser(
            description="Configure IP settings on the interface and NAT.",
            epilog="Available suboptions:\n"
                    "   address <IPv4 Address>/<CIDR> [secondary]               Set IP address/CIDR {optional secondary}.\n"
                    "   proxy-arp                                               Enable proxy ARP.\n"
                    "   drop-gratuitous-arp                                     Enable drop-gratuitous-ARP.\n"
                    "   static-arp <inet> <mac> [arpa]                          Add/Del static ARP entry.\n"
                    "   nat [inside|outside] pool <nat-pool-name> acl <acl-id>  Configure NAT for inside or outside interface."
                    "\n"
                    "Use <suboption> --help to get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        address_cidr_parser = subparsers.add_parser("address",
            help="Set a static IP address on the interface (e.g., 'ip address 192.168.1.1/24 [secondary]')."
        )
        address_cidr_parser.add_argument("ipv4_address_cidr",
                                help="IPv4 address/subnet to configure.")       
        address_cidr_parser.add_argument("secondary", nargs="?", const=True, default=False, 
            help="Indicate that this is a secondary IP address.")

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
        nat_in_out_parser.add_argument("nat_direction_pool",
            choices=['inside', 'outside'],
            help="Specify 'inside' for configuring NAT on the internal interface or 'outside' for the external interface."
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

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == "address":
            ipv4_address_cidr = args.ipv4_address_cidr
            is_secondary = args.secondary
            
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            if '/' in ipv4_address_cidr:
                ipv4_address, cidr = ipv4_address_cidr.split('/')
            else:
                ipv4_address, cidr = ipv4_address_cidr, "24"

            if not self.is_valid_ipv4(ipv4_address):
                raise InvalidInterface(f"Invalid Inet Address ({ipv4_address})")

            if not cidr.isdigit() or int(cidr) < 0 or int(cidr) > 32:
                raise InvalidInterface(f"Invalid CIDR prefix length ({cidr}). Must be between 0 and 32.")

            ip_prefix = IPUltils().convert_ip_mask_to_cidr(ipv4_address, int(cidr))

            if negate:
                self.log.debug(f"Removing IP: {ipv4_address}/{int(cidr)} to interface: {self.if_name} secondary: {is_secondary}")
                self.del_inet_address(self.ifName, ipv4_address, int(cidr), is_secondary)

                if ip_prefix:
                    IFCDB().update_ip_address(self.ifName, ip_prefix, is_secondary, negate)
                    IFCDB().add_line_to_interface(f"no ip {args.subcommand} {ipv4_address}/{cidr}")
                else:
                    self.log.fatal("Unable to add IP address to DB")
            else:
                self.log.debug(f"Setting IP: {ipv4_address}/{int(cidr)} to interface: {self.if_name} secondary: {is_secondary}")
                self.set_inet_address(self.ifName, ipv4_address, int(cidr), is_secondary)
                IFCDB().update_ip_address(self.ifName, ip_prefix, is_secondary, negate)
                IFCDB().add_line_to_interface(f"ip {args.subcommand} {ipv4_address}/{cidr}")
 
        elif args.subcommand == "proxy-arp":
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            
            if negate:
                disable = not negate
                self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> disable: {negate}")
                Arp().set_proxy_arp(self.ifName, negate)
                IFCDB().update_proxy_arp(self.ifName, disable)
                IFCDB().add_line_to_interface(f"no {args.subcommand}") 
            else:
                enable_proxy_arp = not negate
                self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> enable: {enable_proxy_arp}")
                Arp().set_proxy_arp(self.ifName, enable_proxy_arp)
                IFCDB().update_proxy_arp(self.ifName, enable_proxy_arp)
                IFCDB().add_line_to_interface(f"{args.subcommand}")
                
        elif args.subcommand == "drop-gratuitous-arp":
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            
            if negate:
                disable = not negate
                Arp().set_drop_gratuitous_arp(self.ifName, negate)
                IFCDB().update_drop_gratuitous_arp(self.ifName, disable)
                IFCDB().add_line_to_interface(f"no {args.subcommand}")
            else:
                enable_drop_grat_arp = not negate
                Arp().set_drop_gratuitous_arp(self.ifName, enable_drop_grat_arp)
                IFCDB().update_drop_gratuitous_arp(self.ifName, enable_drop_grat_arp)
                IFCDB().add_line_to_interface(f"{args.subcommand}")

        elif args.subcommand == "static-arp":
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args.ipv4_addr_arp
            mac_addr_arp = args.mac_addr_arp
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}")
            
            if negate:
                
                Arp().set_static_arp(ipv4_addr_arp, mac_addr_arp, 
                                     self.ifName, encap_arp, 
                                     add_arp_entry=False)
                IFCDB().update_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, encap_arp.value, negate=True)
                IFCDB().add_line_to_interface(f"no ip {args.subcommand} {ipv4_addr_arp} {mac_addr_arp}")
            
            else:
                
                self.log.debug(f"Set static-arp on Interface {self.ifName} -> Add ARP Entry: {True}")
                
                Arp().set_static_arp(ipv4_addr_arp, mac_addr_arp, 
                                     self.ifName, encap_arp, 
                                     add_arp_entry=True)
                
                IFCDB().update_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, str(encap_arp.value), negate=False)
                
                IFCDB().add_line_to_interface(f"ip {args.subcommand} {ipv4_addr_arp} {mac_addr_arp}")

        elif args.subcommand == "nat":
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            pool_name = args.pool_name
                        
            self.log.debug(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction} -> Pool: {pool_name}")

            if nat_direction == NATDirection.INSIDE.value:
                self.log.debug("Configuring NAT for the inside interface")
                
                if Nat().create_inside_nat(pool_name, self.ifName, negate):
                    self.log.error(f"Unable to set INSIDE NAT to interface: {self.ifName} to NAT-pool {pool_name}")
                    return STATUS_NOK

                if IFCDB().update_nat_direction(self.ifName, pool_name, NATDirection.INSIDE, negate):
                    self.log.debug(f"Unable to update NAT Direction: {nat_direction}")
                    return STATUS_NOK
                else:
                    IFCDB().add_line_to_interface(f"ip {args.subcommand} {nat_direction} pool {pool_name}")
                  
            elif nat_direction == NATDirection.OUTSIDE.value:
                self.log.debug("Configuring NAT for the outside interface")
                
                if Nat().create_outside_nat(pool_name, self.ifName, negate):
                    self.log.error(f"Unable to set OUTSIDE NAT to interface: {self.ifName} to NAT-pool {pool_name}")
                    return STATUS_NOK
                
                if IFCDB().update_nat_direction(self.ifName, pool_name, NATDirection.OUTSIDE, negate):
                    self.log.debug(f"Unable to update NAT Direction: {nat_direction}")
                    return STATUS_NOK
                else:
                    IFCDB().add_line_to_interface(f"ip {args.subcommand} {nat_direction} pool {pool_name}")                
            else:
                self.log.error(f"Invalid NAT type: {args.nat_type}, Use '{NATDirection.INSIDE.value}' or '{NATDirection.OUTSIDE.value}'")

    def complete_speed(self, text, line, begidx, endidx):
        completions = ['half', 'full', 'auto']        
        return [comp for comp in completions if comp.startswith(text)]

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

        if args in duplex_values:
            duplex = duplex_values[args]
            self.update_interface_duplex(self.ifName, duplex)
                        
        else:
            print(f"Invalid duplex mode ({args}). Use 'auto', 'half', or 'full'.")

    def complete_speed(self, text, line, begidx, endidx):
        completions = ['10', '100', '1000', '10000', 'auto']        
        return [comp for comp in completions if comp.startswith(text)]

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
            self.update_interface_speed(self.ifName, Speed.AUTO_NEGOTIATE)

        elif args in speed_values:
            speed = speed_values[args]
            self.update_interface_speed(self.ifName, speed)
            
        else:
            print("Invalid speed value. Use '10', '100', '1000', '10000', or 'auto'.")

    def complete_bridge(self, text, line, begidx, endidx):
        completions = ['group']
        return [comp for comp in completions if comp.startswith(text)]
        
    def do_bridge(self, args, negate=False):
        """
        Apply a bridge configuration to the interface.

        Args:
            args (str): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Debugging information:
            - This method logs debugging information with the provided arguments.

        Suboptions:
            - group <bridge name>: Set the bridge group identifier.
            - <suboption> --help: Get help for specific suboptions.
        """        
        self.log.debug(f"do_bridge() -> ARGS: ({args}) -> Negate: ({negate}))")
        
        parser = argparse.ArgumentParser(
            description="Apply bridge to interface",
            epilog="Suboptions:\n"
                "  group <bridge name>                          Add bridge to interface bridge group\n"
                "  <suboption> --help                           Get help for specific suboptions."
        )
         
        subparsers = parser.add_subparsers(dest="subcommand")
        bridge_parser = subparsers.add_parser("group",
            help="Set the bridge group ID"
        )
        
        bridge_parser.add_argument("br_grp_name", help="Bridge Group")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == 'group':
            bridge_name = args.br_grp_name
            if negate:
                self.log.debug(f"do_bridge().group -> Deleting Bridge {bridge_name}")
                Bridge().del_bridge_from_interface(self.ifName, args.bridge_name)
            else:
                self.log.debug(f"do_bridge().group -> Adding Bridge: {bridge_name} to Interface: {self.ifName}")
                Bridge().add_bridge_to_interface(self.ifName, bridge_name)
        
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

        self.update_shutdown(self.ifName, ifState)

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
                    self.del_interface_vlan(vlan_id)
                    InterfaceConfigDB.add_line_to_interface(self.ifName, f"no switchport {args.subcommand} {args.access_subcommand} {vlan_id}")
                else:
                    self.log.debug(f"Setting access mode with VLAN ID {vlan_id} to interface: {self.ifName}")
                    self.update_interface_vlan(self.ifName, vlan_id)
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

