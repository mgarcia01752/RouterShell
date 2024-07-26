import logging
from lib.cli.config.bridge.bridge_config import BridgeConfig
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class BridgeConfigCmdError(Exception):
    """Custom exception for BridgeConfigError errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'BridgeConfigError: {self.message}'
   
class BridgeConfigCmd(ConfigurePrompt):
    def __init__(self, bridge_name:str, negate=False):
        super().__init__(sub_cmd_name='br')
        bridge_name = bridge_name[0]
        self.register_top_lvl_cmds(BridgeConfig(bridge_name, negate))
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG_CMD)
    
    def intro(self) -> str:
        return f'Starting Test Config....'
                    
    def help(self):
        pass
