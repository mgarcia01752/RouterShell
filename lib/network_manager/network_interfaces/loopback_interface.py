import logging
from optparse import Option

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

    def __init__(self, loopback_name: str) -> None:
        """
        Initializes a LoopbackInterface instance.

        Args:
            interface_name (str): The name of the loopback interface.
        """
        super().__init__(interface_name=loopback_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS.LOOPBACK_INTERFACE)
        self._127_inet_address = None
        
        if not Interface().does_os_interface_exist(loopback_name):
            self.log.info(f'Adding loopback: {loopback_name} to system')

            if Interface().update_interface_loopback_inet(loopback_name, inet_address_cidr=None):
                self.log.info(f"Loopback: {loopback_name} created successfully.")
            
            if self.set_description(f'Auto Assigned Loopback Address: {self._127_inet_address}'):
                self.log.error(f'Failed to set description for Loopback: {loopback_name}')
            
        else:
            self.log.debug(f'Loopback: {loopback_name} already exists')
        

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

    def auto_inet_127_loopback(self) -> bool:
        """
        Automatically assign the next available 127.x.x.x address to the loopback interface.

        If the loopback interface does not have an assigned 127.x.x.x address,
        this method will find the next available address in the 127.x.x.x range
        and assign it to the loopback interface.

        Returns:
            bool: STATUS_OK if the address was successfully assigned, STATUS_NOK otherwise.
        """
        if not self._127_inet_address:
            next_available_127 = Interface().get_next_loopback_address()

            if not next_available_127:
                self.log.error('Unable to determine the next available 127.x.x.x address.')
                return STATUS_NOK

            if Interface().set_inet_address_loopback(self.interface_name, next_available_127):
                self.log.error(f'Unable to auto-assign: {next_available_127} to loopback: {self.get_interface_name()}')
                return STATUS_NOK

            self.log.debug(f'Auto Assign: {next_available_127} to loopback: {self.get_interface_name()} to OS')
            self._127_inet_address = next_available_127

        return STATUS_OK

    
    def add_inet_address(self, inet_address_cidr:str, secondary_address:bool=False, negate:bool=False) -> bool:
        return STATUS_OK
