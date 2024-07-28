import logging
from lib.cli.base.global_cmd_op import Global
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS

class VlanConfigCmdError(Exception):
    """Custom exception for VlanConfigCmdError errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'VlanConfigCmdError: {self.message}'
   
class VlanConfigCmd(ConfigurePrompt):

    def __init__(self):
        super().__init__(sub_cmd_name='vlan')

        self.register_top_lvl_cmds(TConfig())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().VLAN_CONFIG_CMD)
    
    def intro(self) -> str:
        return f'Starting Vlan Config....'
                    
    def help(self):
        pass
