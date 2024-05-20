import logging

from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.show.arp_show import ArpShow
from lib.cli.show.bridge_show import BridgeShow
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class Show(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().SHOW_MODE)
                
    def show_help(self, args=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
            
    def show_arp(self, args=None):
        """arp\t\t\tDisplay Address Resolution Protocol (ARP) table."""
        ArpShow().arp(args)
        
    def show_bridge(self, args=None):
        """bridge\t\t\tDisplay information about network bridges."""
        BridgeShow().bridge(args)

    def show_dhcpClient(self, args=None):
        pass