import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLGS
from lib.db.system_db import SystemDatabase
from lib.network_services.common.network_ports import NetworkPorts
from lib.network_services.telnet.telnet_server import TelnetService
from lib.system.system_call import SystemCall

class System:
    def __init__(self):
        """
        Initialize the System class with logging configuration.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SYSTEM)
    
    def update_hostname(self, hostname: str) -> bool:
        """
        Update the hostname of the system both in the OS and the system database.

        Parameters:
        hostname (str): The new hostname to set.

        Returns:
        bool: STATUS_OK if successful, STATUS_NOK otherwise.
        """
        # Set hostname in the operating system
        if not SystemCall().set_hostname_os(hostname):
            self.log.error(f"Error: Failed to set the hostname: ({hostname}) to OS")
            return STATUS_NOK

        # Set hostname in the system database
        if not SystemDatabase().set_hostname_db(hostname):
            self.log.error(f"Error: Failed to set the hostname: ({hostname}) to DB")
            return STATUS_NOK

        return STATUS_OK

    def update_telnet_server(self, enable: bool = True, port: int = NetworkPorts.TELNET) -> bool:
        """
        Update the Telnet server configuration.

        Args:
            enable (bool): Whether to enable or disable the Telnet server.
            port (int): The port for the Telnet server.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        self.log.debug(f'update_telnet_server() - enable: {enable} -> port: {port}')
        
        if enable:
            if TelnetService().set_port(port):
                self.log.error(f'Unable to update telnet server port: {port} to OS')
                return STATUS_NOK
            
            if TelnetService().restart_service():
                self.log.error(f'Unable to restart telnet server on port: {port}')
                return STATUS_NOK
            
        else:
            if TelnetService().stop_service():
                self.log.error(f'Unable to stop telnet server')
                return STATUS_NOK                

        if SystemDatabase().set_telnet_server_status(enable, port):
            self.log.error(f'Unable to add telnet server status: enable: {enable} and port: {port} to DB')
            return STATUS_NOK
            
        return STATUS_OK
    
    def update_ssh_server(self, enable: bool = True, port: int = NetworkPorts.SSH) -> bool:
        """
        Update the SSH server configuration.

        Args:
            enable (bool): Whether to enable or disable the SSH server.
            port (int): The port for the SSH server.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK otherwise.
        """
        print(f'SSH Server not implemented yet')
        return STATUS_OK
