from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text as print
from common.common import Common
from typing import Type

class RouterPromptSession:
    """
    Class for managing router prompt session.
    """

    def __init__(self) -> None:
        """
        Initializes RouterPromptSession instance.
        """
        self.top_level_commands = {}
        self.completer = WordCompleter([])
        self.history = InMemoryHistory()
        self.hostname = Common.getHostName()

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
