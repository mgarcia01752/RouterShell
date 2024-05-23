import logging
from typing import List
from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.base.global_cmd_op import Global
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.config.interface.ifconfig import IfConfig
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
   

class InterfaceConfig(ConfigurePrompt):

    def __init__(self):
        super().__init__()

        self.register_top_lvl_cmds(Global())
        self.register_top_lvl_cmds(IfConfig())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().INTERFACE_CONFIG)
    
    def intro(self) -> str:
        return f'Starting Interface Configuration'
                    
    def help(self):
        pass
