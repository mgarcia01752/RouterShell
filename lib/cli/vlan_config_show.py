import logging
import cmd2
from tabulate import tabulate

from lib.cli.router_prompt import ExecMode, RouterPrompt
from lib.cli.global_operation import GlobalUserCommand
from lib.network_manager.vlan import Vlan 

class VlanConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Vlan):
    """Command set for configuring Vlan-Config-Commands"""

    PROMPT_CMD_ALIAS = "vlan"

    def __init__(self, vlan_id:int):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self,ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Vlan().__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)

        self.prompt = self.set_prompt()
        
        self.vlan_id = vlan_id
        
        self.add_vlan_to_db(self.vlan_id)

    def do_name(self, vlan_name:str):
        self.update_vlan_name_to_db(self.vlan_id, vlan_name)
    
    def do_description(self, vlan_descr:str):
        self.update_vlan_description_to_db(self.vlan_id, vlan_descr)

    def do_show(self, args=None):
        print(f"{self.get_vlan_config()}")

class VlanShow(Vlan):
    """Command set for showing Vlan-Show-Commands"""

    def __init__(self, command=None, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        
        self.command = command
        self.arg = arg
    
    def vlan(self):
        """
        Show VLAN configuration.
        """
        self.get_vlan_info()
