import cmd2
import logging

from lib.global_operation import GlobalUserCommand
from lib.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.arp import Arp
from lib.constants import *

class InvalidArpConfig(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class ArpConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Arp):
    
    PROMPT_CMD_ALIAS = "arp"
    
    def __init__(self, args=None):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Arp.__init__(self)
        
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.prompt = self.set_prompt()

    def do_timeout(self, arp_time_out:int=300):
        """
        Set the ARP cache timeout using sysctl.

        :param arp_time_out: The ARP cache timeout value in seconds.
        """
        if self.set_timeout(arp_time_out):
            self.log.debug(f"ARP cache timeout set to {arp_time_out} seconds.")
        else:
            self.log.error(f"Failed to set ARP cache timeout to {arp_time_out} seconds.")

    def do_proxy(self, negate=False) -> bool:
        """
        Enable or disable proxy ARP.

        :param negate: True to disable proxy ARP, False to enable it.
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.set_proxy_arp('all', not negate):
            self.log.error(f"Failed ot set ARP proxy set to {not negate}")
            return STATUS_NOK
        else:
            self.log.debug(f"ARP proxy set to {not negate}")
            return STATUS_OK

    def complete_static(self, text, line, begidx, endidx):
        completions = ['arp']
        return [comp for comp in completions if comp.startswith(text)]

    def do_static(self, args:str, negate=False) -> bool:
        '''
         static <IPv4 Address> <mac address> <interface> arpa
        '''
        parts = args
        
        if not isinstance(args, list):
            parts = args.strip().split()

        if len(parts) != 4:
            self.log.error(f"Invalid Static ARP entries {len(parts)} or 4 entries-> ({args})")
            self.log.error("static <IPv4 Address> <mac address> <interface> arpa")
            return STATUS_NOK
        
        inet, mac, ifName, encap = parts

        Arp().set_static_arp(inet, mac, ifName, encap, not negate)

        return STATUS_OK

    def do_gratuitous(self, negate=False) -> bool:
        """
        Enable or disable Gratuitous ARP.

        :param negate: True to disable proxy ARP, False to enable it.
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.set_drop_gratuitous_arp('all', not negate):
            self.log.error(f"Failed ot set Gratuitous ARP set to {not negate}")
            return STATUS_NOK
        else:
            self.log.debug(f"Gratuitous ARP set to {not negate}")
            return STATUS_OK      

    def complete_no(self, text, line, begidx, endidx):
        completions = ['proxy', 'gratuitous', 'static']
        return [comp for comp in completions if comp.startswith(text)]

    def do_no(self, line:str) -> bool:
        self.log.debug(f"do_no() -> Line -> {line}")
        
        parts = line.strip().split()
        start_cmd = parts[0]
        
        self.log.debug(f"do_no() -> Start-CMD -> {start_cmd}")
        
        if start_cmd == 'proxy':
            self.log.debug(f"Set proxy-arp -> ({line})")
            self.do_proxy(negate=True)
        
        elif start_cmd == 'gratuitous':
            self.log.debug(f"Set gratuitous-arp -> ({line})")
            self.do_gratuitous(negate=True)
            
        elif start_cmd == 'static':
            static_arp_args = parts[1:]
            self.log.debug(f"Delete static-arp -> ({static_arp_args})")
            self.do_static(static_arp_args, negate=True)
        
class ArpShow(Arp):
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg        

    def arp(self, args=None):
            self.get_arp()
