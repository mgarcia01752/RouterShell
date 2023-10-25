import logging

'''
TODO ADD TO CLASS
from lib.cli.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

        self.log.setLevel(RSLGS().BRIDGE_CONFIG)

'''

class RouterShellLoggingGlobalSettings():
    '''
        LOGGING LEVELS: INFO WARN ERROR FATAL CRITICAL
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
    
    INTERFACE           = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    INTERFACE_DB        = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    
    IF_CONFIG           = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    IF_CONFIG_DB        = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG
    
    ROUTE               = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    IP_ROUTE_CONFIG     = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    NAT                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    NAT_DB              = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    NAT_CONFIG          = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    VLAN                = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    VLAN_CONFIG         = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    ARP                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ARP_CONFIG          = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    WIRELESS            = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    INET                = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    MAC                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    PHY                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    RUN                 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSCTL              = logging.DEBUG if GLOBAL_DEBUG else logging.INFO