import logging


from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_services.dhcp.dnsmasq.dnsmasq import DNSMasqService

from lib.common.common import STATUS_NOK, STATUS_OK


class DHCPServerService(DNSMasqService):

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_SERVER_SERVICE)
    
    def start(self):
        return self.start_dnsmasq()
    
    def restart(self):
        return self.restart_dnsmasq()
    
    def stop(self):
        return self.stop_dnsmasq()
    
    
    