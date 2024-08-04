import logging
from typing import List, Optional

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.command_class_interface import CmdPrompt
from lib.cli.common.prompt_response import PromptResponse
from lib.cli.show.arp_show import ArpShow
from lib.cli.show.bridge_show import BridgeShow
from lib.cli.show.dhcp_show import DHCPClientShow, DHCPServerShow
from lib.cli.show.dump_db_show import DbDumpShow
from lib.cli.show.interface_show import InterfaceShow
from lib.cli.show.ip_route_show import RouteShow
from lib.cli.show.nat_show import NatShow
from lib.cli.show.router_configuration import RouterConfiguration
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
from lib.common.string_formats import StringFormats
from lib.hardware.hardware_detection import HardwareDetection
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.system.linux_calls import LinuxSystem
from lib.system.system_call import SystemCall


class Show(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SHOW_MODE)
               
    def show_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        STATUS_OK
    
    @CmdPrompt.register_sub_commands()         
    def show_arp(self, args: List=None) -> None:
        ArpShow().arp(args)
        STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['group'])      
    def show_bridge(self, args: List=None) -> None:
                
        if not args:
            BridgeShow().show_bridges()
            
        elif 'group' in args:
            BridgeShow().show_bridge_group_interface_table()    
            
        STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['client' , 'log'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['server', 'leases' , 'lease-log', 'server-log', 'status'])
    def show_dhcp(self, args: List=None) -> None:
        self.log.debug(f'show_dhcp: {args}')
        
        if '?'in args:
            str_hash = StringFormats.generate_hash_from_list(args[:-1])
            print(CmdPrompt.get_help(str_hash))
        
        elif 'client' and 'log' in args:
            DHCPClientShow().flow_log()
        
        elif 'server' and 'leases' in args:
            print(DHCPServerShow().leases())
            STATUS_OK

        elif 'server' and 'lease-log' in args:
            DHCPServerShow().dhcp_lease_log()
            STATUS_OK
        
        elif 'server' and 'server-log' in args:                
            print(DHCPServerShow().dhcp_server_log())
            STATUS_OK            

        elif 'server' and 'status' in args: 
            print(DHCPServerShow().status())
            STATUS_OK 
        
        else:
            STATUS_OK
        
        STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['brief'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['statistic'])
    def show_interface(self, args:List) -> None:
        """interfaces\t\t\tDisplay information about network interfaces."""
        
        self.log.debug(f'show_interfaces: {args}')
        
        if '?'in args:
            str_hash = StringFormats.generate_hash_from_list(args[:-1])
            print(CmdPrompt.get_help(str_hash))
        
        elif 'brief' in args:
            print(InterfaceShow().show_ip_interface_brief())
            STATUS_OK
            
        elif 'statistic' in args:
            print(InterfaceShow().show_interface_statistics())
            STATUS_OK
              
        else:
            PromptResponse.invalid_cmd(args)
            return STATUS_NOK

        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['cpu'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['network'])
    def show_hardware(self, args: List) -> None:
        """hardware\t\t\tDisplay information about hardware."""
        
        self.log.debug(f'show_hardware: {args}')
        
        if '?'in args:
            str_hash = StringFormats.generate_hash_from_list(args[:-1])
            print(CmdPrompt.get_help(str_hash))
        
        elif 'cpu' in args:
            print(HardwareDetection().hardware_cpu())
            return
            
        elif 'network' in args:
            print(HardwareDetection().hardware_network())
            return

        else:
            PromptResponse.invalid_cmd(args)
            return STATUS_NOK
        
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
    def show_ip(self, args: List) -> None:
        """ip\t\t\t\tDisplay information about IP addresses."""
        
        self.log.debug(f'show_ip: {args}')
        
        if '?'in args:
            str_hash = StringFormats.generate_hash_from_list(args[:-1])
            print(CmdPrompt.get_help(str_hash))
        
        else:
            print('Not Working Yet')
            STATUS_OK   
    
    @CmdPrompt.register_sub_commands()    
    def show_route(self, args: List) -> None:
        
        self.log.debug(f'show_route: {args}')
        
        if '?'in args:
            str_hash = StringFormats.generate_hash_from_list(args[:-1])
            print(CmdPrompt.get_help(str_hash))
        
        else:
            RouteShow().route()
            STATUS_OK
        
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['configuration', 'system-commands'])      
    def show_running(self, args: List) -> None:

        self.log.debug(f'show_running: {args}')

        if '?'in args:
            str_hash = StringFormats.generate_hash_from_list(args[:-1])
            print(CmdPrompt.get_help(str_hash))

        elif 'configuration' in args:
            for line in RouterConfiguration().get_running_configuration():
                print(line)
                
        elif 'system-commands' in args:
            for line in SystemCall().get_run_log():
                print(line)                
            
        STATUS_OK
                
    @CmdPrompt.register_sub_commands()      
    def show_nat(self, args: List) -> None:

        self.log.debug(f'show_running: {args}')

        if '?'in args:
            str_hash = StringFormats.generate_hash_from_list(args[:-1])
            print(CmdPrompt.get_help(str_hash))
            
        else:
            NatShow().getNatTable()

    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['all', 'interface', 'nat', 'bridge'])     
    def show_db(self, args: List) -> None:
        if 'all' in args:
            DbDumpShow().dump_db()
            
        elif 'interface' in args:
            DbDumpShow().dump_db(include_schema=False, search_term='Interface')
        
        elif 'nat' in args:
            DbDumpShow().dump_db(include_schema=False, search_term='NAT')
        
        elif 'bridge' in args:
            DbDumpShow().dump_db(include_schema=False, search_term='Bridge')
        
        else:    
            PromptResponse.invalid_cmd(args)
                
    @CmdPrompt.register_sub_commands()
    def show_dmesg(self, args: Optional[List[str]] = None) -> bool:
        """Displays kernel ring buffer messages using LinuxSystem.get_dmesg().

        This function retrieves kernel ring buffer messages and prints them
        to the console.

        Args:
            args (Optional[List[str]]): Optional arguments passed to
                LinuxSystem.get_dmesg() (implementation may vary).

        Returns:
            int: STATUS_OK on success, an error code otherwise.
        """
        self.log.debug(f'show_dmesg() -> {args}')
        print(LinuxSystem().get_dmesg(args))
        return STATUS_OK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['--help'])
    def show_journalctl(self, args: Optional[List[str]] = None) -> int:
        """Displays systemd journal entries using LinuxSystem.get_journalctl().

        This function retrieves systemd journal entries based on provided
        arguments and prints them to the console.

        Args:
            args (Optional[List[str]]): Optional arguments passed to
                LinuxSystem.get_journalctl() (implementation may vary).

        Returns:
            int: STATUS_OK on success, an error code otherwise.
        """

        self.log.debug(f'show_journalctl() -> {args}')
        print(LinuxSystem().get_journalctl(args))
        return STATUS_OK                                                   