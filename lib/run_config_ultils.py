import cmd2
import logging
import argparse

from lib.global_operation import GlobalUserCommand
from lib.router_prompt import ExecMode, RouterPrompt
from lib.constants import *

class InvalidSubCommand(Exception):
    def __init__(self, message):
        super().__init__(message)

class RunConfig(cmd2.Cmd, RouterPrompt):
    """Command set for configuring Run-Config-Commands"""

    def __init__(self, arg):
        super().__init__()
        RouterPrompt.__init__(self,ExecMode.CONFIG_MODE)
        self.log = logging.getLogger(self.__class__.__name__)

        # Set a custom prompt for interface configuration
        self.prompt = self.set_prompt()
        
class RunShow(cmd2.Cmd, RouterPrompt):
    """Command set for configuring Run-Config-Commands"""

    def __init__(self, arg):
        super().__init__()
        RouterPrompt.__init__(self,ExecMode.CONFIG_MODE,'sub')
        self.log = logging.getLogger(self.__class__.__name__)

        # Set a custom prompt for interface configuration
        self.prompt = self.set_prompt()


