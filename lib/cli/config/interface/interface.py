
import logging
from typing import List

from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class Interface(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().TEST_DEFAULT)
               
    def interface_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        pass
    
    @CmdPrompt.register_sub_commands(sub_cmds=['sub-command'])         
    def interface_cmd(self, args: List=None) -> None:
        self.log.debug(f'test_cmd -> {args}')
        pass
   