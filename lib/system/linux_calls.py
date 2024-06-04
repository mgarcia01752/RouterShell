import logging
from typing import List
from lib.db.system_db import SystemDatabase
from lib.network_manager.common.run_commands import RunCommand
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS


class InvalidLinuxSystem(Exception):
    def __init__(self, message):
        super().__init__(message)

class LinuxSystem(RunCommand):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_CONFIG)
        self.arg = arg
        self.sys_db = SystemDatabase()

    def get_dmesg(self) -> List:
        """dmesg – Shows Kernel Messages"""
        
        result = self.run(['dmesg'])
        
        if result.exit_code:
            self.log.error(f'Unable to get kernel dmesg; Reason: {result.stderr}')
            return []

        return result.stdout
    
    def get_journalctl(self, args: List=None) -> List:
        """journalctl – Query Contents of Systemd Journal"""
        
        result = self.run(['journalctl'])
        
        if result.exit_code:
            self.log.error(f'Unable to get Systemd journalctl; Reason: {result.stderr}')
            return []
        
        return result.stdout