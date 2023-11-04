import logging

from lib.network_manager.network_manager import NetworkManager

class Wireless(NetworkManager):
    """Command set for showing Wireless-Commands"""

    def __init__(self, command, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        
    def interface(self, args=None):
        '''
            iw dev
            
            interface_name, addr, txpower, 
        '''
        return False