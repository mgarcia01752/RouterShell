import logging
from lib.cli.base.global_cmd_op import Global
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.test.test import Test
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS


class TestMode(ConfigurePrompt):

    def __init__(self):
        super().__init__()

        self.register_top_lvl_cmds(Global())
        self.register_top_lvl_cmds(Test())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().TEST_DEFAULT)
    
    def intro(self) -> str:
        return f'Starting Test Mode....'
        
    def start(self) -> bool:

        self._print_top_lvl_cmds()
        print(f'\n\n')
        print(self.intro())
                
        while True:
            try:
                command = self.rs_prompt()
                self.log.debug(f'start-cmd: {command}')

                if not command or not command[0]:
                    self.log.debug(f'No command input')
                    continue

                if '?' in command[0]:
                    self.help()
                    continue
                
                if 'end' in command[0]:
                    break
                
                cmd_args = command[1:] if len(command) > 1 else command

                if self.get_top_level_cmd_object(command).execute(cmd_args):
                        print(f"Command {command} not found.")
                            
                self.log.debug(f'Command: {command} -> args: {cmd_args} - Executed!!!')
                    
            except KeyboardInterrupt:
                continue
            
    def help(self):
        pass
