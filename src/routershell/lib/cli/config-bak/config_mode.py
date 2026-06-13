import logging
from routershell.lib.cli.base.global_cmd_op import Global
from routershell.lib.cli.config.configure_prompt import ConfigurePrompt
from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS


class ConfigMode(ConfigurePrompt):

    def __init__(self):
        super().__init__()

        self.register_top_lvl_cmds(Global())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_PROMPT)
    
    def intro(self) -> str:
        return f'Starting Configuration Mode....'
        
    def help(self):
        return 'No Help'
      
