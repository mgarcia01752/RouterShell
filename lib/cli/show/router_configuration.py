import logging
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class RouterConfiguration():

    def __init__(self, args=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTER_CONFIG)
    
    def copy_running_configuration_to_statup_configuration(self, args=None):
        pass
    
    def show_running_configuration(self, args=None):
        
        '''Global'''
        
        '''Global-NAT'''
        
        '''Global-VLAN'''
        
        '''INTERFACE'''
        
        '''INTERFACE-LOOPBACK'''
        
        '''INTERFACE-ETHERNET'''
        
        '''INTERFACE-WIFI'''
        
        '''ACCESS-CONTROL-LIST'''
        
        
