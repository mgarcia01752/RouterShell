import logging
from typing import List

from lib.network_manager.network_operations.arp import Arp


class ArpShow(Arp):
    """
    A class used to represent the ArpShow, which is a specialized extension of the Arp class.

    Attributes
    ----------
    log : logging.Logger
        a logger instance to log information specific to this class
    arg : any
        an optional argument that can be passed during the initialization of the class

    Methods
    -------
    arp(args: List=None)
        Calls the get_arp method from the parent Arp class to perform an ARP (Address Resolution Protocol) action.
    """

    def __init__(self, arg=None):
        """
        Initializes the ArpShow class, setting up the logger and storing the optional argument.

        Parameters
        ----------
        arg : any, optional
            An optional argument that can be passed during initialization (default is None)
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg        

    def arp(self, args: List=None):
        """
        Executes the ARP (Address Resolution Protocol) action by calling the get_arp method from the parent Arp class.

        Parameters
        ----------
        args : List, optional
            A list of arguments that can be passed to the ARP method (default is None)
        """
        self.get_arp()
