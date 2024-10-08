import inspect
import logging
import re

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.prompt_response import PromptResponse
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.common.string_formats import StringFormats

class CmdInterface(ABC):
    """
    Interface defining common command methods.
    """

    @abstractmethod
    def isGlobal(self) -> bool:
        """
        Check if the command is a global command.

        Returns:
            bool: True if the command is global, False otherwise.
        """
        pass
    
    @abstractmethod
    def getClassStartCmd(self) -> str:
        """
        Get the class start command.

        Returns:
            str: The class start command.
        """
        pass
    
    @abstractmethod
    def execute(self, subcommand: list = None) -> bool:
        """
        Execute a subcommand.

        Args:
            subcommand (list, optional): Subcommand to execute. Defaults to None.
        
        Returns:
            bool: Status indicating whether the execution was successful.
        """
        pass
    
    @abstractmethod
    def class_methods(self) -> list:
        """
        Get a list of class methods.

        Returns:
            list: List of class methods.
        """
        pass
    
    @abstractmethod
    def get_command_list(self) -> list:
        """
        Get a list of available commands.

        Returns:
            list: List of available commands.
        """
        pass
    
    @abstractmethod
    def get_command_dict(self):
        """
        Get a nested dictionary of available commands.

        Returns:
            dict: Nested dictionary of available commands.
        """
        pass
    
    @abstractmethod
    def help(self) -> None:
        """
        Display help for available commands.
        """
        pass
    
class CmdPrompt(CmdInterface, PromptResponse):
    """
    Implementation of command prompt interface.
    """
    
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log = logging.getLogger(__name__)
    
    # STATIC
    _nested_word_complete_cmd_dict = {}
    _word_complete_cmd_list = []
    _help_dict = {}
    
    def __init__(self, global_commands: bool, 
                 exec_mode: ExecMode
                 ) -> None:
        """
        Initializes command prompt instance.

        Args:
            global_commands (bool): Indicates if the commands are global.
            exec_mode (ExecMode): The execution mode of the command prompt.
        """
        self.CLASS_NAME = self.__class__.__name__.lower()
        self.IS_GLOBAL = global_commands

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().CMD_PROMPT)
                
    def getClassStartCmd(self) -> str:
        """
        Get the class start command.

        Returns:
            str: The class start command.
        """
        self.log.debug(f'Class Name String lower: {self.CLASS_NAME}')
        return self.CLASS_NAME
            
    def execute(self, commands: list) -> bool:
        """
        Execute a subcommand.

        Args:
            commands (list): Commands to execute. Defaults.
        
        Returns:
            bool: STATUS_OK indicating the execution was successful, else STATUS_NOK.
        """
        if not commands:
            self.log.error(f'Command(s) Not Found')
            return STATUS_NOK
                
        self.log.debug(f'execute() -> Commands: {commands}')
        
        if not self.isGlobal():
            commands = commands[1:]
        
        if commands[0] == '?':
            self.help()
            return STATUS_OK
        
        in_class_method_args = {}
        in_class_method = f'{self.getClassStartCmd()}_{commands[0]}'
        
        if commands[1:]:
            in_class_method_args = commands[1:]
                        
        if  hasattr(self, in_class_method) and callable(getattr(self, in_class_method)):
            self.log.debug(f'execute() -> InClassSearch: {in_class_method} -> Args: {commands} - FOUND!!!')
            getattr(self, in_class_method)(in_class_method_args)
        
        else:
            self.log.error('Invalid command format.')
            return STATUS_NOK
        
        return STATUS_OK

    def class_methods(self) -> list:
        """
        Get a list of class methods.

        Returns:
            list: List of class methods.
        """
        return [attr for attr in dir(self) if attr.startswith(f'{self.CLASS_NAME}') 
                and inspect.ismethod(getattr(self, attr))]
  
    def get_command_list(self) -> list:
        """
        Get a list of available commands.

        Returns:
            list: List of available commands.
        """
        elements = self.class_methods()
        prefix_length = len(self.CLASS_NAME) + 1
        return [element[prefix_length:] if element.startswith(f"{self.CLASS_NAME}_") else element for element in elements]

    def get_command_dict(self, skip_top_key: bool=False) -> dict:
        """
        Get a nested dictionary of available commands.

        This method retrieves a nested dictionary of commands associated 
        with the current class name from the CmdPrompt's nested dictionary.

        Returns:
            dict: A nested dictionary containing available commands for the class.
                If the class name is not found, an empty dictionary is returned.

        Raises:
            KeyError: If CmdPrompt._nested_dict is not defined or not a dictionary.
        """
        if (skip_top_key):
            self.log.debug(f'Provide only the Values from Class: {self.CLASS_NAME}')
            return CmdPrompt._nested_word_complete_cmd_dict[self.CLASS_NAME]
        
        try:
            if not isinstance(CmdPrompt._nested_word_complete_cmd_dict, dict):
                raise KeyError("CmdPrompt._nested_dict is not a dictionary.")
            
            if self.CLASS_NAME in CmdPrompt._nested_word_complete_cmd_dict:
                return {self.CLASS_NAME: CmdPrompt._nested_word_complete_cmd_dict[self.CLASS_NAME]}
            
            else:
                return {}
        
        except KeyError as e:
            self.log.error(f"Error accessing command dictionary: {e}")
            return {}
      
    def isGlobal(self) -> bool:
        return self.IS_GLOBAL
    
    def help(self) -> None:
        """
        Display help for available commands.
        """
        pass
    

    @classmethod
    def register_sub_commands(cls,
                              sub_cmds: Optional[List[str]] = None, 
                              nested_sub_cmds: Optional[List[str]] = None,
                              extend_nested_sub_cmds: Optional[List[str]] = None,
                              append_nested_sub_cmds: Optional[List[str]] = None,   
                              help: Optional[str] = None):
        """
        Decorator function for registering sub-commands along with their help messages.

        Args:
            sub_cmds (Optional[List[str]]): A list of sub-commands to register. Defaults to None.
            nested_sub_cmds: (Optional[List[str]]): A list of sub-commands to register. Defaults to None.
            extend_nested_sub_cmds (Optional[List[str]]): A list of additional sub-commands to extend the registration. Defaults to None.
            append_nested_sub_cmds (Optional[List[str]]): A list of additional sub-commands to append the registration. Defaults to None.
            help (Optional[str]): The help message associated with the sub-commands. Defaults to None.

        Returns:
            Callable: The decorator function.
        """

        def decorator(func):
            
            method_name = func.__name__

            if not bool(re.search(r'\b[a-zA-Z]+_[a-zA-Z0-9]+\b', method_name)):
                CmdPrompt.log.fatal(f'Method Call ({method_name}) does not contain a \'_\' ')
                exit()

            command_parts = method_name.split('_')
            
            CmdPrompt.log.debug('-----------------------------------------------------------------')
            CmdPrompt.log.debug(f'Start -> {CmdPrompt._nested_word_complete_cmd_dict}')
            
            # Accessing class methods using self
            class_start_cmd = command_parts[0]
            base_cmd = command_parts[1]

            # Check if the class name is the leading dict member
            if class_start_cmd not in CmdPrompt._nested_word_complete_cmd_dict.keys():
                logging.debug(f'Create top key: {class_start_cmd}')
                CmdPrompt._nested_word_complete_cmd_dict[class_start_cmd] = {}

            current_level = CmdPrompt._nested_word_complete_cmd_dict[class_start_cmd]
            logging.debug(f'\nregister_sub_commands-Start -> {CmdPrompt._nested_word_complete_cmd_dict} -> Current Level -> {current_level} -> SubCmds: {nested_sub_cmds} -> ExtSubCmd: {extend_nested_sub_cmds}')

            # Get the class base commands
            if base_cmd not in current_level:
                CmdPrompt.log.debug(f'Create cmd key: {base_cmd}')
                current_level[base_cmd] = {}

            if nested_sub_cmds and extend_nested_sub_cmds:
                
                append_cmd_list = [nested_sub_cmds] + [nested_sub_cmds[:-1] + [e] for e in extend_nested_sub_cmds]
                                                             
                CmdPrompt.log.debug(f'Extend sub cmds: {nested_sub_cmds} -> {extend_nested_sub_cmds} -> {append_cmd_list}')
                
                for sub_cmd_set in append_cmd_list:
                    CmdPrompt.log.debug(f'Adding sub-cmd: {sub_cmd_set}')
                    CmdPrompt._insert_sub_command(current_level[base_cmd], sub_cmd_set)

            elif nested_sub_cmds and append_nested_sub_cmds:
                
                append_cmd_list = [nested_sub_cmds + [e] for e in append_nested_sub_cmds]
                                                             
                CmdPrompt.log.debug(f'Append sub cmds: {nested_sub_cmds} -> {append_nested_sub_cmds} -> {append_cmd_list}')
                
                for sub_cmd_set in append_cmd_list:
                    CmdPrompt.log.debug(f'Adding sub-cmd: {sub_cmd_set}')
                    CmdPrompt._insert_sub_command(current_level[base_cmd], sub_cmd_set)

            elif extend_nested_sub_cmds:
                
                for ext_sub_cmd_set in extend_nested_sub_cmds:
                    CmdPrompt.log.debug(f'Adding sub-cmd: {ext_sub_cmd_set}')
                    CmdPrompt._insert_sub_command(current_level[base_cmd], [ext_sub_cmd_set])               
            
            elif nested_sub_cmds:
                CmdPrompt.log.debug(f'Insert sub-cmds into: {CmdPrompt._nested_word_complete_cmd_dict} -> sub-cmds: {nested_sub_cmds}')
                CmdPrompt._insert_sub_command(current_level[base_cmd], nested_sub_cmds)
            
            if help: 
                cmd_sub_cmd_list = [base_cmd] + nested_sub_cmds
                CmdPrompt._update_help_dict(cmd_sub_cmd_list, help)

            CmdPrompt.log.debug(f'End -> {CmdPrompt._nested_word_complete_cmd_dict}')
            CmdPrompt.log.debug("")
            
            def wrapper(*args, **kwargs):
                print(f'Executing {func.__name__} with arguments: {args}, {kwargs}')
                return func(*args, **kwargs)
            
            return func

        return decorator
    
    @staticmethod
    def _insert_sub_command(cmd_dict: dict, sub_cmd_list: list) -> dict:
        logging.debug('----------------------------------------------------------------')
        logging.debug(f'insert_sub_command-Start ({cmd_dict} -> {sub_cmd_list})')

        if sub_cmd_list:
            # Get the first entry
            sub_cmd = sub_cmd_list[0]

            # Check if sub-cmd is a key, if so, we access the key to insert the next sub-cmd
            if sub_cmd in cmd_dict:
                CmdPrompt.log.debug(f'Appending ({sub_cmd}) in {cmd_dict}')
                tmp_cmd_dict = cmd_dict[sub_cmd]
                CmdPrompt._insert_sub_command(tmp_cmd_dict, sub_cmd_list[1:])
                
            else:
                CmdPrompt.log.debug(f'Adding ({sub_cmd}) in {cmd_dict}')

                cmd_dict[sub_cmd] = {}
                
                CmdPrompt.log.debug(f'Inserting -> {cmd_dict[sub_cmd]} into: {cmd_dict}')
                
                # Recurse with the new dictionary level
                CmdPrompt._insert_sub_command(cmd_dict[sub_cmd], sub_cmd_list[1:])
                
        CmdPrompt.log.debug(f'Updated cmd_dict: {cmd_dict}')
        return cmd_dict

    @classmethod
    def _update_help_dict(cls, cmd_list: List[str], msg: str) -> str:
        """
        Update the help dictionary with a message for the given command list.

        Args:
            cmd_list (List[str]): The list of command strings.
            msg (str): The message to be associated with the command list.

        Returns:
            str: The hash value used as the key in the help dictionary.
        """
        str_hash = StringFormats.generate_hash_from_list(cmd_list)
        cls._help_dict[str_hash] = msg
        return str_hash
    
    @classmethod
    def get_help(cls, cmd_list_hash: str) -> str:
        """
        Get the help message associated with the given command list hash.

        Args:
            cmd_list_hash (str): The hash value of the command list.

        Returns:
            str: The help message associated with the command list hash, or an error message if the hash is not found.
        """
        try:
            return cls._help_dict[cmd_list_hash]
        except KeyError:
            return f"Error: No Help"

    def get_command_registry(self) -> Dict[str, dict]:
        """
        Get the command registry containing nested dictionaries of available commands.

        Returns:
            Dict[str, dict]: The nested dictionary of available commands.
        """
        try:
            return self._nested_word_complete_cmd_dict
        except AttributeError:
            return {}
