
import logging
from typing import List, Optional

from lib.cli.common.exec_priv_mode import ExecMode

from lib.cli.common.command_class_interface import CmdPrompt
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
from lib.common.string_formats import StringFormats
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.phy import Duplex, Speed, State
from lib.network_manager.network_interfaces.ethernet.ethernet_interface import EthernetInterface
from lib.network_manager.network_operations.arp import Encapsulate
from lib.network_manager.network_operations.bridge import Bridge
from lib.network_manager.network_operations.dhcp.client.dhcp_client import DHCPStackVersion
from lib.network_manager.network_operations.dhcp.client.dhcp_clinet_interface_abc import DHCPInterfaceClient
from lib.network_manager.network_operations.dhcp.server.dhcp_server import DHCPServer
from lib.network_manager.network_operations.nat import NATDirection
from lib.common.constants import STATUS_NOK, STATUS_OK

class InterfaceConfigError(Exception):
    """Custom exception for InterfaceConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'InterfaceConfigError: {self.message}'

class InterfaceConfig(CmdPrompt):

    def __init__(self, net_interface:EthernetInterface) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ETHERNET_CONFIG)
        self.net_interface = net_interface
        self.ifName = net_interface.get_interface_name()
        
        self.log.debug(f'Interface: {net_interface.get_interface_name()}')
               
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
        """"""
        if negate:
            self.log.debug(f'Negating description on interface: {self.ifName}')
            line = [""]
        
        if self.net_interface.set_description(StringFormats.list_to_string(line)):
            print("Unable to add description to DB")
            raise ValueError("Failed to update the description in the database.")
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['auto'],     help='Auto assign mac address')
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address'],  help='Assign mac address <xxxx.xxxx.xxxx>')     
    def interfaceconfig_mac(self, args:str) -> bool:
        
        self.log.debug(f"interfaceconfig_mac() -> args: {args}")
        
        if len(args) == 1 and args[0] == "auto":
            self.log.debug(f"interfaceconfig_mac() -> auto")
            self.net_interface.set_mac_address(mac_addr=None)
                            
        elif len(args) == 2 and args[0] == "address":
            mac = args[1]
            self.log.debug(f"interfaceconfig_mac() -> address -> {mac}")
            self.net_interface.set_mac_address(mac_addr=mac)
            
        else:
            print("Usage: mac [auto | <mac address>]")
            
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def interfaceconfig_ip6(self, args, negate=False) -> bool:
        return STATUS_OK
    
    def X_ip(self, args: List, negate=False) -> bool:

        self.log.debug(f'interfaceconfig_ip() -> {args}')

        if 'address' in args[0]:
            ipv4_address_cidr = args[1]
            is_secondary = False
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.net_interface.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        elif "proxy-arp" in args[0]:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            self.net_interface.set_proxy_arp(negate)
                
        elif "drop-gratuitous-arp" in args[0]:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            self.net_interface.set_drop_gratuitous_arp(negate)

        elif "static-arp" in args[0]:
            '''[no] [ip static-arp ip-address mac-address arpa]'''
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args[1]
            mac_addr_arp = args[2]
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}") 
            self.net_interface.add_static_arp(inet_address=ipv4_addr_arp, mac_addr=mac_addr_arp, negate=negate)
            
        elif "nat" in args[0]:
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            nat_pool_name = args.pool_name
                        
            try:
                nat_direction = NATDirection(nat_direction)
            except ValueError:
                print(f"Error: Invalid NAT direction '{nat_direction}'. Use 'inside' or 'outside'.")

            self.log.debug(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction.value} -> Pool: {nat_pool_name}")

            #if self.set_nat_domain_status(self.ifName, nat_pool_name, nat_direction):
            #    self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")

        elif "dhcp-client" in args[0]:
            '''[no] [ip dhcp-client]'''
            self.log.debug(f"Enable DHCPv4 Client")
            state = State.UP if negate else State.DOWN
            if DHCPInterfaceClient().update_interface_dhcp_client(self.ifName, DHCPStackVersion.DHCP_V4, state):
                self.log.fatal(f"Unable to set DHCPv4 client on interface: {self.ifName}")

        elif "dhcp-server" in args[0]:
            pool_name = args.pool_name
            '''[no] [ip dhcp-server] pool <dhcp-pool-name>'''
            self.log.debug(f"Enable DHCPv4/6 Server")
            DHCPServer().add_dhcp_pool_to_interface(pool_name, self.ifName, negate)
  
        return STATUS_OK

    
    @CmdPrompt.register_sub_commands(sub_cmds=['dhcp-server', 'pool-name'])
    @CmdPrompt.register_sub_commands(sub_cmds=['drop-gratuitous-arp'])        
    @CmdPrompt.register_sub_commands(sub_cmds=['proxy-arp'])
    @CmdPrompt.register_sub_commands(sub_cmds=['static-arp', 'arpa'])
    @CmdPrompt.register_sub_commands(sub_cmds=['address', 'secondary'])
    def interfaceconfig_ip(self, args: List[str], negate=False) -> bool:
        "ip address <> secondary"
        if "address" in args:
            if len(args) < 2:
                self.log.error("Insufficient arguments for 'address' command.")
                print("Insufficient arguments for 'address' command.")
                return STATUS_NOK
            
            ipv4_address_cidr = args[1]
            is_secondary = False
            
            if len(args) > 2 and args[2] == 'secondary':
                is_secondary = True    

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.net_interface.add_inet_address(inet_address=ipv4_address_cidr, secondary_address=is_secondary, negate=negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName}, secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName}, secondary: {is_secondary}")

        elif "proxy-arp" in args:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            return self.net_interface.set_proxy_arp(negate)
                
        elif "drop-gratuitous-arp" in args:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            return self.net_interface.set_drop_gratuitous_arp(negate)

        elif "static-arp" in args:
            '''[no] [ip static-arp ip-address mac-address arpa]'''
            if len(args) < 3:
                self.log.error("Insufficient arguments for 'static-arp' command.")
                print("Insufficient arguments for 'static-arp' command.")
                return STATUS_NOK
            
            ipv4_addr_arp = args[1]
            mac_addr_arp = args[2]
            encap_arp = Encapsulate.ARPA  # Assuming Encapsulate is a predefined enum or constant.
            
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}") 
            return self.net_interface.add_static_arp(inet_address=ipv4_addr_arp, mac_addr=mac_addr_arp, negate=negate)
        
        elif "dhcp-server" in args:
            
            if 'pool-name' in args[1:]:
                pool_name = args[2]
                return DHCPServer().add_dhcp_pool_to_interface(pool_name, self.ifName, negate)
                
            else:
                print("Invalid arguments for 'dhcp-server' command.")
                return STATUS_NOK
            
        else:
            self.log.debug(f'Invalid subcommand: {args}')
            print('Invalid subcommand')
            return STATUS_NOK

        return STATUS_OK


    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['auto', 'half', 'full'])    
    def interfaceconfig_duplex(self, args: List[str]) -> bool:
        """ duplex """
        
        if not args:
            print("Usage: duplex <auto | half | full>")
            return STATUS_NOK

        if self.interface_type != InterfaceType.ETHERNET:
            self.net_interface.set_duplex(Duplex.NONE)
            print("interface must be of ethernet type")
            return STATUS_NOK
        
        duplex_values = {d.value: d for d in Duplex}
        self.log.debug(f'Interface: {self.ifName} -> Duplex: {args}')
        args = args.lower()

        if args in duplex_values:
            duplex = duplex_values[args]
            self.net_interface.set_duplex(duplex)
                        
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
            self.net_interface.set_interface_speed(Speed.NONE)
            print("interface must be of ethernet type")
            return
        
        self.log.debug(f"do_speed() -> ARGS: {args}")
        
        speed_values = {str(s.value): s for s in Speed}
        args = args.lower()

        if args == "auto":
            self.net_interface.set_interface_speed(Speed.AUTO_NEGOTIATE)

        elif args in speed_values:
            speed = speed_values[args]
            self.net_interface.set_interface_speed(speed)
            
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
        """ shutdown """
        ifState = State.DOWN
        
        if negate:
            ifState = State.UP

        self.log.debug(f'interfaceconfig_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.net_interface.set_interface_shutdown_state(ifState)
        
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
    
    