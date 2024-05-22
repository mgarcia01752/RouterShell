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

    _nested_dict = {}
    
    
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
        
        # self._generate_command_dict()

    def _generate_command_dict(self) -> dict:
        """
        Generate a nested dictionary for command completion based on class methods.

        Returns:
            dict: Nested dictionary for command completion.
        """
        commands = self.get_command_list()
        
        if not self.isGlobal():
            CmdPrompt._nested_dict = {self.CLASS_NAME: {}}

        for cmd in commands:
            
            parts = cmd.split('_')
            self.log.debug(f'cmd-parts: {parts}')
            
            if not self.isGlobal():
                nest_dict_key_value = CmdPrompt._nested_dict[self.CLASS_NAME]
                
            else:
                nest_dict_key_value = CmdPrompt._nested_dict
                
            self.log.debug(f'cmd-parts: {nest_dict_key_value}')
            
            for part in parts:
                self.log.debug(f'Part: {part} -> {parts}')
                if part not in nest_dict_key_value:
                    nest_dict_key_value[part] = {}
                nest_dict_key_value = nest_dict_key_value[part]

        self.log.debug(f'Nested-Cmds: {CmdPrompt._nested_dict}')
        
        return CmdPrompt._nested_dict
        
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
        return CmdPrompt._nested_dict
    
    def isGlobal(self) -> bool:
        return self.IS_GLOBAL
    
    def help(self) -> None:
        """
        Display help for available commands.
        """
        pass


    @classmethod
    def register_command(self, base_class_command, subcommands: list = None):
        
        def decorator(func):
            print('-----------------------------------------------------------------')
            print(f'Start -> {CmdPrompt._nested_dict}')
            
            # Accessing class methods using self
            class_start_cmd = 'show'

            # Check if the class name is the leading dict member
            if class_start_cmd not in CmdPrompt._nested_dict.keys():
                print(f'Create top key: {class_start_cmd}')
                CmdPrompt._nested_dict[class_start_cmd] = {}

            current_level = CmdPrompt._nested_dict[class_start_cmd]
            print(f'\nregister_command-Start -> {CmdPrompt._nested_dict} -> Current Level -> {current_level} -> SubCmds: {subcommands}')

            # Get the class base commands
            if base_class_command not in current_level:
                print(f'Create cmd key: {base_class_command}')
                current_level[base_class_command] = {}

            if subcommands:
                print(f'Insert sub-cmds into: {CmdPrompt._nested_dict} -> sub-cmds: {subcommands}')
                CmdPrompt._insert_sub_command(current_level[base_class_command], subcommands)

            print(f'End -> {CmdPrompt._nested_dict}')
            print()
            
            # No need for a wrapper if it just calls the original function
            return func

        return decorator

    @staticmethod
    def _insert_sub_command_TMP(cmd_dict: dict, sub_cmd_list: list) -> dict:
        
        print(f'insert_sub_command-Start ({cmd_dict} -> {sub_cmd_list})')

        for sub_cmd in sub_cmd_list:
            
            print(f'insert_sub_command -> {cmd_dict} -> {sub_cmd_list} -> {sub_cmd}')
            
            if sub_cmd not in cmd_dict:
                
                print(f'Create sub_cmd key: {sub_cmd}')
                
                temp = {}
                temp[sub_cmd] = temp
                
                if cmd_dict:
                    print(f'Inserting -> {temp} into: {cmd_dict}')
                    cmd_dict[next(iter(cmd_dict))] = temp
                    
                else:
                    cmd_dict = temp
                
                print(f'insert_sub_command(Update-Next) -> {cmd_dict} -> curr-sub-cmd: ({sub_cmd}) -> new-cmd-list: {sub_cmd_list[1:]}')
                
                CmdPrompt._insert_sub_command(temp, sub_cmd_list[1:])
                
                print(f'insert_sub_command(Updated) -> {cmd_dict}')
                
            else:
                
                print(f'insert_sub_command ({sub_cmd} found in keys) -> {cmd_dict} -> {sub_cmd_list[1:]} -> {sub_cmd} -> {cmd_dict[sub_cmd]}')
                
                CmdPrompt._insert_sub_command(cmd_dict, sub_cmd_list[1:])
                
                return cmd_dict
            
            return cmd_dict
        
        print (f'insert_sub_command-END -> {cmd_dict}')
        print(f'-----------------------------------------------------------------\n')
        return cmd_dict
    
    @staticmethod
    def _insert_sub_command(cmd_dict: dict, sub_cmd_list: list) -> dict:
        print('----------------------------------------------------------------')
        print(f'insert_sub_command-Start ({cmd_dict} -> {sub_cmd_list})')

        if sub_cmd_list:
            # Get the first entry
            sub_cmd = sub_cmd_list[0]

            # Check if sub-cmd is a key, if so, we access the key to insert the next sub-cmd
            if sub_cmd in cmd_dict:
                print(f'Extending ({sub_cmd}) in {cmd_dict}')
                tmp_cmd_dict = cmd_dict[sub_cmd]
                CmdPrompt._insert_sub_command(tmp_cmd_dict, sub_cmd_list[1:])
            else:
                print(f'Adding ({sub_cmd}) in {cmd_dict}')

                # Create a new dictionary for the new sub-command
                cmd_dict[sub_cmd] = {}

                print(f'Inserting -> {cmd_dict[sub_cmd]} into: {cmd_dict}')
                
                # Recurse with the new dictionary level
                CmdPrompt._insert_sub_command(cmd_dict[sub_cmd], sub_cmd_list[1:])
                
        print(f'Updated cmd_dict: {cmd_dict}')
        return cmd_dict  # Optionally return the updated dictionary for verification


    def get_command_registry(self):
        return CmdPrompt._nested_dict