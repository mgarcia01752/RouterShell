import logging

from lib.cli.base.clear_mode import ClearMode
from lib.cli.common.router_prompt import RouterPrompt
from lib.cli.config.config import Configure
from lib.cli.base.copy import Copy
from lib.cli.show.show import Show
from lib.system.system_call import SystemCall
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
        self.register_top_lvl_cmds(ClearMode())
        self.register_top_lvl_cmds(Configure())
        self.register_top_lvl_cmds(Copy())        
        self.register_top_lvl_cmds(Show())

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTERCLI)
        
        self.intro_message()
        
    def intro_message(self):
        banner_motd = SystemCall().get_banner()
        self.intro = f"\n{banner_motd}\n" if banner_motd else "Welcome to the Router CLI!\n"

    def run(self):
        print(self.intro)
        self.start()
    
