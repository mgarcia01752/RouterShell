import inspect
import logging

from abc import ABC, abstractmethod
from lib.cli.base.exec_priv_mode import ExecMode
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS

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

    def __init__(self, global_commands: bool, exec_mode: ExecMode) -> None:
        """
        Initializes command prompt instance.

        Args:
            global_commands (bool): Indicates if the commands are global.
            exec_mode (ExecMode): The execution mode of the command prompt.
        """
        self.CLASS_NAME = self.__class__.__name__.lower()
        self.IS_GLOBAL = global_commands
        self._nested_dict = {}

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().CMD_PROMPT)
        
        self._generate_command_dict()

    def _generate_command_dict(self) -> dict:
        """
        Generate a nested dictionary for command completion based on class methods.

        Returns:
            dict: Nested dictionary for command completion.
        """
        commands = self.get_command_list()
        
        if not self.isGlobal():
            self._nested_dict = {self.CLASS_NAME: {}}

        for cmd in commands:
            
            parts = cmd.split('_')
            self.log.debug(f'cmd-parts: {parts}')
            
            if not self.isGlobal():
                nest_dict_key_value = self._nested_dict[self.CLASS_NAME]
                
            else:
                nest_dict_key_value = self._nested_dict
                
            self.log.debug(f'cmd-parts: {nest_dict_key_value}')
            
            for part in parts:
                self.log.debug(f'Part: {part} -> {parts}')
                if part not in nest_dict_key_value:
                    nest_dict_key_value[part] = {None}
                nest_dict_key_value = nest_dict_key_value[part]

        self.log.debug(f'Nested-Cmds: {self._nested_dict}')
        
        return self._nested_dict
        
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

    def get_command_dict(self):
        """
        Get a nested dictionary of available commands.

        Returns:
            dict: Nested dictionary of available commands.
        """
        return self._nested_dict
    
    def isGlobal(self) -> bool:
        return self.IS_GLOBAL
    
    def help() -> None:
        """
        Display help for available commands.
        """
        pass