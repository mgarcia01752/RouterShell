
class Cmd2GlobalSettings():
    
    DEBUG_GLOBAL = True
    
    DEBUG_ROUTER_SHELL_DB   = DEBUG_GLOBAL or True
    
    DEBUG_BRIDGE_CONFIG     = DEBUG_GLOBAL or True
    DEBUG_BRIDGE_DB         = DEBUG_GLOBAL or True 
    DEBUG_BRIDGE            = DEBUG_GLOBAL or True
     
    DEBUG_CONFIGURE_MODE    = DEBUG_GLOBAL or True

    DEBUG_IF_CONFIG         = DEBUG_GLOBAL or True
    DEBUG_INTERFACE_DB      = DEBUG_GLOBAL or True
    
    DEBUG_WIFI_CONFIG       = DEBUG_GLOBAL or True
    
    DEBUG_NAT               = DEBUG_GLOBAL or True
    DEBUG_NAT_CONFIG        = DEBUG_GLOBAL or True
    DEBUG_NAT_DB            = DEBUG_GLOBAL or True
    
    DEBUG_RUN               = DEBUG_GLOBAL or True
    DEBUG_SYSCTL            = DEBUG_GLOBAL or True
    
    DEBUG_SHOW_INTERFACE    = DEBUG_GLOBAL or True
    
    '''Add Per Class Debug'''
    