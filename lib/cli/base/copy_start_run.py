import os
from time import sleep
from lib.cli.common.router_prompt import RouterPrompt
from lib.cli.config.config import Configure
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
        self.register_top_lvl_cmds(Configure())

    def read_start_config(self) -> bool:
        """
        Reads the startup configuration file.

        Attempts to read the startup configuration file located in the router configuration directory.
        If the file is not found, it raises a CopyStartRunError.

        Returns:
            bool: STATUS_OK if the file is successfully read and processed, STATUS_NOK if there is an error.

        Raises:
            CopyStartRunError: If the startup configuration file is not found or cannot be read.
        """
        config_file = os.path.join(ROUTER_CONFIG_DIR, "startup-config.cfg")
        
        try:
            with open(config_file, "r") as file:
                file_contents = file.read()

            # Process each line from the file
            for line in file_contents.splitlines():
                print(f'{line}')
                sleep(1)
                #self.rs_prompt(line)
        
        except FileNotFoundError:
            self.log.error(f"File not found: {config_file}")
            raise CopyStartRunError(f"Startup configuration file not found: {config_file}")
        
        return STATUS_OK
