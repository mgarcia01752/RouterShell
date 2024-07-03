import logging
from typing import List, Optional

from lib.cli.common.exec_priv_mode import ExecMode

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.string_formats import StringFormats
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.phy import Duplex, Speed, State
from lib.network_manager.network_interfaces.ethernet_interface import EthernetInterface
from lib.network_manager.network_operations.arp import Encapsulate
from lib.network_manager.network_operations.bridge import Bridge
from lib.network_manager.network_operations.dhcp_client import DHCPVersion
from lib.network_manager.network_operations.dhcp_server import DHCPServer
from lib.network_manager.network_operations.interface import Interface
from lib.network_manager.network_operations.nat import NATDirection
from lib.common.constants import STATUS_NOK, STATUS_OK

class EthernetConfigError(Exception):
    """Custom exception for InterfaceConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'InterfaceConfigError: {self.message}'

class EthernetConfig(CmdPrompt):

    def __init__(self, eth_interface_obj:EthernetInterface) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ETHERNET_CONFIG)
        self.eth_interface_obj = eth_interface_obj
        self.ifName = eth_interface_obj.get_interface_name()
        
        self.log.debug(f'Ethernet: {eth_interface_obj.get_interface_name()}')
               
    def ethernetconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
        return STATUS_OK
            
    @CmdPrompt.register_sub_commands() 
    def ethernetconfig_description(self, line: Optional[str], negate: bool = False) -> bool:

        if negate:
            self.log.debug(f'Negating description on interface: {self.ifName}')
            line = [""]
        
        if self.eth_interface_obj.set_description(StringFormats.list_to_string(line)):
            print("Unable to add description to DB")
            raise ValueError("Failed to update the description in the database.")
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['auto'],     help='Auto assign mac address')
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address'],  help='Assign mac address <xxxx.xxxx.xxxx>')     
    def ethernetconfig_mac(self, args:str) -> bool:
        
        self.log.debug(f"ethernetconfig_mac() -> args: {args}")
        
        if len(args) == 1 and args[0] == "auto":
            self.log.debug(f"ethernetconfig_mac() -> auto")
            self.eth_interface_obj.set_mac_address(mac_addr=None)
                            
        elif len(args) == 2 and args[0] == "address":
            mac = args[1]
            self.log.debug(f"ethernetconfig_mac() -> address -> {mac}")
            self.eth_interface_obj.set_mac_address(mac_addr=mac)
            
        else:
            print("Usage: mac [auto | <mac address>]")
            
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ethernetconfig_ip6(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['drop-gratuitous-arp'])        
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['proxy-arp'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['static-arp', 'arpa'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'inside', 'pool', 'acl'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'outside', 'pool', 'acl'])
    def X_ip(self, args: List, negate=False) -> bool:

        self.log.debug(f'ethernetconfig_ip() -> {args}')

        if 'address' in args[0]:
            ipv4_address_cidr = args[1]
            is_secondary = False
            is_secondary = True if is_secondary else False

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self.ifName}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.eth_interface_obj.update_interface_inet(self.ifName, ipv4_address_cidr, is_secondary, negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName} secondary: {is_secondary}")

        elif "proxy-arp" in args[0]:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            self.eth_interface_obj.set_proxy_arp(negate)
                
        elif "drop-gratuitous-arp" in args[0]:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            self.eth_interface_obj.set_drop_gratuitous_arp(negate)

        elif "static-arp" in args[0]:
            '''[no] [ip static-arp ip-address mac-address arpa]'''
            self.log.debug(f"Set static-arp on Interface {self.ifName}")
            
            ipv4_addr_arp = args[1]
            mac_addr_arp = args[2]
            encap_arp = Encapsulate.ARPA         
                    
            self.log.debug(f"Set static-arp on Interface {self.ifName} -> negate: {negate}") 
            self.eth_interface_obj.add_static_arp(inet_address=ipv4_addr_arp, mac_addr=mac_addr_arp, negate=negate)
            
        elif "nat" in args[0]:
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            nat_pool_name = args.pool_name
                        
            try:
                nat_direction = NATDirection(nat_direction)
            except ValueError:
                print(f"Error: Invalid NAT direction '{nat_direction}'. Use 'inside' or 'outside'.")

            self.log.debug(f"Configuring NAT for Interface: {self.ifName} -> NAT Dir: {nat_direction.value} -> Pool: {nat_pool_name}")

            self.eth_interface_obj
            
            #if self.set_nat_domain_status(self.ifName, nat_pool_name, nat_direction):
            #    self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")

        elif "dhcp-client" in args[0]:
            '''[no] [ip dhcp-client]'''
            self.log.debug(f"Enable DHCPv4 Client")
            if Interface().update_interface_dhcp_client(self.ifName, DHCPVersion.DHCP_V4, negate):
                self.log.fatal(f"Unable to set DHCPv4 client on interface: {self.ifName}")

        elif "dhcp-server" in args[0]:
            pool_name = args.pool_name
            '''[no] [ip dhcp-server] pool <dhcp-pool-name>'''
            self.log.debug(f"Enable DHCPv4/6 Server")
            DHCPServer().add_dhcp_pool_to_interface(pool_name, self.ifName, negate)
  
        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['drop-gratuitous-arp'])        
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['proxy-arp'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['static-arp', 'arpa'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'inside', 'pool-name'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'outside', 'pool-name'])    
    def ethernetconfig_ip(self, args: List[str], negate=False) -> bool:
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
            result = self.eth_interface_obj.add_inet_address(inet_address=ipv4_address_cidr, secondary_address=is_secondary, negate=negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self.ifName}, secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self.ifName}, secondary: {is_secondary}")

        elif "proxy-arp" in args:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self.ifName} -> negate: {negate}")
            return self.eth_interface_obj.set_proxy_arp(negate)
                
        elif "drop-gratuitous-arp" in args:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self.ifName}")
            return self.eth_interface_obj.set_drop_gratuitous_arp(negate)

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
            return self.eth_interface_obj.add_static_arp(inet_address=ipv4_addr_arp, mac_addr=mac_addr_arp, negate=negate)
    
        elif "nat" in args:
            if args[1] in ['inside', 'outside']:
                self.log.debug(f"Set nat {args[1]} on Interface {self.ifName}")
                
                try:
                    nat_direction = NATDirection(args[1])
                except ValueError:
                    print(f"Error: Invalid NAT direction '{args[1]}'. Use 'inside' or 'outside'.")
                    return STATUS_NOK

                if args[2] == 'pool-name':
                    if len(args) < 4:
                        print("Error: 'pool-name' argument is missing.")
                        return STATUS_NOK

                    nat_pool_name = args[3]
                    
                    if not self.eth_interface_obj.set_nat_domain_direction(nat_pool_name, nat_direction, negate):
                        self.log.debug(f"Successfully set NAT: {nat_pool_name} direction: {nat_direction.value} on interface: {self.ifName}")
                    else:
                        self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")
                        return STATUS_NOK
                else:
                    print(f"Error: Invalid NAT argument, expecting pool-name; {args[2]}")
            else:
                print(f"Error: Invalid NAT direction '{args[1]}'. Use 'inside' or 'outside'.")
                return STATUS_NOK
       
        else:
            self.log.debug(f'Invalid subcommand: {args}')
            print('Invalid subcommand')
            return STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['auto', 'half', 'full'])    
    def ethernetconfig_duplex(self, args: List[str]) -> bool:
        if not args:
            print("Usage: duplex <auto | half | full>")
            return STATUS_NOK
        
        duplex_arg = args[0].lower()

        if self.eth_interface_obj.get_ifType() != InterfaceType.ETHERNET:
            self.eth_interface_obj.set_duplex(Duplex.NONE)
            print("interface must be of ethernet type")
            return STATUS_NOK
        
        duplex_values = {d.value: d for d in Duplex}
        self.log.debug(f'ethernetconfig_duplex() -> Interface: {self.ifName} -> Duplex: {duplex_arg}')
    
        if duplex_arg in duplex_values:
            self.log.debug(f'ethernetconfig_duplex() -> Duplex: {duplex_arg} -> DuplexEnum: {duplex_values[duplex_arg]}')
            self.eth_interface_obj.set_duplex(duplex_values[duplex_arg])
                        
        else:
            print(f"Invalid duplex mode ({args}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['10', '100', '1000', '2500', '10000', 'auto'])    
    def ethernetconfig_speed(self, args: Optional[str]) -> bool:
        
        if not args:
            print("Usage: speed <10 | 100 | 1000 | 2500 | 10000 | auto>")
            return

        self.log.debug(f'ethernetconfig_speed() -> Arg: {args}')
        speed_arg = args[0].lower()

        if self.eth_interface_obj.get_ifType() != InterfaceType.ETHERNET:
            self.eth_interface_obj.set_interface_speed(Speed.NONE)
            print("interface must be of ethernet type")
            return
        
        speed_values = {str(s.value): s for s in Speed}
        self.log.debug(f"ethernetconfig_speed() -> ARGS: {speed_arg} -> Values: {speed_values}")
        
        if speed_arg == "auto":
            self.eth_interface_obj.set_interface_speed(Speed.AUTO_NEGOTIATE)

        elif speed_arg in speed_values:
            if self.eth_interface_obj.set_interface_speed(speed_values[speed_arg]):
                self.log.debug(f'Unable to set interface speed: {speed_values[speed_arg].value}Mbps')
                return STATUS_NOK
            
        else:
            print("Invalid speed value. Use '10', '100', '1000', '2500', '10000', or 'auto'.")
            return STATUS_NOK
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['group'], 
                                     append_nested_sub_cmds=Bridge().get_bridge_list_os())    
    def ethernetconfig_bridge(self, args: Optional[str], negate=False) -> bool:
        
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
    def ethernetconfig_shutdown(self, args=None, negate=False) -> bool:

        ifState = State.DOWN
        
        if negate:
            ifState = State.UP

        self.log.debug(f'ethernetconfig_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.eth_interface_obj.set_interface_shutdown_state(ifState)
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['access-vlan'])    
    def ethernetconfig_switchport(self, args=None, negate=False) -> bool:
        if 'access-vlan' in args:
            
            vlan_id = args[1]
            self.log.debug(f"Configuring switchport as access with VLAN ID: {vlan_id}")
            
            if self.update_interface_vlan(self.ifName, vlan_id):
                self.log.error(f"Unable to add vlan id: {vlan_id}")
            
        else:
            self.log.error("Unknown subcommand")
            
        return STATUS_OK        

    @CmdPrompt.register_sub_commands()    
    def ethernetconfig_wireless(self, args=None, negate:bool=False) -> bool:
       return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'description', 'bridge', 'ip', 'switchport'])    
    def ethernetconfig_no(self, args: List) -> bool:
        
        self.log.debug(f"ethernetconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self.ifName}")
            self.ethernetconfig_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({args})")
            self.ethernetconfig_bridge(args[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({args})")
            self.ethernetconfig_ip(args[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({args})")
            self.ethernetconfig_ipv6(args[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({args})")
            self.ethernetconfig_switchport(args[1:], negate=True)
        
        elif start_cmd == 'description':
            self.log.debug(f"Remove description -> ({args})")
            self.ethernetconfig_description(args[1:], negate=True)
        
        else:
            print(f"No negate option for {start_cmd}")
        
        return STATUS_OK
    
    