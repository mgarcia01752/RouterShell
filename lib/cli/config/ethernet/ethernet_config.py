import logging
from typing import List, Optional

from lib.cli.common.exec_priv_mode import ExecMode

from lib.cli.common.command_class_interface import CmdPrompt
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
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
        self.log.setLevel(RSLS().ETHERNET_CONFIG)
        self.eth_interface_obj = eth_interface_obj
        self._interface_name = eth_interface_obj.get_interface_name()
        
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
            self.log.debug(f'Negating description on interface: {self._interface_name}')
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
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['dhcp-client', 'dual-stack'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['dhcp-server', 'pool-name'], 
                                     append_nested_sub_cmds=DHCPServer().get_dhcp_pool_name_list())
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'inside', 'pool-name'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['nat', 'outside', 'pool-name'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['bridge', 'group'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['switchport', 'access-vlan-id'])        
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

            self.log.debug(f"Configuring {'Secondary' if is_secondary else 'Primary'} IP Address on Interface ({self._interface_name}) -> Inet: ({ipv4_address_cidr})")

            action_description = "Removing" if negate else "Setting"
            result = self.eth_interface_obj.add_inet_address(inet_address=ipv4_address_cidr, secondary_address=is_secondary, negate=negate)

            if result:
                self.log.error(f"Failed to {action_description} IP: {ipv4_address_cidr} on interface: {self._interface_name}, secondary: {is_secondary}")
            else:
                self.log.debug(f"{action_description} IP: {ipv4_address_cidr} on interface: {self._interface_name}, secondary: {is_secondary}")

        elif "proxy-arp" in args:
            '''[no] [ip proxy-arp]'''
            self.log.debug(f"Set proxy-arp on Interface {self._interface_name} -> negate: {negate}")
            return self.eth_interface_obj.set_proxy_arp(negate)
                
        elif "drop-gratuitous-arp" in args:
            '''[no] [ip drop-gratuitous-arp]'''
            self.log.debug(f"Set drop-gratuitous-arp on Interface {self._interface_name}")
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
            
            self.log.debug(f"Set static-arp on Interface {self._interface_name} -> negate: {negate}") 
            return self.eth_interface_obj.add_static_arp(inet_address=ipv4_addr_arp, mac_addr=mac_addr_arp, negate=negate)
    
        elif "nat" in args:
            
            if args[1] in ['inside', 'outside']:
                self.log.debug(f"Set nat {args[1]} on Interface {self._interface_name}")
                
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
                        self.log.debug(f"Successfully set NAT: {nat_pool_name} direction: {nat_direction.value} on interface: {self._interface_name}")
                    else:
                        self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self._interface_name}")
                        return STATUS_NOK
                else:
                    print(f"Error: Invalid NAT argument, expecting pool-name; {args[2]}")
            else:
                print(f"Error: Invalid NAT direction '{args[1]}'. Use 'inside' or 'outside'.")
                return STATUS_NOK

        elif "dhcp-client" in args[0]:
            '''[no] [ip dhcp-client dual-stack]'''
            
            self.log.debug(f'dhcp-client -> {args}')
            
            state = State.DOWN if negate else State.UP
            
            if 'dual-stack' in args:
                self.log.debug(f'dhcp-client -> Dual-Stack')
                if self.eth_interface_obj.update_interface_dhcp_client(DHCPStackVersion.DHCP_DUAL_STACK, state):
                    self.log.fatal(f"Unable to set DHCP-DUAL_STACK client on interface: {self._interface_name}")
                    return STATUS_NOK
                            
            else:
                self.log.debug(f'dhcp-client -> IPv4')
                if self.eth_interface_obj.update_interface_dhcp_client(DHCPStackVersion.DHCP_V4, state):
                    self.log.fatal(f"Unable to set DHCPv4 client on interface: {self._interface_name}")
                    return STATUS_NOK
                
            self.log.debug(f'Added dhcp-client to interface: {self._interface_name}')

            return STATUS_OK
        
        elif "dhcp-server" in args:
            '''[no] [ip dhcp-server pool-name <dhcp-pool-name>]'''
            if 'pool-name' in args[1:]:
                pool_name = args[2]
                return DHCPServer().add_dhcp_pool_to_interface(pool_name, self._interface_name, negate)
                
            else:
                print("Invalid arguments for 'dhcp-server' command.")
                return STATUS_NOK
        
        elif ['bridge', 'group'] == args[:2]:
            bridge_group = args[2] if len(args) > 2 else STATUS_NOK
            if self.eth_interface_obj.set_bridge_group(bridge_group):
                self.log.debug(f"Failed to set bridge group {bridge_group} to interface: {self._interface_name}")
                return STATUS_OK

        elif ['switchport', 'access-vlan-id'] == args[:3]:
            vlan_id = args[2] if len(args) > 2 else STATUS_NOK
            if self.eth_interface_obj.set_interface_to_vlan(vlan_id):
                self.log.debug(f"Failed to set switchport vlan-id {vlan_id} to interface: {self._interface_name}")
                return STATUS_NOK

        elif "nat" in args[0]:
            '''[no] [ip nat [inside | outside] pool <nat-pool-name>]'''
            nat_direction = args.nat_direction_pool
            nat_pool_name = args.pool_name
                        
            try:
                nat_direction = NATDirection(nat_direction)
            except ValueError:
                print(f"Error: Invalid NAT direction '{nat_direction}'. Use 'inside' or 'outside'.")

            self.log.debug(f"Configuring NAT for Interface: {self._interface_name} -> NAT Dir: {nat_direction.value} -> Pool: {nat_pool_name}")

            self.eth_interface_obj
            
            #if self.set_nat_domain_status(self.ifName, nat_pool_name, nat_direction):
            #    self.log.error(f"Unable to add NAT: {nat_pool_name} direction: {nat_direction.value} to interface: {self.ifName}")
           
        else:
            self.print_invalid_cmd_response(args)
            return STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['auto', 'half', 'full'])    
    def ethernetconfig_duplex(self, duplex_args: List[str]) -> bool:
        if not duplex_args:
            print("Usage: duplex <auto | half | full>")
            return STATUS_NOK
        
        duplex_arg = duplex_args[0].lower()

        if self.eth_interface_obj.get_ifType() != InterfaceType.ETHERNET:
            self.eth_interface_obj.set_duplex(Duplex.NONE)
            print("interface must be of ethernet type")
            return STATUS_NOK
        
        duplex_values = {d.value: d for d in Duplex}
        self.log.debug(f'ethernetconfig_duplex() -> Interface: {self._interface_name} -> Duplex: {duplex_arg}')
    
        if duplex_arg in duplex_values:
            self.log.debug(f'ethernetconfig_duplex() -> Duplex: {duplex_arg} -> DuplexEnum: {duplex_values[duplex_arg]}')
            self.eth_interface_obj.set_duplex(duplex_values[duplex_arg])
                        
        else:
            self.print_invalid_cmd_response(f"Invalid duplex mode ({duplex_args}). Use 'auto', 'half', or 'full'.")
            return STATUS_NOK
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['10', '100', '1000', '2500', '10000', 'auto'])    
    def ethernetconfig_speed(self, speed_args: Optional[str]) -> bool:
        
        if not speed_args:
            print("Usage: speed <10 | 100 | 1000 | 2500 | 10000 | auto>")
            return

        self.log.debug(f'ethernetconfig_speed() -> Arg: {speed_args}')
        speed_arg = speed_args[0].lower()

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
            self.print_invalid_cmd_response("speed value. Use '10', '100', '1000', '2500', '10000', or 'auto'.")
            return STATUS_NOK
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['group'], 
                                     append_nested_sub_cmds=Bridge().get_bridge_list_os())    
    def ethernetconfig_bridge(self, bridge_args: Optional[str], negate=False) -> bool:
        
        if 'group' in bridge_args:
            
            self.log.info(f'ethernetconfig_bridge() -> args: {bridge_args}')
            bridge_name = bridge_args[1]
            
            if negate:
                self.log.debug(f"ethernetconfig_bridge().group -> Deleting Bridge {bridge_name}")
                Bridge().del_interface_to_bridge_group(self._interface_name, bridge_name)
                
            else:
                self.log.debug(f"ethernetconfig_bridge().group -> Adding Bridge: {bridge_name} to Interface: {self._interface_name}")
                Bridge().add_interface_to_bridge_group(self._interface_name, bridge_name)
        
        else:
            self.print_invalid_cmd_response(bridge_args)
            STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ethernetconfig_shutdown(self, args=None, negate=False) -> bool:

        ifState = State.UP if negate else State.DOWN
        self.log.debug(f'ethernetconfig_shutdown(negate: {negate}) -> State: {ifState.name}')
        self.eth_interface_obj.set_interface_shutdown_state(ifState)
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['access-vlan'])    
    def ethernetconfig_switchport(self, args=None, negate=False) -> bool:
        
        if 'access-vlan' in args:
            vlan_id = args[1]
            self.log.info(f"Configuring switchport as access with vlan-id: {vlan_id}")
            
            if self.eth_interface_obj.set_interface_to_vlan(vlan_id):
                self.print_error_response(f'invalid vlan {vlan_id}')
            
        else:
            self.print_invalid_cmd_response(args)
            
        return STATUS_OK        

    @CmdPrompt.register_sub_commands()    
    def ethernetconfig_wireless(self, args=None, negate:bool=False) -> bool:
       return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['shutdown', 'description', 'bridge', 'ip', 'switchport'])    
    def ethernetconfig_no(self, args: List) -> bool:
        
        self.log.debug(f"ethernetconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self._interface_name}")
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
            self.print_invalid_cmd_response(f"No negate option for {start_cmd}")
        
        return STATUS_OK
    
    