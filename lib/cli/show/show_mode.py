import json
import cmd2
import logging
import argparse

from tabulate import tabulate

from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.router_prompt import RouterPrompt
from lib.cli.common.exec_priv_mode import ExecMode, ExecException
from lib.cli.show.arp_show import ArpShow
from lib.cli.show.bridge_show import BridgeShow
from lib.cli.show.dhcp_show import DHCPClientShow, DHCPServerShow
from lib.cli.show.interface_show import InterfaceShow
from lib.cli.show.ip_route_show import RouteShow
from lib.cli.show.nat_show import NatShow
from lib.cli.show.router_configuration import RouterConfiguration
from lib.cli.show.vlan_show import VlanShow
from lib.db.vlan_db import VlanDatabase
from lib.db.interface_db import InterfaceDatabase
from lib.db.nat_db import NatDB
from lib.common.constants import *
from lib.hardware.hardware_detection import HardwareDetection


class InvalidShowMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class ShowMode(cmd2.Cmd, GlobalUserCommand, RouterPrompt):
    """Command set for Show-Mode-Commands"""

    def __init__(self, usr_exec_mode: ExecMode, arg=None):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.PRIV_MODE)
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.log.debug(f"Entering ShowMode({arg})")

        if usr_exec_mode is ExecMode.USER_MODE:
            msg = f"Does not have necessary configure privileges ({usr_exec_mode})"
            self.log.error(msg)
            print(msg)
            raise ExecException(msg)
        
        self.current_exec_mode = usr_exec_mode
        self.prompt = self.set_prompt()
        self.show(arg)
        
    def show(self, args):

        """
        Show information.

        Args:
            arg (str): Command arguments.
            
            show arp                            (Implemented)
            show bridge                         (Implemented)
            show interfaces [brief | statistic] (Implemented)
            show dhcp-client [log]
            show dhcp-server [leases | lease-log | server-log | status]
            show hardware [cpu | network]
            show nat
            show nat-db
            show vlan                           (Implemented)
            show vlan database
            show route                          (Implemented)
            show running-config
            show ip route
            show ip6 route
            show ip interface
            show if-db                          (Implemented)
            show wireless
            
        """  
        
        self.log.debug(f"Entering show({args})")
                          
        parser = argparse.ArgumentParser(
            description="Show commands:",
            epilog="Cisco-style suboptions:\n"
                "  arp\n"
                "  bridge\n"
                "  interfaces\n"
                "  vlan\n"
                "  ip\n"
                "  ip6\n"
                "  route\n"
                "  <suboption> --help                         Get help for specific suboptions."
        )
        show_parser = parser.add_subparsers(dest="subcommand")

        show_arp_parser = show_parser.add_parser("arp",
            help="Display Address Resolution Protocol (ARP) table."
        )

        show_bridge_parser = show_parser.add_parser("bridge",
            help="Display information about network bridges."
        )

        show_dhcp_client_parser = show_parser.add_parser("dhcp-client", help="Specify dhcp-client")
        
        show_dhcp_client_parser.add_argument("dhcp_client_get_option", choices=['log'],
            help="Specify dhcp-client [log]"
        )   

        show_dhcp_server_parser = show_parser.add_parser("dhcp-server", help="Specify dhcp-server")
        
        show_dhcp_server_parser.add_argument("dhcp_server_get_option", choices=['leases', 'lease-log', 'server-log', 'status'],
            help="Specify dhcp-server [leases | lease-log | server-log | status]"
        )        

        show_interfaces_parser = show_parser.add_parser("interfaces",
            help="Display information about network interfaces."
        )

        show_interfaces_parser.add_argument("interface_show_type", choices=['brief', 'statistic'],
            help="Specify interface [brief | statistic]"
        )
        
        show_hardware_parser = show_parser.add_parser("hardware",
            help="Display information about network interfaces."
        )
        
        show_hardware_parser.add_argument("hardware_type", choices=['cpu', 'network'],
            help="Specify hardware type"
        )
        
        show_ip_parser = show_parser.add_parser("ip",
            help="Display IP-related information."
        )

        show_ip6_parser = show_parser.add_parser("ip6",
            help="Display IPv6-related information."
        )

        show_nat = show_parser.add_parser("nat",
            help="Display Network Address Translation (NAT) information."
        )

        show_nat_db = show_parser.add_parser("nat-db",
                                            help="Display the NAT pool database."
        )

        show_vlan_parser = show_parser.add_parser("vlan",
            help="Display information about VLANs."
        )

        show_vlan_db_parser = show_parser.add_parser("vlan-db",
            help="Display the VLAN database."
        )

        show_if_db_parser = show_parser.add_parser("if-db",
            help="Display information about network interfaces in the database."
        )

        show_route_parser = show_parser.add_parser("route",
            help="Display routing table information."
        )

        show_running_config_parser = show_parser.add_parser("running-config",
            help="Display running configuration."
        )

        try:
            args = parser.parse_args(args.split())
        except SystemExit:
            return

        if args.subcommand == 'arp':
            self.log.debug("Show arp command")
            ArpShow().arp()
            return
        
        elif args.subcommand == 'bridge':
            self.log.debug("Show bridge command")
            BridgeShow().show_bridges()
            return

        elif args.subcommand == 'dhcp-client':
            self.log.debug("Show DHCP Client command")
            
            dhcp_client_get_option = args.dhcp_client_get_option
            
            if dhcp_client_get_option == 'log':
                DHCPClientShow().flow_log()
                return
        
        elif args.subcommand == 'dhcp-server':
            
            self.log.debug("Show DHCP Server command")

            dhcp_server_get_option = args.dhcp_server_get_option
            
            if dhcp_server_get_option == 'leases':
                print(DHCPServerShow().leases())
                return

            if dhcp_server_get_option == 'lease-log':
                DHCPServerShow().dhcp_lease_log()
                return
                            
            elif dhcp_server_get_option == 'server-log':
                print(DHCPServerShow().dhcp_server_log())
                return            

            elif dhcp_server_get_option == 'status':
                print(DHCPServerShow().status())
                return            
                
        elif args.subcommand == 'interfaces':
            self.log.debug("Show interfaces command")
            
            interface_show_type = args.interface_show_type
            
            if interface_show_type == 'brief':
                print(InterfaceShow().show_ip_interface_brief())
                return
                
            elif interface_show_type == 'statistic':
                print(InterfaceShow().show_interface_statistics())
                return

        elif args.subcommand == 'hardware':

            hardware_type = args.hardware_type
            self.log.debug(f"Show hardware-{hardware_type}")

            if hardware_type == 'cpu':
                print(HardwareDetection().hardware_cpu())
                return
                
            elif hardware_type == 'network':
                print(HardwareDetection().hardware_network())
                return
                        
        elif args.subcommand == 'ip':
            self.log.debug("Show ip command")
            return
        
        elif args.subcommand == 'ip6':
            self.log.debug("Show ip6 command")
            return
        
        elif args.subcommand == 'route':
            self.log.debug("Show route command")
            RouteShow().route()
            return

        elif args.subcommand == 'running-config':
            self.log.debug("Show running configuration")
            run_config = RouterConfiguration().get_running_configuration()
            for line in run_config:        
                print(line)
        
        elif args.subcommand == 'nat':
            self.log.debug("Show nat command")
            NatShow().getNatTable()
            return
        
        elif args.subcommand == 'nat-db':
            self.log.debug("Show nat command")
            print(NatDB().to_json())
            return
        
        elif args.subcommand == 'vlan':
            self.log.debug("Show vlan command")
            VlanShow().vlan()
            return
        
        elif args.subcommand == 'vlan-db':
            self.log.debug("Show vlan database")
            print(f"{json.dumps(VlanDatabase.to_json(), indent=4)}")
            return
        
        elif args.subcommand == 'if-db':
            self.log.debug("Show interface database")
            print(f"{json.dumps(InterfaceDatabase.to_json(), indent=4)}")
            return
        else:
            return