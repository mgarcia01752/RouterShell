import logging
from lib.cli.base.global_cmd_op import Global
from lib.cli.config.configure_prompt import ConfigurePrompt
from lib.cli.test.test import Test
from lib.common.constants import STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS


class ConfigMode(ConfigurePrompt):

    def __init__(self):
        super().__init__()

        self.register_top_lvl_cmds(Global())
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CONFIGURE_PROMPT)
    
    def intro(self) -> str:
        return f'Starting Configuration Mode....'
        
    def start(self) -> bool:

        self._print_top_lvl_cmds()
        print(f'\n\n')
        print(self.intro())
                
        while True:
            try:
                command = self.rs_prompt()
                self.log.info(f'start-cmd: {command}')

                if not command or not command[0]:
                    print(f'No command input')
                    continue

                if '?' in command[0]:
                    # self.show_help()
                    continue
                
                cmd_args = command[1:] if len(command) > 1 else command

                top_level_cmd_obj = self.get_top_level_cmd_object(command)
                
                if top_level_cmd_obj:
                    
                    if top_level_cmd_obj.execute(cmd_args) == STATUS_OK:
                        self.log.info(f'Command: {command} -> args: {cmd_args} - Executed!!!')
                    
                else:
                    print(f"Command {command} not found.")

            except KeyboardInterrupt:
                continue
            
      
