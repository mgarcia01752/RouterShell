import os
from typing import Optional
from lib.network_manager.common.run_commands import RunCommand
from enum import Enum

class InitSystem(Enum):
    SYSTEMD = 'systemd'
    SYSV = 'sysv'
    UNKNOWN = 'unknown'

class InitSystemChecker(RunCommand):
    """
    A class to check whether the Linux system is using SysV init or Systemd, implemented as a Singleton.
    """

    _instance: Optional['InitSystemChecker'] = None
    _init_system: Optional[InitSystem] = None

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
            cls._instance = super(InitSystemChecker, cls).__new__(cls, *args, **kwargs)
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
            if os.path.exists('/run/systemd/system'):
                return InitSystem.SYSTEMD
            
            result = self.run(['systemctl', '--version'], suppress_error=True)
            if result.exit_code == 0:
                return InitSystem.SYSTEMD
            
        except FileNotFoundError:
            pass
        
        except Exception as e:
            print(f"An error occurred while checking Systemd: {e}")
        
        return InitSystem.SYSV

    def is_systemd(self) -> bool:
        """
        Checks if the system is using Systemd.

        Returns:
            bool: True if Systemd is in use, False otherwise.
        """
        return self._init_system == InitSystem.SYSTEMD

    def is_sysv(self) -> bool:
        """
        Checks if the system is using SysV init.

        Returns:
            bool: True if SysV is in use, False otherwise.
        """
        return self._init_system == InitSystem.SYSV
    
    def get_system_init(self) -> InitSystem:
        """
        Gets the current init system.

        Returns:
            InitSystem: The enum representing the current init system.
        """
        return self._init_system
