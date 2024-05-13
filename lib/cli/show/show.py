import logging
import inspect


from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.show.arp_show import ArpShow
from lib.cli.show.bridge_show import BridgeShow
from lib.common.common import STATUS_NOK, STATUS_OK, Common
from lib.network_manager.network_mgr import NetworkManager
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class Show():

    def __init__(self) -> None:
        """
        Initializes Global instance.
        """
        self.CLASS_NAME = self.__class__.__name__.lower()

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SHOW_MODE)

    def execute(self, subcommand: str = None) -> None:
        """
        Executes a subcommand.

        Args:
            subcommand (str, optional): Subcommand to execute. Defaults to None.
        """
        if subcommand:
            getattr(self, f"{self.CLASS_NAME}_{subcommand}")()

    def class_methods(self) -> list:
        """
        Get a list of class methods.

        Returns:
            list: List of class methods.
        """
        return [attr for attr in dir(self) if attr.startswith(f'{self.CLASS_NAME}') 
                and inspect.ismethod(getattr(self, attr))]
  
    def get_command_list(self) -> list:
        """
        Get a list of available commands.

        Returns:
            list: List of available commands.
        """
        elements = self.class_methods()
        prefix_length = len(self.CLASS_NAME) + 1
        return [element[prefix_length:] if element.startswith(f"{self.CLASS_NAME}_") else element for element in elements]

    def help(self) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
    def show_arp(self, args=None):
        """arp\t\t\tDisplay ARP table"""
        ArpShow().arp(args)
        
    def show_bridge(self, args=None):
        """bridge\t\t\tShow Bridge"""
        BridgeShow().bridge(args)
    
    def show_bridges(self, args=None):
        """bridge\t\t\tShow Bridges"""
        BridgeShow().show_bridges(args)