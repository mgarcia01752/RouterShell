import logging

from lib.cli.base.exec_priv_mode import ExecMode, ExecException

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import *
from lib.system.system_config import SystemConfig

class RouterPrompt:
    '''CMD prompt formatter'''

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
    
    def __init__(self, exec_mode: ExecMode = ExecMode.USER_MODE, sub_cmd_name: str = None):
        '''
        Initialize a RouterPrompt object with the specified configuration mode and sub-command name.

        Args:
            config_mode (CliMode): The CLI privilege mode (e.g., USER_MODE, CONFIG_MODE).
            sub_cmd_name (str, optional): The sub-command name when in CONFIG_MODE. Defaults to None.
        '''
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTER_PROMPT)
        
        '''Start Prompt Router>'''
        self._prompt_dict = {
                    'Hostname' : self.DEF_START_HOSTNAME,
                    'ConfigMode' : self.DEF_NO_CONFIG_MODE_PROMPT,
                    'ExecModePrompt' : self.USER_MODE_PROMPT
                   }
        
        self.SUB_CMD_START = sub_cmd_name
        self.execute_mode = exec_mode
        
        self.update_prompt_hostname()
        
        self._prompt_dict['Hostname'] = self.get_prompt_hostname()

        if self.execute_mode is ExecMode.USER_MODE:
            self.log.debug("User Mode")
            self._prompt_dict['ConfigMode'] = self.DEF_NO_CONFIG_MODE_PROMPT
            self._prompt_dict['ExecModePrompt'] = self.USER_MODE_PROMPT
            self.log.debug(f"User Mode - Prompt-Parts {self._prompt_dict}")
            
        elif self.execute_mode is ExecMode.PRIV_MODE:
            self.log.debug("Privilege Mode")
            self._prompt_dict['ConfigMode'] = self.DEF_NO_CONFIG_MODE_PROMPT
            self._prompt_dict['ExecModePrompt'] = self.PRIV_MODE_PROMPT
            self.log.debug(f"Privilege Mode - Prompt-Parts {self._prompt_dict}")       
            
        elif self.execute_mode is ExecMode.CONFIG_MODE:
            self.log.debug("Config Mode")
            self._prompt_dict['ConfigMode'] = self.DEF_CONFIG_MODE_PROMPT
            self._prompt_dict['ExecModePrompt'] = self.PRIV_MODE_PROMPT
            self.log.debug(f"Config Mode - Prompt-Parts {self._prompt_dict}")
        
        self.set_prompt()

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


