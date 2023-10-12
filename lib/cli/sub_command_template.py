import argparse
import cmd2
import logging

from lib.cli.global_operation import GlobalUserCommand
from lib.cli.router_prompt import RouterPrompt, ExecMode

from lib.common.constants import *

class InvalidSub(Exception):
    def __init__(self, message):
        super().__init__(message)

class SubConfig(cmd2.Cmd, 
                GlobalUserCommand, 
                RouterPrompt):
    
    PROMPT_CMD_ALIAS = 'sub'
    
    def __init__(self, args: str):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.log.info(f"SubConfig() -> {args}")
        
    def complete_sub(self, text, line, begidx, endidx):
        completions = ['sub-1', 'sub-2']
        completions.extend(['sub-3-1', 'sub-3-2'])
        return [comp for comp in completions if comp.startswith(text)]
            
    def do_sub(self, args, negate=False):
        self.log.info(f"do_sub() -> args: {args} -> negate: {negate}")

        parser = argparse.ArgumentParser(
            description="Configure Sub commands",
            epilog="Available suboptions:\n"
                    "   sub-1 <sub1>                        Set sub-1\n"
                    "   sub-2 <sub2>                        Set sub-2\n"
                    "   sub-3-1 <sub3.1> sub-3-2 <sub3.2>    Set sub-3.1 and sub-3.2\n"
                    "\n"
                    "Use <suboption> --help to get help for specific suboptions."
        )
        
        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)       
        except SystemExit:
            return

        if args.subcommand == "sub-1":
            # Handle sub-1 command here
            pass
        elif args.subcommand == "sub-2":
            # Handle sub-2 command here
            pass
        elif args.subcommand == "sub-3-1":
            # Handle sub-3-1 command here
            pass
        elif args.subcommand == "sub-3-2":
            # Handle sub-3-2 command here
            pass
        else:
            print("Invalid subcommand")


