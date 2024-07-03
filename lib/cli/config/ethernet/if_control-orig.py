import argparse
import logging
from typing import List, Optional

from lib.cli.common.exec_priv_mode import ExecMode

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.string_formats import StringFormats
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.phy import Duplex, Speed, State
from lib.network_manager.network_operations.arp import Encapsulate
from lib.network_manager.network_operations.bridge import Bridge
from lib.network_manager.network_operations.dhcp_client import DHCPStackVersion
from lib.network_manager.network_operations.dhcp_server import DHCPServer
from lib.network_manager.network_operations.interface import Interface
from lib.network_manager.network_operations.nat import NATDirection


class InterfaceConfigError(Exception):
    """Custom exception for IfConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'IfConfigError: {self.message}'

class InterfaceConfig(CmdPrompt, Interface):

    def __init__(self, ifName: str=None, ifType: InterfaceType=InterfaceType.ETHERNET) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ETHERNET_CONFIG)
        
        self.ifName = ifName
               
    def interfaceconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
        return STATUS_OK
            
    @CmdPrompt.register_sub_commands() 
    def interfaceconfig_description(self, line: Optional[str], negate: bool = False) -> bool:
        """
        Updates the interface configuration description in the database.
        
        Args:
            line (Optional[str]): The description to be added. If None, the description will be empty.
            negate (bool): If True, the line will be set to None.
        
        Returns:
            bool: STATUS_OK indicating the operation was successful.
        
        Raises:
            ValueError: If there is an issue updating the database description.
        """
        if negate:
            self.log.debug(f'Negating description on interface: {self.ifName}')
            line = [""]
        
        if self.update_db_description(self.ifName, StringFormats.list_to_string(line)):
            print("Unable to add description to DB")
            raise ValueError("Failed to update the description in the database.")
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['auto'],     help='Auto assign mac address')
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address'],  help='Assign mac address <xxxx.xxxx.xxxx>')     
    def interfaceconfig_mac(self, args:str) -> bool:
        
        self.log.debug(f"interfaceconfig_mac() -> args: {args}")
        
        if len(args) == 1 and args[0] == "auto":
            self.log.debug(f"interfaceconfig_mac() -> auto")
            self.update_interface_mac(self.ifName)
                            
        elif len(args) == 2 and args[0] == "address":
            mac = args[1]
            self.log.debug(f"interfaceconfig_mac() -> address -> {mac}")
            self.update_interface_mac(self.ifName, mac)
            
        else:
            print("Usage: mac [auto | <mac address>]")
            
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_ip6(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['drop-gratuitous-arp'])        
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['proxy-arp'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['static-arp', 'arpa'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'inside', 'pool', 'acl'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'outside', 'pool', 'acl'])
    def X_ip(self, args: List, negate=False) -> bool:

        self.log.debug(f'interfaceconfig_ip() -> {args}')

        if 'address' in args[0]:
            ipv4_address_cidr = args[1]
            is_secondary = False
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        elif "proxy-arp" in args[0]:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            self.update_interface_proxy_arp(self.ifName, negate)
                
        elif "drop-gratuitous-arp" in args[0]:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            self.update_interface_drop_gratuitous_arp(self.ifName, negate)

        elif "static-arp" in args[0]:
            '''[no] [ip static-arp ip-address mac-address arpa]'''
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args[1]
            mac_addr_arp = args[2]
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}") 
            self.update_interface_static_arp(self.ifName, ipv4_addr_arp, mac_addr_arp, encap_arp, negate)
            
        elif "nat" in args[0]:
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            nat_pool_name = args.pool_name
                        
            try:
                nat_direction = NATDirection(nat_direction)
            except ValueError:
                print(f"Error: Invalid NAT direction '{nat_direction}'. Use 'inside' or 'outside'.")

            self.log.debug(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction.value} -> Pool: {nat_pool_name}")

            if self.set_nat_domain_status(self.ifName, nat_pool_name, nat_direction):
                self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")

        elif "dhcp-client" in args[0]:
            '''[no] [ip dhcp-client]'''
            self.log.debug(f"Enable DHCPv4 Client")
            if Interface().update_interface_dhcp_client(self.ifName, DHCPStackVersion.DHCP_V4, negate):
                self.log.fatal(f"Unable to set DHCPv4 client on interface: {self.ifName}")

        elif "dhcp-server" in args[0]:
            pool_name = args.pool_name
            '''[no] [ip dhcp-server] pool <dhcp-pool-name>'''
            self.log.debug(f"Enable DHCPv4/6 Server")
            DHCPServer().add_dhcp_pool_to_interface(pool_name, self.ifName, negate)
  
        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    def interfaceconfig_ip(self, args: List[str], negate=False) -> bool:
        """
        Configure IP settings on the interface.

        Args:
            args (List[str]): Command arguments.
            negate (bool, optional): True to negate the command, False otherwise. Defaults to False.

        Available suboptions:
        - `address <IP Address>/<CIDR> [secondary]`     : Set a static IP address.
        Use `<suboption> --help` to get help for specific suboptions.
        """

        self.log.debug(f'interfaceconfig_ip4() -> ({args})')
        if not args:
            print('Missing command arguments')
            return STATUS_NOK

        if '?' in args:
            args = [arg if arg != '?' else '--help' for arg in args]

        parser = argparse.ArgumentParser(
            description="Configure IP settings on the interface.",
            epilog="Available suboptions:\n"
                   "   address <IPv4 Address>/<CIDR> [secondary]   Set IP address/CIDR (optional secondary).\n"
                   "Use <suboption> --help to get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        address_parser = subparsers.add_parser("address",
                                               help="Set a static IP address on the interface (e.g., 'ip address 192.168.1.1/24 [secondary]').")
        
        address_parser.add_argument("ipv4_address_cidr",
                                    help="IPv4 address/subnet to configure.")
        address_parser.add_argument("secondary", nargs="?", const=True, default=False,
                                    help="Indicate that this is a secondary IP address.")
        
        # Parse the arguments
        parsed_args = parser.parse_args(args)

        if parsed_args.subcommand == "address":
            ipv4_address_cidr = parsed_args.ipv4_address_cidr
            is_secondary = parsed_args.secondary
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        else:
            self.log.debug(f'Invalid subcommand: {parsed_args.subcommand}')
            print('Invalid subcommand')
            return STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['auto', 'half', 'full'])    
    def interfaceconfig_duplex(self, args: List[str]) -> bool:
        """
        Updates the interface duplex mode based on the provided arguments.
        
        Args:
            args (Optional[str]): The duplex mode argument, expected to be 'auto', 'half', or 'full'.
        
        Returns:
            bool: STATUS_OK (True) indicating the operation was successful.
        
        Raises:
            ValueError: If the duplex mode is invalid.
        """
        
        if not args:
            print("Usage: duplex <auto | half | full>")
            return STATUS_NOK

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_duplex(self.ifName, Duplex.NONE)
            print("interface must be of ethernet type")
            return STATUS_NOK
        
        duplex_values = {d.value: d for d in Duplex}
        self.log.info(f'Interface: {self.ifName} -> Duplex: {args}')
        args = args.lower()

        if args in duplex_values:
            duplex = duplex_values[args]
            self.update_interface_duplex(self.ifName, duplex)
                        
        else:
            print(f"Invalid duplex mode ({args}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['10', '100', '1000', '2500', '10000', 'auto'])    
    def interfaceconfig_speed(self, args: Optional[str]) -> bool:
        args = StringFormats.list_to_string(args)
        
        if not args:
            print("Usage: speed <10 | 100 | 1000 | 2500 | 10000 | auto>")
            return

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_speed(self.ifName, Speed.NONE)
            print("interface must be of ethernet type")
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
            print("Invalid speed value. Use '10', '100', '1000', '2500', '10000', or 'auto'.")
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['group'], 
                                     append_nested_sub_cmds=Bridge().get_bridge_list_os())    
    def interfaceconfig_bridge(self, args: Optional[str], negate=False) -> bool:
        
        if 'group' in args:
            
            bridge_name = args[1]
            
            if negate:
                self.log.debug(f"do_bridge().group -> Deleting Bridge {bridge_name}")
                Bridge().del_bridge_from_interface(self.ifName, args.bridge_name)
            else:
                self.log.debug(f"do_bridge().group -> Adding Bridge: {bridge_name} to Interface: {self.ifName}")
                Bridge().add_bridge_to_interface(self.ifName, bridge_name)
        
        else:
            print(f'error: invalid command: {args}')
            STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_shutdown(self, args=None, negate=False) -> bool:
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

        self.log.debug(f'interfaceconfig_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.update_shutdown(self.ifName, ifState)
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['access-vlan'])    
    def interfaceconfig_switchport(self, args=None, negate=False) -> bool:
        if 'access-vlan' in args:
            
            vlan_id = args[1]
            self.log.debug(f"Configuring switchport as access with VLAN ID: {vlan_id}")
            
            if self.update_interface_vlan(self.ifName, vlan_id):
                self.log.error(f"Unable to add vlan id: {vlan_id}")
            
        else:
            self.log.error("Unknown subcommand")
            
        return STATUS_OK        

    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_wireless(self, args=None, negate:bool=False) -> bool:
       return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'description', 'bridge', 'ip', 'switchport'])    
    def interfaceconfig_no(self, args: List) -> bool:
        
        self.log.debug(f"interfaceconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self.ifName}")
            self.interfaceconfig_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({args})")
            self.interfaceconfig_bridge(args[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({args})")
            self.interfaceconfig_ip(args[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({args})")
            self.interfaceconfig_ipv6(args[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({args})")
            self.interfaceconfig_switchport(args[1:], negate=True)
        
        elif start_cmd == 'description':
            self.log.debug(f"Remove description -> ({args})")
            self.interfaceconfig_description(args[1:], negate=True)
        
        else:
            print(f"No negate option for {start_cmd}")
        
        return STATUS_OK