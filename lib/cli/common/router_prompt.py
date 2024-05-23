import logging

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit import print_formatted_text as print

from typing import List, Union

from common.common import Common
from lib.cli.common.CommandClassInterface import CmdPrompt
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
    DEF_START_HOSTNAME = "RouterShell"
    DEF_CONFIG_MODE_PROMPT = 'config'
    DEF_NO_CONFIG_MODE_PROMPT = None
    PREFIX_SEP = ':'
    
    def __init__(self, exec_mode: ExecMode = ExecMode.USER_MODE, sub_cmd_name: str = None) -> None:
        """
        Initializes RouterPromptSession instance.
        """
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ROUTER_PROMPT)
         
        self._register_top_lvl_cmds = {}
        self._command_dict_completer = {'enable':{}}
        
        self.execute_mode = exec_mode
        self.SUB_CMD_START = sub_cmd_name
        
        self.completer = NestedCompleter.from_nested_dict({'FAKE':{}})
        self.history = InMemoryHistory()
        self.session = PromptSession(completer=self.completer, history=self.history)

        self.hostname = Common.getHostName()
        
        '''Start Prompt Router>'''
        self._prompt_dict = {
            'Hostname' : self.DEF_START_HOSTNAME,
            'ConfigMode' : self.DEF_CONFIG_MODE_PROMPT,
            'ExecModePrompt' : self.USER_MODE_PROMPT
        }

        if (Common.getHostName() is None):
            self.hostname = self.DEF_START_HOSTNAME

        self.update_prompt()
         
    def rs_prompt(self, split: bool = True) -> list:
        """
        Displays router prompt and returns user input.

        Args:
            split (bool, optional): Whether to split the output. Defaults to False.

        Returns:
            str or list: User input from the prompt. If split is True, returns a list of words.
        """
        self.update_prompt()
        
        _ = self.session.prompt(f'{self.get_prompt()}',completer=self.completer, complete_in_thread=False)
        
        if _.split(' ')[0] == 'enable':
            self.execute_mode = ExecMode.PRIV_MODE
            self.update_prompt()
            return ''
        
        if not split:
            return _
        
        return _.split(' ')

    def register_top_lvl_cmds(self, class_name: CmdPrompt) -> bool:
        """
        Register top-level commands for the router prompt session.

        Args:
            class_name (Type): Class containing top-level commands.
            class_nested_cmds (bool, optional): Whether the commands are nested or not. Defaults to False.
        
        Returns:
            bool: Status indicating whether the registration was successful.
        """
        cmd_list = class_name.get_command_list()
        due_to_global = True
        
        for cmd in cmd_list:

            if not class_name.isGlobal():
                cmd = class_name.getClassStartCmd() + '_' + cmd
                due_to_global = False
            
            self.log.debug(f'Top-Level-Cmd: {cmd}\tClass: {class_name}')
                        
            self._register_top_lvl_cmds[cmd] = class_name
            
            cmd_dict = class_name.get_command_dict(skip_top_key=due_to_global)
            
            self._command_dict_completer.update(cmd_dict)
        
        # This populates the tab completions    
        self.completer = NestedCompleter.from_nested_dict(self._command_dict_completer)

        return STATUS_OK

    def update_prompt(self) -> str:
        '''
        Update the router command prompt based on the current configuration mode and optional interface name.

        Returns:
            str: The formatted command prompt string.
        '''
        self.log.debug(f"update_prompt() -> Execute-Mode: {self.execute_mode}")
        
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
        self.update_prompt()

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

    def get_top_level_cmd_object(self, cmd: List[str]) -> Union[CmdPrompt, None]:
        """
        Retrieve the top-level command object.

        Args:
            cmd (List[str]): List of command parts to search for.

        Returns:
            Union[CmdPrompt, None]: The command object if found, else None.
        """
        self.log.debug(f"TOP-LVL-CMD-SEARCH: ({cmd})\n" + "\n".join([f"{key} ----> {value}" \
            for key, value in self._register_top_lvl_cmds.items()]))

        # Check to see if key exists exactly
        if cmd[0] in self._register_top_lvl_cmds:
            self.log.debug(f'Command Found (Global): {cmd[0]}')
            return self._register_top_lvl_cmds[cmd[0]]
        
        combined_cmd = '_'.join(cmd[:2])
        if combined_cmd in self._register_top_lvl_cmds:
            self.log.debug(f'Command Found (Non-Global): {combined_cmd}')
            return self._register_top_lvl_cmds[combined_cmd]
        
        self.log.debug(f'cmd: {cmd} - No Match!!!')
        
        return None

    def clear_completer(self):
        """
        Clear the current completer, removing all suggestions.
        """
        self.session.completer = None
        
    def start(self) -> bool:
        """
        Start the command prompt.

        This method initializes the command prompt interface, printing top-level
        commands and introduction, and enters a loop to process user commands.

        Returns:
            bool: True if the prompt exits normally, False if interrupted.
        """
        self._print_top_lvl_cmds()

        while True:
            try:
                command = self._get_command()
                if not command:
                    continue

                if self._process_command(command):
                    break

            except KeyboardInterrupt:
                self.log.debug('Keyboard interrupt received, continuing...')
                continue
            except EOFError:
                self.log.debug('EOFError received, exiting...')
                break

        return True

    def _get_command(self) -> list:
        """
        Get the user command from the prompt.

        Returns:
            list: The user command split into components.
        """
        command = self.rs_prompt()
        self.log.debug(f'start-cmd: {command}')
        return command

    def _process_command(self, command: list) -> bool:
        """
        Process the user command.

        Args:
            command (list): The user command split into components.

        Returns:
            bool: True if the loop should exit, False otherwise.
        """
        if not command or not command[0]:
            self.log.debug('No command input')
            return False

        if '?' in command[0]:
            self.help()
            return False

        if 'end' in command[0]:
            return True

        cmd_args = command[1:] if len(command) > 1 else command

        if not self._execute_command(command[0], cmd_args):
            print(f"Command {command[0]} not found.")
        else:
            self.log.debug(f'Command: {command[0]} -> args: {cmd_args} - Executed!!!')

        return False

    def _execute_command(self, cmd: str, args: list) -> bool:
        """
        Execute the given command with its arguments.

        Args:
            cmd (str): The command to execute.
            args (list): The arguments for the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.
        """
        try:
            cmd_object = self.get_top_level_cmd_object([cmd])
            return cmd_object.execute(args)
        except Exception as e:
            self.log.debug(f'Error executing command {cmd}: {e}')
            return False
            
    def _print_top_lvl_cmds(self):
        """
        Print the top-level commands with each key-value pair on a new line.
        """
        formatted_cmds = "\n".join([f"{key}\t\t\t{value}" for key, value in self._register_top_lvl_cmds.items()])
        self.log.debug(f"TOP-LVL-CMD:\n{formatted_cmds}")
                   