
import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_services.dhcp.common.dhcp_service_abstract import DHCPServerAbstract
from lib.network_services.dhcp.dnsmasq.dnsmasq_config_gen import DnsmasqConfigurator
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class DnsmasqFactory(DHCPServerAbstract, DnsmasqConfigurator):
      
    def __init__(self, dhcp_pool_name: str, ip_subnet_mask: str, negate=False):        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DNSMASQ)

