import logging

from lib.cli.common.router_prompt import PromptFeeder, RouterPrompt
from lib.cli.config.config import Configure
from lib.common.common import Common
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.common.constants import STATUS_OK

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
        self.log.setLevel(RSLS().COPY_START_RUN)
        
        self.register_top_lvl_cmds(Configure())

    def read_start_config(self, startup_config_fname: str = None) -> bool:
        """
        Reads the startup configuration file and initializes the prompt feeder.

        This method attempts to read a startup configuration file from a specified path.
        If no file name is provided, it defaults to 'startup-config.cfg' located in the 'config'
        directory under the project's root directory. The method then processes the configuration
        file using PromptFeeder and initializes the system with the loaded configuration.

        Args:
            startup_config_fname (str, optional): The startup configuration file name.
                If None, the default 'startup-config.cfg' is used.

        Returns:
            bool: STATUS_OK on successful reading and initialization of the configuration file.
        """
        
        if not startup_config_fname:
            start_config_fname = 'startup-config.cfg'
        else:
            start_config_fname = startup_config_fname

        rs_path = Common.get_env('ROUTERSHELL_PROJECT_ROOT')
        prompt_file = f'{rs_path}/config/{start_config_fname}'

        pf = PromptFeeder(PromptFeeder.process_file(prompt_file))
        self.log.debug(f'{pf.__str__()}')
        self.start(pf)

        return STATUS_OK
