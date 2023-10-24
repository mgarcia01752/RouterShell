import logging

from lib.cli.base.exec_priv_mode import ExecMode, ExecException

# Importing constants from a separate module
from lib.common.constants import *

class RouterPrompt:
    '''CMD prompt formatter'''

    USER_MODE_PROMPT = '>'
    PRIV_MODE_PROMPT = '#'
  
    PROMPT_PARTS_CMD = 0
    PROMPT_PARTS_IF = 1
    PROMPT_MAX_LENGTH = 2

    DEF_PREFIX_START = ""
    DEF_START_PROMPT = "Router"
    CONFIG_MODE_PROMPT = 'config'
    PREFIX_SEP = ':'
    if_name = ""

    def __init__(self, exec_mode: ExecMode, sub_cmd_name: str = None):
        '''
        Initialize a RouterPrompt object with the specified configuration mode and sub-command name.

        Args:
            config_mode (CliMode): The CLI privilege mode (e.g., USER_MODE, CONFIG_MODE).
            sub_cmd_name (str, optional): The sub-command name when in CONFIG_MODE. Defaults to None.
        '''
        self.log = logging.getLogger(self.__class__.__name__)
        self.SUB_CMD_START = sub_cmd_name        
        self.execute_mode = exec_mode
        self.prompt_parts = [self.DEF_START_PROMPT]
        self.prompt_prefix = self.current_prompt = ""
        
        if self.execute_mode is ExecMode.USER_MODE:
            self.log.debug("User Mode")
            self.log.debug(f"User Mode - Prompt-Parts ({self.prompt_parts})")
                   
        elif self.execute_mode is ExecMode.CONFIG_MODE:
            self.log.debug("Config Mode")
            self.prompt_parts.append(self.CONFIG_MODE_PROMPT)

            if self.SUB_CMD_START:
                self.prompt_parts.append(self.SUB_CMD_START)
                self.log.debug(f"SUB-CMD-NAME:({self.SUB_CMD_START}) - Prompt-Parts: ({self.prompt_parts})")
        
        # Set the prompt for the first time
        self.set_prompt()

    def set_prompt(self, if_name: str = None) -> str:
        '''
        Set the router command prompt based on the current configuration mode and optional interface name.

        Args:
            if_name (str, optional): The interface name when in CONFIG_MODE. Defaults to None.

        Returns:
            str: The formatted command prompt string.
        '''
        
        self.log.debug(f"set_prompt() -> Execute Mode: {self.execute_mode}")
        
        #Clean up Current Prompt
        self.log.debug(f"set_prompt() -> Current-Prompt-Before-Cleanup -> {self.current_prompt}")
        
        if self.current_prompt and self.current_prompt[-1] in [self.USER_MODE_PROMPT, self.PRIV_MODE_PROMPT]:
            self.current_prompt = self.current_prompt[:-1]
                 
        self.log.debug(f"set_prompt() -> Current-Prompt-After-Cleanup -> {self.current_prompt}")
        
        if self.execute_mode is ExecMode.USER_MODE:
            self.log.debug("User Mode")
            self.prompt_parts = [self.DEF_START_PROMPT]
            self.current_prompt = f"{self.prompt_parts[0]}"
            prompt_mode = self.USER_MODE_PROMPT
            self.log.debug(f"User Mode - Prompt-Parts -> ({self.prompt_parts})") 
            self.log.debug(f"User Mode - Prompt -> {self.current_prompt} -> prompt_mode: ({prompt_mode})")
     
        elif self.execute_mode is ExecMode.PRIV_MODE:
            self.log.debug("Priv Mode")
            self.prompt_parts = [self.DEF_START_PROMPT]
            prompt_mode = self.PRIV_MODE_PROMPT
            self.current_prompt = f"{self.prompt_parts[0]}"
            self.log.debug(f"Priv Mode - Prompt-Parts -> ({self.prompt_parts})") 
            self.log.debug(f"Priv Mode - Prompt -> {self.current_prompt} -> Prompt_mode: ({prompt_mode})")
     
        elif self.execute_mode is ExecMode.CONFIG_MODE:
            self.log.debug("Config Mode")
            prompt_mode = self.PRIV_MODE_PROMPT                        
            if self.SUB_CMD_START:    
                self.log.debug(f"Config Mode - SubCommand -> ({self.SUB_CMD_START})")
                self.log.debug(f"Config Mode - Prompt-Parts -> ({self.prompt_parts})")            
                
            self.current_prompt = f"{self.prompt_parts[0]}({'-'.join(self.prompt_parts[1:])})"
            self.log.debug(f"Config Mode -> Prompt -> {self.current_prompt}")
        else:
            self.log.error(f"No execute_mode defined ({self.execute_mode})")  
        
        self.log.debug(f"set_prompt() -> Prompt-Mode -> ({prompt_mode})") 
        self.log.debug(f"set_prompt() -> Return Prompt-Without-Prompt-Mode -> {self.current_prompt}")                 
        
        self.current_prompt = self.current_prompt + prompt_mode
        
        return self.current_prompt 

    def popInterfacePrompt(self):
        '''
        Pop the interface prompt level when exiting a sub-configuration mode.

        Returns:
            str: Status message ('STATUS_OK' or 'STATUS_NOK').
        '''
        if len(self.prompt_parts) is self.PROMPT_MAX_LENGTH:
            self.log.debug(f"popInterfacePrompt() -> {self.prompt_parts}")
            self.prompt_parts.pop()
            self.log.debug(f"popInterfacePrompt() - popped -> {self.prompt_parts}")
            return STATUS_OK
        return STATUS_NOK
    
    def set_prompt_prefix(self, prefix: str) -> str:
        '''
        Add a prefix to the command prompt, typically the hostname.

        Args:
            prefix (str): The prefix to be added to the prompt.

        Returns:
            str: The updated command prompt string.
        '''
        self.prompt_prefix = prefix

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

