import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.CommandClassInterface import CmdPrompt
from lib.common.common import Common
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.phy import State
from lib.network_manager.network_interface_factory import NetInterface

class LoopbackConfig(CmdPrompt):

    def __init__(self, net_interface: NetInterface) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.PRIV_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().LOOPBACK_CONFIG)
        self.log.setLevel(logging.DEBUG)
        self.net_interface = net_interface
        
        self.log.debug(f'Loopback: {net_interface.get_interface_name()}')
               
    def loopbackconfig_help(self, args: List=None) -> None:
        """
        Display help for available commands.
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")

    @CmdPrompt.register_sub_commands()         
    def loopbackconfig_description(self, line: List[str] = None) -> bool:
        """
        Configures the description of the loopback network interface.

        This function accepts a potentially nested list of arguments, flattens
        the list, and sets it as the description for the loopback interface.

        Parameters
        ----------
        line : list, optional
            A list of arguments that will be used to set the description of the
            loopback interface. The list can be nested, and the function will
            flatten it to a single level before applying it.

        Returns
        -------
        bool
            The function returns STATUS_OK to indicate that the operation was
            successful.
        """
        self.log.debug(f'loopbackconfig_description -> {line}')
        self.net_interface.set_description(Common.flatten_list(line))
        return STATUS_OK
    
    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])         
    def loopbackconfig_ip(self, args: List[str] = None, negate: bool = False) -> bool:
        """
        Configures the IP address of the loopback interface.

        Args:
            args (List[str], optional): Arguments for the configuration. Expected to contain at least 'address' and a valid IP address.
            negate (bool, optional): Flag to determine if the address should be added or removed. Defaults to False.

        Returns:
            bool: Returns STATUS_OK to indicate the function executed successfully, or STATUS_NOK if there was an error.
        """
        try:
            self.log.debug(f'loopbackconfig_ip -> {args}')
            
            if args is None or not isinstance(args, list) or len(args) < 2:
                self.log.debug(f'Invalid arguments: {args}')
                return STATUS_NOK
            
            if 'address' in args and Common.is_valid_ip(args[1]):
                secondary_addr = False
                secondary_addr = 'secondary' in args
                self.log.debug(f'Inet: {args[1]}, Secondary: {secondary_addr}, Negate: {negate}')
                
                self.net_interface.add_inet_address(args[1], secondary_addr, negate)
                return STATUS_OK
            else:
                self.log.debug(f'Invalid IP address or missing "address" keyword: {args}')
                return STATUS_NOK

        except Exception as e:
            self.log.debug(f'Error in loopbackconfig_ip: {e}')
            return STATUS_NOK

    @CmdPrompt.register_sub_commands(nested_sub_cmds=['address', 'secondary'])         
    def loopbackconfig_ipv6(self, args: List=None, negate: bool=False) -> bool:
        self.log.debug(f'loopbackconfig_ipv6 -> {args}')
        return STATUS_OK

    @CmdPrompt.register_sub_commands()         
    def loopbackconfig_shutdown(self, args: List[str] = None, negate: bool = False) -> bool:
        """
        Configures the shutdown state of the loopback interface.

        Args:
            args (List[str], optional): Additional arguments for the configuration. Defaults to None.
            negate (bool, optional): Flag to determine the state. If True, set the state to DOWN; otherwise, set to UP. Defaults to False.

        Returns:
            bool: Returns STATUS_OK to indicate the function executed successfully.
        """
        try:
            self.log.debug(f'loopbackconfig_shutdown -> {args}')
            state = State.UP if negate else State.DOWN
            self.net_interface.set_interface_shutdown_state(state)
            return STATUS_OK
        except Exception as e:
            self.log.debug(f'Error in loopbackconfig_shutdown: {e}')
            return STATUS_NOK
        
    @CmdPrompt.register_sub_commands(extend_nested_sub_cmds=['ip', 'ipv6', 'shutdown'])         
    def loopbackconfig_no(self, args: List=None) -> bool:
        self.log.debug(f'loopbackconfig_no -> {args}')
        
        if 'ip' in args:
            return self.loopbackconfig_ip(args, negate=True)
        elif 'ipv6' in args:
            return self.loopbackconfig_ipv6(args, negate=True)
        elif 'shutdown' in args:
            return self.loopbackconfig_shutdown(args, negate=True)
        else:
            print(f"Invalid argument: {args}")
        
        return STATUS_OK    