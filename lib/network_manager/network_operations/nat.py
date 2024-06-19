from enum import Enum
import ipaddress
import logging

from lib.db.nat_db import NatDB
from lib.network_manager.common.sysctl import SysCtl
from lib.common.constants import STATUS_NOK, STATUS_OK

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_operations.network_mgr import NetworkManager

class NATDirection(Enum):
    """
    Enumeration representing NAT directions.

    - `INSIDE`: Indicates NAT is applied to the inside interface.
    - `OUTSIDE`: Indicates NAT is applied to the outside interface.
    """
    INSIDE = 'inside'
    OUTSIDE = 'outside'

class Nat(NetworkManager):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().NAT)
        self.sysctl = SysCtl()

    def enable_ip_forwarding(self, negate: bool = False) -> bool:
        """
        Enable or disable IP forwarding in the system.

        Args:
            negate (bool): If True, disable IP forwarding; if False, enable IP forwarding. (default: False)

        Returns:
            bool: STATUS_OK if IP forwarding was successfully enabled or disabled, STATUS_NOK otherwise.
        """
        self.log.debug(f"enable_ip_forwarding() negate:{negate}")
        if self.sysctl.write_sysctl('net.ipv4.ip_forward', 1 if not negate else 0):
            self.log.error("Failed to set IP forwarding.")
            return STATUS_NOK

        return STATUS_OK

    def create_nat_pool(self, nat_pool_name: str, negate: bool = False) -> bool:
        """
        Create or delete a NAT pool configuration in the NAT database.

        This method allows you to create or delete a NAT pool configuration in the NAT database.
        You can specify the `nat_pool_name` to create or delete, and set `negate` to True to delete
        the NAT pool.

        Args:
            - nat_pool_name (str): The name of the NAT pool to create or delete.
            - negate (bool, optional): If STATUS_OK, the method will delete the NAT pool; if False, it will create it (default: STATUS_NOK).

        Returns:
            - bool: STATUS_OK if the operation is successful, STATUS_NOK if there was an error during the operation.

        """
        self.log.debug(f"create_nat_pool() -> NAT Pool: {nat_pool_name} -> negate: {negate}")
        
        try:
            if NatDB().pool_name_exists(nat_pool_name):
                self.log.error(f"Can Not create NAT pool '{nat_pool_name}' does exist.")
                return STATUS_NOK

            if negate:
                result = NatDB().delete_global_nat_pool_name(nat_pool_name)
                self.log.debug(f"Deleting NAT pool: {nat_pool_name}")
            else:
                result = NatDB().insert_global_nat_pool_name(nat_pool_name)
                self.log.debug(f"Creating NAT pool: {nat_pool_name}")
            
            if result:
                self.log.debug(f"Did Not Update NAT pool: {nat_pool_name} -> negate: {negate}")
                return STATUS_NOK
            
            else:
                self.log.debug(f"Updated NAT pool: {nat_pool_name} -> negate: {negate}")
                return STATUS_OK

        except Exception as e:
            self.log.error(f"An error occurred while creating or deleting NAT pool: {e}")
            return STATUS_NOK

    def create_nat_ip_pool(self, nat_pool_name: str,
                        nat_inside_ip_start: ipaddress.IPv4Address,
                        nat_inside_ip_end: ipaddress.IPv4Address,
                        nat_outside_ip_address: ipaddress.IPv4Address = None,
                        nat_outside_ifName: str = None,
                        negate: bool = False) -> bool:
        """
        Create a NAT pool.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            nat_inside_ip_start (ipaddress.IPv4Address): Start IP address of the NAT pool.
            nat_inside_ip_end (ipaddress.IPv4Address): End IP address of the NAT pool.
            nat_outside_ip_address (ipaddress.IPv4Address, optional): External IP address for NAT (mutually exclusive with nat_outside_ifName).
            nat_outside_ifName (str, optional): Name of the external interface (mutually exclusive with nat_outside_ip_address).

        Returns:
            bool: True if NAT pool creation is successful, False otherwise.
        """
        self.log.debug(f"create_nat_ip_pool()")
        try:
            if nat_outside_ip_address:
                outside_nat_arg = f"--to-source {nat_outside_ip_address}"
            elif nat_outside_ifName:
                outside_nat_arg = f"--to-source {nat_outside_ifName}"
            else:
                raise ValueError("Either nat_outside_ip_address or nat_outside_ifName must be provided")

            command = f'iptables -t nat -A POSTROUTING -s {nat_inside_ip_start}-{nat_inside_ip_end} -j SNAT {outside_nat_arg}'
            self.log.debug(f"Adding NAT CMD: {command}")

            result = self.run([command])
            if result.exit_code:
                self.log.error(f"Failed to create NAT pool: {result.stderr}")
                self.log.error(command)
                return STATUS_NOK
            return STATUS_OK
        except Exception as e:
            self.log.error(f"An error occurred while creating NAT pool: {e}")
            return STATUS_NOK
    
    def apply_nat_acl_to_pool(self, in_out: NATDirection, acl_id, nat_pool_name) -> bool:
        '''
        ip nat inside source list <acl-id> pool <nat-pool-name>
        '''
        
        direction = 'inside' if in_out == NATDirection.INSIDE else 'outside'
        command = f'ip nat {direction} source list {acl_id} pool {nat_pool_name}'
        
        result = self.run([command])
        if result.exit_code:
            self.log.error(f"Failed to apply NAT ACL to pool: {result.stderr}")
            return STATUS_NOK
        
        return STATUS_OK

    def create_outside_nat(self, nat_pool_name: str, interface_name: str, negate: bool = False) -> bool:
        """
        Create or destroy outside NAT (Source NAT) rule.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            interface_name (str): Name of the external or outside facing interface.
            negate (bool, optional): True to destroy the NAT rule, False to create it. Defaults to False.

        Returns:
            bool: STATUS_OK if the NAT rule is created or destroyed successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"create_outside_nat() -> Pool: {nat_pool_name} -> Interface: {interface_name} -> negate: {negate}")
        
        nat_pool = NatDB().pool_name_exists(nat_pool_name)
        
        if not nat_pool:
            self.log.error(f"NAT pool {nat_pool_name} not found.")
            return STATUS_NOK

        if NatDB().is_interface_direction_in_nat_pool(interface_name, nat_pool_name, NATDirection.INSIDE.value).status:
            self.log.error(f"Cannot create outside NAT rule for NAT pool {nat_pool_name} "
                            "with active inside interfaces. Delete inside interfaces first.")
            return STATUS_NOK

        try:
            create_destroy = '-D' if negate else '-A'
            
            command = f'iptables -t nat {create_destroy} POSTROUTING -o {interface_name} -j MASQUERADE'
            result = self.run(command.split())
            if result.exit_code:
                self.log.error(f"Failed to {'destroy' if negate else 'create'} outside NAT rule: {result.stderr}")
                self.log.error(command)
                return STATUS_NOK

            if not negate:
                if NatDB().add_outside_interface(nat_pool_name, interface_name):
                    self.log.error(f"Unable to add outside interface: {interface_name} to NAT pool: {nat_pool_name} via DB")
                    return STATUS_NOK
            else:
                NatDB().delete_outside_interface(interface_name)

            return STATUS_OK
        except Exception as e:
            self.log.error(f"An error occurred while {'destroying' if negate else 'creating'} outside NAT rule: {e} via OS")
            return STATUS_NOK

    def create_inside_nat(self, nat_pool_name: str, ifName_inside: str, negate: bool = False) -> bool:
        """
        Create or destroy inside NAT (Source NAT) rule.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            ifName_inside (str): Name of the internal interface.
            negate (bool, optional): True to destroy the NAT rule, False to create it. Defaults to False.

        Returns:
            bool: STATUS_OK if the NAT rule is created or destroyed successfully, STATUS_NOK otherwise.
        """
 
        nat_pool = NatDB().pool_name_exists(nat_pool_name)
        if not nat_pool:
            self.log.error(f"NAT pool {nat_pool_name} not found.")
            return STATUS_NOK

        if NatDB().is_interface_direction_in_nat_pool(ifName_inside, 
                                                      nat_pool_name,
                                                      NATDirection.INSIDE.value).status:
            '''Not an error, just a check in case we are re-applying'''
            self.log.debug(f"Interface {ifName_inside} is part of {NATDirection.INSIDE.value} NAT pool {nat_pool_name}")
            return STATUS_NOK
        
        outside_nat_interfaces = NatDB().get_interface_direction_in_nat_pool_list(nat_pool_name, NATDirection.OUTSIDE.value)
        
        if len(outside_nat_interfaces) > 1:
            self.log.error(f"More than 1 interfaces are defined in: {nat_pool}.  DataBase ERROR")
            return STATUS_NOK

        outside_nat_interface = outside_nat_interfaces[0]
        
        if outside_nat_interface.status:
            self.log.error(f'Unable to retrieve outside NAT interface: {outside_nat_interface.reason}')
            return STATUS_NOK
            
        outside_nat_interface = outside_nat_interface.result
        
        outside_nat_if_ip_addr = self.get_interface_ip_addresses(outside_nat_interface['InterfaceName'], 'ipv4')
        
        self.log.debug(f"NAT-Pool: {nat_pool_name} -> Out-NAT-ifName: {outside_nat_interface} -> Out-NAT-Inet: {outside_nat_if_ip_addr}")

        if not outside_nat_if_ip_addr:
            self.log.error(f"No IPv4 address assigned to outside NAT interface: {outside_nat_interface}")
            return STATUS_NOK
        
        try:
            create_destroy = '-D' if negate else '-A'
            
            command = f'iptables -t nat {create_destroy} PREROUTING -i {ifName_inside} -j DNAT --to-destination {outside_nat_if_ip_addr[0]}'
            self.log.debug(f"create_inside_nat() -> cmd: {command}")
            
            result = self.run(command.split())
            
            if result.exit_code:
                self.log.error(f"Failed to {'destroy' if negate else 'create'} inside NAT rule: {result.stderr}")
                return STATUS_NOK

            if negate:
                if NatDB().delete_inside_interface(nat_pool_name, ifName_inside):
                    self.log.error(f"Unable to destroy NAT pool: {nat_pool_name} from interface: {ifName_inside} inside interface to DB")
                    return STATUS_NOK

            else:
                if NatDB().add_inside_interface(nat_pool_name, ifName_inside):
                    self.log.error(f"Unable to add NAT pool: {nat_pool_name} to interface: {ifName_inside} inside interface to DB")
                    return STATUS_NOK

            return STATUS_OK
        
        except Exception as e:
            self.log.error(f"An error occurred while {'destroying' if negate else 'creating'} inside NAT rule: {e}")
            return STATUS_NOK
    
    def create_fw_nat_rule(self, in_ifName: str, out_ifName: str) -> bool:
        '''
        sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
        sudo iptables -A INPUT -i Gig0 -j ACCEPT
        sudo iptables -A FORWARD -i Gig0 -o Gig1 -j ACCEPT
        '''

        # INPUT chain rules
        input_rules = [
             'iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT',
            f'iptables -A INPUT -i {in_ifName} -j ACCEPT'
        ]

        # FORWARD chain rules
        forward_rules = [
            f'iptables -A FORWARD -i {in_ifName} -o {out_ifName} -j ACCEPT'
        ]

        for rule in input_rules + forward_rules:
            
            result = self.run([rule])
            
            if result.exit_code:
                self.log.error(f"Unable to apply fire-wall NAT rule: {result.stderr}")    
                return STATUS_NOK

        return STATUS_OK

    def flush_nat_configuration(self) -> None:
        """
        Flush NAT configurations and reset the NAT pool Data Base.

        This method performs the following actions:
        1. Flush the NAT rules in the nat table.
        2. Flush the NAT rules in the mangle table (if used for NAT).
        3. Delete any user-defined chains in the nat table (optional).
        4. Delete any user-defined chains in the mangle table (optional).
        5. Flush the NAT rules in the nat table for IPv6.
        6. Delete any user-defined chains in the nat table for IPv6 (optional).
        7. Reset NatPool Database.

        Note:
        - This method uses the 'sudo' command to execute iptables and ip6tables commands.
        - Ensure that your NatPoolDB class has a proper method or logic to destroy NatPoolDB.

        Returns:
        None
        """
        # Flush the NAT rules in the nat table
        self.run(['sudo', 'iptables', '-t', 'nat', '-F'], suppress_error=True)

        # Flush the NAT rules in the mangle table (if used for NAT)
        self.run(['sudo', 'iptables', '-t', 'mangle', '-F'], suppress_error=True)

        # Delete any user-defined chains in the nat table (optional)
        self.run(['sudo', 'iptables', '-t', 'nat', '-X'], suppress_error=True)

        # Delete any user-defined chains in the mangle table (optional)
        self.run(['sudo', 'iptables', '-t', 'mangle', '-X'], suppress_error=True)

        # Flush the NAT rules in the nat table for IPv6
        self.run(['sudo', 'ip6tables', '-t', 'nat', '-F'], suppress_error=True)

        # Delete any user-defined chains in the nat table for IPv6 (optional)
        self.run(['sudo', 'ip6tables', '-t', 'nat', '-X'], suppress_error=True)

        NatDB().reset_db()
        
    def getNatIpTable(self) -> str:
        command = "iptables -t nat -L"
        out = self.run(command.split())
        return out.stdout