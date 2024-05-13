from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text as print

class RouterPromptSession:
    
    def __init__(self):
        self.top_level_commands = {}
        self.completer = WordCompleter([])
        self.history = InMemoryHistory()
        self.hostname = "Router"

    def rs_prompt(self):
        return prompt(f'{self.hostname}> ', completer=self.completer, history=self.history)

    def register_top_level_commands(self, class_name):
        
        cmd_list = class_name.get_command_list()
        
        for cmd in cmd_list:
            self.top_level_commands[cmd] = class_name
        
        self.completer = WordCompleter(list(self.top_level_commands.keys()))