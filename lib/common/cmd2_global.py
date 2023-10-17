import logging

'''
from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG)
        self.debug = CGS().DEBUG_BRIDGE_CONFIG
'''

class RouterShellLoggingGlobalSettings:
    GLOBAL_DEBUG = True

    CONFIGURE_MODE      = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    SHOW                = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    ROUTERCLI           = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    
    BRIDGE              = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_CONFIG       = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
      
    DHCPD               = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CONFIG         = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    INTERFACE           = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    IF_CONFIG           = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    ROUTE               = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    IP_ROUTE_CONFIG     = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    NAT                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    NAT_CONFIG          = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    VLAN                = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    VLAN_CONFIG         = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    ARP                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ARP_CONFIG          = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    WIRELESS            = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    RUN                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSCTL              = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    INET                = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    MAC                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    PHY                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
class Cmd2GlobalSettings():
    
    DEBUG_GLOBAL = True
    
    DEBUG_BRIDGE_CONFIG = DEBUG_GLOBAL or True
    DEBUG_CONFIGURE_MODE = DEBUG_GLOBAL or True
    '''Add Per Class Debug'''
    