from enum import Enum
import ipaddress
import logging

from lib.network_manager.inet import InetServiceLayer
from lib.db.nat_db import NatDB
from lib.network_manager.sysctl import SysCtl
from lib.common.constants import STATUS_NOK, STATUS_OK


class NATDirection(Enum):
    """
    Enumeration representing NAT directions.

    - `INSIDE`: Indicates NAT is applied to the inside interface.
    - `OUTSIDE`: Indicates NAT is applied to the outside interface.
    """
    INSIDE = 'inside'
    OUTSIDE = 'outside'

class Nat(InetServiceLayer):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
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
        Create or destroy a NAT pool.

        Args:
            nat_pool_name (str): The name of the NAT pool to create or destroy.
            negate (bool, optional): True to destroy the NAT pool, False to create it. Defaults to False.
        """
        self.log.debug(f"create_nat_pool() nat-pool: {nat_pool_name} -> negate:{negate}")
        
        # Check if the NAT pool with the given name already exists in your database
        if nat_pool_name in NatDB().nat_pool_db:
            if negate:
                NatDB().delete_global_pool_name(nat_pool_name)
                self.log.info(f"Destroyed NAT pool: {nat_pool_name}")
            else:
                self.log.warn(f"NAT pool with the name {nat_pool_name} already exists.")
        else:
            if negate:
                self.log.warn(f"NAT pool with the name {nat_pool_name} does not exist.")
            else:
                nat_pool = NatDB().create_global_pool_name(nat_pool_name)
                self.log.info(f"Created NAT pool: {nat_pool}")
    
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
        try:
            if nat_outside_ip_address:
                outside_nat_arg = f"--to-source {nat_outside_ip_address}"
            elif nat_outside_ifName:
                outside_nat_arg = f"--to-source {nat_outside_ifName}"
            else:
                raise ValueError("Either nat_outside_ip_address or nat_outside_ifName must be provided")

            command = f'iptables -t nat -A POSTROUTING -s {nat_inside_ip_start}-{nat_inside_ip_end} -j SNAT {outside_nat_arg}'
            self.log.info(f"Adding NAT CMD: {command}")

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

    def create_outside_nat(self, nat_pool_name: str, ifName: str, negate: bool = False) -> bool:
        """
        Create or destroy outside NAT (Source NAT) rule.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            ifName (str): Name of the external interface.
            negate (bool, optional): True to destroy the NAT rule, False to create it. Defaults to False.

        Returns:
            bool: STATUS_OK if the NAT rule is created or destroyed successfully, STATUS_NOK otherwise.
        """
        self.log.info(f"create_outside_nat() -> Pool: {nat_pool_name} -> Interface: {ifName} -> negate: {negate}")
        
        create_destroy = '-D' if negate else '-A'

        # Check if the NAT pool exists
        nat_pool = NatDB().get_pool(nat_pool_name)
        if not nat_pool:
            self.log.error(f"NAT pool {nat_pool_name} not found.")
            return STATUS_NOK

        # Check if there are inside interfaces associated with the NAT pool
        if not negate and nat_pool.inside_interfaces:
            self.log.error(f"Cannot create outside NAT rule for NAT pool {nat_pool_name} "
                            "with active inside interfaces. Delete inside interfaces first.")
            return STATUS_NOK

        try:
            command = f'iptables -t nat {create_destroy} POSTROUTING -o {ifName} -j MASQUERADE'
            result = self.run(command.split())
            if result.exit_code:
                self.log.error(f"Failed to {'destroy' if negate else 'create'} outside NAT rule: {result.stderr}")
                self.log.error(command)
                return STATUS_NOK

            if not negate:
                if NatDB().set_outside_interface(nat_pool_name, ifName):
                    self.log.error(f"Unable to add outside interface: {ifName} to NAT pool: {nat_pool_name}")
                    return STATUS_NOK
            else:
                NatDB().delete_outside_interface(ifName)

            return STATUS_OK
        except Exception as e:
            self.log.error(f"An error occurred while {'destroying' if negate else 'creating'} outside NAT rule: {e}")
            return STATUS_NOK

    def create_inside_nat(self, nat_pool_name: str, inside_ifName: str, negate: bool = False) -> bool:
        """
        Create or destroy inside NAT (Source NAT) rule.

        Args:
            nat_pool_name (str): Name of the NAT pool.
            inside_ifName (str): Name of the internal interface.
            negate (bool, optional): True to destroy the NAT rule, False to create it. Defaults to False.

        Returns:
            bool: STATUS_OK if the NAT rule is created or destroyed successfully, STATUS_NOK otherwise.
        """
        create_destroy = '-D' if negate else '-A'

        # Check if the NAT pool exists
        nat_pool = NatDB().get_pool(nat_pool_name)
        if not nat_pool:
            self.log.error(f"NAT pool {nat_pool_name} not found.")
            return STATUS_NOK

        # Check if the inside interface is part of the NAT pool
        if inside_ifName not in nat_pool.inside_interfaces:
            self.log.info(f"Inside interface {inside_ifName} is not part of NAT pool {nat_pool_name}")

        # Check if an outside interface is defined in the NAT pool
        outside_nat_ifName = NatDB().get_outside_interface(nat_pool_name)
        if not outside_nat_ifName:
            self.log.error(f"Define an outside interface before creating inside NAT rules for poll: {nat_pool}.")
            return STATUS_NOK

        if outside_nat_ifName == inside_ifName:
            self.log.error(f"Outside interface and inside interface cannot be the same in NAT pool {nat_pool_name}.")
            return STATUS_NOK

        outside_nat_ip_addr = self.get_interface_ip_addresses(outside_nat_ifName, 'ipv4')
        self.log.info(f"NAT-Pool: {nat_pool_name} -> Out-NAT-ifName: {outside_nat_ifName} -> Out-NAT-Inet: {outside_nat_ip_addr}")

        if not outside_nat_ip_addr:
            self.log.error(f"No IPv4 address assigned to outside NAT interface: {outside_nat_ifName}")
            return STATUS_NOK
        
        try:
            command = f'iptables -t nat {create_destroy} PREROUTING -i {inside_ifName} -j DNAT --to-destination {outside_nat_ip_addr[0]}'
            result = self.run(command.split())
            
            if result.exit_code:
                self.log.error(f"Failed to {'destroy' if negate else 'create'} inside NAT rule: {result.stderr}")
                return STATUS_NOK

            if negate:
                NatDB().delete_inside_interface(nat_pool_name, inside_ifName)
            else:
                NatDB().add_inside_interface(nat_pool_name, inside_ifName)

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