
import logging
from typing import List, Optional

from lib.cli.base.exec_priv_mode import ExecMode

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.string_formats import StringFormats
from lib.network_manager.arp import Encapsulate
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.common.phy import Duplex, State
from lib.network_manager.dhcp_client import DHCPVersion
from lib.network_manager.dhcp_server import DHCPServer
from lib.network_manager.interface import Interface
from lib.network_manager.nat import NATDirection

class IfConfigError(Exception):
    """Custom exception for IfConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'IfConfigError: {self.message}'

class IfConfig(CmdPrompt, Interface):

    def __init__(self, ifName: str=None, ifType: str=None) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().IF_CONFIG)
        
        self.ifName = ifName
               
    def ifconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
        return STATUS_OK
            
    @CmdPrompt.register_sub_commands() 
    def ifconfig_description(self, line: Optional[str], negate: bool = False) -> bool:
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
            self.log.info(f'Negating description on interface: {self.ifName}')
            line = [""]
        
        if self.update_db_description(self.ifName, StringFormats.list_to_string(line)):
            print("Unable to add description to DB")
            raise ValueError("Failed to update the description in the database.")
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(sub_cmds=['auto'],     help='Auto assign mac address')
    @CmdPrompt.register_sub_commands(sub_cmds=['address'],  help='Assign mac address <xxxx.xxxx.xxxx>')     
    def ifconfig_mac(self, args:str) -> bool:
        
        self.log.debug(f"ifconfig_mac() -> args: {args}")
        
        if len(args) == 1 and args[0] == "auto":
            self.log.debug(f"ifconfig_mac() -> auto")
            self.update_interface_mac(self.ifName)
                            
        elif len(args) == 2 and args[0] == "address":
            mac = args[1]
            self.log.debug(f"ifconfig_mac() -> address -> {mac}")
            self.update_interface_mac(self.ifName, mac)
            
        else:
            print("Usage: mac [auto | <mac address>]")
            
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_ipv6(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(sub_cmds=['address', 'secondary'], help='set ')
    @CmdPrompt.register_sub_commands(sub_cmds=['drop-gratuitous-arp'],  help='Enable drop-gratuitous-ARP')        
    @CmdPrompt.register_sub_commands(sub_cmds=['drop-gratuitous-arp'],  help='Enable drop-gratuitous-ARP')
    @CmdPrompt.register_sub_commands(sub_cmds=['proxy-arp'],            help='Enable proxy ARP')
    @CmdPrompt.register_sub_commands(sub_cmds=['static-arp', 'arpa'],   help='Add/Del static ARP entry.')
    @CmdPrompt.register_sub_commands(sub_cmds=['nat', 'inside', 'pool', 'acl'],     help='nat [inside|outside] pool <nat-pool-name> acl <acl-id> ')
    @CmdPrompt.register_sub_commands(sub_cmds=['nat', 'outside', 'pool', 'acl'],    help='nat [inside|outside] pool <nat-pool-name> acl <acl-id> ')
    def ifconfig_ip(self, args: List, negate=False) -> bool:

        self.log.info(f'ifconfig_ip() -> {args}')
  
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_sub_cmds=['auto', 'half', 'full'])    
    def ifconfig_duplex(self, args: Optional[str]) -> bool:
        """
        Updates the interface duplex mode based on the provided arguments.
        
        Args:
            args (Optional[str]): The duplex mode argument, expected to be 'auto', 'half', or 'full'.
        
        Returns:
            bool: STATUS_OK (True) indicating the operation was successful.
        
        Raises:
            ValueError: If the duplex mode is invalid.
        """
        args = StringFormats.list_to_string(args)
        
        if not args:
            print("Usage: duplex <auto | half | full>")
            return

        if self.interface_type != InterfaceType.ETHERNET:
            self.update_interface_duplex(self.ifName, Duplex.NONE)
            print("interface must be of ethernet type")
            return
        
        duplex_values = {d.value: d for d in Duplex}
        
        args = args.lower()

        if args in duplex_values:
            duplex = duplex_values[args]
            self.update_interface_duplex(self.ifName, duplex)
                        
        else:
            print(f"Invalid duplex mode ({args}). Use 'auto', 'half', or 'full'.")
                    
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_speed(self, args) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_bridge(self, args, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_shutdown(self, args=None, negate=False) -> bool:
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

        self.log.debug(f'ifconfig_shutdown(negate: {negate}) -> State: {ifState.name}')

        self.update_shutdown(self.ifName, ifState)
        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_switchport(self, args=None, negate=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands()    
    def ifconfig_wireless(self, args=None, negate:bool=False) -> bool:
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_sub_cmds=['shutdown', 'description'])    
    def ifconfig_no(self, args: List):
        
        self.log.debug(f"ifconfig_no() -> Line -> {args}")

        start_cmd = args[0]
                
        if start_cmd == 'shutdown':
            self.log.debug(f"up/down interface -> {self.ifName}")
            self.ifconfig_shutdown(None, negate=True)
        
        elif start_cmd == 'bridge':
            self.log.debug(f"Remove bridge -> ({args})")
            self.ifconfig_bridge(args[1:], negate=True)
        
        elif start_cmd == 'ip':
            self.log.debug(f"Remove ip -> ({args})")
            self.ifconfig_ip(args[1:], negate=True)
        
        elif start_cmd == 'ipv6':
            self.log.debug(f"Remove ipv6 -> ({args})")
            self.ifconfig_ipv6(args[1:], negate=True)

        elif start_cmd == 'switchport':
            self.log.debug(f"Remove switchport -> ({args})")
            self.ifconfig_switchport(args[1:], negate=True)
        
        elif start_cmd == 'description':
            self.log.info(f"Remove description -> ({args})")
            self.ifconfig_description(args[1:], negate=True)
        
        else:
            print(f"No negate option for {start_cmd}")
        
        return STATUS_OK