
import logging
from lib.cli.base.exec_priv_mode import ExecMode

from lib.cli.common.router_prompt import RouterPrompt
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS


class ConfigurePrompt(RouterPrompt):

    def __init__(self, exec_mode: ExecMode = ExecMode.PRIV_MODE, sub_cmd_name: str = 'config'):
        super().__init__(exec_mode, sub_cmd_name)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTERCLI)

        

        