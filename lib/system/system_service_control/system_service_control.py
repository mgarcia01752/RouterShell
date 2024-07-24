import enum
import logging
from typing import List

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunCommand
from lib.system.init_system import InitSystem, InitSystemChecker
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS

class SysServCntrlAction(enum.Enum):
    """
    Enumeration for system service actions.
    """
    START = 'start'
    RESTART = 'restart'
    STOP = 'stop'
    STATUS = 'status'

class SystemServiceControl(RunCommand):
    
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM_SERVICE_CTRL)
        
        self.init_system = InitSystemChecker().get_init_system()

    def service_control(self, service_name: str, service_action: SysServCntrlAction) -> bool:
        """
        Controls a system service using the appropriate init system.

        Args:
            service_name (str): The name of the service to control.
            service_action (SysServCntrlAction): The action to perform on the service.

        Returns:
            bool: STATUS_OK if the command succeeds, STATUS_NOK otherwise.
        """
        if not service_name:
            self.log.error('Service name is not defined')
            return STATUS_NOK
        
        command = self._init_system_control(service_name, service_action)

        if not command:
            self.log.error('Service control command is not defined')
            return STATUS_NOK
        
        result = self.run(command)
        
        if result.exit_code:
            self.log.error(f"Failed to {service_action.value} service {service_name}. Exit code: {result.exit_code}")
            return STATUS_NOK

        self.log.debug(f"Service {service_name} {service_action.value}ed successfully.")
        return STATUS_OK

    def _init_system_control(self, service_name: str, service_action: SysServCntrlAction) -> List[str]:
        """
        Constructs the appropriate command for the current init system.

        Args:
            service_name (str): The name of the service to control.
            service_action (SysServCntrlAction): The action to perform on the service.

        Returns:
            List[str]: The command to run.
        """
        if self.init_system == InitSystem.SYSV:
            return ['service', service_name, service_action.value]
        elif self.init_system == InitSystem.SYSTEMD:
            return ['systemctl', service_action.value, service_name]
        else:
            self.log.error(f"Unsupported init system: {self.init_system}")
            return []