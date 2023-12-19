import argparse
import os

from bs4 import Comment
from lib.cli.base.exec_priv_mode import ExecMode
from lib.common.common import STATUS_NOK, STATUS_OK, Common
import subprocess

from lib.network_manager.network_mgr import NetworkManager

class GlobalPrivCommand(NetworkManager):

    def __init__(self):
        super().__init__()
        
    def do_reboot(self, args=None):
        '''
        Reboot the system.
        
        Args:
            line (str): Additional arguments (not used).
        
        Returns:
            bool: False if reboot is canceled, otherwise returns False.
        '''
        parser = argparse.ArgumentParser(description="Reboot the system",
                                         epilog="")
        parser.add_argument("--force", action="store_true", help="Force reboot")
        
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print(f"Unable to reboot, must be in Privilege Mode")
            return
        
        try:
            args = parser.parse_args(args.split())
        except SystemExit:
            return
        
        if args.force:
            # Add logic for a forced reboot here
            print("Forced Rebooting...")
        else:
            confirmation = input("Are you sure you want to reboot? (yes/no): ")
            if confirmation.lower() == 'yes':
                reboot_command = Common.get_reboot_command()
                print(f"Using reboot command: {reboot_command}")
                os.system(reboot_command)  # Execute the selected reboot command
            else:
                print("Reboot canceled.")
        
    def do_flush(self, interface_name: str):
        """
        Command to flush the configuration of a network interface.

        This command allows the user to flush the configuration of a network interface,
        effectively removing all assigned IP addresses and resetting the interface.

        Args:
            interface_name (str): The name of the network interface to flush.

        Usage:
            flush <interface_name>

        Example:
            flush eth0
        """
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print(f"Unable to flush, must be in Privilege Mode")
            return
                
        self.flush_interface(interface_name)

    def do_adduser(self, args=None):
        '''
        Add a user (implementation pending).
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False (implementation pending).
        '''
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print(f"Unable to add user, must be in Privilege Mode")
            return
                
        return False
    
    def do_deluser(self, args=None):
        '''
        Delete a user (implementation pending).
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False (implementation pending).
        '''
        if self.get_exec_mode() != ExecMode.PRIV_MODE:
            print(f"Unable to delete user, must be in Privilege Mode")
            return
        return False
    
    def set_prompt_prefix(self, prefix: str) -> str:
        '''
        Add a prefix to the command prompt, typically the hostname.

        Args:
            prefix (str): The prefix to be added to the prompt.

        Returns:
            str: The updated command prompt string.
        '''
        self.prompt_prefix = prefix

class GlobalUserCommand():

    def __init__(self, args=None):
        pass

    def do_end(self, args=None):
        '''
        Drop from top to lower level
        '''
        raise SystemExit
                
    def do_cls(self, args=None):
        """
        Clear the screen (console).
        
        Args:
            arg (str, optional): Additional arguments (not used).
        
        Returns:
            None
        """
        parser = argparse.ArgumentParser(description="Clear the screen",
                                         epilog="")
        
        try:
            args = parser.parse_args(args.split())
        except SystemExit:
            # In this case, just return without taking any action.
            return
        
        if os.name == 'posix':  # Unix/Linux/Mac
            os.system('clear')

    def do_clock(self, args=None):
        '''
        Display the current system time.
        
        Args:
            line (str): Additional arguments (not used).
        
        Returns:
            bool: Always returns False.
        '''
        
        print(Comment.getclock("%H:%M:%S.%f PST %a %b %d %Y"))
        return False
    
    def do_reload(self, args=None):
        '''
        Reload the system (alias for 'do_reboot').
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False if reboot is canceled, otherwise returns False.
        '''
        self.do_reboot(args=None)
        return False

    def do_version(self, args=None):
        '''
        Show version of RouterCLI.
        
        Args:
            args=None (str): Additional arguments (not used).
        
        Returns:
            bool: False.
        '''
        if len(args=None.split()) < 1:
            print("Takes no arguments")
            return False
        print("v1.0")
        return False
    
    def do_ping(self, args=None):
        '''
        Ping a destination.
        
        Args:
            args=None (str): The destination to ping.
        
        Returns:
            bool: True if the ping is successful, otherwise False.
        '''
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
    
    def do_ping6(self, args=None):
        '''
        Ping a destination using IPv6.
        
        Args:
            args=None (str): The destination to ping.
        
        Returns:
            bool: False (implementation pending).
        '''
        return False
        
    def do_traceroute(self, args=None):
        '''
        Perform a traceroute to a destination.
        
        Args:
            args=None (str): The destination to trace.
        
        Returns:
            bool: True if the traceroute is successful, otherwise False.
        '''
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


