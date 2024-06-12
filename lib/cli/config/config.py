import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.config.config_mode import ConfigMode
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class Configure(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CONFIGURE_MODE)
               
    def configure_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        pass
    
    @CmdPrompt.register_sub_commands()
    def configure_terminal(self, args: List) -> bool:
        self.log.debug(f'Entering into configure mode')
        ConfigMode().start()
        return STATUS_OK
