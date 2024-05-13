import subprocess
import inspect
import os

from bs4 import Comment
from lib.cli.base.exec_priv_mode import ExecMode
from lib.common.common import STATUS_NOK, STATUS_OK, Common

from lib.network_manager.network_mgr import NetworkManager

class Global(NetworkManager):
    
    def __init__(self):
        self.CLASS_NAME = self.__class__.__name__.lower()
        pass
    
    def execute(self, subcommand=None):
        if (subcommand):
            getattr(self, f"{self.CLASS_NAME}_{subcommand}")()

    def class_methods(self):
        return  [attr for attr in dir(self) if attr.startswith(f'{self.CLASS_NAME}') 
                 and inspect.ismethod(getattr(self, attr))]
  
    def get_command_list(self):
            elements = self.class_methods()
            prefix_length = len(self.CLASS_NAME) + 1
            return [element[prefix_length:] if element.startswith(f"{self.CLASS_NAME}_") else element for element in elements]

    def help(self):
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
        
        print(Comment.getclock("%H:%M:%S.%f PST %a %b %d %Y"))
        return False
    
    def global_reload(self, args=None):
        """reload\t\t\tReboot"""
        self.global_reboot(args=None)
        return False

    def global_reboot(self, args=None):
        """reload\t\t\tReboot"""
        return False

    def global_version(self, args=None):
        """version\t\t\tGet version"""
        if len(args=None.split()) < 1:
            print("Takes no arguments")
            return False
        print("v1.0")
        return False
    
    def global_ping(self, args=None):
        """ping\t\t\tping"""
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