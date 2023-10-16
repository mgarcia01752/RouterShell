import ipaddress
import cmd2
import logging

from lib.cli.global_operation import GlobalUserCommand
from lib.network_manager.mac import MacServiceLayer
from lib.cli.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.arp import Arp
from lib.common.constants import *

class InvalidArpConfig(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class ArpConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Arp):
    
    PROMPT_CMD_ALIAS = "arp"
    
    def __init__(self, arg=None, negate=False):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE)
        Arp.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        
        """START"""
        
        self.log.debug(f"__init__ -> (negate={negate}) -> arg -> {arg}")
        self.arg = arg 
                
        self.prompt = self.set_prompt()

        if arg:
            if negate:
                self.run_command(arg)
            self.run_command(self.arg, negate)
              
    def run_command(self, cli: str, negate=False):
        self.log.debug(f"run_command() -> cli: {cli} -> negate: {negate}")
        self.negate = negate
        
        if not isinstance(cli, list):
            cli = cli.strip().split()
            self.log.debug(f"convert clt to a list: {cli}")
        
        cli = ' '.join([item for item in cli[1:]])       
        
        self.command = cli[0]
        self.log.debug(f"run_command({self.command}) -> {cli}")

        do_method_name = f"do_{self.command}"

        if hasattr(self, do_method_name) and callable(getattr(self, do_method_name)):
            getattr(self, do_method_name)(cli, negate)
        else:
            print(f"Command '{self.command}' not recognized.")

    '''Do not change above this comment'''

    def complete_arp(self, text, line, begidx, endidx):
        completions = ['timeout', 'proxy', 'drop-gratuitous']
        return [comp for comp in completions if comp.startswith(text)]

    def do_arp(self, args, negate=False):
        """
        [no] arp timeout <seconds>
        [no] arp proxy
        [no] arp drop-gratuitous

        """

        self.log.debug(f"do_arp() -> line: {args} -> negate: {negate}")
        
        args_parts = args.strip().split()
        
        if args_parts[0] == 'timeout':
            self.log.debug(f"do_arp(timeout) -> args: {args_parts}")

            if self.set_timeout(args_parts[1]):
                self.log.error(f"Failed to set ARP cache timeout to {args_parts[1]} seconds.")
            else:
                self.log.debug(f"ARP cache timeout set to {args_parts[1]} seconds.")
            pass

        elif args_parts[0] == 'proxy':
            self.log.debug(f"do_arp(proxy) -> args: {args_parts}")
            self.do_proxy(negate)
            pass

        elif args_parts[0] == 'drop-gratuitous':
            self.log.debug(f"do_arp(drop-gratuitous) -> args: {args_parts}")
            self.do_gratuitous(negate)
            pass
        
        else:
            print("Invalid  command {args}")

    def do_timeout(self, arp_time_out:int=300):
        """
        Set the ARP cache timeout using sysctl.

        :param arp_time_out: The ARP cache timeout value in seconds.
        """
        if self.set_timeout(arp_time_out):
            self.log.error(f"Failed to set ARP cache timeout set to {arp_time_out} seconds.")
        else:
            self.log.debug(f"ARP cache timeout to {arp_time_out} seconds.")

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

        if Arp().set_static_arp(inet, mac, ifName, encap, not negate):
            self.log.error(f"Unable to set static-arp: {args}")
            return STATUS_NOK

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
        
        elif start_cmd == 'drop-gratuitous':
            self.log.debug(f"Set drop-gratuitous -> ({line})")
            self.do_gratuitous(negate=True)
            
        else:
            print(f"Invalid command: {line}")

