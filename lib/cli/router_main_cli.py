from lib.cli.common.router_prompt_session import RouterPrompt
from system.system_config import SystemConfig
from system.system_start_up import SystemStartUp
from common.constants import ROUTER_CONFIG, STATUS_OK
from lib.cli.base.global_cmd_op import Global
import logging

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
        self.register_top_level_commands(Global())

        self.log = logging.getLogger(self.__class__.__name__)
        
        self.intro_message()

    def intro_message(self):
        banner_motd = SystemConfig().get_banner()
        self.intro = f"\n{banner_motd}\n" if banner_motd else "Welcome to the Router CLI!\n"

    def run(self):
        print(self.intro)
        while True:
            try:
                user_input = self.rs_prompt()
                command = user_input.strip().lower()

                if command == '?':
                    self.show_help()
                    
                elif command in self.top_level_commands:
                    self.top_level_commands[command].execute(command)
                
                else:
                    print(f"Command '{command}' not found.")
            
            except KeyboardInterrupt:
                continue

    def show_help(self): 
        print("Global Commands")
        print("------------------------------------------")         
        print(Global().help())
