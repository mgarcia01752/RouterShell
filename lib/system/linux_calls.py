import logging
from typing import List, Optional
from lib.db.system_db import SystemDatabase
from lib.network_manager.common.run_commands import RunCommand
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS


class InvalidLinuxSystem(Exception):
    """Raised when an invalid Linux system object is encountered."""

    def __init__(self, message="The provided Linux system is invalid."):
        super().__init__(message)

class LinuxSystem(RunCommand):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().LINUX_SYSTEM)
        self.arg = arg
        self.sys_db = SystemDatabase()

    def get_dmesg(self, args: Optional[List[str]] = None) -> str:
        """Queries the kernel ring buffer using 'dmesg' command.

        This function retrieves kernel ring buffer messages based on provided arguments.
        It handles potential errors and returns the message output as a string.

        Args:
            args (Optional[List[str]]): Optional arguments to pass to 'dmesg'
                (implementation may vary, consult 'dmesg' documentation).

        Returns:
            str: The output of the 'dmesg' command as a string, or an empty
                string on error.

        Raises:
            RuntimeError: If the `dmesg` command fails to execute.
        """

        command = ['dmesg']
        if args:
            command.extend(args)

        result = self.run(command)

        if result.exit_code:
            self.log.error(f'Failed to get kernel dmesg; Reason: {result.stderr}')
            raise RuntimeError("Error retrieving kernel messages")

        return result.stdout.strip()

    
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
            command.extend(args)

        result = self.run(command)

        if result.exit_code:
            self.log.error(f'Failed to get Systemd journalctl; Reason: {result.stderr}')
            raise RuntimeError("Error retrieving journal entries")

        return result.stdout.strip()
