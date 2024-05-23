import logging

from lib.cli.common.router_prompt import RouterPrompt
from lib.cli.config.config import Configure
from lib.cli.show.show import Show
from system.system_config import SystemConfig
from system.system_start_up import SystemStartUp
from common.constants import ROUTER_CONFIG, STATUS_OK
from lib.cli.base.global_cmd_op import Global
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/log/routershell.log')
    ]
)

class RouterCLI(RouterPrompt):

    def __init__(self):
        super().__init__()
        SystemStartUp()
        RouterPrompt.__init__(self)
        
        self.register_top_lvl_cmds(Global())
        self.register_top_lvl_cmds(Show())
        self.register_top_lvl_cmds(Configure())

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTERCLI)
        
        self.intro_message()

    def intro_message(self):
        banner_motd = SystemConfig().get_banner()
        self.intro = f"\n{banner_motd}\n" if banner_motd else "Welcome to the Router CLI!\n"

    def run(self) -> None:
        """
        Run the command prompt interface, processing user input in a loop.
        """
        print(self.intro)
        
        self._print_top_lvl_cmds()
        
        while True:
            try:
                command = self.rs_prompt()
                self.log.debug(f'run-cmd: {command}')

                if not command or not command[0]:
                    continue

                if command[0] == '?':
                    self.show_help()
                    continue
                
                cmd_args = command[1:] if len(command) > 1 else command

                top_level_cmd_obj = self.get_top_level_cmd_object(command)
                
                if top_level_cmd_obj:
                    
                    if top_level_cmd_obj.execute(cmd_args) == STATUS_OK:
                        self.log.debug(f'Command: {command} -> args: {cmd_args} - Executed!!!')
                    
                else:
                    print(f"Command {command} not found.")

            except KeyboardInterrupt:
                continue

    def show_help(self): 
        print("Global Commands")
        print("------------------------------------------")         
        print(Global().help())
        print()     
