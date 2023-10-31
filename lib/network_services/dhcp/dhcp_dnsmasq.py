
import logging
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_services.dhcp.common.dhcp_service_abstract import DHCPServerAbstract


class DnsmasqFactory(DHCPServerAbstract):
      
    def __init__(self, dhcp_pool_name: str, ip_subnet_mask: str, negate=False):        
        self.log = logging.getLogger(self.__class__.__name__)

