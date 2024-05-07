from prompt_toolkit import prompt
from cli.base.global_operation import GlobalUserCommand, GlobalPrivCommand
from cli.common.router_prompt import RouterPrompt
from cli.base.exec_priv_mode import ExecMode
from system.copy_mode import CopyMode, CopyType
from system.system_config import SystemConfig
from system.system_start_up import SystemStartUp
from common.constants import ROUTER_CONFIG, STATUS_OK
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/log/routershell.log')
    ]
)

class RouterCLI(GlobalUserCommand, GlobalPrivCommand, RouterPrompt):

    def __init__(self):
        super().__init__()
        SystemStartUp()
        RouterPrompt.__init__(self, ExecMode.USER_MODE)
        GlobalUserCommand.__init__(self)
        GlobalPrivCommand.__init__(self)
                               
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.set_prompt()
        self.prompt = self.get_prompt()
        
        self.intro_message()

    def intro_message(self):
        banner_motd = SystemConfig().get_banner()
        self.intro = f"\n{banner_motd}\n" if banner_motd else "Welcome to the Router CLI!\n"
    

    def run(self):
        while True:
            user_input = prompt('Router> ')
            self.process_input(user_input)

    def process_input(self, user_input):
        # Split user input into command and arguments
        parts = user_input.split()
        if not parts:
            return  # Empty input

        command = parts[0]
        args = parts[1:]

        # Process the command
        if command == 'help':
            self.show_help()
        elif command == 'show':
            self.show_command(args)
        elif command == 'configure':
            self.configure_command(args)
        elif command == 'exit':
            print("Exiting Router CLI. Goodbye!")
            exit()
        else:
            print(f"Command '{command}' not recognized. Type 'help' for available commands.")

    def show_help(self):
        print("Available commands:")
        print("  help          - Show available commands")
        print("  show [arg]    - Execute show command")
        print("  configure [arg] - Execute configure command")
        print("  exit          - Exit the CLI")

    def show_command(self, args):
        if not args:
            print("Usage: show [argument]")
            return

        # Here, you would implement logic to handle 'show' commands
        print(f"Executing 'show' command with arguments: {args}")

    def configure_command(self, args):
        if not args:
            print("Usage: configure [argument]")
            return

        # Here, you would implement logic to handle 'configure' commands
        print(f"Executing 'configure' command with arguments: {args}")
