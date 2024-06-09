import logging
from lib.network_manager.nat import Nat


class NatShow(Nat):
    
    def __init__(self, args=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.args = args        

    def getNatTable(self, args=None):
        self.log.debug(f"getNatTable()")
        print(f"{self.getNatIpTable()}")
