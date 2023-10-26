import json
import cmd2
import logging
import argparse

from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.router_prompt import RouterPrompt
from lib.cli.base.exec_priv_mode import ExecMode, ExecException
from lib.network_manager.arp import Arp
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
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
            description="Clear ARP entries on the network device.",
            epilog="Supported subcommand:\n"
                    "   arp [interface _name]           Clear ARP cache for a specific interface.\n"
                    "   interface [interface name]      Clear interface.\n"
        )

        # Create a subparser for the 'arp' subcommand.
        subparsers = parser.add_subparsers(dest="subcommand", help="Subcommands")
        arp_parser = subparsers.add_parser("arp", help="Clear ARP cache for a specific interface")
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
        else:
            return