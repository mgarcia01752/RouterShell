import logging
from typing import List

from lib.cli.common.exec_priv_mode import ExecMode
from lib.cli.common.command_class_interface import CmdPrompt
from lib.common.constants import STATUS_NOK
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLGS
from lib.network_manager.network_operations.dhcp.server.dhcp_server import DhcpPoolFactory


class DhcpPoolConfig(CmdPrompt):
    """
    Class to configure DHCP pool settings.
    
    This class extends CmdPrompt to provide command-line interface functionalities 
    for DHCP pool configuration.
    
    Attributes:
        log (Logger): Logger instance for logging messages.
        _dhcp_pool_factory (DhcpPoolFactory): Factory instance for managing DHCP pools.
    """

    def __init__(self, dhcp_pool_name: str, negate: bool) -> None:
        super().__init__(global_commands=True, exec_mode=ExecMode.USER_MODE)
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().DHCP_POOL_CONFIG)
        
        if negate:
            DhcpPoolFactory(dhcp_pool_name).delete_pool_name()
            return None
        
        self._dhcp_pool_fact = DhcpPoolFactory(dhcp_pool_name)
                   
    def dhcppoolconfig_help(self, args: List = None) -> None:
        """
        Display help for available commands.
        
        Args:
            args (List, optional): List of arguments (not used).
        """
        for method_name in self.class_methods():
            method = getattr(self, method_name)
            print(f"{method.__doc__}")
    
    @CmdPrompt.register_sub_commands()
    def dhcppoolconfig_subnet(self, inet_subnet_cidr: str | list[str]) -> bool:
        """
        Configure a subnet for the DHCP pool.
        
        Args:
            inet_subnet_cidr (str | list[str]): The CIDR notation of the subnet or a list containing one CIDR notation.
        
        Returns:
            bool: STATUS_OK if the subnet was added successfully, STATUS_NOK otherwise.
        """
        # Check if inet_subnet_cidr is a list and ensure it has only one entry
        if isinstance(inet_subnet_cidr, list):
            if len(inet_subnet_cidr) != 1:
                self.log.error(f'Invalid subnet list: {inet_subnet_cidr}. The list must contain exactly one entry.')
                return STATUS_NOK
            inet_subnet_cidr = inet_subnet_cidr[0]  # Flatten the list by taking the first entry

        # Proceed with the subnet configuration
        self.log.debug(f'DHCP pool configuration -> subnet: {inet_subnet_cidr}')
        return self._dhcp_pool_fact.add_pool_subnet(inet_subnet_cidr)

    @CmdPrompt.register_sub_commands()
    def dhcppoolconfig_pool(self, args: List[str]) -> bool:
        """
        Configure the IP range for the DHCP pool.
        
        Args:
            args (List, optional): List of arguments [start_ip, end_ip, subnet_cidr].
        
        Returns:
            bool: STATUS_OK if the pool was added successfully, STATUS_NOK otherwise.
        """
        if len(args) != 3:
            self.log.error(f'pool must have 3 arguments')
            return STATUS_NOK
            
        return self._dhcp_pool_fact.add_inet_pool_range(inet_start=args[0],
                                                        inet_end=args[1],
                                                        inet_subnet_cidr=args[2])

    @CmdPrompt.register_sub_commands()
    def dhcppoolconfig_option(self, args: List[str]) -> bool:
        """
        Configure DHCP options.
        
        Args:
            args (List, optional): List of arguments [option_name, value].
        
        Returns:
            bool: STATUS_OK if the option was added successfully, STATUS_NOK otherwise.
        """
        if len(args) != 2:
            self.log.error(f'dhcp option must have 2 arguments')
            return STATUS_NOK        
        return self._dhcp_pool_fact.add_option(dhcp_option=args[0],
                                                  value=args[1])
