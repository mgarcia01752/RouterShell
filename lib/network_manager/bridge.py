from enum import Enum, auto
import logging
import re
from typing import Optional

from tabulate import tabulate
from lib.db.bridge_db import BridgeDatabase 
from lib.network_manager.common.phy import State
from lib.common.common import STATUS_NOK, STATUS_OK

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.network_manager import NetworkManager

class BridgeProtocol(Enum):
    
    IEEE_802_1D = auto()
    '''
    IEEE 802.1D STP: STP is the original Spanning Tree Protocol, and it was designed 
    to prevent loops in bridged networks. However, it has relatively slow convergence times. 
    When a network topology change occurs (e.g., a link failure or recovery), 
    STP can take several seconds or even longer to recompute the spanning tree 
    and re-converge the network. During this time, some network segments may be blocked, 
    leading to suboptimal network performance.
    '''
    
    IEEE_802_1W = auto()
    '''
                            !!!!!!!!Currently not Supported!!!!!!!!
    IEEE 802.1W RSTP: Rapid Spanning Tree Protocol is designed to provide rapid convergence. 
    It improves upon the slow convergence of STP.  RSTP is much faster at detecting network 
    topology changes and re-converging the network. In many cases, RSTP can converge within 
    a few seconds or less. This rapid convergence is achieved by introducing new port states 
    and mechanisms to minimize the time it takes to transition to a new topology.
    '''
    
    IEEE_802_1S = auto()
    '''
                            !!!!!!!!Currently not Supported!!!!!!!!
    IEEE 802.1S is a network standard that defines the Multiple Spanning Tree Protocol (MSTP). 
    MSTP is an extension of the original Spanning Tree Protocol (STP) defined in IEEE 802.1D 
    and is designed to improve the efficiency of loop prevention in Ethernet networks, 
    especially in environments with multiple VLANs (Virtual LANs).
    '''

class STP_STATE(Enum):
    STP_DISABLE='0'
    STP_ENABLE='1'
    
class Bridge(NetworkManager):

    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE)
        
        self.bridgeDB = BridgeDatabase()
        self.arg = arg
        
    def get_bridge_list_os(self) -> list:
        """
        Get a list of bridge names from OS

        Returns:
            List[str]: A list of bridge names.
        """
        result = self.run(['ip', 'link', 'show', 'type', 'bridge'])

        if result.exit_code:
            self.log.warn("Unable to get bridge list")
            return []

        bridge_list = [line.split(':')[1].strip() for line in result.stdout.splitlines()]
        return bridge_list

    def add_bridge_global(self, bridge_name: str, bridge_protocol: BridgeProtocol = BridgeProtocol.IEEE_802_1D, stp_status: bool=True) -> bool:
        """
        Add a bridge using global commands and store in the database

        Args:bridge_exists
            bridge_name (str): The name of the bridge to add.
            bridge_protocol (BridgeProtocol, optional): The bridge protocol to use (default is IEEE 802.1D).
            stp_status (bool, optional): Whether to enable STP on the bridge (default is True).

        Returns:
            bool: STATUS_OK if the bridge was added successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"add_bridge_global_cmd() - Bridge: {bridge_name} -> Protocol: {bridge_protocol.value} -> STP: {stp_status}")

        if not bridge_name:
            self.log.fatal(f"No Bridge name provided")
            return STATUS_NOK

        # Check if the bridge already exists in the database
        bridge_exist_db = self.bridgeDB.does_bridge_exists_db(bridge_name)
        self.log.debug(f"add_bridge_global_cmd() - Bridge: {bridge_name} -> Exists in DB: {bridge_exist_db}")
        
        # Check if the bridge already exists in Linux system
        bridge_exist_os = self.does_bridge_exist_os(bridge_name)
        self.log.debug(f"add_bridge_global_cmd() - Bridge: {bridge_name} -> Exists in OS: {bridge_exist_os}")
        
        if bridge_exist_os:          
            self.log.debug(f"Bridge {bridge_name} exists in os")

            if not bridge_exist_db:
                self.log.debug(f"Adding bridge: {bridge_name} to DB")
                
                add_result = self.bridgeDB.add_bridge_db(bridge_name, bridge_protocol.value, stp_status)

                if add_result.status:
                    self.log.error(f"Unable to add bridge: {bridge_name}, result: {add_result.reason}")
                    return STATUS_NOK
                            
                '''Exit if bridge exist and added to DB '''
                return STATUS_OK            
        
        else:
            self.log.debug(f"Bridge {bridge_name} does not exists in os")
            
            if self._create_bridge_os(bridge_name):
                self.log.error(f"add_bridge_global() - Unable to configure bridge: {bridge_name} to os")
                
                if bridge_exist_db:
                    self.bridgeDB.del_bridge_db(bridge_name, bridge_protocol.value, stp_status)
                    
                return STATUS_NOK

        if not bridge_exist_db:
            self.log.debug(f"add_bridge_global() - Adding bridge: {bridge_name} to db")
            add_result = self.bridgeDB.add_bridge_db(bridge_name, bridge_protocol.value, stp_status)

            if add_result.status:
                self.log.error(f"Unable to add bridge: {bridge_name}, result: {add_result.reason}")
                return STATUS_NOK

        self.log.debug(f"Bridge {bridge_name} created.")
        return STATUS_OK

    def _create_bridge_os(self, bridge_name: str) -> bool:
        """
        Create a bridge with Spanning Tree Protocol (STP) enabled.

        Args:
            bridge_name (str): The name of the bridge to create.

        Returns:
            bool: STATUS_OK (False) if the bridge is created with STP enabled successfully, STATUS_NOK (True) if creation fails.
        """
        self.log.debug(f"_create_bridge_with_stp() -> Adding bridge: {bridge_name} to os")
        
        result = self.run(['ip', 'link', 'add', 'name', bridge_name, 'type', 'bridge'])
        if result.exit_code:
            self.log.warning(f"Bridge {bridge_name} cannot be created - exit-code: {result.exit_code}")
            return STATUS_NOK

        result = self.run(['ip', 'link', 'set', 'dev', bridge_name, 'type', 'bridge', 'stp_state', str(STP_STATE.STP_ENABLE.value)])
        if result.exit_code:
            self.log.warning(f"Bridge {bridge_name} unable to enable IEEE_802_1D - exit-code: {result.exit_code}")
            return STATUS_NOK

        self.log.debug(f"_create_bridge_with_stp() -> Added bridge: {bridge_name} to os")
        return STATUS_OK

    def does_bridge_exist_os(self, bridge_name, suppress_error=False) -> bool:
        """
        Check if a bridge with the given name exists via iproute.
        Will also remove bridge name in db if the interface is not available

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        self.log.debug(f"does_bridge_exist() -> Checking bridge name exists: {bridge_name}")
        
        output = self.run(['ip', 'link', 'show', 'dev', bridge_name], suppress_error=True)
        
        if output.exit_code:
            self.log.debug(f"does_bridge_exist() -> Bridge does NOT exist: {bridge_name} - exit-code: {output.exit_code}")
            return False
            
        self.log.debug(f"does_bridge_exist(exit-code({output.exit_code})) -> Bridge does exist: {bridge_name}")
        
        return True

    def get_assigned_bridge_from_interface(self, ifName: str) -> str:
        """
        Get the name of the bridge to which a network interface is assigned.

        Args:
            ifName (str): The name of the network interface.

        Returns:
            str: The name of the assigned bridge, or an empty string if not assigned.
        """
        result = self.run(["ip", "link", "show", "type", "bridge_slave", ifName], suppress_error=True)

        for line in result.stdout.split('\n'):
            if "master" in line:
                tokens = line.strip().split()
                for i in range(len(tokens)):
                    if tokens[i] == "master" and i + 1 < len(tokens):
                        return tokens[i + 1]

        return ""     

    def del_bridge_from_interface(self, interface_name: str, bridge_name:str) -> bool:
        """
        Delete bridge from interface via os
        Delete bridge from interface bridge-group via db
        
        This is applied at the interface level

        Args:
            interface_name (str): The name of the interface to add to the bridge.
            bridge_name (str): The name of the bridge.

        Returns:
            bool: STATUS_OK if the interface is added to the bridge successfully, STATUS_NOK otherwise.
        """
        if not (bridge_name and self.does_bridge_exist_os(bridge_name)):
            self.log.error(f"del_bridge_from_interface() -> Bridge does not exist: {bridge_name}")
            return STATUS_NOK
        
        if not interface_name:
            self.log.fatal(f"del_bridge_from_interface()-> No Interface provided")
            return STATUS_NOK

        if self._del_bridge_from_interface_bridge_group(bridge_name):
            self.log.error(f"del_bridge_from_interface()-> Interface {interface_name} unable to delete from bridge {bridge_name}.")
            return STATUS_NOK
        
        if self.bridgeDB.update_interface_bridge_group(interface_name, bridge_name, True):
            self.log.error(f"del_bridge_from_interface90 -> Unable to delete bridge: {bridge_name} from interface: {interface_name} bridge-group via db")
            return STATUS_NOK
        
        return STATUS_OK

    def _del_bridge_from_interface_bridge_group(self, bridge_name: str) -> bool:
        """
        Set an interface to have no master.

        Args:
            bridge_name (str): The name of the bridge to set to have no master.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK if the operation fails.
        """
        result = self.run(['ip', 'link', 'set', 'dev', bridge_name, 'nomaster'])
        if result.exit_code:
            self.log.warning(f"Failed to set {bridge_name} to have no master - exit-code: {result.exit_code}")
            return STATUS_NOK

        return STATUS_OK

    def add_bridge_to_interface(self, interface_name: str, bridge_name:str=None, stp:BridgeProtocol=BridgeProtocol.IEEE_802_1D) -> bool:
        """
        Add bridge to interface bridge-group via os.
        Add bridge to interface bridge-group via db
        This is applied at the interface level

        Args:
            interface_name (str): The name of the interface to add to the bridge.
            bridge_name (str): The name of the bridge.

        Returns:
            bool: STATUS_OK if the interface is added to the bridge successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"add_interface_cmd() -> Interface: {interface_name} -> Bridge: {bridge_name} STP: {stp}")
        
        if not (bridge_name and self.does_bridge_exist_os(bridge_name)):
            self.log.error(f"add_interface_cmd() -> Bridge does not exist: {bridge_name}")
            return STATUS_NOK
        
        if not interface_name:
            self.log.fatal(f"No Interface provided")
            return STATUS_NOK
        
        if self._set_bridge_to_interface_bridge_group(interface_name, bridge_name):
            self.log.error(f"Unable to add bridge: {bridge_name} to interface: {interface_name} bridge-group via os")
            return STATUS_NOK        

        if self.bridgeDB.update_interface_bridge_group(interface_name, bridge_name):
            self.log.error(f"Unable to add bridge: {bridge_name} to interface: {interface_name} bridge-group via db")
            return STATUS_NOK        
    
        return STATUS_OK

    def _set_bridge_to_interface_bridge_group(self, interface_name: str, bridge_name: str) -> bool:
        """
        Set an interface as a master of a bridge.

        Args:
            interface_name (str): The name of the network interface to set as the master.
            bridge_name (str): The name of the bridge.

        Returns:
            bool: STATUS_OK if the operation is successful, STATUS_NOK if the operation fails.
        """
        self.log.debug(f"_set_bridge_to_interface_bridge_group() -> Interface: {interface_name} -> Bridge: {bridge_name}")

        result = self.run(['ip', 'link', 'set', 'dev', interface_name, 'master', bridge_name])

        if result.exit_code:
            self.log.error(f"_set_bridge_to_interface_bridge_group() -> Interface {interface_name} unable to be set as the master of bridge {bridge_name}.")
            return STATUS_NOK

        self.stp_status_cmd(bridge_name)

        self.log.debug(f"_set_bridge_to_interface_bridge_group() -> Interface {interface_name} set as the master of bridge {bridge_name}.")

        return STATUS_OK

    def stp_status_cmd(self, bridge_name: str, stp_status: Optional[str] = 'enable') -> bool:
        """
        Set the STP (Spanning Tree Protocol) status for a bridge.

        Args:
            bridge_name (str): The name of the bridge.
            stp_status (str, optional): The STP status ('enable' or 'disable'). Defaults to 'enable'.

        Returns:
            bool: STATUS_OK if the interface is added to the bridge successfully, otherwise (STATUS_OK).
        """
        if not self.does_bridge_exist_os(bridge_name):
            self.log.error(f"stp_status_cmd() -> No Bridge name provided")
            return STATUS_NOK
        
        stp = '1' if stp_status == 'enable' else '0'

        result = self.run(['ip', 'link', 'set', 'dev', bridge_name, 'type', 'bridge', 'stp_state', stp])

        if result.exit_code:
            self.log.debug(f"stp_status_cmd() -> STP status for bridge {bridge_name} was NOT set to {stp}.")
            return STATUS_NOK

        self.log.debug(f"stp_status_cmd() -> STP status for bridge {bridge_name} set to {stp}.")
        return STATUS_OK

    def shutdown_cmd(self, bridge_name: str, negate=False) -> bool:
        """
        Change bridge state UP/DOWN.

        Returns:
            bool: STATUS_OK if the bridge was successfully change state, STATUS_NOK otherwise.
        """
        
        if not bridge_name or self.does_bridge_exist_os(bridge_name):
            self.log.error(f"No Bridge name provided")
            return STATUS_NOK

        state = State.DOWN
        
        if negate:
            state = State.UP
        
        result = self.run(['ip', 'link', 'set', 'dev', bridge_name, state])
        
        if result.exit_code:
            print(f"Failed to change bridge {bridge_name} to STATE: {state}.")
            return STATUS_NOK
        
        self.log.debug(f"bridge {bridge_name} -> state: {state}.")
        return STATUS_OK

    def destroy_bridge_cmd(self, bridge_name) -> bool:
        """
        Destroy the current bridge using iproute2 with sudo.

        Returns:
            bool: STATUS_OK if the bridge was successfully destroyed, STATUS_NOK otherwise.
        """
        self.log.debug(f"destroy_bridge_cmd() -> Bridge: {bridge_name}")
        if not bridge_name:
            self.log.error("No bridge selected. Use 'bridge <bridge_name>' to select a bridge.")
            return STATUS_NOK
        
        if not self.does_bridge_exist_os(bridge_name):
            self.log.debug(f"Invalid Bridge Name: {bridge_name}")
            return STATUS_NOK
        
        result = self.run(['ip', 'link', 'delete', bridge_name, 'type', 'bridge'])
        
        if result.exit_code:
            self.log.error(f"Failed to destroy bridge {bridge_name}")
            return STATUS_NOK
        else:
            self.log.debug(f"Destroyed bridge {bridge_name}.")
            return STATUS_OK
        
    def is_interface_connect_to_bridge(self, ifName:str, bridge_name:str) -> bool:
        """
        Check if a network interface is connected to a specific bridge.

        Args:
            ifName (str): The name of the network interface to check.
            bridge_name (str): The name of the bridge to check against.

        Returns:
            bool: STATUS_OK if the network interface is connected to the bridge, STATUS_NOK otherwise.
        """

        result = self.run(['ip', 'link', 'show', 'type', 'bridge_slave', ifName, 'master', bridge_name], suppress_error=True)

        if result.exit_code:
            self.log.debug(f"Interface: {ifName} is not part of Bridge: {bridge_name}")
            return STATUS_NOK

        return STATUS_OK
        
    def get_bridge(self, arg=None):

        """
        Get information about bridge interfaces.

        This method retrieves information about bridge interfaces, including their names, MAC addresses, IPv4 and IPv6
        addresses, state, and associated interfaces. The information is displayed in a tabulated format.

        Args:
            arg (Any, optional): Additional argument (not used).

        Returns:
            None
        """
                
        '''21: br0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 1000'''
        interface_patter = r'(\d+):(.*):\s+<(.*)>\s+(.*)'
        
        '''link/ether 8e:a5:07:16:1c:be brd ff:ff:ff:ff:ff:ff'''
        mac_pattern = r'\s+link/ether\s+(..:..:..:..:..:.[0-9a-fA-F])\s+.*'
        
        '''inet 192.168.0.11/24 brd 192.168.0.255 scope global dynamic noprefixroute eno1'''
        inet_pattern = r'\s+inet\s+(.*/\d+)\s+.*'
        
        '''inet6 2601:586:8300:5760:8790:b4f7:f663:b93/64 scope global temporary dynamic '''
        inet6_pattern = r'\s+inet6\s+(.*/\d+)\s+.*'
        
        bridge_info = []
        bridge_mac = ""
        bridge_inet = ""

        # Get a list of all bridges
        ip_arr_out = self.run(["ip", "address", "show", "type", "bridge"])
        
        for line in ip_arr_out.stdout.splitlines():
            
            self.log.debug(f"ip_rte_br_out -> {line}")
            bridge_match = re.match(interface_patter, line)
            if bridge_match:    
                bridge_idx = bridge_match.group(1).strip()
                bridge_name = bridge_match.group(2).strip()
                bridge_flags = bridge_match.group(3).strip()
                bridge_state = bridge_match.group(4).strip().split("state")[1].strip().split(" ")[0]
            
                # Print the extracted information
                self.log.debug(f"Bridge Index: ({bridge_idx}), Bridge Name: ({bridge_name}), Bridge Flags: ({bridge_flags}), Bridge State: ({bridge_state})")

            # Match the MAC address pattern
            mac_match = re.match(mac_pattern, line)
            if mac_match:
                # Extract the MAC address
                bridge_mac = mac_match.group(1).strip()
                
                # Print the extracted MAC address
                self.log.debug(f"Bridge MAC Address: ({bridge_mac})")

            # Match the IPv4 address pattern
            inet_match = re.match(inet_pattern, line)
            if inet_match:
                # Extract the IPv4 address
                bridge_inet = inet_match.group(1).strip()
                
                # Print the extracted IPv4 address
                self.log.debug(f"Bridge IPv4 Address: ({bridge_inet})")

            # Match the IPv6 address pattern
            inet6_match = re.match(inet6_pattern, line)
            if inet6_match:
                # Extract the IPv6 address
                bridge_inet6 = inet6_match.group(1).strip()
                
                # Print the extracted IPv6 address
                self.log.debug(f"Bridge IPv6 Address: ({bridge_inet6})")

                # Get details for each bridge
                bridge_details = self.run(["ip", "link", "show", bridge_name])

                # Get associated interfaces
                bridge_interfaces = self.run(["ip", "link", "show", "type", "bridge_slave", "master", bridge_name])
                interface_list = "\n".join([re.search(r"(\S+)(?:@|$)", iface).group(1) for iface in bridge_interfaces.stdout.splitlines() if "@" in iface])

                bridge_debug.append([bridge_name, bridge_mac, bridge_inet, bridge_inet6, bridge_state, interface_list])

        # Display the information in a tabulated format
        headers = ["Bridge", "Mac", "IPv4", "IPv6", "State", "Interfaces"]
        print(tabulate(bridge_info, headers, tablefmt="simple"))
        
        
