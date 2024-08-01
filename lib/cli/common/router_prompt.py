import logging
from typing import Any, List, Optional, Union

from time import sleep
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit import print_formatted_text as print
from common.common import Common
from lib.cli.common.command_class_interface import CmdPrompt
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
from lib.cli.common.exec_priv_mode import ExecMode
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.string_formats import StringFormats
from lib.system.system_call import SystemCall

class PromptFeeder:
    """
    A class to manage and simulate feeding prompts.

    This class is designed to handle a list of prompt commands or inputs,
    allowing them to be processed sequentially.

    Attributes:
        prompt_feed (List[List[str]]): The initial list of prompts/commands.
        start_length (int): The length of the initial prompt feed.

    Methods:
        pop() -> bool:
            Removes the top entry from the prompt feed.
        top() -> List[str]:
            Returns the top entry from the prompt feed without removing it.
        length() -> int:
            Returns the current length of the prompt feed.
        get_start_length() -> int:
            Returns the initial length of the prompt feed.
        next() -> List[str]:
            Returns and removes the top entry from the prompt feed.
    """
    @staticmethod
    def process_file(file_path: str) -> List[List[str]]:
        """
        Processes a file and creates a nested list where each line is a list,
        and each word in the line is a string.

        Args:
            file_path (str): The path to the input file.

        Returns:
            List[List[str]]: The processed nested list.
        """
        nested_list = []

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line_list = [word for word in line.strip().split()]
                    nested_list.append(line_list)
                            
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

        return nested_list
    
    def __init__(self, prompt_feed: List[List[str]] = []):
        """
        Initializes the PromptFeed with a list of prompts/commands.

        Args:
            prompt_feed (List[List[str]]): The initial list of prompts/commands.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().PROMPT_FEEDER)
                
        self.prompt_feed = prompt_feed[:]
        self.start_length = len(self.prompt_feed)

    def pop(self) -> bool:
        """
        Removes the top entry from the prompt feed.

        Returns:
            bool: STATUS_OK if the operation is successful.
        """
        if self.prompt_feed:
            self.prompt_feed.pop(0)
        return STATUS_OK

    def top(self) -> List[str]:
        """
        Returns the top entry from the prompt feed without removing it.

        Returns:
            List[str]: The top entry or an empty list if the prompt feed is empty.
        """
        if self.prompt_feed:
            return self.prompt_feed[0]
        return []

    def length(self) -> int:
        """
        Returns the current length of the prompt feed.

        Returns:
            int: The current length of the prompt feed.
        """
        return len(self.prompt_feed)

    def get_start_length(self) -> int:
        """
        Returns the initial length of the prompt feed.

        Returns:
            int: The initial length of the prompt feed.
        """
        return self.start_length

    def next(self) -> List[str]:
        """
        Returns and removes the top entry from the prompt feed.

        Returns:
            List[str]: The top entry from the prompt feed, or an empty list if the prompt feed is empty.
        """
        if self.prompt_feed:
            return self.prompt_feed.pop(0)
        return []

    def __str__(self) -> str:
        """
        Returns a string representation of the PromptFeed object.

        Returns:
            str: A string representation of the PromptFeed object.
        """
        return f"PromptFeed(start_length={self.start_length}, current_length={len(self.prompt_feed)}, top_entry={self.top()})"


class RouterPromptError(Exception):
    """
    Custom exception class for RouterPrompt errors.

    This exception is raised when there are issues RouterPrompt.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

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
    
    PROMPT_REMARK_SYMBOL = [';', '!']
    
    #Create an shared empty object
    _prompt_feeder_obj = PromptFeeder([])
    
    #Keep track of user execute mode
    _current_execute_mode = ExecMode.USER_MODE
    
    def __init__(self, exec_mode: ExecMode = ExecMode.USER_MODE, 
                 sub_cmd_name: str = None) -> None:
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

    def prompt_feeder_length(self) -> int:
        """
        Get the length of the prompt feeder.

        Returns:
            int: The length of the prompt feeder.
        """
        return RouterPrompt._prompt_feeder_obj.length()
    
    def get_prompt_feeder(self) -> Optional[PromptFeeder]:
        """
        Get the current prompt feeder.

        Returns:
            Optional[PromptFeeder]: The current prompt feeder if available, otherwise None.
        """
        return RouterPrompt._prompt_feeder_obj
    
    def load_prompt_feeder(self, pf: PromptFeeder) -> bool:
        """
        Load a new prompt feeder.

        Args:
            pf (PromptFeeder):  The new prompt feeder to load. 

        Returns:
            bool: STATUS_OK if the prompt feeder is successfully loaded, STATUS_NOK otherwise.
        """
        if not isinstance(pf, PromptFeeder):
            return False
        
        RouterPrompt._prompt_feeder_obj = pf
        if RouterPrompt._prompt_feeder_obj.length() < 0:
            return STATUS_NOK
        
        return STATUS_OK
        
    def intro(self) -> str:
        return ""
         
    def rs_prompt(self, 
                  split: bool=True, 
                  ws_trim_lead: bool=True,
                  ws_reduce: bool=True) -> List|Any:
        """
        Displays router prompt and returns user input.

        Args:
            split (bool, optional): Whether to split the output. Defaults to False.

        Returns:
            str or list: User input from the prompt. If split is True, returns a list of words.
        """
        self.update_prompt()
        
        _ = self.session.prompt(f'{self.get_prompt()}',completer=self.completer, complete_in_thread=False)
        
        # Check if the input contains any remark symbols, if so, skip line
        if any(_.startswith(symbol) for symbol in RouterPrompt.PROMPT_REMARK_SYMBOL):
            return []
        
        if ws_trim_lead:
            _.lstrip()
            
        if ws_reduce:
            _ = StringFormats.reduce_ws(_)
        
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
        self.log.debug(f'register_top_lvl_cmds() -> {class_name}')
        
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
            self._prompt_dict['ExecModePrompt'] = self.PRIV_MODE_PROMPT
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
        self._prompt_dict['Hostname'] = SystemCall().get_hostname_os()
            
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
        self.log.debug(f'get_top_level_cmd_object() -> cmds: {cmd}')
        
        #self.log.debug(f"TOP-LVL-CMD-SEARCH: ({cmd})\n" + "\n".join([f"{key} ----> {value}" \
        #    for key, value in self._register_top_lvl_cmds.items()]))

        # Check for Global defined classes
        if cmd[0] in self._register_top_lvl_cmds:
            self.log.debug(f'get_top_level_cmd_object() -> Command Found (Global): {cmd[0]}')
            return self._register_top_lvl_cmds[cmd[0]]
        
        # Check for non-global classes
        combined_cmd = '_'.join(cmd[:2])
        self.log.debug(f'get_top_level_cmd_object() -> combined_cmd: {combined_cmd}')
        if combined_cmd in self._register_top_lvl_cmds:
            self.log.debug(f'get_top_level_cmd_object() -> Command Found (Non-Global): {combined_cmd}')
            return self._register_top_lvl_cmds[combined_cmd]
        
        self.log.debug(f'get_top_level_cmd_object() -> cmd: {cmd} - No Match!!!')
        
        return None

    def clear_completer(self):
        """
        Clear the current completer, removing all suggestions.
        """
        self.session.completer = None

    def _process_prompt_feeder_line(self, line: List[str]) -> List[str]:
        """
        Processes a single line from the prompt feeder.

        This method checks if the line contains any remark symbols and skips it if so.
        Additionally, it updates the execution mode if the line contains the 'enable' command.

        Args:
            line (List[str]): The line to be processed, represented as a list of strings.

        Returns:
            List[str]: The processed line, or an empty list if the line is a remark or contains the 'enable' command.
        """
        # Check if the line is empty
        if not line:
            return []
        
        # Check if the input contains any remark symbols, if so, skip line
        if any(line[0].startswith(symbol) for symbol in RouterPrompt.PROMPT_REMARK_SYMBOL):
            return []
        
        # Check if the line starts with the 'enable' command
        if line[0] == 'enable':
            self.execute_mode = ExecMode.PRIV_MODE
            self.update_prompt()
            return []

        return line

    def _read_prompt_file(self, pf: PromptFeeder , sleep_ms: float=200) -> bool:
       
        self.log.debug(f'_read_prompt_file() PromptFeed: {pf.__str__()} - sleep_ms: {sleep_ms}')
       
        while pf.length():
            
            line = pf.next()
            self.log.debug(f'Line: {line}')
            line = self._process_prompt_feeder_line(line)
            
            if sleep_ms > 0:
                sleep((sleep_ms/1000))
            
            if self._process_command(line):
                break
                    
        return STATUS_OK

    def start(self, pf : PromptFeeder = None) -> bool:
        """
        Start the process with an optional prompt feeder.

        Args:
            pf PromptFeeder`: The optional prompt feeder object.

        Returns:
            bool: STATUS_OK if the process starts successfully, STATUS_NOK otherwise.
        """
        self._DEBUG_print_top_lvl_cmds()
        
        if self.load_prompt_feeder(pf):
            self.log.debug('Invalid PromptFeeder Object')
        
        # PromptFeeder Has Priority
        if self.get_prompt_feeder().length():
            self.log.debug(f'PromptFeeder, has {self.get_prompt_feeder().length()} entries')
            self._read_prompt_file(self.get_prompt_feeder())
            return STATUS_OK
        
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

        return STATUS_OK

    def _get_command(self) -> list:
        """
        Get the user command from the prompt.

        Returns:
            list: The user command split into components.
        """
        command = self.rs_prompt()
        self.log.debug(f'start-cmd: {command}')
        return command

    def _process_command(self, commands: list) -> bool:
        """
        Process the user command.

        Args:
            commands (list): The user command split into components.

        Returns:
            bool: STATUS_OK if the loop should exit, STATUS_NOK otherwise.
        """
        if not commands or not commands[0]:
            self.log.debug('No command input')
            return STATUS_OK

        # TODO Need to provide and overload method
        if 'end' in commands[0]:
            return STATUS_NOK

        if '?' in commands[0]:
            return STATUS_OK
        
        if self._execute_commands(commands[0], commands):
            print(f"Command {commands[0]} not found.")
            
        else:
            self.log.debug(f'Command: {commands} Executed!!!')

        return STATUS_OK

    def _execute_commands(self, cmd: str, args: list) -> bool:
        """
        Execute the given command with its arguments.

        Args:
            cmd (str): The command to execute.
            args (list): The arguments for the command.

        Returns:
            bool: True if the command was executed successfully, False otherwise.
        """
        self.log.debug(f'_execute_commands() -> cmd: {cmd} -> args: {args}')
        
        try:
            cmd_object = self.get_top_level_cmd_object(args)
                        
            return cmd_object.execute(args)
        
        except Exception as e:
            self.log.debug(f'Error _execute_commands() {cmd}: {e}')
            return STATUS_NOK
            
    def _DEBUG_print_top_lvl_cmds(self):
        """
        Print the top-level commands with each key-value pair on a new line.
        """
        # formatted_cmds = "\n".join([f"{key}\t\t\t{value}" for key, value in self._register_top_lvl_cmds.items()])
        # self.log.debug(f"TOP-LVL-CMD:\n{formatted_cmds}")
                   