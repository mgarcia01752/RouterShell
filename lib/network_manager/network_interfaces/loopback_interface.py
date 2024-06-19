import logging

from lib.common.common import Common
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.interface import InterfaceType
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory, NetworkInterface
from lib.network_manager.network_operations.interface import Interface

class LoopbackInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CreateLoopBackNetInterface:
    def __init__(self, loopback_name: str):
        """
        Initialize a CreateLoopBackNetInterface instance to create a loopback network interface.

        Args:
            loopback_name (str): The name of the loopback network interface.

        Raises:
            InvalidNetInterface: If the loopback interface already exists or if creation fails.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS.CREATE_LB_INTERFACE)
        self.loopback_name = loopback_name
        self.interface = Interface()
        self.log.debug(f'Loopback-Name: {loopback_name}')
        
        if Interface().does_os_interface_exist(loopback_name):
            self.log.debug(f'Loopback: {loopback_name} exists')

            if not Interface().db_lookup_interface_exists(loopback_name):
                self.log.debug(f'Loopback: {loopback_name} does not exist in DB...adding')
                Interface().update_interface_db_from_os(loopback_name)
        
        elif not Interface().create_os_dummy_interface(loopback_name):
            self.log.debug(f'Loopback: {loopback_name} didn not exist on OS...Added to OS')
            
            if Interface().add_db_interface_entry(interface_name=loopback_name, ifType=InterfaceType.LOOPBACK):
                raise LoopbackInterfaceError(f"Unable to add {loopback_name} interface db entry.")
        
        else:
            raise LoopbackInterfaceError(f"Unable to create {loopback_name} interface.")
                
        self._net_interface = NetInterfaceFactory(self.loopback_name).get()
    
    def getLoopbackInterface(self) -> 'LoopbackInterface':
        """
        Get a NetInterfaceFactory instance for the created loopback network interface.

        Returns:
            NetInterface: A NetInterface object associated with the created loopback interface.
        """
        self.log.debug(f'getLoopbackInterface() -> Interface: {self._net_interface.get_ifType()}')
        return self._net_interface

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

