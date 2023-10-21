import logging

'''
TODO ADD TO CLASS
from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG)
        self.debug = CGS().DEBUG_BRIDGE_CONFIG
'''

class RouterShellLoggingGlobalSettings():
    '''
        LOGGING LEVELS: INFO WARN ERROR FATAL
    '''
    
    GLOBAL_DEBUG = False

    ROUTER_SHELL_DB     = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG

    CONFIGURE_MODE      = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SHOW                = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ROUTERCLI           = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    CLEAR_MODE          = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    BRIDGE              = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_DB           = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_CONFIG       = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
      
    DHCPD               = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CONFIG         = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    INTERFACE           = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    IF_CONFIG           = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    ROUTE               = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    IP_ROUTE_CONFIG     = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    NAT                 = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    NAT_DB              = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    NAT_CONFIG          = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    
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
    
    DEBUG_ROUTER_SHELL_DB   = DEBUG_GLOBAL or True
    
    DEBUG_BRIDGE_CONFIG     = DEBUG_GLOBAL or True
    DEBUG_BRIDGE_DB         = DEBUG_GLOBAL or True 
    DEBUG_BRIDGE            = DEBUG_GLOBAL or True
     
    DEBUG_CONFIGURE_MODE    = DEBUG_GLOBAL or True

    DEBUG_IF_CONFIG         = DEBUG_GLOBAL or True
    
    DEBUG_NAT               = DEBUG_GLOBAL or True
    DEBUG_NAT_CONFIG        = DEBUG_GLOBAL or True
    DEBUG_NAT_DB            = DEBUG_GLOBAL or True
    
    DEBUG_RUN               = DEBUG_GLOBAL or True
    DEBUG_SYSCTL            = DEBUG_GLOBAL or True
    '''Add Per Class Debug'''
    