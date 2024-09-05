import logging
from typing import Dict, Union

from lib.network_manager.common.interface import InterfaceType
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS
from lib.network_manager.network_interfaces.loopback_interface import LoopbackInterface
from lib.network_manager.network_interfaces.network_interface_factory import NetInterfaceFactory
from lib.network_manager.network_operations.interface import Interface

class CreateLoopBackNetInterfaceError(Exception):
    def __init__(self, message):
        super().__init__(message)

class CreateLoopBackNetInterface:
    
    # Singleton {'interface_name': LoopbackInterface}
    _loopback_net_interface_obj_dict: Dict[str, LoopbackInterface] = {}

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
        self.log.setLevel(RSLS.CREATE_LB_INTERFACE)
        self.loopback_name = loopback_name
        self.interface = Interface()
        self.log.debug(f'Loopback-Name: {loopback_name}')
        
        if Interface().does_os_interface_exist(loopback_name):
            
            if Interface().does_db_interface_exist(loopback_name):
                
                #If both exists, that mean we added it either at start-up or run-time
                if not self.loopback_name in CreateLoopBackNetInterface._loopback_net_interface_obj_dict:
                    self.log.error(f'Interface: {self.loopback_name} not found in NetInterface dict Object')
                
        else:
            self.log.debug(f'Adding Loopback: {loopback_name} to OS')
            ni = NetInterfaceFactory(self.loopback_name, InterfaceType.LOOPBACK).getNetInterface(self.loopback_name)            
            
            if ni.auto_inet_127_loopback():
                self.log.error(f'Unable to auto-assign 127 subnet to looopback: {self.loopback_name}')
            
            ni.set_description(f'Auto Assign loopback')
            CreateLoopBackNetInterface._loopback_net_interface_obj_dict[self.loopback_name] = ni
    
    def getLoopbackInterface(self, loopback_name:str) -> LoopbackInterface:
        """
        Get a NetInterfaceFactory instance for the created loopback network interface.

        Returns:
            NetInterface: A NetInterface object associated with the created loopback interface.
        """
        self.log.debug(f'getLoopbackInterface() -> Interface: {loopback_name}')
        return CreateLoopBackNetInterface._loopback_net_interface_obj_dict[loopback_name]