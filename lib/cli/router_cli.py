import argparse
import readline
import signal
import logging
import cmd2
from lib.cli.clear_commands import ClearMode

from lib.cli.router_prompt import RouterPrompt
from lib.cli.exec_priv_mode import ExecMode
from lib.cli.global_operation import GlobalUserCommand, GlobalPrivCommand
from lib.cli.show_operation import ShowMode
from lib.cli.configuration_operation import ConfigureMode
from lib.db.router_shell_db import RouterShellDatabaseConnector as RSDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler('/tmp/log/routershell.log')
    ]
)

class RouterCLI(cmd2.Cmd, 
                GlobalUserCommand, 
                GlobalPrivCommand, 
                RouterPrompt):
    """Router Command-Line Interface"""

    def __init__(self):
        super().__init__()
        GlobalUserCommand.__init__(self)
        GlobalPrivCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.USER_MODE)
        
        RSDB()
                
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.set_prompt()
        self.prompt = self.get_prompt()

        # Define a custom intro message
        intro = "Welcome to the Router CLI!\n"
        
    def preloop(self):
        """Perform preloop setup."""
        # Install a hook to catch control characters (e.g., Ctrl+C)
        readline.set_pre_input_hook(self.pre_input_hook)

        # Set up a signal handler for Ctrl+C
        signal.signal(signal.SIGINT, self.handle_ctrl_c)

    def pre_input_hook(self):
        """Handle control characters."""
        pass  # Do nothing and continue if control characters are encountered

    def handle_ctrl_c(self, signal, frame):
        """Handle Ctrl+C interrupt."""
        # Handle Ctrl+C by providing a message and allowing the loop to continue
        print("\nUse 'exit' to exit configuration mode.")

    def precmd(self, line):
        # Check if the line starts with "!" and treat it as a comment
        if line.strip().startswith("!"):
            return ""
        return line
    
    def do_exit(self, args: str) -> bool:
        """
        Exit the Router CLI.
                # Enter configuration commands, one per line. End with CNTL-Z.
        Args:
            args (str): Command arguments (unused).

        Returns:
            bool: Always returns True to exit the CLI.
        """
        return True

    def do_enable(self, line: str = None) -> bool:
        """
        Enter privilege mode.

        Args:
            line (str, optional): Command line input (unused).

        Returns:
            bool: Always returns False.
        """
        self.set_exec_mode(ExecMode.PRIV_MODE)
        self.prompt = self.set_prompt()
        return False

    def complete_show(  self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        """
        Tab completion for the 'configure' command.

        Args:
            text (str): The current word being completed.
            line (str): The entire line of text.
            begidx (int): The beginning index of the current word.
            endidx (int): The ending index of the current word.

        Returns:
            list[str]: List of completions that start with the provided text.
        """
        show_commands = ['arp', 'bridge', 'interfaces', 'route']
        show_commands.extend(['nat', 'nat-db', 'vlan', 'vlan-db'])
        return [cmd for cmd in show_commands if cmd.startswith(text)]
    
    def do_show(self, arg: str) -> None:
        """
        Show information.

        Args:
            arg (str): Command arguments.
            
            show arp        (Implemented)
            show bridge     (Implemented)
            show interface  (Implemented)
            show vlan       (Implemented)
            show vlan-db    (Implemented)
            show route      (Implemented)
            show ip route
            show ip6 route
            show ip interface
            
        """
        ShowMode(ExecMode.PRIV_MODE, arg)

    def complete_configure(  self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        """
        Tab completion for the 'configure' command.

        Args:
            text (str): The current word being completed.
            line (str): The entire line of text.
            begidx (int): The beginning index of the current word.
            endidx (int): The ending index of the current word.

        Returns:
            list[str]: List of completions that start with the provided text.
        """
        configure_commands = ["terminal"]
        return [cmd for cmd in configure_commands if cmd.startswith(text)]

    def do_configure(self, args: str) -> None:
        """
        Enter configuration mode.

        Args:
            args (str): Command arguments.
        """
        # Create an ArgumentParser
        parser = argparse.ArgumentParser(description="Configuration Mode")
        
        # Add a positional argument for the command
        parser.add_argument("command", nargs="*", help="Command to execute (e.g., 'terminal')")
        
        try:
            # Parse the arguments
            parsed_args = parser.parse_args(args.split())
            
            # Check if the command is "terminal"
            if parsed_args.command and parsed_args.command[0] == "terminal":
                print("Enter configuration commands, one per line. End with Control-Z.")
                self.set_exec_mode(ExecMode.CONFIG_MODE)
                self.prompt = self.set_prompt()
                ConfigureMode(ExecMode.CONFIG_MODE).cmdloop()
                self.set_exec_mode(ExecMode.PRIV_MODE)
                self.prompt = self.set_prompt()
            else:
                # Handle other cases or provide an error message
                print("Invalid command. Use 'configure terminal' to enter configuration mode.")
        except SystemExit:
            # In this case, just return without taking any action.
            return

    def complete_clear(  self, text: str, line: str, begidx: int, endidx: int) -> list[str]:
        configure_commands = ['arp']
        return [cmd for cmd in configure_commands if cmd.startswith(text)]

    def do_clear(self, args: str) -> None:
        '''
            clear arp [interface]
        '''
        ClearMode(ExecMode.PRIV_MODE, args)