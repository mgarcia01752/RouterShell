import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_interfaces.network_interface import NetworkInterface
from lib.network_manager.network_operations.interface import Interface

class LoopbackInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class LoopbackInterface(NetworkInterface):
    """
    Class for managing loopback interfaces.

    Attributes:
        interface_name (str): The name of the loopback interface.
        log (Logger): Logger instance for the class.
    """

    def __init__(self, loopback_name: str):
        """
        Initializes a LoopbackInterface instance.

        Args:
            interface_name (str): The name of the loopback interface.
        """
        super().__init__(interface_name=loopback_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS.LOOPBACK_INTERFACE)

    def destroy(self) -> bool:
        """
        Destroys the loopback interface by removing its database entry and 
        deleting the OS-level dummy interface.

        Returns:
            bool: STATUS_OK if the loopback interface was successfully destroyed,
                  STATUS_NOK otherwise.
        """
        if Interface().del_db_interface(self.interface_name):
            self.log.error(f'Failed to delete interface {self.interface_name} from database')
            return STATUS_NOK
        
        if Interface().destroy_os_dummy_interface(self.interface_name):
            self.log.error(f'Failed to delete interface {self.interface_name} from OS')
            return STATUS_NOK
        
        return STATUS_OK

    def add_inet_address(self, inet_address, secondary_address:bool=False, negate:bool=False) -> bool:
        
        Interface().set_inet_address()
        
        return STATUS_OK
