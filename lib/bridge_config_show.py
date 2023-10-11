import logging
import json
import cmd2

from tabulate import tabulate

from lib.global_operation import GlobalUserCommand
from lib.router_prompt import ExecMode, RouterPrompt
from lib.network_manager.phy import State
from lib.constants import *

from lib.network_manager.bridge import Bridge
class InvalidBridge(Exception):
    def __init__(self, message):
        super().__init__(message)

class BridgeConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Bridge):
    """Command set for configuring Bridge-Config-Configuration"""

    PROMPT_CMD_ALIAS = "br"
    
    def __init__(self, bridge_ifName: str):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Bridge.__init__(self)
        
        if (self.does_bridge_exist(bridge_ifName, suppress_error=True) is STATUS_NOK):
            if self.add_bridge_global_cmd(bridge_ifName):
                self.log.error(f"Unable to add ({bridge_ifName})")
                        
        self.bridge_ifName = bridge_ifName
                   
        # Set a custom prompt for interface configuration
        self.prompt = self.set_prompt()
             
    def do_protocol(self, args=None):
        return 
    
    def do_shutdown(self, args=None, negate=False) -> bool:
        """
        Change the state of a network interface.

        :param args: Additional arguments (optional).
        :param negate: If True, set the state to UP; otherwise, set it to DOWN.
        :return: True if the interface state was successfully changed, False otherwise.
        """
        self.log.debug(f"do_shutdown() -> Bridge: {self.bridge_ifName} -> negate: {negate}")
        
        state = State.DOWN
        
        if negate:
            state = State.UP
        
        return Bridge().set_interface_state(self.bridge_ifName, state)
        
    def complete_no(self, text, line, begidx, endidx):
        completions = ['shutdown', 'name', 'protocol']
        return [comp for comp in completions if comp.startswith(text)]
          
    def do_no(self, line):    
        self.log.debug(f"do_no() -> Line -> {line}")
        
        parts = line.strip().split()
        start_cmd = parts[0]
        
        self.log.debug(f"do_no() -> Start-CMD -> {start_cmd}")        
        
        if start_cmd == 'shutdown':
            self.log.debug(f"Enable interface -> {self.bridge_ifName}")
            self.do_shutdown(None, negate=True)
                    
class BridgeShow(Bridge):
    """Command set for showing Bridge-Show-Command"""

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg

    def bridge(self, arg=None):
        self.get_bridge()

    def show_bridges(self, args=None):
        # Run the 'ip -json link show type bridge' command and capture its output
        result = self.run(['ip', '-json', 'link', 'show', 'type', 'bridge'])

        # Check if the command was successful
        if result.exit_code != 0:
            print("Error executing 'ip -json link show type bridge'.")
            return

        # Parse the JSON output
        json_data = result.stdout

        # Parse the JSON data into a list of bridge interfaces
        bridge_data = json.loads(json_data)

        # Prepare data for tabulation
        table_data = []
        
        # Check if bridge_data is a list
        if isinstance(bridge_data, list):
            for info in bridge_data:
                bridge_name = info.get("ifname", "")
                ether = info.get("address", "")
                state = "UP" if info.get("operstate") == "UP" else "DOWN"

                table_data.append([bridge_name, ether, state])
        else:
            bridge_name = bridge_data.get("ifname", "")
            ether = bridge_data.get("address", "")
            state = "UP" if bridge_data.get("operstate") == "UP" else "DOWN"

            table_data.append([bridge_name, ether, state])

        # Define headers
        headers = ["Bridge Name", "ether", "State"]

        # Display the table using tabulate
        table = tabulate(table_data, headers, tablefmt="simple")

        print(table)