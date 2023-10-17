import ipaddress
import cmd2
import logging

from tabulate import tabulate

from lib.cli.global.global_operation import GlobalUserCommand
from lib.common.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.route import Route
from lib.common.common import Common
from lib.common.constants import *

class InvalidRouteConfig(Exception):
    def __init__(self, message):
        super().__init__(message)
        
class IpRouteConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Route):
    
    PROMPT_CMD_ALIAS="route"
    CLI_PREFIX_CMD = ['ip', 'route']
    
    def __init__(self, arg=None, negate=False):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE)
        Route.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        
        """START"""
        
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
            # Pass the entire command line to the do_route method as a string
            getattr(self, method_name)(cli, negate)
        else:
            print(f"Command '{self.command}' not recognized.")

    '''Do not change above this comment'''

    def do_help(self):
        print("classless")
        print("ip")
        print("ipv6")
            
    def do_classless(self, negate=False) -> bool:
        '''usage: no classless disable classless routeing'''
        
        if self.set_classless_routing(not negate):
            self.log.error(f"Unable to set IP Forwarding, classless Routing to {not negate}")
            return STATUS_NOK
        return STATUS_OK

    def complete_route(self, text, line, begidx, endidx):
        completions = ['metric', 'via']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_route(self, args: str, negate=False) -> bool:
        '''usage: [no] [ip|ipv6] route <destination>/<mask> <next-hop> <metric>'''
        
        do_route_min_arg = 3
                    
        self.log.debug(f"do_route() -> {args}")

        cli_parts = args
            
        try:
            if not isinstance(args, list):
                cli_parts = args.strip().split()    
        except SystemExit:
            return

        if len(cli_parts) < do_route_min_arg:
            self.log.error(f"Not enough arguments for route -> arg-len: {len(cli_parts)} -> ({do_route_min_arg} args needed) -> {args}")
            return STATUS_NOK

        dest_inet_mask, next_hop, metric = cli_parts

        # Try to split the destination and mask
        dest_parts = dest_inet_mask.split('/')
        if len(dest_parts) != 2:
            self.log.error(f"Invalid destination format: {dest_inet_mask}")
            return STATUS_NOK

        dest_address, dest_mask = dest_parts

        # Try to validate the destination IP address and mask
        try:
            dest_network = ipaddress.IPv4Network(dest_inet_mask, strict=False)
        except ValueError:
            self.log.error(f"Invalid destination network address: {dest_inet_mask}")
            return STATUS_NOK

        # Try to validate the next_hop IP address
        try:
            next_hop = ipaddress.IPv4Address(next_hop)
        except ValueError:
            self.log.error(f"Invalid next hop: {next_hop}")
            return STATUS_NOK

        self.log.debug(f"{dest_network} | {next_hop} | {metric}")

        # Call the add_route function with the parsed arguments
        if self.add_route(str(dest_address) + '/' + dest_mask, str(next_hop), metric, negate):
            self.log.error(f"Unable to add route -> {args}")
            return STATUS_NOK
        
        return True

    def complete_ip(self, text, line, begidx, endidx):
        completions = ['classless', 'route']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_ip(self, args:str, negate=False) -> bool:
        
        self.log.debug(f"do_ip() -> line: {args}")
        args_parts = args.strip().split()
        
        if args_parts[0] == 'route':
            self.log.debug(f"do_ip() -> do_route() -> args: {args_parts}")    
            self.do_route(args_parts[1:], negate)
        
        elif args_parts[0] == 'classless':    
            self.do_route(args, negate)
        
        else:
            print(f"Invalid command: {args}")

    def complete_no(self, text, line, begidx, endidx):
        completions = ['ip', 'ipv6']
        return [comp for comp in completions if comp.startswith(text)]
    
    def do_no(self, line):
        self.log.debug(f"do_no() -> line: {line}")
        self.run_command(line, negate=True)
        
    
