import logging


from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_services.dhcp.dnsmasq.dnsmasq import DnsmasqFactory

from lib.common.common import STATUS_NOK, STATUS_OK


class DHCPServerService(DnsmasqFactory):

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_SERVER_SERVICE)
    
    def start(self):
        return STATUS_OK
    
    def restart(self):
        return STATUS_OK
    
    def stop(self):
        return STATUS_OK
    
    
    