from enum import Enum
import logging

from tabulate import tabulate 
from lib.network_manager.common.mac import MacServiceLayer
from lib.network_manager.common.inet import InetServiceLayer
from lib.network_manager.common.sysctl import SysCtl

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

class Encapsulate(Enum):
    ARPA = 'arpa'
    """arpa Enables encapsulation for an Ethernet 802.3 network."""
    
    FRAME_RELAY = 'frame-relay'
    """frame-relay Enables encapsulation for a Frame Relay network."""
    
    SNAP = 'snap'
    """snap Enables encapsulation for FDDI and Token Ring networks."""
    
class Arp(MacServiceLayer):

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ARP)

    def arp_clear(self, ifName:str=None):
        """
        Clear the ARP cache for a specific network interface or all interfaces.

        :param ifName: The name of the network interface. If None, clears the ARP cache for all interfaces.
        :return: The output of the ARP cache clearing command.
        """
        
        cmd = ['ip', 'neigh', 'flush']

        if ifName:
            cmd.extend(['dev', ifName])
        else:
            cmd.append('all')

        self.log.debug(f"CMD: {cmd}")

        result = self.run(cmd)
        
        return STATUS_OK if result.exit_code else STATUS_NOK

    def set_timeout(self, arp_time_out: int = 300) -> bool:
        """
        Set the ARP cache timeout using sysctl.

        :param arp_time_out: The ARP cache timeout value in seconds.
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        sysctl_param = "net.ipv4.neigh.default.gc_stale_time"
        
        if SysCtl().write_sysctl(sysctl_param, str(arp_time_out)):
            print(f"Unable to setARP cache timeout set to {arp_time_out} seconds.")
            return STATUS_NOK
        else:
            print(f"Set ARP cache timeout to {arp_time_out} seconds.")
        
        return STATUS_OK

    def set_arp_accept(self, ifName: str="all", enable: bool=True) -> bool:
        """
        Enable or disable ARP request acceptance for a specific network interface.

        :param ifName: The name of the network interface.
        :param enable: True to enable ARP request acceptance, False to disable it.
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_accept_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_accept"
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_accept_file, value)

    def set_arp_announce(self, ifName:str, value:int) -> bool:
        """
        Set the ARP announce value for a specific network interface.

        :param ifName: The name of the network interface.
        :param value: The ARP announce value (0, 1, or 2).
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_announce_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_announce"
        return SysCtl().write_sysctl(arp_announce_file, str(value))

    def set_arp_evict_nocarrier(self, ifName: str="all", enable: bool=True) -> bool:
        """
        Enable or disable ARP eviction on no carrier for a specific network interface.

        :param ifName: The name of the network interface. Default is 'all' to apply to all interfaces.
        :param enable: True to enable ARP eviction on no carrier, False to disable it.
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_evict_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_evict_nocarrier"
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_evict_file, value)

    def set_arp_filter(self, ifName: str="all", enable: bool=True) -> bool:
        """
        Enable or disable ARP filtering for a specific network interface.

        :param ifName: The name of the network interface. Default is 'all' to apply to all interfaces.
        :param enable: True to enable ARP filtering, False to disable it.
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_filter_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_filter"
        value = "1" if enable else "0"
        
        return SysCtl.write_sysctl(arp_filter_file, value)

    def set_arp_ignore(self, ifName: str="all", enable: bool=True) -> bool:
        """
        Set the ARP ignore value for a specific network interface.

        :param ifName: The name of the network interface. Default is 'all' to apply to all interfaces.
        :param value: The ARP ignore value (0, 1, or 2).
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_ignore_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_ignore"
        return SysCtl().write_sysctl(arp_ignore_file, str(value))

    def set_arp_notify(self, ifName: str = "all", enable: bool = True) -> bool:
        """
        Enable or disable ARP notifications for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable ARP notifications, False to disable them.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise. Most of the time, it will be one of these values.
        """
        arp_notify_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_notify"
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_notify_file, value)

    def set_drop_gratuitous_arp(self, ifName: str = "all", enable: bool = True) -> bool:
        """
        Enable or disable the dropping of gratuitous ARP packets for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable dropping of gratuitous ARP packets, False to disable it.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise. Most of the time, it will be one of these values.
        """

        value = "1" if enable else "0"
        arp_file = f"/proc/sys/net/ipv4/conf/{ifName}/drop_gratuitous_arp"
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]
        
        results = self.run(command)
        
        self.log.debug(f"set_drop_gratuitous_arp(ifname: {ifName} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set gratuitous ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set gratuitous ARP to {value}")
            return STATUS_OK

    def set_proxy_arp(self, ifName: str = 'all', enable: bool = True) -> bool:
        """
        Enable or disable proxy ARP for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable proxy ARP, False to disable it.

        Returns:
            bool: True for success (STATUS_OK), False for failure (STATUS_NOK).
        """       
        value = "1" if enable else "0"
        
        arp_file = f"/proc/sys/net/ipv4/conf/{ifName}/proxy_arp"
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]

        results = self.run(command)
        
        self.log.debug(f"set_proxy_arp(ifname: {ifName} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set proxy ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set proxy ARP to {value}")
            return STATUS_OK
            
    def set_proxy_arp_pvlan(self, ifName: str, enable: bool) -> bool:
        """
        Enable or disable proxy ARP for Private VLAN (PVLAN) on a specific network interface.

        Args:
            ifName (str): The name of the network interface.
            enable (bool): True to enable proxy ARP for PVLAN, False to disable it.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """

        proxy_arp_pvlan_file = f"/proc/sys/net/ipv4/conf/{ifName}/proxy_arp_pvlan"
        value = "1" if enable else "0"
        
        self.log.debug(f"set_proxy_arp(ifname: {ifName}) -> File: {proxy_arp_pvlan_file} -> enable: {enable}")
                
        return SysCtl().write_sysctl(proxy_arp_pvlan_file, value)

    def set_static_arp(self, inet:str, mac_address:str, ifName:str,
                       encap:Encapsulate=Encapsulate.ARPA, add_arp_entry:bool=True) -> bool:
        """
        Configure or remove a static ARP entry using iproute2.

        Args:
            inet (str): The IPv4 address for the static ARP entry.
            mac_address (str): The MAC address for the static ARP entry.
            ifName (str): The name of the network interface.
            encap (Encapsulate, optional): The ARP encapsulation type (default is ARPA).
            add_arp_entry (bool, optional): True to configure the entry (default), False to remove it.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.

        Note:
            - To configure a static ARP entry, set `enable` to True.
            - To remove a static ARP entry, set `enable` to False.
        """
        arp_entry_action='add'
        
        if not InetServiceLayer().is_valid_ipv4(inet):
            self.log.error(f"Invalid Inet Address -> ({inet})")
            return STATUS_NOK
            
        status, mac_address = self.format_mac_address(mac_address)
        
        if status:
            self.log.error(f"Invalid Mac Address -> ({mac_address})")
            return STATUS_NOK
        
        if not add_arp_entry:
           arp_entry_action='del' 
        
        command = ['ip', 'neigh', arp_entry_action, inet, 'lladdr', mac_address, 'dev', ifName]
        
        self.log.debug(f"Static ARP CMD: {command}")
        
        results = self.run(command, suppress_error=True)
        
        if results.exit_code:
            self.log.error(f"Unable to set static arp entry {inet} -> {mac_address} : {results.stderr}")
            return STATUS_NOK
        
        self.log.debug(f"set_static_arp(ifName: {ifName}) -> inet: {inet} -> mac: {mac_address}")
        return STATUS_OK
            
    def get_arp(self, args=None):
        try:
            
            self.log.debug(f"get_arp()")
            
            # Run the 'ip neighbor show' command and capture the output
            output = self.run(['ip', 'neighbor', 'show'])

            self.log.debug(f"get_arp() stderr: ({output.stderr}) -> exit_code: ({output.exit_code }) -> stdout: \n{output.stdout}")
            
            if output.exit_code == 0:
                
                # Split the ARP table output into lines
                arp_lines = output.stdout.strip().split('\n')

                # Parse the ARP table into a list of lists (rows)
                arp_table = [line.split() for line in arp_lines]

                # Define headers for the ARP table with proper column widths
                headers = ["IP Address", "Device", "Interface", "Type", "MAC Address", "State"]

                # Pretty-print the ARP table using the 'tabulate' library
                table = tabulate(arp_table, headers=headers, tablefmt='simple', colalign=("left", "left", "left", "left", "left"))

                # Print the formatted ARP table
                print(table)
            else:
                print(f"Error executing 'ip neighbor show' command: {output.stderr}")
        except Exception as e:
            print(f"Error: {e}")