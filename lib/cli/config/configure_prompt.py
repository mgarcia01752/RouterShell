import logging
from lib.cli.common.exec_priv_mode import ExecMode

from lib.cli.common.router_prompt import RouterPrompt
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

class ConfigurePrompt(RouterPrompt):

    def __init__(self, exec_mode: ExecMode = ExecMode.CONFIG_MODE, sub_cmd_name: str = None):
        RouterPrompt.__init__(self, exec_mode, sub_cmd_name=sub_cmd_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_PROMPT)
        