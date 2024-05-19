import logging
import subprocess
import inspect
import os

from lib.cli.base.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdInterface
from lib.common.common import STATUS_NOK, STATUS_OK, Common
from lib.network_manager.network_mgr import NetworkManager
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class Global(NetworkManager):
    """
    Class representing global commands.
    Inherits from NetworkManager.
    """

    def __init__(self) -> None:
        """
        Initializes Global instance.
        """
        self.CLASS_NAME = self.__class__.__name__.lower()

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().GLOBAL_MODE)
        
        self._generate_command_dict()
 
    def _generate_command_dict(self) -> dict:
        """
        Generate a nested dictionary for command completion based on class methods.

        Returns:
            dict: Nested dictionary for command completion.
        """
        self._nested_dict = {}

        commands = self.get_command_list()
        self.log.debug(f'Class Commands: {commands}')

        for cmd in commands:
            parts = cmd.split('_')
            current_level = self._nested_dict
            for part in parts:
                if part not in current_level:
                    current_level[part] = {None}
                current_level = current_level[part]

        self.log.debug(f'Nested-Cmds: {self._nested_dict}')
        return self._nested_dict
   
    def get_command_dict(self):
        return self._nested_dict
    
    def execute(self, subcommand: list) -> None:
        """
        Executes a subcommand.

        Args:
            subcommand (str, optional): Subcommand to execute. Defaults to None.
        """
        # Check its a list
        self.log.debug(f'execute: {subcommand}')
        if subcommand:
            getattr(self, f"{self.CLASS_NAME}_{subcommand[0]}")(subcommand[1:])

    def class_methods(self) -> list:
        """
        Get a list of class methods.

        Returns:
            list: List of class methods.
        """
        return [attr for attr in dir(self) if attr.startswith(f'{self.CLASS_NAME}') 
                and inspect.ismethod(getattr(self, attr))]
  
    def get_command_list(self) -> list:
        """
        Get a list of available commands.

        Returns:
            list: List of available commands.
        """
        elements = self.class_methods()
        prefix_length = len(self.CLASS_NAME) + 1
        return [element[prefix_length:] if element.startswith(f"{self.CLASS_NAME}_") else element for element in elements]

    def help(self) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            method_name_stripped = method_name.lstrip('_')
            print(f"{method.__doc__}")
            
    def global_end(self, args=None):
        """end\t\t\tend configuration"""
        raise SystemExit
                
    def global_cls(self, args=None):
        """cls\t\t\tClear Screen"""
        print("\033[2J\033[H")       

    def global_clock(self, args=None):
        """clock\t\t\tShow clock"""
        
        print(Common.getclock("%H:%M:%S.%f PST %a %b %d %Y"))
        return False
    
    def global_reload(self, args=None):
        """reload\t\t\tReboot"""
        self.global_reboot(args=None)
        return False

    def global_reboot(self, args=None):
        """reboot\t\t\tReboot"""
        return False

    def global_version(self, args=None):
        """version\t\t\tGet version"""
        print("v1.0")
        return False
    
    def global_ping(self, args=None):
        """ping\t\t\tping <IPv4 address>"""
        self.log.debug(f'ping: {args}')
        
        if isinstance(args, list):
            args = args[0]
        
        try:
            # Split the input args=None into individual arguments
            args = args.split()

            if len(args) < 1:
                print("Usage: ping <destination>")
                return False

            # Construct the ping command
            ping_command = ['ping', '-c', '4', args[0]]

            # Start the ping process in the background
            self.ping_process = subprocess.Popen(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Read and print the output of the ping process
            while True:
                output_line = self.ping_process.stdout.readline()
                if not output_line:
                    break
                print(output_line.strip())

            # Wait for the ping process to complete
            self.ping_process.wait()

            return False  # Command executed successfully

        except Exception as e:
            print(f"Error: {e}")
            return False  # Command execution failed
    
    def global_ping6(self, args=None):
        """ping6\t\t\tping6"""
        return False
        
    def global_traceroute(self, args=None):
        """traceroute\t\ttraceroute"""
        try:
            # Split the input args=None into individual arguments
            args = args.split()

            if len(args) < 1:
                print("Usage: traceroute <destination>")
                return False  # Command execution failed

            # Construct the traceroute command with the '-n' option to disable DNS resolution
            traceroute_command = ['traceroute', '-n'] + args

            # Execute the traceroute command and capture the output
            traceroute_output = subprocess.run(traceroute_command, capture_output=True, text=True)

            if traceroute_output.returncode == 0:
                # Print the traceroute results
                print(traceroute_output.stdout)
                return True  # Command executed successfully
            else:
                print(f"Error executing 'traceroute' command: {traceroute_output.stderr}")
                return False  # Command execution failed

        except Exception as e:
            print(f"Error: {e}")
            return False  # Command execution failed