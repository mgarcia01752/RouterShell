import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_manager import NetworkManager
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DNSMasqConfigurator
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS

class DNSMasqService(NetworkManager, DNSMasqConfigurator):
      
    def __init__(self, dhcp_pool_name: str, ip_subnet_mask: str, negate=False):
        super().__init__()      
        self.log = logging.getLogger(self.__class__.__name)
        self.log.setLevel(RSLGS().DNSMASQ_SERVICE)
        
    def start(self):
        start_command = ['systemctl', 'start', 'dnsmasq']
        return self.run(start_command)

    def restart(self):
        restart_command = ['systemctl', 'restart', 'dnsmasq']
        return self.run(restart_command)

    def stop(self):
        stop_command = ['systemctl', 'stop', 'dnsmasq']
        return self.run(stop_command)
