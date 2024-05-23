import inspect
import logging
import re

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from lib.cli.base.exec_priv_mode import ExecMode
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.common.strings import StringFormats

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
    
class CmdPrompt(CmdInterface):
    """
    Implementation of command prompt interface.
    """

    _nested_dict = {}
    _help_dict = {}
    
    def __init__(self, global_commands: bool, exec_mode: ExecMode) -> None:
        """
        Initializes command prompt instance.

        Args:
            global_commands (bool): Indicates if the commands are global.
            exec_mode (ExecMode): The execution mode of the command prompt.
        """
        self.CLASS_NAME = self.__class__.__name__.lower()
        self.IS_GLOBAL = global_commands

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CMD_PROMPT)
                
    def getClassStartCmd(self) -> str:
        """
        Get the class start command.

        Returns:
            str: The class start command.
        """
        self.log.debug(f'Class Name String lower: {self.CLASS_NAME}')
        return self.CLASS_NAME
            
    def execute(self, subcommand: list = None) -> bool:
        """
        Execute a subcommand.

        Args:
            subcommand (list, optional): Subcommand to execute. Defaults to None.
        
        Returns:
            bool: STATUS_OK indicating the execution was successful, else STATUS_NOK.
        """
        if not subcommand:
            self.log.error(f'SubCommand Not Found')
            return STATUS_NOK
        
        self.log.debug(f'SubCmd: {subcommand}')
        
        if subcommand[0] == '?':
            self.help()
            return STATUS_OK
        
        in_class_method = f'{self.getClassStartCmd()}_{subcommand[0]}'
        self.log.debug(f'Subcommand: {subcommand} - InClassSearch: {in_class_method}')

        if  hasattr(self, in_class_method) and callable(getattr(self, in_class_method)):
            self.log.debug(f'Subcommand: {subcommand} - InClassSearch: {in_class_method} - FOUND!!!')
            getattr(self, in_class_method)(subcommand)
        
        else:
            self.log.error('Invalid subcommand format')
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
            return CmdPrompt._nested_dict[self.CLASS_NAME]
        
        try:
            if not isinstance(CmdPrompt._nested_dict, dict):
                raise KeyError("CmdPrompt._nested_dict is not a dictionary.")
            
            if self.CLASS_NAME in CmdPrompt._nested_dict:
                return {self.CLASS_NAME: CmdPrompt._nested_dict[self.CLASS_NAME]}
            
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
    def register_sub_commands(cls, sub_cmds: Optional[List[str]] = None, help: Optional[str] = None):
        """
        Decorator function for registering sub-commands along with their help messages.

        Args:
            sub_cmds (Optional[List[str]]): A list of sub-commands to register. Defaults to None.
            help (Optional[str]): The help message associated with the sub-commands. Defaults to None.

        Returns:
            Callable: The decorator function.
        """  
        def decorator(func):
            
            method_name = func.__name__

            if not bool(re.search(r'\b[a-zA-Z]+_[a-zA-Z0-9]+\b', method_name)):
                logging.fatal(f'Method Call ({method_name}) does not contain a \'_\' ')
                exit()

            command_parts = method_name.split('_')
            
            logging.debug('-----------------------------------------------------------------')
            logging.debug(f'Start -> {CmdPrompt._nested_dict}')
            
            # Accessing class methods using self
            class_start_cmd = command_parts[0]
            base_cmd = command_parts[1]

            # Check if the class name is the leading dict member
            if class_start_cmd not in CmdPrompt._nested_dict.keys():
                logging.debug(f'Create top key: {class_start_cmd}')
                CmdPrompt._nested_dict[class_start_cmd] = {}

            current_level = CmdPrompt._nested_dict[class_start_cmd]
            logging.debug(f'\nregister_sub_commands-Start -> {CmdPrompt._nested_dict} -> Current Level -> {current_level} -> SubCmds: {sub_cmds}')

            # Get the class base commands
            if base_cmd not in current_level:
                logging.debug(f'Create cmd key: {base_cmd}')
                current_level[base_cmd] = {}

            if sub_cmds:
                logging.debug(f'Insert sub-cmds into: {CmdPrompt._nested_dict} -> sub-cmds: {sub_cmds}')
                CmdPrompt._insert_sub_command(current_level[base_cmd], sub_cmds)
            
            if help: 
                cmd_sub_cmd_list = [base_cmd] + sub_cmds
                CmdPrompt._update_help_dict(cmd_sub_cmd_list, help)

            logging.debug(f'End -> {CmdPrompt._nested_dict}')
            logging.debug("")
            
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
                logging.info(f'Appending ({sub_cmd}) in {cmd_dict}')
                tmp_cmd_dict = cmd_dict[sub_cmd]
                CmdPrompt._insert_sub_command(tmp_cmd_dict, sub_cmd_list[1:])
                
            else:
                logging.info(f'Adding ({sub_cmd}) in {cmd_dict}')

                cmd_dict[sub_cmd] = {}
                
                logging.info(f'Inserting -> {cmd_dict[sub_cmd]} into: {cmd_dict}')
                
                # Recurse with the new dictionary level
                CmdPrompt._insert_sub_command(cmd_dict[sub_cmd], sub_cmd_list[1:])
                
        logging.debug(f'Updated cmd_dict: {cmd_dict}')
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
            return self._nested_dict
        except AttributeError:
            return {}
