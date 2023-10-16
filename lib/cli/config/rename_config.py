import ipaddress
import cmd2
import logging

from lib.cli.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.interface import Interface
from lib.common.constants import *

class InvalidRouteConfig(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class RenameConfig(cmd2.Cmd, RouterPrompt):
        
    def __init__(self, arg=None, negate=False):
        super().__init__()
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE)
        self.log = logging.getLogger(self.__class__.__name__)
                
        self.log.debug(f"__init__ -> (negate={negate}) -> arg -> {arg}")
        self.arg = arg 
                
        self.prompt = self.set_prompt()

        if negate:
            self.run_command(arg)
        
        self.run_command(self.arg, negate)
        
    def run_command(self, cli: str, negate=False):
        
        self.log.debug(f"run_command() -> cli: {cli} -> negate: {negate}")
        
        if not isinstance(cli, list):
            cli = cli.strip().split()

        start_cmd = cli[0]

        self.log.debug(f"CLI is a list: {cli}")
        cli = ' '.join([item for item in cli[1:]])
        self.log.debug(f"CLI is a flatten?: {cli}")
        
        self.log.debug(f"run_command({start_cmd}) -> {cli}")

        method_name = f"do_{start_cmd}"

        if hasattr(self, method_name) and callable(getattr(self, method_name)):
            getattr(self, method_name)(cli, negate)
        else:
            print(f"Command '{self.command}' not recognized.")

    '''Do not change above this comment'''
            
    def do_if(self, args:str, negate=False) -> bool:
        '''rename if enx3c8cf8f943a2 if-alias [auto|<new-interface-name>]'''
        
        Interface().rename_interface()
