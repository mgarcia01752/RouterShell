import logging
import cmd2
from lib.cli.exec_priv_mode import ExecMode

from lib.cli.router_prompt import RouterPrompt


class RunShow(cmd2.Cmd, RouterPrompt):
    """Command set for configuring Run-Config-Commands"""

    def __init__(self, arg):
        super().__init__()
        RouterPrompt.__init__(self,ExecMode.CONFIG_MODE,'sub')
        self.log = logging.getLogger(self.__class__.__name__)

        # Set a custom prompt for interface configuration
        self.prompt = self.set_prompt()