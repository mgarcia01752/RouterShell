import logging
import cmd2
from tabulate import tabulate

from lib.cli.common.router_prompt import ExecMode, RouterPrompt
from lib.cli.base.global_operation import GlobalUserCommand
from lib.network_manager.vlan import Vlan 
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK

class VlanConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Vlan):
    """Command set for configuring Vlan-Config-Commands"""

    PROMPT_CMD_ALIAS = "vlan"

    def __init__(self, vlan_id:int):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self,ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Vlan().__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().VLAN_CONFIG)

        self.prompt = self.set_prompt()
        self.vlan_id = vlan_id
        
        if self.check_or_add_vlan_to_db(self.vlan_id).status:
            self.log.debug(f"VLAN-ID {self.vlan_id} is already configured")

    def do_name(self, vlan_name: str):
        """
        Change the name of the VLAN.

        Args:
            vlan_name (str): The new name for the VLAN.

        Returns:
            int: STATUS_OK if the name update is successful, STATUS_NOK if it fails.

        """
        if self.update_vlan_name(self.vlan_id, vlan_name).status:
            print(f"Unable to add name: {vlan_name} to Vlan-ID {self.vlan_id}")

    def do_description(self, vlan_descr: str) -> int:
        """
        Change the description of the VLAN.

        Args:
            vlan_descr (str): The new description for the VLAN.

        Returns:
            int: STATUS_OK if the description update is successful, STATUS_NOK if it fails.

        """
        if self.update_vlan_description_to_db(self.vlan_id, vlan_descr).status:
            self.log.error(f"Unable to add description: {vlan_descr} to Vlan-ID {self.vlan_id}")
            return STATUS_NOK
        return STATUS_OK

    def do_show(self, args=None):
        print(f"{self.get_vlan_db()}")

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
