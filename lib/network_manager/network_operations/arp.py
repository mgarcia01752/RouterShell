from enum import Enum
import json
import logging
from typing import Any, Dict, List, Optional

from tabulate import tabulate 
from lib.network_manager.common.inet import InetServiceLayer
from lib.network_manager.common.sysctl import SysCtl

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_operations.network_mgr import NetworkManager


class Encapsulate(Enum):
    """Enumeration of encapsulation types."""
    
    ARPA = 'arpa'
    """arpa Enables encapsulation for an Ethernet 802.3 network."""
    
    FRAME_RELAY = 'frame-relay'
    """frame-relay Enables encapsulation for a Frame Relay network."""
    
    SNAP = 'snap'
    """snap Enables encapsulation for FDDI and Token Ring networks."""

class ArpException(Exception):
    """Exception raised for ARP (Address Resolution Protocol) related errors."""

    def __init__(self, message="ARP error occurred"):
        self.message = message
        super().__init__(self.message)

class Arp(NetworkManager):
    """
    Class for managing ARP (Address Resolution Protocol) settings.

    Inherits from NetworkManager.
    """
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().ARP)

    def is_arp_entry_exists(self, ip_address: str, interface: str = None) -> bool:
        """
        Check if an ARP entry already exists for a specific IP address on a given interface.

        Parameters:
            ip_address (str): The IP address to check.
            interface (str): The network interface to check. If None, checks all interfaces.

        Returns:
            bool: True if the ARP entry exists, False otherwise.
        """
        try:
            output = self.run(['ip', 'neighbor', 'show'])

            if output.exit_code == 0:
                arp_lines = output.stdout.strip().split('\n')

                for line in arp_lines:
                    words = line.split()

                    if ip_address in words:
                        if interface and interface in words:
                            return True
                        elif not interface:
                            return True
                return False
            else:
                self.log.error(f"Error executing 'ip neighbor show' command: {output.stderr}")
                return False
            
        except ArpException as e:
            self.log.error(f"Error: {e}")
            return False

    def arp_clear(self, ifName: str = 'all') -> str:
        """
        Clears the ARP cache for a specific network interface or all interfaces.

        This method constructs and runs the appropriate command to flush the ARP cache 
        for a specified network interface if provided. If 'all' is specified, it will 
        flush the ARP cache for all interfaces.

        Args:
            ifName (str): The name of the network interface for which to flush 
                        the ARP cache. Default is 'all', which flushes the ARP cache 
                        for all interfaces.

        Returns:
            str: A status string indicating the result of the operation. STATUS_OK if the 
                command was successful, STATUS_NOK otherwise.
        """
        cmd = ['ip', 'neigh', 'flush']

        if ifName == 'all':
            cmd.append('all')
        else:
            cmd.extend(['dev', ifName])

        self.log.debug(f"CMD: {cmd}")

        result = self.run(cmd)

        return STATUS_OK if result.exit_code else STATUS_NOK

    def set_os_timeout(self, arp_time_out: int = 300) -> bool:
        """
        Sets the ARP cache timeout in the operating system.

        This method writes the given ARP cache timeout value to the system configuration
        using the `sysctl` interface. It sets the timeout value for the ARP cache entries.

        Args:
            arp_time_out (int): The desired timeout value for ARP cache entries in seconds.
                                Default is 300 seconds.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        sysctl_param = "net.ipv4.neigh.default.gc_stale_time"
        
        if SysCtl().write_sysctl(sysctl_param, str(arp_time_out)):
            print(f"Unable to set ARP cache timeout to {arp_time_out} seconds.")
            return STATUS_NOK
        else:
            print(f"Set ARP cache timeout to {arp_time_out} seconds.")
        
        return STATUS_OK

    def set_os_arp_accept(self, ifName: str = "all", enable: bool = True) -> bool:
        """
        Sets the ARP accept mode for a specific network interface or all interfaces.

        This method writes the given ARP accept mode value to the system configuration
        file corresponding to the specified network interface. Enabling ARP accept mode
        allows the system to respond to ARP requests that match the host.

        Args:
            ifName (str): The name of the network interface for which to set ARP accept mode.
                        Default is "all", which applies the setting to all interfaces.
            enable (bool): If True, enables ARP accept mode. If False, disables ARP accept mode.
                        Default is True.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_accept_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_accept"
        value = "1" if enable else "0"
        
        return SysCtl().write_sysctl(arp_accept_file, value)

        def set_os_arp_announce(self, ifName:str, value:int) -> bool:
            """
            Set the ARP announce value for a specific network interface.

            :param ifName: The name of the network interface.
            :param value: The ARP announce value (0, 1, or 2).
            :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
            """
            arp_announce_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_announce"
            return SysCtl().write_sysctl(arp_announce_file, str(value))

    def set_os_arp_evict_nocarrier(self, ifName: str = "all", enable: bool = True) -> bool:
        """
        Sets the ARP eviction behavior on carrier loss for a specific network interface or all interfaces.

        This method writes the given value to the system configuration file corresponding 
        to the specified network interface. Enabling ARP eviction on carrier loss causes 
        ARP entries to be removed when the carrier is lost.

        Args:
            ifName (str): The name of the network interface for which to set ARP eviction behavior.
                        Default is "all", which applies the setting to all interfaces.
            enable (bool): If True, enables ARP eviction on carrier loss. If False, disables it.
                        Default is True.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_evict_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_evict_nocarrier"
        value = "1" if enable else "0"
        return SysCtl().write_sysctl(arp_evict_file, value)

    def set_os_arp_filter(self, ifName: str = "all", enable: bool = True) -> bool:
        """
        Sets the ARP filtering behavior for a specific network interface or all interfaces.

        This method writes the given value to the system configuration file corresponding 
        to the specified network interface. Enabling ARP filtering allows the system to use 
        more stringent rules when selecting ARP responses.

        Args:
            ifName (str): The name of the network interface for which to set ARP filtering behavior.
                        Default is "all", which applies the setting to all interfaces.
            enable (bool): If True, enables ARP filtering. If False, disables it.
                        Default is True.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_filter_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_filter"
        value = "1" if enable else "0"
        return SysCtl.write_sysctl(arp_filter_file, value)

    def set_os_arp_ignore(self, ifName: str="all", enable: bool=True) -> bool:
        """
        Set the ARP ignore value for a specific network interface.

        :param ifName: The name of the network interface. Default is 'all' to apply to all interfaces.
        :param value: The ARP ignore value (0, 1, or 2).
        :return: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        arp_ignore_file = f"/proc/sys/net/ipv4/conf/{ifName}/arp_ignore"
        value = "1" if enable else "0"
        return SysCtl().write_sysctl(arp_ignore_file, str(value))

    def set_os_arp_notify(self, ifName: str = "all", enable: bool = True) -> bool:
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

    def set_os_drop_gratuitous_arp(self, if_name: str = "all", enable: bool = True) -> bool:
        """
        Enable or disable the dropping of gratuitous ARP packets for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable dropping of gratuitous ARP packets, False to disable it.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise. Most of the time, it will be one of these values.
        """

        value = "1" if enable else "0"
        arp_file = f"/proc/sys/net/ipv4/conf/{if_name}/drop_gratuitous_arp"
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]
        
        results = self.run(command)
        
        self.log.debug(f"set_drop_gratuitous_arp(ifname: {if_name} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set gratuitous ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set gratuitous ARP to {value}")
            return STATUS_OK

    def set_os_proxy_arp(self, if_name: str = 'all', enable: bool = True) -> bool:
        """
        Enable or disable proxy ARP for a specific network interface.

        Args:
            ifName (str): The name of the network interface. Default is 'all' to apply to all interfaces.
            enable (bool): True to enable proxy ARP, False to disable it.

        Returns:
            bool: STATUS_OK for success, STATUS_NOK for failure.
        """       
        value = "1" if enable else "0"
        
        arp_file = f"/proc/sys/net/ipv4/conf/{if_name}/proxy_arp"
        
        command = ["sh", "-c", f"echo {value} > {arp_file}"]

        results = self.run(command)
        
        self.log.debug(f"set_proxy_arp(ifname: {if_name} -> enable: {enable}) -> Cmd: {command}")
        
        if results.exit_code:
            self.log.error(f"Failed to set proxy ARP to {value} due to {results.stderr}")
            return STATUS_NOK
        else:
            self.log.debug(f"Set proxy ARP to {value}")
            return STATUS_OK
            
    def set_os_proxy_arp_pvlan(self, ifName: str, enable: bool) -> bool:
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

    def set_os_static_arp(self, interface_name:str, inet:str, mac_address:str, encap:Encapsulate=Encapsulate.ARPA, add_arp_entry:bool=True) -> bool:
        """
        Configure or remove a static ARP entry using iproute2.

        Args:
            interface_name (str): The name of the network interface.
            inet (str): The IPv4 address for the static ARP entry.
            mac_address (str): The MAC address for the static ARP entry.
            encap (Encapsulate, optional): The ARP encapsulation type (default is ARPA).
            add_arp_entry (bool, optional): True to configure the entry (default), False to remove it.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.

        Note:
            - To configure a static ARP entry, set `enable` to True.
            - To remove a static ARP entry, set `enable` to False.
        """
        self.log.debug(f"set_os_static_arp() interface: {interface_name} -> inet: {inet} -> mac: {mac_address} -> encap: {encap} -> add-arp: {add_arp_entry}")
        arp_entry_action='add'
        
        if not InetServiceLayer().is_valid_ipv4(inet):
            self.log.error(f"Invalid Inet Address -> ({inet})")
            return STATUS_NOK
            
        status, mac_address = self.format_mac_address(mac_address)
        
        if not status:
            self.log.error(f"Invalid Mac Address -> ({mac_address})")
            return STATUS_NOK
        
        if not add_arp_entry:
           arp_entry_action='del' 
        
        command = ['ip', 'neigh', arp_entry_action, inet, 'lladdr', mac_address, 'dev', interface_name]
        
        self.log.debug(f"Static ARP CMD: {command}")
        
        results = self.run(command, suppress_error=True)
        
        if results.exit_code:
            self.log.error(f"Unable to set static arp entry {inet} -> {mac_address} : {results.stderr}")
            return STATUS_NOK
        
        self.log.debug(f"set_static_arp(ifName: {interface_name}) -> inet: {inet} -> mac: {mac_address}")
        return STATUS_OK
            
    def get_arp(self, args: Optional[List[str]] = None) -> None:
        """
        Retrieves the ARP table and prints it in a formatted table.

        This method runs the 'ip -json neighbor show' command to fetch the ARP table
        and processes the JSON output to display it in a readable format using the
        'tabulate' library.

        Args:
            args (Optional[List[str]]): Additional arguments to pass to the 'ip' command.
                                        Default is None.

        Raises:
            ArpException: If an error occurs while executing the command.
        """
        try:
            self.log.debug("get_arp()")

            # Run the 'ip -json neighbor show' command and capture the output
            cmd = ['ip', '-json', 'neighbor', 'show']
            if args:
                cmd.extend(args)

            output = self.run(cmd)

            self.log.debug(f"get_arp() stderr: ({output.stderr}) -> exit_code: ({output.exit_code}) -> stdout: \n{output.stdout}")

            if output.exit_code == 0:
                # Parse the JSON output
                arp_entries: List[Dict[str, Any]] = json.loads(output.stdout)

                # Define headers for the ARP table
                headers = ["IP Address", "Device", "MAC Address", "State"]

                if not arp_entries:
                    # Print an empty table with headers
                    print(tabulate([], headers=headers, tablefmt='simple', colalign=("left", "left", "left", "left")))
                    print("ARP table is empty.")
                    return

                # Transform the JSON data into a list of lists (rows) for tabulate
                arp_table = [
                    [entry.get("dst", ""), entry.get("dev", ""), entry.get("lladdr", ""), entry.get("state", "")]
                    for entry in arp_entries
                ]

                # Pretty-print the ARP table using the 'tabulate' library
                table = tabulate(arp_table, headers=headers, tablefmt='simple', colalign=("left", "left", "left", "left"))

                # Print the formatted ARP table
                print(table)
            else:
                print(f"Error executing 'ip -json neighbor show' command: {output.stderr}")
        except Exception as e:
            raise ArpException(f"Error: {e}")
