from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text as print
from common.common import Common
from typing import Type

from lib.cli.base.exec_priv_mode import ExecMode

class RouterPromptSession:
    """
    Class for managing router prompt session.
    """
    USER_MODE_PROMPT = '>'
    PRIV_MODE_PROMPT = '#'
  
    PROMPT_PARTS_CMD = 0
    PROMPT_PARTS_IF = 1
    PROMPT_MAX_LENGTH = 2

    DEF_PREFIX_START = ""
    DEF_START_HOSTNAME = "Router"
    DEF_CONFIG_MODE_PROMPT = 'config'
    DEF_NO_CONFIG_MODE_PROMPT = None
    PREFIX_SEP = ':'
    
    def __init__(self, exec_mode: ExecMode = ExecMode.USER_MODE, sub_cmd_name: str = None) -> None:
        """
        Initializes RouterPromptSession instance.
        """
        self.execute_mode = exec_mode
        self.top_level_commands = {}
        self.completer = WordCompleter([])
        self.history = InMemoryHistory()
        self.hostname = Common.getHostName()
        
        if (Common.getHostName() is None):
            self.hostname = self.DEF_START_HOSTNAME
        
    def rs_prompt(self) -> str:
        """
        Displays router prompt and returns user input.

        Returns:
            str: User input from the prompt.
        """
        return prompt(f'{self.hostname}> ', completer=self.completer, history=self.history)

    def register_top_level_commands(self, class_name: Type) -> None:
        """
        Registers top-level commands for the router prompt session.

        Args:
            class_name (Type): Class containing top-level commands.
        """
        cmd_list = class_name.get_command_list()

        for cmd in cmd_list:
            self.top_level_commands[cmd] = class_name
        
        self.completer = WordCompleter(list(self.top_level_commands.keys()))
