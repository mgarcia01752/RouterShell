import logging
from lib.network_manager.vlan import Vlan


class VlanShow(Vlan):
    """Command set for showing Vlan-Show-Commands"""

    def __init__(self, command=None, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.command = command
        self.arg = arg
    
    def vlan(self):
        """
        Show VLAN configuration.
        """
        self.get_vlan_info()