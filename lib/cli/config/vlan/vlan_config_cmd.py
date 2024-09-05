import logging
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.vlan.vlan_config import VlanConfig
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

class VlanConfigCmdError(Exception):
    """Custom exception for VlanConfigCmdError errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'VlanConfigCmdError: {self.message}'
   
class VlanConfigCmd(ConfigurePrompt):

    def __init__(self, vlan_id:int, negate:bool = False):
        super().__init__(sub_cmd_name='vlan')
        self.register_top_lvl_cmds(VlanConfig(vlan_id, negate))
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().VLAN_CONFIG_CMD)
        self.log.debug(f'Starting Vlan config Command for VlanID: {vlan_id}')
    
    def intro(self) -> str:
        return f'Starting Vlan Config....'
                    
    def help(self):
        pass
