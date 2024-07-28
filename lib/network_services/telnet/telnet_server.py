import logging
from typing import Optional
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunCommand
from lib.network_services.common.network_ports import NetworkPorts
from lib.system.init_system import InitSystemChecker, InitSystem
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLGS

class TelnetService(RunCommand):
    """
    A class to manage the Telnet service using either SysV init system or Systemd.

    Attributes:
        port (int): The port number on which the Telnet service listens.
        telnet_config_file (Optional[str]): Path to the Telnet configuration file for SysV init.
        init_system (InitSystem): The init system in use (SysV or Systemd).
    """
    
    _instance: Optional['TelnetService'] = None
    init_system: InitSystem
    port: int
    telnet_config_file: Optional[str] = None

    def __new__(cls, *args, **kwargs) -> 'TelnetService':
        if cls._instance is None:
            cls._instance = super(TelnetService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self, port: int = NetworkPorts.TELNET) -> None:
        """
        Initializes the TelnetService with the specified port.

        Args:
            port (int): The port number for the Telnet service. Default is 23.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().TELNET_SERVER)
        
        self.init_system = InitSystemChecker().get_init_system()
        self.port = port
        
        # Set configuration file path based on init system
        if self.init_system == InitSystem.SYSV:
            self.telnet_config_file = '/etc/xinetd.d/telnet'
        else:
            self.telnet_config_file = None  # For Systemd, config management might differ

    def set_port(self, port: int) -> bool:
        """
        Sets a new port for the Telnet service and updates the configuration.

        Args:
            port (int): The new port number for the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, False otherwise.
        """
        self.log.debug(f'set_port() -> {port}')
        self.port = port
        
        if self.init_system == InitSystem.SYSV:
            return self.update_telnet_config()
        
        # For Systemd, port configuration might be managed differently
        return STATUS_OK
    
    def set_timeout(self, timeout: int=60) -> bool:
        '''timeout in seconds if no login is achived'''
        return STATUS_OK
    
    def set_max_login_attempts(self, max_attemps: int=3) -> bool:
        '''max login attempts the restart login'''
        return STATUS_OK
    
    def set_max_concurrent_users(self, max_users: int=5) -> bool:
        '''max concurrent users'''
        return STATUS_OK

    def update_telnet_config(self) -> bool:
        """
        Updates the Telnet configuration file with the new port and restarts the service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.telnet_config_file:
            try:
                with open(self.telnet_config_file, 'r') as file:
                    lines = file.readlines()
                
                with open(self.telnet_config_file, 'w') as file:
                    for line in lines:
                        if line.strip().startswith('port ='):
                            self.log.debug(f'Overwriting port to {self.port}')
                            file.write(f'port = {self.port}\n')
                        else:
                            file.write(line)
                            
                return self.restart_service()
            
            except IOError as e:
                self.log.error(f"An error occurred while updating the config file: {e}")
                return STATUS_NOK
            
        return STATUS_OK

    def start_service(self) -> bool:
        """
        Starts the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            rtn = self.run(['service', 'xinetd', 'start'])
            if rtn.exit_code:
                self.log.error(f'Unable to start telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        elif self.init_system == InitSystem.SYSTEMD:
            rtn = self.run(['systemctl', 'start', 'telnet.service'])
            if rtn.exit_code:
                self.log.error(f'Unable to start telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
        
        self.log.debug(f'Telnet-Server-Start message: {rtn.stdout}')
        
        return STATUS_OK

    def stop_service(self) -> bool:
        """
        Stops the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            rtn = self.run(['service', 'xinetd', 'stop'])
            if rtn.exit_code:
                self.log.error(f'Unable to stop telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        elif self.init_system == InitSystem.SYSTEMD:
            rtn = self.run(['systemctl', 'stop', 'telnet.service'])
            if rtn.exit_code:
                self.log.error(f'Unable to stop telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
        
        self.log.debug(f'Telnet-Server-Stop message: {rtn.stdout}')
            
        return STATUS_OK

    def restart_service(self) -> bool:
        """
        Restarts the Telnet service.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            rtn = self.run(['service', 'xinetd', 'restart'])
            if rtn.exit_code:
                self.log.error(f'Unable to restart telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        elif self.init_system == InitSystem.SYSTEMD:
            rtn = self.run(['systemctl', 'restart', 'telnet.service'])
            if rtn.exit_code:
                self.log.error(f'Unable to restart telnet server service, reason: {rtn.stderr}')
                return STATUS_NOK
            
        self.log.debug(f'Telnet-Server-Restart message: {rtn.stdout}')
            
        return STATUS_OK

    def status_service(self) -> bool:
        """
        Checks the status of the Telnet service.

        Returns:
            bool: True if the service status check was successful, False otherwise.
        """
        if self.init_system == InitSystem.SYSV:
            result = self.run(['service', 'xinetd', 'status'])
        
        elif self.init_system == InitSystem.SYSTEMD:
            result = self.run(['systemctl', 'status', 'telnet.service'])
            
        else:
            self.log.error('Unsupported init system')
            return STATUS_NOK

        if result.exit_code:
            self.log.error(f'Unable to get status of telnet server service, reason: {result.stderr}')
            return STATUS_NOK

        self.log.debug(f'Telnet service status: {result.stdout}')
        return STATUS_OK
