from enum import Enum, auto
import json
import logging
import re
from typing import List, Optional

from tabulate import tabulate
from lib.db.bridge_db import BridgeDatabase 
from lib.network_manager.common.phy import State
from lib.common.common import STATUS_NOK, STATUS_OK

from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.network_manager.common.run_commands import RunCommand
from lib.network_manager.network_operations.bridge.bridge_settings import STP_STATE, BridgeProtocol

class Bridge(RunCommand, BridgeDatabase):

    def __init__(self):
        super().__init__()
        BridgeDatabase().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE)
        
    def get_bridge_list_os(self) -> List[str]:
        """
        Get a list of bridge names from OS

        Returns:
            List[str]: A list of bridge names.
        """
        result = self.run(['ip', '-j', 'link', 'show', 'type', 'bridge'])

        if result.exit_code:
            self.log.error("Unable to get bridge list")
            return []

        try:
            bridge_links = json.loads(result.stdout)
            bridge_names = [link['ifname'] for link in bridge_links]
            return bridge_names
        
        except json.JSONDecodeError as e:
            self.log.debug(f"Failed to parse JSON: {e}")
            return []
        
        except KeyError as e:
            self.log.debug(f"Unexpected data format: {e}")
            return []

    def add_bridge(self, bridge_name: str) -> bool:
        """
        Add a bridge to the system and database. The method checks if the bridge exists in the OS and the database,
        and performs appropriate actions based on its presence.

        Args:
            bridge_name (str): The name of the bridge to be added.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.does_bridge_exist_os(bridge_name):
            if not self.does_bridge_exists_db(bridge_name):
                self.log.warn(f'Bridge {bridge_name} not in DB, adding to DB')
                if self.add_bridge_db(bridge_name):
                    self.log.error(f'Failed to add bridge: {bridge_name} to DB')
                    return STATUS_NOK
                return STATUS_OK
            
            self.log.debug(f"Bridge {bridge_name} already exists in DB")
            return STATUS_NOK
        
        # If bridge does not exist in the OS, it might still exist in the DB, so handle this case
        if self.does_bridge_exists_db(bridge_name):
            self.log.debug(f"Bridge {bridge_name} already exists in DB - Deleting and re-adding")
            if self.del_bridge_db(bridge_name):
                self.log.debug(f"Failed to delete existing bridge {bridge_name} from DB")
                return STATUS_NOK
        
        if self.add_bridge_db(bridge_name):
            self.log.error(f"Failed to add bridge {bridge_name} to DB")
            return STATUS_NOK
        
        return STATUS_OK

    def add_bridge_global(self, bridge_name: str, 
                          bridge_protocol: BridgeProtocol = BridgeProtocol.IEEE_802_1D, 
                          stp_status: bool=True) -> bool:
        """
        Add a bridge using global commands and store in the database

        Args:bridge_exists
            bridge_name (str): The name of the bridge to add.
            bridge_protocol (BridgeProtocol, optional): The bridge protocol to use (default is IEEE 802.1D).
            stp_status (bool, optional): Whether to enable STP on the bridge (default is True).

        Returns:
            bool: STATUS_OK if the bridge was added successfully, STATUS_NOK otherwise.
        """
        self.log.debug(f"add_bridge_global() - Bridge: {bridge_name} -> Protocol: {bridge_protocol.value} -> STP: {stp_status}")

        if not bridge_name:
            self.log.fatal(f"No Bridge name provided")
            return STATUS_NOK

        # Check if the bridge already exists in the database
        bridge_exist_db = self.does_bridge_exists_db(bridge_name)
        self.log.debug(f"add_bridge_global() - Bridge: {bridge_name} -> Exists in DB: {bridge_exist_db}")
        
        # Check if the bridge already exists in Linux system
        bridge_exist_os = self.does_bridge_exist_os(bridge_name)
        self.log.debug(f"add_bridge_global - Bridge: {bridge_name} -> Exists in OS: {bridge_exist_os}")
        
        if bridge_exist_os:          
            self.log.debug(f"Bridge {bridge_name} exists in os")

            if not bridge_exist_db:
                self.log.debug(f"Adding bridge: {bridge_name} to DB")
                
                if self.add_bridge_db(bridge_name, bridge_protocol.value, stp_status):
                    self.log.error(f'Unable to add bridge: {bridge_name} to DB')
                    return STATUS_NOK
                            
                return STATUS_OK            
        
        else:
            self.log.debug(f"Bridge {bridge_name} does not exists in os")
            
            if self._create_bridge_os(bridge_name):
                self.log.error(f"add_bridge_global() - Unable to configure bridge: {bridge_name} to os")
                
                if bridge_exist_db:
                    self.del_bridge_db(bridge_name, bridge_protocol.value, stp_status)
                    
                return STATUS_NOK

        if not bridge_exist_db:
            self.log.debug(f"add_bridge_global() - Adding bridge: {bridge_name} to db")
            add_result = self.add_bridge_db(bridge_name, bridge_protocol.value, stp_status)

            if add_result.status:
                self.log.error(f"Unable to add bridge: {bridge_name}, result: {add_result.reason}")
                return STATUS_NOK

        self.log.debug(f"Bridge {bridge_name} created.")
        return STATUS_OK

    def does_bridge_exist_os(self, bridge_name:str, suppress_error=False) -> bool:
        """
        Check if a bridge with the given name exists via iproute.
        Will also remove bridge name in db if the interface is not available

        Args:
            bridge_name (str): The name of the bridge to check.

        Returns:
            bool: True if the bridge exists, False otherwise.
        """
        self.log.debug(f"does_bridge_exist_os() -> Checking bridge name exists: {bridge_name}")
        
        output = self.run(['ip', 'link', 'show', 'dev', bridge_name], suppress_error=True)
        
        if output.exit_code:
            self.log.debug(f"does_bridge_exist_os() -> Bridge does NOT exist: {bridge_name} - exit-code: {output.exit_code}")
            return False
            
        self.log.debug(f"does_bridge_exist_os(exit-code({output.exit_code})) -> Bridge does exist: {bridge_name}")
        
        return True

    def get_assigned_bridge_from_interface(self, interface_name: str) -> str:
        """
        Get the name of the bridge to which a network interface is assigned.

        Args:
            interface_name (str): The name of the network interface.

        Returns:
            str: The name of the assigned bridge, or an empty string if not assigned.
        """
        result = self.run(["ip", "-details", "-json", "link", "show", interface_name])
        
        try:
            interfaces = json.loads(result.stdout)
            for interface in interfaces:
                if "ifname" in interface and interface["ifname"] == interface_name:
                    if "linkinfo" in interface and "info_slave_data" in interface["linkinfo"]:
                        if "master" in interface["linkinfo"]["info_slave_data"]:
                            return interface["linkinfo"]["info_slave_data"]["master"]
        except json.JSONDecodeError:
                raise
        
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
        
        if self.update_interface_bridge_group(interface_name, bridge_name, True):
            self.log.error(f"del_bridge_from_interface90 -> Unable to delete bridge: {bridge_name} from interface: {interface_name} bridge-group via db")
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

        if self.update_interface_bridge_group(interface_name, bridge_name):
            self.log.error(f"Unable to add bridge: {bridge_name} to interface: {interface_name} bridge-group via db")
            return STATUS_NOK        
    
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

    def shutdown_cmd(self, bridge_name: str, state: State = State.DOWN) -> bool:
        """
        Change the state of the specified bridge.

        Args:
            bridge_name (str): The name of the bridge to be shut down or brought up.
            state (State): The desired state for the bridge (State.DOWN or State.UP). Defaults to State.DOWN.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        self.log.info(f"shutdown_cmd() -> Bridge: {bridge_name} -> current-state: {self.get_bridge_state(self.bridge_name).value} -> change-state: {state.value}")    
        
        if not bridge_name or not self.does_bridge_exist_os(bridge_name):
            self.log.error("No Bridge name provided or bridge does not exist.")
            return STATUS_NOK

        if self.run(['ip', 'link', 'set', 'dev', bridge_name, state.value]).exit_code:
            self.log.error(f"Failed to change bridge {bridge_name} to STATE: {state.value}.")
            return STATUS_NOK

        self.log.info(f"shutdown_cmd() -> Bridge: {bridge_name} -> current-state: {self.get_bridge_state(self.bridge_name).value} -> change-state: {state.value}")

        return STATUS_OK

    def destroy_bridge_cmd_os(self, bridge_name) -> bool:
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

                # TODO Need to figure out why I put bridge_debug HERE??
                # bridge_debug.append([bridge_name, bridge_mac, bridge_inet, bridge_inet6, bridge_state, interface_list])

        # Display the information in a tabulated format
        headers = ["Bridge", "Mac", "IPv4", "IPv6", "State", "Interfaces"]
        print(tabulate(bridge_info, headers, tablefmt="simple"))
        
    def get_bridge_state(self, bridge_name: str) -> State:
        """
        Get the current state of the specified network bridge.

        Parameters:
        bridge_name (str): The name of the bridge whose state is to be retrieved.

        Returns:
        State: The state of the bridge, which can be 'UP', 'DOWN', or 'UNKNOWN'.
        """
                
        # Run the ip link show command to get information about the bridge
        result = self.run(['ip', '-json', 'link', 'show', bridge_name], suppress_error=True)
        
        try:

            bridge_info = json.loads(result.stdout)
            
            for interface in bridge_info:
                if interface.get('ifname') == bridge_name:
                    operstate = interface.get('operstate', 'UNKNOWN').upper()
                    
                    if operstate == State.UP.name:
                        return State.UP
                    elif operstate == State.DOWN.name:
                        return State.DOWN
                    else:
                        return State.UNKNOWN
            
            return State.UNKNOWN
        
        except json.JSONDecodeError:
            print(f"Error decoding JSON output for bridge: {bridge_name}")
            return State.UNKNOWN
        except Exception as e:
            print(f"Unexpected error: {e}")
            return State.UNKNOWN

    def create_bridge(self, bridge_name:str, stp:STP_STATE = STP_STATE.STP_ENABLE) -> bool:
        """
        Create a new network bridge.
        """
        if self.does_bridge_exist_os(bridge_name): 
            self.log.info(f'Can not create bridge {bridge_name}, already exists on OS')
            return STATUS_NOK
        
        if self.does_bridge_exists_db(bridge_name):
            self.log.info(f'Can not create bridge {bridge_name}, already exists on DB')
            return STATUS_NOK
        
        if self._create_bridge_os(bridge_name):
            self.log.info(f'Can not create bridge {bridge_name} on OS')
            return STATUS_NOK
        
        if self.add_bridge_db(bridge_name):
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

