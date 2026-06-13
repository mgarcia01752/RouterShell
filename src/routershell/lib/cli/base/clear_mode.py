import logging

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB as DB
from routershell.lib.network_manager.network_operations.arp import Arp
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.system.system_start_up import SystemStartUp


class InvalidClearMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class ClearMode(CmdPrompt):

    def __init__(self, arg=None):
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CLEAR_MODE)
        
        self.log.debug(f"Entering Clear({arg})")

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['arp'], append_nested_sub_cmds=['all'] + Interface().get_os_network_interfaces())
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['router-db'])
    def clearmode_clear(self, args: list):

        self.log.debug(f"Entering clear({args})")

        if 'arp' in args[0]:
            
            interface = args[1]
            self.log.debug(f"Clear ARP cache command -> Clear Arp Interface: {interface}")
            
            return Arp().arp_clear(interface)
                
        if 'router-db' in args[0]:
            self.log.debug("Clear RouterShell DB command")
                       
            confirmation = input("Are you sure? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                DB().reset_database()
            else:
                print("Command canceled.")
            
            confirmation = input("Rebuild Router? (yes/no): ").strip().lower()
            if confirmation == 'yes':
                SystemStartUp()
            
            return STATUS_OK

        else:
            print(f'Invalid clear command: {args}')
            return STATUS_OK