import argparse
import cmd2
import logging

from lib.cli.config.arp_config import ArpConfig
from lib.cli.config.dhcp_server_config import DHCPServerConfig
from lib.cli.config.if_config import InterfaceConfig
from lib.cli.config.bridge_config import BridgeConfig
from lib.cli.config.vlan_config import VlanConfig
from lib.cli.config.ip_route_config import IpRouteConfig
from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.base.exec_priv_mode import ExecMode, ExecException
from lib.cli.config.wireless_cell_config import WirelessCellPolicyConfig
from lib.cli.config.wireless_wifi_config import WirelessWifiPolicyConfig
from lib.network_manager.interface import Interface
from lib.network_manager.bridge import Bridge
from lib.cli.common.router_prompt import RouterPrompt
from lib.network_manager.nat import Nat

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.cli.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.system.system_config import SystemConfig

class InvalidConfigureMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class ConfigureMode(cmd2.Cmd, GlobalUserCommand, RouterPrompt):
    """Command set for ConfigureMode-Commands"""  
    """
        arp                     (Implemented)
        banner                  (Implemented)
        bridge                  (Implemented)
        dhcp
        interface <ifName>      (Implemented)
        interface <vlan-id>     (Implemented)
        ip nat                  (Implemented)
        ip route
        ipv6 route
        rename                  (Implemented)
        vlan                    (Implemented)
        vlanDB                  (Implemented)           
        wireless [cell | wifi]         
    """ 

    def __init__(self, usr_exec_mode: ExecMode, arg=None):
        super().__init__()

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CONFIGURE_MODE)
        self.debug = CGS().DEBUG_CONFIGURE_MODE

        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE)
                
        if usr_exec_mode is ExecMode.USER_MODE:
            msg = f"Does not have necessary configure privileges ({usr_exec_mode})"
            self.log.error(msg)
            print(msg)
            raise ExecException(msg)
        
        self.current_exec_mode = usr_exec_mode
        
        # Set a custom prompt for interface configuration
        self.prompt = self.set_prompt()

    def do_banner(self, line) -> None:
        """
        Configure the banner Message of the Day (Motd) through the command-line interface.

        Args:
            self: The ConfigureMode class instance.
            line (str): The input string provided by the user.

        Returns:
            None

        """
        banner_config = []

        self.poutput("Enter the banner text. Type '^' on a new line to finish.")
        while True:
            line = input("> ")
            if line.lower().strip() == '^':
                break
            banner_config.append(line)

        SystemConfig().set_banner('\n'.join(banner_config))

    def complete_interface(self, text, line, begidx, endidx):
        completions = ['loopback', 'vlan']
        '''Dynamically add interfaces to tab completion'''
        completions.extend(Interface().get_network_interfaces())
        return [comp for comp in completions if comp.startswith(text)]
    
    @cmd2.with_argument_list
    def do_interface(self, args=None):
        """
        Enter the Interface configuration mode for a specific interface or subinterface.

        This method allows you to enter the Interface configuration mode for a specific network interface
        or subinterface. You can specify the interface name as an argument to enter the configuration mode.
        Optionally, you can specify a subinterface name along with the parent interface.

        Usage:
            interface <interface_name> [subinterface_name]

        Args:
            args (list): A list of arguments. It should contain one or two elements:
                        - The first element is the name of the interface (required).
                        - The second element (optional) is the name of the subinterface.

        Raises:
            InvalidConfigureMode: If the number of arguments is not one or two, an error is raised.

        Returns:
            None
        """
        self.log.debug(f"Interface ARGS -> {args}")
        
        if (len(args) < 1) or (len(args) > 2):
            self.log.error(f"Interface -> {args}")
            raise InvalidConfigureMode(f"Invalid Interface name")
        
        self.log.debug(f"do_interface() -> Interface: ({args})")
           
        if (len(args) == 1):
            InterfaceConfig(args[0]).cmdloop()
        else:
            InterfaceConfig(args[1], args[0]).cmdloop()

    def complete_bridge(self, text, line, begidx, endidx):
        completions = Bridge().get_bridge_list_os()
        return [comp for comp in completions if comp.startswith(text)]

    @cmd2.with_argument_list
    def do_bridge(self, args=None, negate=False):
        """
        Enter the Bridge configuration mode for a specific Bridge.

        This method allows you to enter the Bridge configuration mode for a specific Bridge.
        You must specify the Bridge name as an argument to enter the configuration mode.

        Usage:
            bridge <bridge_name>

        Args:
            args (list): A list of arguments. It should contain one element, which is the name of the Bridge.

        Raises:
            InvalidConfigureMode: If the number of arguments is not exactly one, an error is raised.

        Returns:
            None
        """
        self.log.debug(f"Bridge ARGS -> {args}")
        
        if len(args) != 1:
            self.log.error(f"bridge -> {args[0]}")
            raise InvalidConfigureMode(f"Invalid Bridge name")
        
        self.log.debug(f"do_bridge() -> Bridge: ({args[0]})")    
        BridgeConfig(args[0]).cmdloop()

    @cmd2.with_argument_list
    def do_vlan(self, args=None, negate=False) -> None:
        """
        Enter the VLAN configuration mode for a specific VLAN.

        This method allows you to enter the VLAN configuration mode for a specific VLAN.
        You must specify the VLAN ID as an argument to enter the configuration mode.

        Usage:
            vlan <vlan_id>

        Args:
            args (str): A string representing the VLAN ID. It should be a single argument.
            negate (bool): A boolean parameter with a default value of False.

        Raises:
            ValueError: If the number of arguments is not exactly one, or if the VLAN ID is not a valid integer (1-4096).

        Returns:
            None
        """
        self.log.debug(f"do_vlan(args={args}, negate={negate})")
                
        # Check if the number of arguments is exactly one
        if len(args) != 1:
            raise ValueError(f"vlan command expects exactly one argument, received: {len(args)}")
        
        # Check if the argument is a valid integer in the range 1-4096
        vlan_id = args[0]
        if not vlan_id.isdigit() or not (1 <= int(vlan_id) <= 4096):
            raise ValueError(f"Invalid VLAN ID: {vlan_id}. VLAN ID must be an integer in the range 1-4096.")
        
        # Enter VLAN configuration mode
        VlanConfig(vlan_id).cmdloop()

   

    def do_vlanDB(self, args=None) -> None:
        """
        Enter the VLAN Database configuration mode for a specific VLAN.

        This method allows you to enter the VLAN Database configuration mode for a specific VLAN.
        You must specify the VLAN name as an argument to enter the configuration mode.

        Usage:
            vlanDB <vlan_name>

        Args:
            args (list): A list of arguments. It should contain one element, which is the name of the VLAN.

        Raises:
            InvalidConfigureMode: If the number of arguments is not exactly one, an error is raised.

        Returns:
            None
        """
        self.log.debug(f"Vlan DataBase ARGS -> {args}")
        
        if len(args) != 1:
            self.log.error(f"vlan -> {args[0]}")
            raise InvalidConfigureMode(f"Invalid vlan name")
        
        self.log.debug(f"do_vlan() -> Bridge: ({args[0]})")    
        VlanConfig(args[0]).cmdloop() 

    def complete_arp(self, text, line, begidx, endidx):
        completions = ['timeout', 'proxy', 'drop-gratuitous']
        return [comp for comp in completions if comp.startswith(text)]

    def do_arp(self, args=None) -> None:
        self.log.debug(f"do_arp() -> command: ({args})")    
        ArpConfig(f"arp {args}").cmdloop()       

    def complete_dhcp(self, text, line, begidx, endidx):
        completions = ['global']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_dhcp(self, args=None) -> None:
        self.log.debug(f"do_dhcp() -> command: ({args})")    
        DHCPServerConfig(args).cmdloop()   

    def complete_ip(self, text, line, begidx, endidx):
        completions =       ['route']
        completions.extend( ['nat', 'pool', 'inside', 'outside'])
        return [comp for comp in completions if comp.startswith(text)]

    def do_ip(self, args=None):
        self.log.debug(f"do_ip() -> command: ({args})")

        parser = argparse.ArgumentParser(
            description="Configure IP settings",
            epilog="Usage:\n"
            "   [no] ip nat <nat-policy-name>\n"
            "   [no] ip route <src-inet-subnet> <src-inet-mast> <gw-inet-address>\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        parser.add_argument("ip_command", choices=["nat", "route"],
                            help="Choose between 'nat' or 'route'")
        parser.add_argument("ip_args", nargs="*",
                            help="Additional arguments for IP configuration")

        parsed_args = parser.parse_args(args.split())

        try:
            if parsed_args.ip_command == "route":
                self._handle_ip_route(parsed_args.ip_args)
                
            elif parsed_args.ip_command == "nat":
                self.log.debug("IP-NAT-CONFIG")
                self._handle_ip_nat(parsed_args.ip_args[0])
            
            else:
                raise ValueError(f"Invalid command: {parsed_args.ip_command}")

        except Exception as e:
            self.log.error(f"Error handling IP command: {e}")
            print(f"Error: {e}")

    def _handle_ip_route(self, args):
        # Logic for handling IP routing configuration
        IpRouteConfig(args)

    def _handle_ip_nat(self, args):
        # Logic for handling NAT configuration
        if Nat().create_nat_pool(args):
            print(f"Unable to create ANT pool: {args}")

    def complete_ipv6(self, text, line, begidx, endidx):
        completions = ['route']
        return [comp for comp in completions if comp.startswith(text)]
 
    def do_ipv6(self, args=None, negate=False) -> None:
        self.log.debug(f"do_route() -> command: ({args})")    
        IpRouteConfig().cmdloop() 

    def complete_rename(self, text, line, begidx, endidx):
        completions = ['if', 'if-alias']
        completions.extend(Interface().get_network_interfaces())
        return [comp for comp in completions if comp.startswith(text)]

    def do_rename(self, args: str, negate: bool = False) -> None:
        '''
        Rename a network interface.

        Usage:
            if <initial interface> if-alias <new interface>

        Args:
            args (str): The input string containing the command.
            negate (bool, optional): If True, undo the renaming. Defaults to False.

        Returns:
            None
        '''

        self.log.debug(f"do_rename() -> args: {args}")

        args_parts = args.strip().split()

        self.log.debug(f"do_rename() -> arg-parts: {args_parts}")

        if args_parts[0] == 'if':
            self.log.debug(f"do_rename() -> if")
            
            if len(args_parts) == 4:
                self.log.debug(f"do_rename() -> args-parts: {args_parts}")
                Interface().rename_interface(args_parts[1], args_parts[3])
            else:
                print(f"Invalid command: rename {args}")

    def complete_wireless(self, text, line, begidx, endidx):
        completions = ['cell', 'wifi']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_wireless(self, args, negate=False):
        self.log.debug(f"do_wireless() -> command: ({args}) -> negate: {negate}")
        
        parser = argparse.ArgumentParser(
            description="Configure Wireless Policy",
            epilog="Usage:\n"
            "   [cell | wifi] <wireless-policy-name>\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )
        
        subparsers = parser.add_subparsers(dest="wireless_type")

        wifi_parser = subparsers.add_parser("wifi", help="Configure Wi-Fi wireless policies")
        wifi_parser.add_argument("wireless_policy_name", help="Name of the Wi-Fi wireless policy")
        
        cell_parser = subparsers.add_parser("cell", help="Configure Cellular wireless policies")
        cell_parser.add_argument("wireless_policy_name", help="Name of the Cellular wireless policy")

        # Parse the arguments
        parsed_args = parser.parse_args(args.split())
        self.log.debug(f"do_wireless() -> args-parsed: {parsed_args}")
        
        if parsed_args.wireless_type == "wifi":
            self.log.debug(f"do_wireless() -> wireless-type: wifi -> wireless-wifi-policy: {parsed_args.wireless_policy_name}")
            WirelessWifiPolicyConfig(parsed_args.wireless_policy_name).cmdloop()

        elif parsed_args.wireless_type == "cell":
            self.log.debug(f"do_wireless() -> wireless-type: cell -> wireless-cell-policy: {parsed_args.wireless_policy_name}")
            WirelessCellPolicyConfig(parsed_args.wireless_policy_name).cmdloop()

        else:
            print(f"Invalid wireless type: {parsed_args.wireless_type}")
                        
    def complete_no(self, text, line, begidx, endidx):
        completions = ['arp', 'bridge', 'ip', 'ipv6']
        return [comp for comp in completions if comp.startswith(text)]
            
    def do_no(self, line) -> None:

        self.log.debug(f"do_no() -> Line -> {line}")
        
        line_parts = line.strip().split()
        start_cmd = line_parts[0]
        
        self.log.debug(f"do_no() -> Start-CMD -> {start_cmd}")
        
        if start_cmd == 'arp':
            self.log.debug(f"do_no(arp) -> {line_parts}")
            ArpConfig().do_arp(line_parts[1], negate=True)

        elif start_cmd == 'bridge':
            self.log.debug(f"do_no(bridge) -> {line_parts}")
            if len(line_parts) == 2:
                self.log.debug(f"Remove bridge -> {line_parts}")
                if Bridge().destroy_bridge_cmd(line_parts[1]):
                    self.log.error(f'do_no() -> {line_parts}')
                    print(f"Unable to remove bridge: {line_parts[1]}")
            else:
                print(f"Invalid command: {line}")
        
        elif start_cmd == 'ip':
            self.log.debug(f"do_no(ip) -> {line_parts}")
            IpRouteConfig(line_parts, negate=True).cmdloop()
            
        elif start_cmd == 'ipv6':
            self.log.debug(f"do_no(ipv6) -> {line_parts}")
            
        elif start_cmd == 'rename':
            self.log.debug(f"do_no(rename) -> {line_parts}")
               
        elif line_parts[0] == 'if':
            self.log.debug(f"do_alias() -> if")
            if len(line_parts) == 4:
                self.log.debug(f"do_alias() -> args-parts: {line_parts}")
                Interface().rename_interface(line_parts[3], line_parts[1])
            else:
                print(f"Invalid command: rename {line}")        
        else:
            print(f"Invalid command: {line}")
            
                
