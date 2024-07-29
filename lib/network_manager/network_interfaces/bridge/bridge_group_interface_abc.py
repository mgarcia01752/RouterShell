from abc import ABC
import logging

from lib.network_manager.network_operations.bridge import Bridge

class BridgeGroup(ABC):
    """
    Abstract base class representing a bridge group for network interfaces.
    
    This class provides methods to set and delete bridge groups for a specified network interface.
    """

    def __init__(self, interface_name: str):
        """
        Initializes the BridgeGroup with a network interface name.

        Args:
            interface_name (str): The name of the network interface.
        """
        self._interface_name = interface_name
        self.log = logging.getLogger(self.__class__.__name__)
    
    def set_bridge_group(self, bridge_group: str) -> bool:
        """
        Adds the network interface to the specified bridge group.

        Args:
            bridge_group (str): The name of the bridge group to add the interface to.

        Returns:
            bool: STATUS_OK if the interface was successfully added to the bridge group,
                  STATUS_NOK otherwise.
        """
        return Bridge().add_interface_to_bridge_group(self._interface_name, bridge_group)
    
    def del_bridge_group(self, bridge_group: str) -> bool:
        """
        Removes the network interface from the specified bridge group.

        Args:
            bridge_group (str): The name of the bridge group to remove the interface from.

        Returns:
            bool: STATUS_OK if the interface was successfully removed from the bridge group,
                  STATUS_NOK otherwise.
        """
        return Bridge().del_interface_to_bridge_group(self._interface_name, bridge_group)
