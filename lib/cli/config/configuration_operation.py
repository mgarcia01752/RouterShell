import cmd2
import logging

from lib.cli.config.arp_config import ArpConfig
from lib.cli.config.dhcpd_config import DHCPServerConfig
from lib.cli.config.if_config import InterfaceConfig
from lib.cli.config.bridge_config import BridgeConfig
from lib.cli.config.nat_config import NatConfig
from lib.cli.config.vlan_config import VlanConfig
from lib.cli.config.ip_route_config import IpRouteConfig
from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.base.exec_priv_mode import ExecMode, ExecException
from lib.network_manager.interface import Interface
from lib.network_manager.bridge import Bridge
from lib.common.router_prompt import RouterPrompt
from lib.common.constants import *

from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS

class InvalidConfigureMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class ConfigureMode(cmd2.Cmd, GlobalUserCommand, RouterPrompt):
    """Command set for ConfigureMode-Commands"""  
    """
        arp                 (Implemented)
        bridge              (Implemented)
        dhcp
        interface <ifName>  (Implemented)
        interface <vlan-id> (Implemented)
        ip nat
        ip route
        ipv6 route
        vlan                (Implemented)
        vlanDB              (Implemented)           
        wireless        
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
        completions = Bridge().get_bridge_list()
        return [comp for comp in completions if comp.startswith(text)]

    @cmd2.with_argument_list
    def do_bridge(self, args=None):
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
    def do_vlan(self, args=None) -> None:
        """
        Enter the VLAN configuration mode for a specific VLAN.

        This method allows you to enter the VLAN configuration mode for a specific VLAN.
        You must specify the VLAN name as an argument to enter the configuration mode.

        Usage:
            vlan <vlan_name>

        Args:
            args (list): A list of arguments. It should contain one element, which is the name of the VLAN.

        Raises:
            InvalidConfigureMode: If the number of arguments is not exactly one, an error is raised.

        Returns:
            None
        """
        self.log.debug(f"Vlan ARGS -> {args}")
        
        if len(args) != 1:
            self.log.error(f"vlan -> {args[0]}")
            raise InvalidConfigureMode(f"Invalid vlan name")
        
        self.log.debug(f"do_vlan() -> Bridge: ({args[0]})")    
        VlanConfig(args[0]).cmdloop()       

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

    def do_ip(self, args=None, negate=False) -> None:
        self.log.debug(f"do_ip() -> command: ({args})")
          
        args_parts = args.strip().split()
        
        if args_parts[0] == "route":
            self.log.debug(f"do_ip(route) -> command: ({args})")  
            IpRouteConfig(args)
        
        elif args_parts[0] == "nat":
            self.log.debug(f"do_ip(nat) -> command: ({args})")  
            NatConfig(args)
        
        else:
            print(f"Invalid command: {args}")

    def complete_ipv6(self, text, line, begidx, endidx):
        completions = ['route']
        return [comp for comp in completions if comp.startswith(text)]
 
    def do_ipv6(self, args=None, negate=False) -> None:
        self.log.debug(f"do_route() -> command: ({args})")    
        IpRouteConfig().cmdloop() 

    def complete_rename(self, text, line, begidx, endidx):
        completions = ['if', 'if-alias', 'auto']
        return [comp for comp in completions if comp.startswith(text)]

    def do_rename(self, args: str, negate: bool = False) -> None:
        '''
        Rename a network interface.

        Usage:
            if <existing interface> if-alias <new interface>

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
            self.log.debug(f"do_alias() -> if")
            
            if len(args_parts) == 4:
                self.log.debug(f"do_alias() -> args-parts: {args_parts}")
                Interface().rename_interface(args_parts[1], args_parts[3])
            else:
                print(f"Invalid command: rename {args}")
            
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
            
                
