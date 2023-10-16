import logging
from lib.network_manager.interface import Interface


class InterfaceShow(Interface):
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg
        
    def interfaces(self, args=None):
        self.get_interfaces()     