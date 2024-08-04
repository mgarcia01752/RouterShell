import logging

from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.dhcp.pool.dhcp_pool_config import DhcpPoolConfig
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLS

class DhcpPoolConfigCmdError(Exception):
    """Custom exception for TestConfig errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'DhcpPoolConfigCmdError: {self.message}'
   
class DhcpPoolConfigCmd(ConfigurePrompt):

    def __init__(self, dhcp_pool_name: str, negate: bool=False):
        super().__init__(sub_cmd_name='dhcp')
                    
        self.register_top_lvl_cmds(DhcpPoolConfig(dhcp_pool_name, negate))
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().DHCP_POOL_CONFIG_CMD)
    
    def intro(self) -> str:
        return f'Starting DHCP Pool Config....'
                    
    def help(self):
        pass
