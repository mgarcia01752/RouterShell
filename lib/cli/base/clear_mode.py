import cmd2
import logging
import argparse

from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.router_prompt import RouterPrompt
from lib.cli.base.exec_priv_mode import ExecMode, ExecException
from lib.network_manager.arp import Arp
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.constants import *

class InvalidClearMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class ClearMode(cmd2.Cmd, GlobalUserCommand, RouterPrompt):
    """Clear-Mode-Commands"""

    def __init__(self, usr_exec_mode: ExecMode, arg=None):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.PRIV_MODE)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CLEAR_MODE)
        
        self.log.debug(f"Entering Clear({arg})")

        if usr_exec_mode is ExecMode.USER_MODE:
            msg = f"Does not have necessary configure privileges ({usr_exec_mode})"
            self.log.error(msg)
            print(msg)
            raise ExecException(msg)
        
        self.current_exec_mode = usr_exec_mode
        self.prompt = self.set_prompt()
        self.clear(arg)
        
    def clear(self, args):
        """
        Clear entries on router.

        Args:
            args (str): Command arguments in the format "clear <command>".

        """
        self.log.debug(f"Entering clear({args})")

        # Define a parser with a more informative description and epilog.
        parser = argparse.ArgumentParser(
            description="Clear entries on the network device.",
            epilog="Supported subcommands:\n"
                    "   arp [interface_name]           Clear ARP cache for a specific interface.\n"
                    "   router-db                      Clear RouterShell DB cache.\n"
        )

        # Create a subparser for the 'arp' subcommand.
        subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")
        arp_parser = subparsers.add_parser("arp", help="Clear ARP cache for a specific interface")
        router_db_parser = subparsers.add_parser("router-db", help="Clear RouterShell Database")
        arp_parser.add_argument("interface", nargs='?', help="Name of the interface")

        try:
            parsed_args = parser.parse_args(args.split())
        except SystemExit:
            return

        if parsed_args.subcommand == 'arp':
            self.log.debug("Clear ARP cache command")
            interface = parsed_args.interface
            Arp().arp_clear(interface)
            return
        
        elif parsed_args.subcommand == 'router-db':
            self.log.debug("Clear RouterShell DB command")
            confirmation = input("Are you sure? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                RSDB().reset_database()
            else:
                print("Command canceled.")


             