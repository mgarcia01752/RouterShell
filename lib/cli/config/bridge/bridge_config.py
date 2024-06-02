import logging
from lib.cli.config.bridge.bridge import Bridge
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class BridgeConfigError(Exception):
    """Custom exception for BridgeConfigError errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'BridgeConfigError: {self.message}'
   
class BridgeConfig(ConfigurePrompt):
    def __init__(self, bridge_name:str):
        super().__init__(sub_cmd_name='br')

        self.register_top_lvl_cmds(Bridge())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG)
    
    def intro(self) -> str:
        return f'Starting Test Config....'
                    
    def help(self):
        pass
