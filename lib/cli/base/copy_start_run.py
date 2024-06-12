import logging
import os
from time import sleep
from typing import List
from lib.cli.common.router_prompt import PromptFeeder, RouterPrompt
from lib.cli.config.config import Configure
from lib.common.common import Common
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.cli.show.router_configuration import RouterConfiguration
from lib.common.constants import ROUTER_CONFIG_DIR, STATUS_NOK, STATUS_OK

class CopyStartRunError(Exception):
    """
    Custom exception class for CopyStartRun errors.

    This exception is raised when there are issues with reading or processing the configuration files.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class CopyStartRun(RouterPrompt):
    """
    A class that extends RouterPrompt to include functionality for copying and running startup configurations.

    This class initializes with the top-level commands registered for configuration and provides methods to read
    the startup configuration file.

    Attributes:
        None
    """

    def __init__(self):
        """
        Initializes the CopyStartRun class.

        Calls the superclass initializer and registers top-level commands from the Configure class.
        """
        super().__init__()
        RouterPrompt.__init__(self)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().COPY_START_RUN)
        
        self.register_top_lvl_cmds(Configure())

    def read_start_config(self) -> bool:

        rs_path = Common.get_env('ROUTERSHELL_PROJECT_ROOT')    
        prompt_file=f'{rs_path}/config/startup-config.cfg'
        
        pf = PromptFeeder(PromptFeeder.process_file(prompt_file))
        self.load_prompt_feeder(pf)
        self.log.debug(f'{pf.__str__()}')
        
        self.start()
        
        return STATUS_OK
    