import os
import re
from enum import Enum

from routershell.lib.common.constants import SYSTEMD_RUNTIME_DIR, SYSV_BOOT_LOG_FILE, SYSV_MESSAGES_LOG_FILE
from routershell.lib.common.types import PredicateResult
from routershell.lib.network_manager.common.run_commands import RunCommand


class InitSystem(Enum):
    SYSTEMD = 'systemd'
    SYSV = 'sysv'
    UNKNOWN = 'unknown'

class InitSystemChecker(RunCommand):
    """
    A class to check whether the Linux system is using SysV init or Systemd, implemented as a Singleton.
    """

    _instance: 'InitSystemChecker | None' = None
    _init_system: InitSystem | None = None

    def __new__(cls, *args, **kwargs) -> 'InitSystemChecker':
        """
        Creates a new instance of InitSystemChecker if one does not already exist.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            InitSystemChecker: The singleton instance of InitSystemChecker.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """
        Initializes the singleton instance by detecting the init system.
        """
        self._init_system = self._detect_init_system()

    def _detect_init_system(self) -> InitSystem:
        """
        Detects the current init system.

        Returns:
            InitSystem: An enum representing the init system.
        """
        try:
            if os.path.exists(SYSTEMD_RUNTIME_DIR):
                return InitSystem.SYSTEMD
            
            result = self.run(['systemctl', '--version'], suppress_error=True)
            if result.exit_code == 0:
                return InitSystem.SYSTEMD
            
        except FileNotFoundError:
            pass
        
        except Exception as e:
            print(f"An error occurred while checking Systemd: {e}")
        
        return InitSystem.SYSV

    def is_systemd(self) -> PredicateResult:
        """
        Checks if the system is using Systemd.

        Returns:
            StatusResult: True if Systemd is in use, False otherwise.
        """
        return self._init_system == InitSystem.SYSTEMD

    def is_sysv(self) -> PredicateResult:
        """
        Checks if the system is using SysV init.

        Returns:
            StatusResult: True if SysV is in use, False otherwise.
        """
        return self._init_system == InitSystem.SYSV
    
    def get_init_system(self) -> InitSystem:
        """
        Gets the current init system.

        Returns:
            InitSystem: The enum representing the current init system.
        """
        return self._init_system
    
class SysV:
    """
    A class for running commands on a SysV init system.
    """

    def __init__(self):
        self.run_command = RunCommand()
    
    def get_messages(self, grep: str | None = None) -> list[str]:
        """
        Retrieves the system messages from the /var/log/messages file.

        Args:
            grep (str | None): A regular expression string to filter the log messages. If None, all messages are returned.

        Returns:
            list[str]: A list of log messages from /var/log/messages. If the command fails, an empty list is returned.
        """
        command = ['cat', str(SYSV_MESSAGES_LOG_FILE)]
        result = self.run_command.run(command, suppress_error=True)
        
        if result.exit_code:
            return []

        lines = result.stdout.split('\n')
        if grep:
            pattern = re.compile(grep)
            lines = [line for line in lines if pattern.search(line)]
        
        return lines
    
    def get_boot_log(self, grep: str | None = None) -> list[str]:
        """
        Retrieves the system messages from the /var/log/boot file.

        Args:
            grep (str | None): A regular expression string to filter the log messages. If None, all messages are returned.

        Returns:
            list[str]: A list of boot log messages from /var/log/boot. If the command fails, an empty list is returned.
        """
        command = ['cat', str(SYSV_BOOT_LOG_FILE)]
        result = self.run_command.run(command, suppress_error=True)
        
        if result.exit_code:
            return []

        lines = result.stdout.split('\n')
        if grep:
            pattern = re.compile(grep)
            lines = [line for line in lines if pattern.search(line)]
        
        return lines
        
        
