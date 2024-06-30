import logging
import argparse
from typing import List

from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.common.exec_priv_mode import ExecMode, ExecException
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.constants import *
from lib.network_manager.network_operations.arp import Arp
from lib.network_manager.network_operations.interface import Interface


class InvalidClearMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class ClearMode(CmdPrompt):

    def __init__(self, arg=None):
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CLEAR_MODE)
        
        self.log.debug(f"Entering Clear({arg})")

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['arp'], append_nested_sub_cmds=['all'] + Interface().get_os_network_interfaces())
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['router-db'])
    def clearmode_clear(self, args: List):

        self.log.debug(f"Entering clear({args})")

        if 'arp' in args[0]:
            
            interface = args[1]
            self.log.debug(f"Clear ARP cache command -> Clear Arp Interface: {interface}")
            
            return Arp().arp_clear(interface)
                
        if 'router-db' in args[0]:
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
            print(f'Invalid clear command: {args}')
            return STATUS_OK