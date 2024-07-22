import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.config.bridge.bridge_config_cmd import BridgeConfigCmd
from lib.cli.config.loopback.loopback_config_cmd import LoopbackConfigCmd
from lib.cli.config.ethernet.ethernet_config_cmd import EthernetConfigCmd
from lib.cli.config.vlan.vlan_config_cmd import VlanConfigCmd
from lib.common.common import Common
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.interface import InterfaceType
from lib.network_manager.network_operations.bridge import Bridge
from lib.network_manager.network_operations.interface import Interface
from lib.network_manager.network_operations.nat import Nat
from lib.network_manager.network_operations.network_mgr import NetworkManager
from lib.network_manager.network_operations.vlan import Vlan
from lib.network_services.common.network_ports import NetworkPorts
from lib.system.system import System

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
    
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_os_network_interfaces() + [InterfaceType.LOOPBACK.value])         
    def configcmd_interface(self, args: List[str]=None) -> bool:
        self.log.debug(f'configcmd_interface -> {args}')
        
        interface_name = args[0]

        if Common().is_loopback_if_name_valid(interface_name, add_loopback_if_name=['lo']):
            self.log.debug(f'configcmd_interface() -> Loopback: {interface_name}')
            LoopbackConfigCmd(loopback_name=args).start()
            
        elif interface_name in Interface().get_os_network_interfaces(InterfaceType.ETHERNET):
            self.log.debug(f'configcmd_interface() -> Ethernet: {interface_name}')
            EthernetConfigCmd(eth_name=args).start()        
           
        elif interface_name in Interface().get_os_network_interfaces(InterfaceType.WIRELESS_WIFI):
            self.log.debug(f'configcmd_interface() -> WireLess WiFI: {interface_name}')
            print('Not implemented yet')
                        
        else:
            self.log.debug(f'Interface Type not found for interface: {interface_name}')
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
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['telnet-server', 'port', '23'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['ssh-server', 'port', '22'])  
    def configcmd_system(self, args: List=[str], negate: bool=False) -> bool:
        
        self.log.debug(f'configcmd_system() -> {args} -> negate: {negate}')

        if 'telnet-server' in args:

            if negate:
                self.log.debug('configcmd_system() -> Telnet Server: stopping service')
                return System().update_telnet_server(enable=(not negate))
            
            port = NetworkPorts.TELNET

            if 'port' in args:
                try:
                    port_index = args.index('port') + 1
                    if port_index < len(args):
                        port = int(args[port_index])

                        if port < 1 or port > 65535:
                            self.log.error(f'configcmd_system() -> Invalid port number: {port}')
                            return STATUS_NOK

                        self.log.debug(f'configcmd_system() -> telnet-server -> port: {port} -> negate: {negate}')
                    else:
                        self.log.error('Port number not specified after "port" keyword.')
                        print(f'error: port number not specified in command: {args}')
                        return STATUS_NOK

                except (ValueError, IndexError) as e:
                    self.log.error(f'Invalid port value or index error: {e}')
                    print(f'error: invalid port value in command: {args}')
                    return STATUS_NOK

            if System().update_telnet_server(enable=(not negate), port=port):
                self.log.error('Unable to set telnet server parameter via cli')
                return STATUS_NOK
                                
        elif 'ssh-server' in args:
            self.log.debug(f'configcmd_system() -> ssh-server -> negate: {negate}')
            
        else:
            self.log.error(f'Invalid command: {args}')
            print(f'error: invalid command: {args}')
            return STATUS_NOK
            
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
        if None == args:
            self.log.error('No hostname specified.')
            return STATUS_NOK
        
        return System().update_hostname(args[0])
  
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

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['pool-name'])
    def configcmd_nat(self, args: List[str], negate: bool=False) -> bool:

        if args[0] == 'pool-name':
            if len(args) < 2:
                self.log.error("configcmd_nat() -> Missing pool name.")
                print("Error: Missing pool name.")
                return STATUS_NOK
            
            pool_name = args[1]
            self.log.debug(f"configcmd_nat() -> pool-name: {pool_name}")
            
            if Nat().create_nat_pool(pool_name, negate):
                self.log.error(f'Unable to add NAT pool {pool_name} to DB')
                return STATUS_NOK
            
            self.log.debug(f"Successfully added NAT pool {pool_name} to DB")
        else:
            self.log.error(f"configcmd_nat() -> Invalid subcommand: {args[0]}")
            print(f"Error: Invalid subcommand: {args[0]}")
            return STATUS_NOK

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

