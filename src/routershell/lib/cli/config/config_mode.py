import logging

from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.cli.config.config_cmds import ConfigCmd
from routershell.lib.cli.config.configure_prompt import ConfigurePrompt
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS


class ConfigMode(ConfigurePrompt):

    def __init__(self):
        super().__init__()

        self.register_top_lvl_cmds(ConfigCmd())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_MODE)
        
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            self.log.warning("Config mode is not available in non-privileged mode")
        
    def intro(self) -> str:
        return 'Starting Configuration Mode....'
        
    def help(self):
        return 'No Help'
