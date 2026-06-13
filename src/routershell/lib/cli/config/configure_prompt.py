import logging

from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.cli.common.router_prompt import RouterPrompt
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import CommandName


class ConfigurePrompt(RouterPrompt):

    def __init__(self, exec_mode: ExecMode = ExecMode.CONFIG_MODE, sub_cmd_name: CommandName | None = None):
        RouterPrompt.__init__(self, exec_mode, sub_cmd_name=sub_cmd_name)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_PROMPT)
        