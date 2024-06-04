import logging
from typing import List, Optional
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
    
    def get_journalctl(self, args: Optional[List[str]] = None) -> str:
        """Queries the systemd journal using 'journalctl' command.

        This function retrieves systemd journal entries based on provided arguments.
        It handles potential errors and returns the journal output as a string.

        Args:
            args (Optional[List[str]]): Optional arguments to pass to 'journalctl'
                (e.g., `-u <service>`, `--since yesterday`).

        Returns:
            str: The output of the 'journalctl' command as a string, or an empty
                string on error.

        Raises:
            RuntimeError: If the `journalctl` command fails to execute.
        """

        command = ['journalctl']
        if args:
            # Simply append the provided list of arguments
            command.extend(args)
        print(command)
        result = self.run(command)

        if result.exit_code:
            self.log.error(f'Failed to get Systemd journalctl; Reason: {result.stderr}')
            raise RuntimeError("Error retrieving journal entries")  # Raise an exception

        return result.stdout.strip()  # Remove leading/trailing whitespace
