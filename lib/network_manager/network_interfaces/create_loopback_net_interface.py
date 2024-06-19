import logging

from lib.network_manager.common.interface import InterfaceType
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_interfaces.loopback_interface import LoopbackInterface
from lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory
from lib.network_manager.network_operations.interface import Interface

class CreateLoopBackNetInterfaceError(Exception):
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
                raise CreateLoopBackNetInterfaceError(f"Unable to add {loopback_name} interface db entry.")
        
        else:
            raise CreateLoopBackNetInterfaceError(f"Unable to create {loopback_name} interface.")
                
        self._net_interface = NetInterfaceFactory(self.loopback_name).get()
    
    def getLoopbackInterface(self) -> LoopbackInterface:
        """
        Get a NetInterfaceFactory instance for the created loopback network interface.

        Returns:
            NetInterface: A NetInterface object associated with the created loopback interface.
        """
        self.log.debug(f'getLoopbackInterface() -> Interface: {self._net_interface.get_ifType()}')
        return self._net_interface