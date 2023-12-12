import datetime
import enum
import logging
import os
import shutil


from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.common import STATUS_NOK, STATUS_OK, ROUTER_CONFIG_DIR
from lib.db.system_db import SystemDatabase

class InvalidSystemConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class CopyType(enum):
    DEST_FILE = 'file'
    DEST_START_UP = 'start-up'
    DEST_BACK_UP = 'back-up' 

class CopyCommand():

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().COPY_COMMAND)
        self.arg = arg
    
    def copy_running_config(self, copy_type: CopyType = CopyType.DEST_START_UP, destination:str=None) -> bool:
        
        if not destination:
            destination = f"{ROUTER_CONFIG_DIR}/startup-config.cfg"
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_config_file = f"{ROUTER_CONFIG_DIR}/startup-config-backup-{timestamp}.cfg"

        # Check if the startup configuration file exists
        if os.path.exists(destination):
            shutil.copy2(destination, backup_config_file)
            self.log.debug(f"Backup of startup configuration created: {backup_config_file}")

        # Save the new running configuration to the startup configuration file
        running_config = self.get_running_configuration()
        with open(destination, 'w') as file:
            file.write('\n'.join(running_config))

        self.log.debug(f"Running configuration copied to startup configuration: {destination}")        
        return STATUS_OK
    
    