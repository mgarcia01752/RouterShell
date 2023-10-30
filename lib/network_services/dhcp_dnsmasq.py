
import ipaddress
import logging
from lib.common.constants import STATUS_NOK, STATUS_OK


class DnsmasqFactory():  
    def __init__(self, dhcp_pool_name: str, ip_subnet_mask: str, negate=False):        
        self.log = logging.getLogger(self.__class__.__name__)

