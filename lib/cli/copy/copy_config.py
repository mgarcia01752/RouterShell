import logging
from lib.cli.base.global_cmd_op import Global
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.test.t_config import Bridge
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class CopyConfigError(Exception):
    """Custom exception for TestMode errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'TestConfigError: {self.message}'
   
class CopyConfig(ConfigurePrompt, Bridge):

    def __init__(self):
        super().__init__()
        Bridge.__init__()

        self.register_top_lvl_cmds(Global())
        self.register_top_lvl_cmds(CopyConfig())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().TEST_DEFAULT)
    
    def intro(self) -> str:
        return f'Starting Test Config....'
                    
    def help(self):
        pass