import logging

from routershell.lib.cli.common.command_class_interface import CmdPrompt
from routershell.lib.cli.common.exec_priv_mode import ExecMode
from routershell.lib.cli.config.config_mode import ConfigMode
from routershell.lib.common.constants import STATUS_OK
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS


class Configure(CmdPrompt):

    def __init__(self, args: str=None) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=False, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CONFIGURE_MODE)
               
    def configure_help(self, args: list=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
        pass
    
    @CmdPrompt.register_sub_commands()
    def configure_terminal(self, args: list) -> bool:
        self.log.debug('Entering into configure mode')
        ConfigMode().start()
        return STATUS_OK
