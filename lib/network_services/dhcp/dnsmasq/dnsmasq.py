from enum import Enum
import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunResult
from lib.network_manager.network_manager import NetworkManager
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DNSmasqConfigurator
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS


class DNSMasqExitCode(Enum):
    """
    Enum class representing DNSMasq exit codes.

    EXIT CODES:
    0 - Dnsmasq successfully forked into the background, or terminated normally if backgrounding is not enabled.
    1 - A problem with configuration was detected.
    2 - A problem with network access occurred (address in use, attempt to use privileged ports without permission).
    3 - A problem occurred with a filesystem operation (missing file/directory, permissions).
    4 - Memory allocation failure.
    5 - Other miscellaneous problem.
    11 or greater - a non-zero return code was received from the lease-script process "init" call or a --conf-script file.
                    The exit code from dnsmasq is the script's exit code with 10 added.
    """

    SUCCESS = 0
    CONFIG_PROBLEM = 1
    NETWORK_ACCESS_PROBLEM = 2
    FILESYSTEM_OPERATION_PROBLEM = 3
    MEMORY_ALLOCATION_FAILURE = 4
    MISC_PROBLEM = 5

    @classmethod
    def from_script_exit_code(cls, script_exit_code):
        """
        Map a script exit code to a DNSMasq exit code.

        Args:
            script_exit_code (int): The script's exit code.

        Returns:
            DNSmasqExitCode: The corresponding DNSMasq exit code.
        """
        if script_exit_code >= 11:
            return cls(script_exit_code - 10)
        else:
            raise ValueError("Invalid DNSMasq exit code")

class DNSMasqService(NetworkManager, DNSmasqConfigurator):
      
    def __init__(self, dhcp_pool_name: str, dhcp_pool_subnet: str, negate=False):
        super().__init__()      
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ_SERVICE)
        
        self.dhcp_pool_name = dhcp_pool_name
        self.dhcp_pool_subnet = dhcp_pool_subnet
        self.negate = negate
        
    def start_dnsmasq(self) -> bool:
        cmd = ['systemctl', 'start', 'dnsmasq']
        cmd_result = self.run(cmd)
        
        if cmd_result.exit_code:
            return STATUS_NOK
        
        return STATUS_OK

    def restart_dnsmasq(self) -> bool:
        cmd = ['systemctl', 'restart', 'dnsmasq']
        cmd_result = self.run(cmd)
        
        if cmd_result.exit_code:
            return STATUS_NOK
        
        return STATUS_OK

    def stop_dnsmasq(self) -> bool:
        cmd = ['systemctl', 'stop', 'dnsmasq']
        cmd_result = self.run(cmd)
        
        if cmd_result.exit_code:
            return STATUS_NOK
        
        return STATUS_OK
        
    
    def add_inet_pool(self, inet_start:str, inet_end:str, inet_subnet:str, lease_time_seconds:int=86400) -> bool:
        return STATUS_OK
    
    def add_reservation(self, hw_address:str, inet_address:str=None) -> bool:
        return STATUS_OK
    
