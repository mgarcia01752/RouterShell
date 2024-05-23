import logging
from lib.cli.base.global_cmd_op import Global
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.test.test import Test
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS


class TestMode(ConfigurePrompt):

    def __init__(self):
        super().__init__()

        self.register_top_lvl_cmds(Global())
        self.register_top_lvl_cmds(Test())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().TEST_DEFAULT)
    
    def intro(self) -> str:
        return f'Starting Test Mode....'
                    
    def help(self):
        pass
