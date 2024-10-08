import logging
from typing import List
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.template.template_config import TemplateConfig
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

class TemplateConfigCmdError(Exception):
    """Custom exception for TestConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'TemplateConfigCmdError: {self.message}'
   
class TemplateConfigCmd(ConfigurePrompt):

    def __init__(self, interface_name: List[str]=None):
        super().__init__(sub_cmd_name='test')

        self.register_top_lvl_cmds(TemplateConfig())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().TEMPLATE_CONFIG)
    
    def intro(self) -> str:
        return f'Starting Template Config....'
                    
    def help(self):
        pass
