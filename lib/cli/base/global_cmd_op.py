import logging
import subprocess
import inspect
import os

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdInterface, CmdPrompt
from lib.common.common import STATUS_NOK, STATUS_OK, Common
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
from lib.network_manager.network_operations.interface import Interface
from lib.network_manager.network_operations.network_mgr import NetworkManager

class Global(CmdPrompt, NetworkManager):
    """
    Class representing global commands.
    """

    def __init__(self) -> None:
        """
        Initializes Global instance.
        """
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().GLOBAL_MODE)
        
    def help(self) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            method_name_stripped = method_name.lstrip('_')
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands()         
    def global_end(self, args=None):
        """end\t\t\tend configuration"""
        raise SystemExit

    @CmdPrompt.register_sub_commands()  
    def global_exit(self, args=None):
        """exit\t\t\texit from current mode"""
        raise SystemExit
    
    @CmdPrompt.register_sub_commands()             
    def global_cls(self, args=None):
        """cls\t\t\tClear Screen"""
        print("\033[2J\033[H")       

    @CmdPrompt.register_sub_commands()     
    def global_clock(self, args=None):
        """clock\t\t\tShow clock"""
        
        print(Common.getclock("%H:%M:%S.%f PST %a %b %d %Y"))
        return False

    @CmdPrompt.register_sub_commands() 
    def global_reload(self, args=None) -> bool:
        confirmation = input("Are you sure you want to reboot? (yes/no): ")
        if confirmation.lower() == 'yes':
            reboot_command = Common.get_reboot_command()
            print(f"Using reboot command: {reboot_command}")
            os.system(reboot_command)
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands() 
    def global_version(self, args=None):
        """version\t\t\tGet version"""
        print("v1.0")
        return STATUS_OK

    @CmdPrompt.register_sub_commands()
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

    @CmdPrompt.register_sub_commands()
    def global_ping6(self, args=None):
        """ping6\t\t\tping6"""
        return False

    @CmdPrompt.register_sub_commands()        
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
        
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=Interface().get_os_network_interfaces())       
    def global_flush(self, interface_name: str) -> bool:
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
        self.log.debug(f'global_flush() -> interface: {interface_name}')

        # TODO
        #if self.get_exec_mode() != ExecMode.PRIV_MODE:
        #    print(f"Unable to flush, must be in Privilege Mode")
        #    return
                
        return self.flush_interface(interface_name[0])