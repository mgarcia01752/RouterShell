import logging
from lib.network_manager.arp import Arp


class ArpShow(Arp):
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg        

    def arp(self, args=None):
            self.get_arp()