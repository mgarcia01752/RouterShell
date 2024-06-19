import enum
import logging

from lib.cli.base.copy_start_run import CopyStartRun
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunCommand
from lib.db.sqlite_db.router_shell_db import RouterShellDB
from lib.network_manager.network_operations.interface import Interface
from lib.system.system_call import SystemCall

class Service(enum.Enum):
    """
    Enumeration for system service actions.
    """
    START = 'start'
    RESTART = 'restart'
    STOP = 'stop'

class SystemService(RunCommand):
    """
    Class for controlling system services.
    
    Inherits from RunCommand.
    """
    def __init__(self):
        """
        Initializes the SystemService class.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_START_UP)

    def control_service(self, service: Service, action: str) -> bool:
        """
        Controls the specified system service.

        Args:
            service (Service): The service to control.
            action (str): The action to perform on the service.

        Returns:
            bool: True if the action was successful, False otherwise.
        """
        service_name = None

        if service == Service.START:
            service_name = "hostapd"
        elif service == Service.RESTART:
            service_name = "hostapd"
            action = "restart"
        elif service == Service.STOP:
            service_name = "dnsmasq"

        if service_name is None:
            self.log.error("Unknown service type")
            return STATUS_NOK

        command = ["sudo", "service", service_name, action]

        if self.run(command).exit_code:
            return STATUS_NOK

        self.log.debug(f"Service {service_name} {action}ed successfully.")

        return STATUS_OK

    def hostapd(self, service: Service) -> bool:
        """
        Controls the 'hostapd' service.

        Args:
            service (Service): The action to perform on the service.

        Returns:
            bool: True if the action was successful, False otherwise.
        """
        # Assuming the actual service name is "hostapd"
        return self.control_service(service, "start")

    def dnsmasq(self, service: Service) -> bool:
        """
        Controls the 'dnsmasq' service.

        Args:
            service (Service): The action to perform on the service.

        Returns:
            bool: True if the action was successful, False otherwise.
        """
        # Assuming the actual service name is "dnsmasq"
        return self.control_service(service, "restart")

class SystemStartUp(Interface):
    """
    Class for managing system startup procedures.

    Inherits from Interface.
    """
    def __init__(self):
        """
        Initializes the SystemStartUp class.
        """
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_START_UP)

        if not self.fetch_db_interface_names():
            self.update_interface_db_from_os()
            
        self.set_os_rename_interface()
        
        self.log.debug('Loading........')
        CopyStartRun().read_start_config()
            
class SystemShutDown(RunCommand):    
    """
    Class for managing system shutdown procedures.

    Inherits from RunCommand.
    """
    def __init__(self):
        """
        Initializes the SystemShutDown class.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_START_UP)
        
class SystemReset(Interface):
    """
    Class for resetting system settings.

    Inherits from Interface.
    """
    def __init__(self):
        """
        Initializes the SystemReset class.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_RESET)
        
    def database(self):
        """
        Resets the system database.

        Reverts some settings in the OS when clearing the database.
        """
        # Flush interfaces
        Interface().flush_interfaces()
                
        # Revert Interfaces back to the original interface name
        Interface().set_os_rename_interface(reverse=True)

class SystemFactoryReset():
    def __init__(self):
        """
        Initializes the SystemFactoryReset class.
        """
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_INIT)

        RouterShellDB().reset_database()
        
        #Build Initial DB Entries based on Interface found on system
        Interface().update_interface_db_from_os()
        
        #Take factory-startup-config and configure router    
        CopyStartRun().read_start_config('factory-startup.cfg')