import enum
import logging

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK
from lib.db.system_db import SystemDatabase
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.interface import Interface

class Service(enum.Enum):
    START = 'start'
    RESTART = 'restart'
    STOP = 'stop'
    
class SystemService(RunCommand):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_START_UP)

    def control_service(self, service: Service, action: str) -> bool:
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
        # Assuming the actual service name is "hostapd"
        return self.control_service(service, "start")

    def dnsmasq(self, service: Service) -> bool:
        # Assuming the actual service name is "dnsmasq"
        return self.control_service(service, "restart")

class SystemStartUp(Interface):
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_START_UP)
        
        if not self.get_interface_via_db():
            self.update_interface_db_from_os()
            
        self.update_rename_interface_via_os() 

class SystemShutDown(RunCommand):
    
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_START_UP)
        
class SystemReset(Interface):
       
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_RESET)
        
    def database(self):
        '''
        When clearing the database, we need to revert some things back in the OS
        '''
        #Flush interfaces
        Interface().flush_interfaces()
                
        #Revert Interfaces back to the original interface name
        Interface().update_rename_interface_via_os(reverse=True)
            