import argparse
import logging
from typing import List

from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS

class TConfig(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().TEST_DEFAULT)
               
    def tconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
    
    @CmdPrompt.register_sub_commands(sub_cmds=['sub-command'])         
    def tconfig_cmd(self, args: List=None) -> None:
        self.log.debug(f'tconfig_cmd -> {args}')

        parser = argparse.ArgumentParser(
            description="Manage TConfig commands",
            epilog="Supported subcommands:\n"
                   "   sub-command [sub_command_arg]           Description of sub-command\n"
        )

        subparsers = parser.add_subparsers(dest='subcommand')
        sub_command_parser = subparsers.add_parser('sub-command', help='sub-command help')
        sub_command_parser.add_argument('sub_command_arg', type=str, help='Sub Command Arg')

        # Parse the arguments passed to this command
        parsed_args = parser.parse_args(args)

        if parsed_args.subcommand == 'sub-command':
            sub_command_arg = parsed_args.sub_command_arg
            print(f'sub-command: {sub_command_arg}')
            self.log.debug(f'sub-command: {sub_command_arg}')
