### Summary
Fixed the RouterShell startup import chain by importing ROUTER_CONFIG_DIR from the central constants module instead of common.common. This resolves the ImportError raised when the editable install loads routershell.lib.system.copy_mode.

### Modified Files
- src/routershell/lib/system/copy_mode.py

### Commands Executed And Results
- `ROUTERSHELL_DB_FILE=/home/dev01/Projects/RouterShell/.routershell/test-import.db PYTHONPATH=src /opt/routershell/venv/bin/python - <<'PY' ...` -> pass; CLI import chain loaded successfully
- `/opt/routershell/venv/bin/python -m pytest tests/packaging/test_imports.py` -> pass; 1 test passed
- `/opt/routershell/venv/bin/python tools/release/qa_checker.py --skip-pycycle` -> pass; Ruff passed and pytest passed with 22 tests

### Tests
- `pytest tests/packaging/test_imports.py` -> pass
- `pytest` -> pass; 22 tests passed through the QA checker
- `ruff` -> pass; All checks passed through the QA checker

### Notes / Warnings
- The CLI import smoke still logs sudo bridge discovery errors in this restricted shell, but those did not block imports.

### Remaining TODOs / Follow-Ups
- Consider deferring bridge discovery side effects during import in a future startup cleanup.

# FILE: src/routershell/lib/system/copy_mode.py
import enum
import logging
import os
import shutil
from datetime import datetime

from routershell.lib.cli.show.router_configuration import RouterConfiguration
from routershell.lib.common.common import STATUS_NOK, STATUS_OK
from routershell.lib.common.constants import ROUTER_CONFIG_DIR
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.common.types import StatusResult


class InvalidCopyMode(Exception):
    def __init__(self, message):
        super().__init__(message)

class CopyType(enum.Enum):
    DEST_FILE = 'file'
    DEST_START_UP = 'start-up'
    DEST_BACK_UP = 'back-up'

class CopyMode:
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().COPY_MODE)
    
    def copy_start_config_to_run_config(self) -> StatusResult:
        self.log.info('copy_start_config_to_run_config()')
        return STATUS_OK

    def copy_running_config(self, copy_type: CopyType = CopyType.DEST_START_UP, destination: str = None) -> StatusResult:
        """
        Copy the running configuration to the specified destination.

        Args:
            copy_type (CopyType, optional): The type of copy operation to perform. Defaults to CopyType.DEST_START_UP.
            destination (str, optional): The destination file name for the copy operation. Defaults to None.

        Returns:
            StatusResult: STATUS_OK if the copy operation is successful, STATUS_NOK otherwise.
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

