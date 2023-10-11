import logging

from lib.network_manager.network_manager import NetworkManager

class WirelessShow(NetworkManager):
    """Command set for showing NetworkManager-Show-Commands"""

    def __init__(self, command, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        
    def interface(self, args=None):
        '''
            iw dev
            
            interface_name, addr, txpower, 
        '''
        return False