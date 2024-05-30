import logging
import argparse
from typing import List

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.base.exec_priv_mode import ExecMode, ExecException
from lib.network_manager.arp import Arp
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.constants import *
from lib.network_manager.interface import Interface

class InvalidClearMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class ClearMode(CmdPrompt):
    """Clear-Mode-Commands"""

    def __init__(self, arg=None):
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CLEAR_MODE)
        
        self.log.debug(f"Entering Clear({arg})")

    @CmdPrompt.register_sub_commands(sub_cmds=['arp'], append_parallel_sub_cmds=Interface().get_network_interfaces())
    @CmdPrompt.register_sub_commands(sub_cmds=['router-db'])
    def clearmode_clear(self, args: List):

        self.log.info(f"Entering clear({args})")

        parser = argparse.ArgumentParser(
            description="Clear entries on router",
            epilog="Supported subcommands:\n"
                    "   arp [interface_name]           Clear ARP cache for a specific interface.\n"
                    "   router-db                      Clear RouterShell DB cache.\n"
        )

        subparsers = parser.add_subparsers(dest='subcommand')

        arp_parser = subparsers.add_parser('arp', help='Clear ARP cache')
        arp_parser.add_argument('interface', type=str, help='Interface name')

        router_db_parser = subparsers.add_parser('router-db', help='Clear RouterShell DB')

        parsed_args = parser.parse_args(args)
        print(f'ParseArgs: {parsed_args}')

        if parsed_args.subcommand == 'arp':
            interface = parsed_args.interface
            self.log.debug(f"Clear ARP cache command -> Clear Arp Interface: {interface}")
            Arp().arp_clear(interface)
            return STATUS_OK
        
        if parsed_args.subcommand == 'router-db':
            self.log.debug(f"Clear RouterShell DB command")
            
            # TODO
            # if self.get_exec_mode() != ExecMode.PRIV_MODE:
            #    print(f"Unable to clear router-db, must be in Privilege Mode")
                       
            confirmation = input("Are you sure? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                RSDB().reset_database()
            else:
                print("Command canceled.")
            
            return STATUS_OK

        else:
            print(f'Invalid clear command: {parsed_args.subcommand}')
            return STATUS_OK