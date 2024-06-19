
import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.config.bridge.bridge_config_cmd import BridgeConfigCmd
from lib.cli.config.ethernet.ethernet_config_cmd import EthernetConfigCmd
from lib.cli.config.interface.interface_config_cmd import InterfaceConfigCmd
from lib.cli.config.loopback.loopback_config_cmd import LoopbackConfigCmd
from lib.cli.config.vlan.vlan_config_cmd import VlanConfigCmd
from lib.common.common import Common
from lib.common.constants import STATUS_NOK, STATUS_OK, Status
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.db.system_db import SystemDatabase
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.network_operations.bridge import Bridge
from lib.network_manager.network_operations.interface import Interface
from lib.network_manager.network_operations.network_mgr import NetworkManager
from lib.network_manager.network_operations.vlan import Vlan
from lib.system.system_call import SystemCall

class ConfigCmd(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CONFIGURE_CMD)
               
    def configcmd_help(self, args: List[str]=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_os_network_interfaces())         
    def configcmd_interface(self, args: List[str]=None) -> bool:
        self.log.debug(f'configcmd_interface -> {args}')
        
        if Common().is_loopback_if_name_valid(args[0], add_loopback_if_name=['lo']):
            self.log.debug(f'configcmd_interface() -> Loopback: {args}')
            LoopbackConfigCmd(loopback_name=args).start()
        
        elif args[0] ==  Interface().get_os_network_interfaces(InterfaceType.ETHERNET):
            self.log.debug(f'configcmd_interface() -> Ethernet: {args}')
            EthernetConfigCmd(interface_name=args).start()        

        elif args[0] ==  Interface().get_os_network_interfaces(InterfaceType.WIRELESS_WIFI):
            self.log.debug(f'configcmd_interface() -> WireLess WiFI: {args}')
            print('Not implemented yet')            
        else:
            return STATUS_NOK        
        return STATUS_OK

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Bridge().get_bridge_list_os())         
    def configcmd_bridge(self, args: List[str]=None, negate: bool=False) -> bool:
        self.log.debug(f'configcmd_bridge -> {args}')
        BridgeConfigCmd(bridge_name=args, negate=negate).start()        
        return STATUS_OK

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Vlan().get_vlan_interfaces())         
    def configcmd_vlan(self, args: List[str]=None, negate: bool=False) -> bool:
        self.log.debug(f'configcmd_vlan -> {args}')
        VlanConfigCmd()(bridge_name=args, negate=negate).start()        
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['telnet-server', 'ssh-server'])  
    def configcmd_system(self, args: List=None, negate: bool=False) -> bool:
        self.log.debug(f'configcmd_system() -> {args}')

        status = Status.DISABLE if negate else Status.ENABLE

        if 'telnet-server' in args:
            self.log.debug(f'configcmd_system() -> telnet-server -> negate: {negate}')    
            SystemCall().set_telnetd_status(status)

        elif 'ssh-server' in args:
            self.log.debug(f'configcmd_system() -> ssh-server -> negate: {negate}') 
            pass

        else:
            print(f'error: invalid command: {args}')

        return STATUS_OK    

    @CmdPrompt.register_sub_commands()
    def configcmd_hostname(self, args: List = None) -> bool:
        """
        Configures the hostname of the system.

        Sets the hostname both in the operating system and the system database.

        Args:
            args (List, optional): A list containing the new hostname to set.

        Returns:
            bool: STATUS_OK if the hostname is successfully set in both the OS and the database, STATUS_NOK otherwise.
        """
        self.log.debug(f"configcmd_hostname() -> args: {args}")

        # Set hostname in the operating system
        if SystemCall().set_hostname_os(args[0]):
            self.log.error(f"Error: Failed to set the hostname: ({args[0]}) to OS")
            return STATUS_NOK

        # Set hostname in the system database
        if SystemDatabase().set_hostname_db(args[0]):
            self.log.error(f"Error: Failed to set the hostname: ({args[0]}) to DB")
            return STATUS_NOK

        return STATUS_OK

    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['if', 'if-alias'])
    def configcmd_rename(self, args: List) -> bool:

        if len(args) != 4:
            print('missing arguments') 
        
        self.log.debug(f"configcmd_rename() -> args: {args}")

        if args[0] == 'if':
            self.log.debug(f"configcmd_rename() -> if")
            
            if len(args) == 4:
                self.log.debug(f"configcmd_rename() -> args-parts: {args}")
                Interface().rename_interface(args[1], args[3])

            else:
                print(f"Invalid command: rename {args}")
                
        return STATUS_OK

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_os_network_interfaces())
    def configcmd_flush(self, interface_name:str) -> bool:

        """
        Command to flush the configuration of a network interface.

        This command allows the user to flush the configuration of a network interface,
        effectively removing all assigned IP addresses and resetting the interface.

        Args:
            interface_name (str): The name of the network interface to flush.

        Usage:
            flush <interface_name>

        Example:
            flush eth0
        """
        self.log.debug(f'configcmd_flush() -> {interface_name}')

        NetworkManager().flush_interface(interface_name[0])

        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['bridge'] , 
                                     append_nested_sub_cmds=Bridge().get_bridge_list_os())
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['system'], append_nested_sub_cmds=['telnet-server', 'ssh-server'])
    def configcmd_no(self, args: List) -> bool:

        if args[0] == 'bridge':
            self.log.debug(f"configcmd_no() -> bridge: {args[1]}")
            Bridge().destroy_bridge_cmd(args[1])

        if args[0] == 'system':
            self.log.debug(f"configcmd_no() -> system: {args[1]}")
            self.configcmd_system(args=args, negate=True)

        return STATUS_OK

    
