import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.common.run_commands import RunResult
from lib.network_manager.network_manager import NetworkManager
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DNSMasqConfigurator
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS

class DNSMasqService(NetworkManager, DNSMasqConfigurator):
      
    def __init__(self, dhcp_pool_name: str, dhcp_pool_subnet: str, negate=False):
        super().__init__()      
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ_SERVICE)
        
        self.dhcp_pool_name = dhcp_pool_name
        self.dhcp_pool_subnet = dhcp_pool_subnet
        self.negate = negate
        
    def start_dnsmasq(self) -> bool:
        start_command = ['systemctl', 'start', 'dnsmasq']
        return self.run(start_command)

    def restart_dnsmasq(self) -> bool:
        restart_command = ['systemctl', 'restart', 'dnsmasq']
        return self.run(restart_command)

    def stop_dnsmasq(self) -> bool:
        stop_command = ['systemctl', 'stop', 'dnsmasq']
        return self.run(stop_command)
    
    
