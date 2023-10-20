import json
import cmd2
import logging
import argparse

from lib.cli.base.global_operation import GlobalUserCommand
from lib.common.router_prompt import RouterPrompt
from lib.cli.base.exec_priv_mode import ExecMode, ExecException
from lib.cli.config.vlan_config import VlanShow
from lib.cli.show.arp_show import ArpShow
from lib.cli.show.bridge_show import BridgeShow
from lib.cli.show.interface_show import InterfaceShow
from lib.cli.show.ip_route_show import RouteShow
from lib.cli.show.nat_show import NatShow
from lib.db.vlan_db import VLANDatabase
from lib.db.interface_db import InterfaceConfigDB
from lib.db.nat_db import NatDB
from lib.common.constants import *

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
            
            show arp                (Implemented)
            show bridge             (Implemented)
            show interface          (Implemented)
            show nat
            show nat-db
            show vlan               (Implemented)
            show vlan database
            show route              (Implemented)
            show ip route
            show ip6 route
            show ip interface
            show if-db              (Implemented)
            
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

        show_interfaces_parser = show_parser.add_parser("interfaces",
            help="Display information about network interfaces."
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
        # show_parser.add_argument("arp", help="show arp")

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

        try:
            args = parser.parse_args(args.split())
        except SystemExit:
            # In this case, just return without taking any action.
            return

        if args.subcommand == 'arp':
            self.log.debug("Show arp command")
            ArpShow().arp()
            return
        elif args.subcommand == 'bridge':
            self.log.debug("Show bridge command")
            BridgeShow().show_bridges()
            return
        elif args.subcommand == 'interfaces':
            self.log.debug("Show interfaces command")
            InterfaceShow().show_interfaces()
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
            print(f"{json.dumps(VLANDatabase.to_json(), indent=4)}")
            return
        elif args.subcommand == 'if-db':
            self.log.debug("Show interface database")
            print(f"{json.dumps(InterfaceConfigDB.to_json(), indent=4)}")
            return
        else:
            return