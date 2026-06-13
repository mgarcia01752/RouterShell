import logging

from routershell.lib.cli.base.copy_start_run import CopyStartRun
from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.common.constants import STATUS_NOK, STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.system.copy_mode import CopyMode, CopyType


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
        self.log.setLevel(RSLS().COPY)
               
    def copy_help(self, args: list=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['running-config', 'startup-config'])
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['startup-config', 'running-config'])       
    def copy_copy(self, args: list=None) -> bool:
        self.log.debug(f'copy_copy -> {args}')
        
        if args[0] == 'running-config':
            
            if args[1] == 'startup-config':
                if CopyMode().copy_running_config(copy_type=CopyType.DEST_START_UP):
                    self.log.error('Unable to copy running-config to startup-config')
                    return STATUS_NOK
    
            else:
                print(f'Invalid {args[0]} command: {args[1]}')
                return STATUS_NOK
            
        elif args[0] == 'startup-config':
            
            if args[1] == 'running-config':
                
                self.log.debug(f'copy_copy -> {args[0]} - {args[0]} - FOUND!!')
                
                if CopyStartRun().read_start_config():
                    self.log.error('Unable to copy startup-config to running-config')
                    return STATUS_NOK

            else:
                print(f'Invalid {args[0]} command: {args[1]}')
                return STATUS_NOK
    
        return STATUS_OK
