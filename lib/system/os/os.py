import logging
import platform
from enum import Enum, auto
import shutil

from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

class SupportedOS(Enum):
    BUSY_BOX = auto()
    UBUNTU = auto()
    UNKNOWN = auto()

class OSChecker:
    """
    A class to check if the current operating system is supported.

    Attributes:
        supported_os (set): A set of supported operating systems.

    Methods:
        is_supported() -> bool:
            Checks if the current operating system is supported.

        get_current_os() -> SupportedOS:
            Returns the current operating system as a SupportedOS enum value.
    """
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().OS_CHECKER)
                
        self.supported_os = {
            SupportedOS.BUSY_BOX: "BusyBox",
            SupportedOS.UBUNTU: "Ubuntu"
        }

    def get_current_os(self) -> SupportedOS:
        """
        Get the current operating system as a SupportedOS enum value.

        Returns:
            SupportedOS: The current operating system enum value.
        """
        # Get system information using uname
        uname_info = platform.uname()
        system = uname_info.system
        version = uname_info.version
        release = uname_info.release
        
        self.log.debug(f'System: {system} Version: {version} Release: {release}')

        if system == "Linux":
            
            if shutil.which('busybox'):
                return SupportedOS.BUSY_BOX
            
            elif "Ubuntu" in version or "Ubuntu" in release:
                return SupportedOS.UBUNTU

        return SupportedOS.UNKNOWN

    def is_supported(self) -> bool:
        """
        Check if the current operating system is supported.

        Returns:
            bool: True if the current operating system is supported, False otherwise.
        """
        current_os = self.get_current_os()
        return current_os in self.supported_os
