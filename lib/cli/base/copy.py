import logging
from typing import List

from lib.cli.base.copy_start_run import CopyStartRun
from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.system.copy_mode import CopyMode, CopyType

class CopyError(Exception):
    """Custom exception for CopyError errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'CopyError: {self.message}'

class Copy(CmdPrompt):

    def __init__(self) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().COPY)
               
    def copy_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['running-config', 'startup-config'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['startup-config', 'running-config'])       
    def copy_copy(self, args: List=None) -> bool:
        self.log.debug(f'copyx_copy -> {args}')
        
        if 'running-config' == args[0]:
            
            if 'startup-config' == args[1]:
                if CopyMode().copy_running_config(copy_type=CopyType.DEST_START_UP):
                    self.log.error('Unable to copy running-config to startup-config')
                    return STATUS_NOK
    
            else:
                print(f'Invalid {args[0]} command: {args[1]}')
                return STATUS_NOK
            
        elif 'startup-config' == args[0]:
            
            if 'running-config' == args[1]:
                if CopyStartRun().read_start_config():
                    self.log.error('Unable to copy startup-config to running-config')
                    return STATUS_NOK

            else:
                print(f'Invalid {args[0]} command: {args[1]}')
                return STATUS_NOK
    
        return STATUS_OK
