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
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/log/routershell.log')
    ]
)

class RouterCLI(RouterPrompt):
    """
    RouterCLI is a command-line interface class for managing and interacting with network routers.
    
    This class inherits from RouterPrompt and initializes the router system with optional startup procedures.
    
    Attributes:
        system_start_up (bool): Determines if the system startup procedures should be executed upon initialization.
        
    Methods:
        __init__(system_start_up=True):
            Initializes the RouterCLI instance and optionally performs system startup procedures.
    """
    
    def __init__(self, system_start_up=False):
        """
        Initializes the RouterCLI instance.
        
        Args:
            system_start_up (bool): If True, performs system startup procedures by calling SystemStartUp(). Defaults to True.
        
        Inherited Methods:
            RouterPrompt.__init__(): Initializes the parent RouterPrompt class.
        
        Example:
            # Create a RouterCLI instance with system startup procedures
            router_cli = RouterCLI(system_start_up=True)
            
            # Create a RouterCLI instance without system startup procedures
            router_cli = RouterCLI(system_start_up=False)
        """
        super().__init__()
        
        if system_start_up:
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
    
