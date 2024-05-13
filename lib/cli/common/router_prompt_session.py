import logging

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import print_formatted_text as print
from common.common import Common
from typing import Type

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.cli.base.exec_priv_mode import ExecMode
from lib.common.constants import STATUS_OK
from lib.system.system_config import SystemConfig

class RouterPrompt:
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
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTER_PROMPT)
                
        self.execute_mode = exec_mode
        self.top_level_commands = {}
        self.completer = WordCompleter([])
        self.history = InMemoryHistory()
        self.hostname = Common.getHostName()
        
        '''Start Prompt Router>'''
        self._prompt_dict = {
                    'Hostname' : self.DEF_START_HOSTNAME,
                    'ConfigMode' : self.DEF_NO_CONFIG_MODE_PROMPT,
                    'ExecModePrompt' : self.USER_MODE_PROMPT
                   }
        
        if (Common.getHostName() is None):
            self.hostname = self.DEF_START_HOSTNAME
        
        self.set_prompt()
        
    def rs_prompt(self) -> str:
        """
        Displays router prompt and returns user input.

        Returns:
            str: User input from the prompt.
        """
        return prompt(f'{self.get_prompt()}', completer=self.completer, history=self.history)

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

    def set_prompt(self) -> str:
        '''
        Set the router command prompt based on the current configuration mode and optional interface name.

        Args:
            interface_name (str, optional): The interface name when in CONFIG_MODE. Defaults to None.

        Returns:
            str: The formatted command prompt string.
        '''
        self.log.debug(f"set_prompt() -> Execute-Mode: {self.execute_mode}")
        
        self.update_prompt_hostname()        
        self.prompt_parts = [self._prompt_dict['Hostname']]
                
        if self.execute_mode is ExecMode.USER_MODE:
            self.log.debug("User-Mode")
            self.current_prompt = f"{self._prompt_dict['Hostname']}{self._prompt_dict['ExecModePrompt']}"
            self.log.debug(f"User-Mode - Prompt -> {self.current_prompt}")
     
        elif self.execute_mode is ExecMode.PRIV_MODE:
            self.log.debug("Priv-Mode")
            self._prompt_dict['ExecModePrompt'] = self.PRIV_MODE_PROMPT
            self.prompt_parts = [self._prompt_dict['Hostname']]
            self.current_prompt = f"{self._prompt_dict['Hostname']}{self._prompt_dict['ExecModePrompt']}"
            self.log.debug(f"Priv-Mode - Prompt -> {self.current_prompt}")
     
        elif self.execute_mode is ExecMode.CONFIG_MODE:
            self.log.debug("Config-Mode")
            self.current_prompt = f"{self._prompt_dict['Hostname']}({self._prompt_dict['ConfigMode']}){self._prompt_dict['ExecModePrompt']}"
                                 
            if self.SUB_CMD_START:
                self.log.debug(f"Config Mode - SubCommand -> ({self.SUB_CMD_START})")
                self.current_prompt = f"{self._prompt_dict['Hostname']}({self._prompt_dict['ConfigMode']}-{self.SUB_CMD_START}){self._prompt_dict['ExecModePrompt']}"  
            
            self.log.debug(f"Config Mode -> Prompt -> {self.current_prompt}")
        
        else:
            self.log.error(f"No execute_mode defined ({self.execute_mode})")  
        
        return self.current_prompt 
    
    def get_prompt(self):
        '''
        Get the current router command prompt.

        Returns:
            str: The current command prompt string.
        '''
        return self.current_prompt
    
    def set_exec_mode(self, execute_mode: ExecMode):
        '''
        Set the execution mode for the CLI session.

        Args:
            execute_mode (ExecMode): The execution mode to set (e.g., EXEC_MODE_NORMAL, EXEC_MODE_DEBUG).

        Returns:
            None
        '''
        self.execute_mode = execute_mode

    def get_exec_mode(self) -> ExecMode:
        return self.execute_mode
        
    def update_prompt_hostname(self) -> bool:
        """
        Update the prompt hostname attribute based on the hostname retrieved from the 'SystemConfig'.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK otherwise.
        """
        self._prompt_dict['Hostname'] = SystemConfig().get_hostname()
            
        return STATUS_OK

    def get_prompt_hostname(self) -> str:
        """
        Get the prompt hostname attribute.

        Returns:
            str: The prompt hostname.
        """
        return self._prompt_dict['Hostname']

