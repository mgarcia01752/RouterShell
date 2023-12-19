import enum
import logging
import os
import shutil
from datetime import datetime
from lib.cli.show.router_configuration import RouterConfiguration

from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_OK, STATUS_NOK, ROUTER_CONFIG_DIR

class InvalidCopyMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class CopyType(enum.Enum):
    DEST_FILE = 'file'
    DEST_START_UP = 'start-up'
    DEST_BACK_UP = 'back-up'

class CopyMode:
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().COPY_MODE)
        self.arg = arg

    def copy_database(self) -> bool:
        STATUS_OK
    
    def copy_running_config(self, copy_type: CopyType = CopyType.DEST_START_UP, destination: str = None) -> bool:
        """
        Copy the running configuration to the specified destination.

        Args:
            copy_type (CopyType, optional): The type of copy operation to perform. Defaults to CopyType.DEST_START_UP.
            destination (str, optional): The destination file name for the copy operation. Defaults to None.

        Returns:
            bool: STATUS_OK if the copy operation is successful, STATUS_NOK otherwise.
        """        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        if copy_type == CopyType.DEST_START_UP:
            config_file = os.path.join(ROUTER_CONFIG_DIR, "startup-config.cfg")
            
        elif copy_type == CopyType.DEST_BACK_UP:
            config_file = os.path.join(ROUTER_CONFIG_DIR, f"startup-config-backup-{timestamp}.cfg")
            
        elif copy_type == CopyType.DEST_FILE:
            if not destination:
                self.log.error("Destination filename not specified")
                return STATUS_NOK
            
            config_file = os.path.join(ROUTER_CONFIG_DIR, destination)

        else:
            self.log.error("Invalid copy type specified")
            return STATUS_NOK

        if os.path.exists(config_file):
            backup_file = f"{config_file}-{timestamp}"
            shutil.copy2(config_file, backup_file)
            self.log.debug(f"Backup of startup configuration created: {backup_file}")

        running_config = RouterConfiguration().get_running_configuration()
        with open(config_file, 'w') as file:
            file.write('\n'.join(running_config))

        self.log.debug(f"Running configuration copied to {copy_type.value} configuration: {config_file}")
        return STATUS_OK



