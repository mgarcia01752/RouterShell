import cmd2
import argparse
import logging

from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.network_manager import InterfaceType
from lib.network_manager.wireless import Wifi

from lib.common.constants import STATUS_NOK, STATUS_OK

class InvalidWirelessCellConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class WirelessCellPolicyConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Wifi):

    PROMPT_CMD_ALIAS = InterfaceType.WIRELESS_CELL.value

    def __init__(self, args=None, negate=False):
        
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Wifi.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)

        self.log.debug(f"__init__ > arg -> {args} -> negate={negate}")

        self.args = args
        self.negate = negate
        self.prompt = self.set_prompt()

        if args and not negate:
            self.run_command(args)
        elif args and negate:
            self.run_command(f'no {args}')
