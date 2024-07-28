from enum import Enum
import logging
import os
from typing import List

import jc
from lib.db.wifi_db import WifiDB
from lib.network_manager.common.run_commands import RunCommand
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLGS
from lib.common.constants import HOSTAPD_CONF_DIR, HOSTAPD_CONF_FILE, STATUS_OK, STATUS_NOK
from lib.network_manager.network_operations.hostapd_mgr import HostapdIEEE802Config, HostapdManager
from lib.network_manager.network_operations.network_mgr import NetworkManager

class WPAVersion(Enum):
    """
    Enum representing different versions of WPA (Wi-Fi Protected Access).

    Attributes:
        WPA1 (int): WPA version 1.
        WPA2 (int): WPA version 2.
        WPA3 (int): WPA version 3.
        UNKNOWN (int): An unknown or undefined version of WPA.
    """
    WPA1 = 1
    WPA2 = 2
    WPA3 = 3
    UNKNOWN = -1

    @classmethod
    def display_list(cls, return_values=True):
        """
        Returns a list of known WPA versions.

        Args:
            return_values (bool): If True, returns version values; if False, returns version names.

        Returns:
            list: A list of known WPA versions.
        """
        if return_values:
            return [version.value for version in cls if version != cls.UNKNOWN]
        else:
            return [version.name for version in cls if version != cls.UNKNOWN]
    
class WPAkeyManagement(Enum):
    """
    Enum representing key management algorithms for Wi-Fi networks.

    Attributes:
        WPA_PSK (str): Wi-Fi Protected Access - Pre-Shared Key (WPA-PSK).
        WPA_EAP (str): Wi-Fi Protected Access - Extensible Authentication Protocol (WPA-EAP).
        WPA_EAP_SHA256 (str): WPA-EAP using SHA256-based encryption.
        WPA_EAP_TLS (str): WPA-EAP using Transport Layer Security (TLS).
    """
    WPA_PSK = 'WPA-PSK'
    WPA_EAP = 'WPA-EAP'
    WPA_EAP_SHA256 = 'WPA-EAP-SHA256'
    WPA_EAP_TLS = 'WPA-EAP-TLS'
    
    @classmethod
    def display_list(cls):
        """
        Returns a list of available key management algorithms.
        """
        return [algorithm.value for algorithm in cls]

class KeyManagementRule:
    '''
    Rules defined in hostapd.config as of 231105

    This section defines a set of accepted key management algorithms for wireless networks.
    The key management algorithms determine how encryption keys are negotiated and managed
    for securing Wi-Fi communication. The entries are separated by spaces.

    - WPA-PSK: WPA-Personal / WPA2-Personal
    - WPA-PSK-SHA256: WPA2-Personal using SHA256 for stronger security
    - WPA-EAP: WPA-Enterprise / WPA2-Enterprise
    - WPA-EAP-SHA256: WPA2-Enterprise using SHA256 for stronger security
    - SAE: Simultaneous Authentication of Equals (WPA3-Personal)
    - WPA-EAP-SUITE-B-192: WPA3-Enterprise with 192-bit security (CNSA suite)
    - FT-PSK: Fast Transition with passphrase/PSK
    - FT-EAP: Fast Transition with EAP
    - FT-EAP-SHA384: Fast Transition with EAP using SHA384 for stronger security
    - FT-SAE: Fast Transition with SAE
    - FILS-SHA256: Fast Initial Link Setup with SHA256
    - FILS-SHA384: Fast Initial Link Setup with SHA384
    - FT-FILS-SHA256: Fast Transition and Fast Initial Link Setup with SHA256
    - FT-FILS-SHA384: Fast Transition and Fast Initial Link Setup with SHA384
    - OWE: Opportunistic Wireless Encryption (a.k.a. Enhanced Open)
    - DPP: Device Provisioning Protocol
    - OSEN: Hotspot 2.0 online signup with encryption

    These rules define the key management algorithms that can be used to secure Wi-Fi networks.
    Please configure your network's key management algorithms based on your security requirements.

    (dot11RSNAConfigAuthenticationSuitesTable)
    '''

    def __init__(self):
        self.allowed_combinations = {
            ('WPA_PSK', 'WPA_EAP'): lambda wpa_key_mgmt: 'WPA-Personal' in wpa_key_mgmt and 'WPA-Enterprise' in wpa_key_mgmt,
            ('WPA_PSK', 'WPA_EAP_SHA256'): lambda wpa_key_mgmt: 'WPA-Personal' in wpa_key_mgmt and 'WPA-Enterprise-SHA256' in wpa_key_mgmt,
            ('WPA_EAP', 'WPA_EAP_SHA256'): lambda wpa_key_mgmt: 'WPA-Enterprise' in wpa_key_mgmt and 'WPA-Enterprise-SHA256' in wpa_key_mgmt,
        }

    def validate_key_management(self, wpa_key_mgmt):
        provided_algorithms = set(wpa_key_mgmt.split())

        for allowed_combination, validation_rule in self.allowed_combinations.items():
            if all(mode in provided_algorithms for mode in allowed_combination) and not validation_rule(wpa_key_mgmt):
                return False

        return True
    
class Pairwise(Enum):
    """
    Enum representing pairwise cipher suites for Wi-Fi security.

    Attributes:
        CCMP (str): Cipher-based encryption for enhanced security (e.g., WPA2).
        TKIP (str): Temporal Key Integrity Protocol, an older encryption method (e.g., WPA).
    """
    CCMP = 'CCMP'
    TKIP = 'TKIP'
    
    @classmethod
    def display_list(cls):
        """
        Returns a list of available pairwise cipher suites for Wi-Fi security.
        """
        return [cipher_suite.value for cipher_suite in cls]
    
class HardwareMode(Enum):
    """
    Enum representing hardware modes for Wi-Fi devices.

    Attributes:
        A (str): Wi-Fi mode 'a' (5 GHz band).
        B (str): Wi-Fi mode 'b' (2.4 GHz band).
        G (str): Wi-Fi mode 'g' (2.4 GHz band).
        AD (str): Wi-Fi mode 'ad' (60 GHz band).
        AX (str): Wi-Fi mode 'ax' (6 GHz band and beyond).
        ANY (str): Represents any hardware mode.
    """
    A = 'a'
    B = 'b'
    G = 'g'
    AD = 'ad'
    AX = 'ax'
    ANY = 'any'
    
    @classmethod
    def display_list(cls):
        """
        Returns a list of available hardware modes for Wi-Fi devices (values only).
        """
        return [mode.value for mode in cls]

class AuthAlgorithms(Enum):
    """
    Enum representing authentication algorithms for Wi-Fi networks.

    Attributes:
        OSA (str): Open System Authentication (OSA).
        SKA (str): Shared Key Authentication (SKA).
    """
    OSA = 'OSA'
    SKA = 'SKA'

    @classmethod
    def display_list(cls):
        """
        Returns a list of available authentication algorithms.
        """
        return [algorithm.value for algorithm in cls]

class WifiChannel(Enum):
    """
    Enum representing Wi-Fi channels.

    Attributes:
        CHANNEL_1 (int): Wi-Fi channel 1.
        CHANNEL_2 (int): Wi-Fi channel 2.
        CHANNEL_3 (int): Wi-Fi channel 3.
        CHANNEL_4 (int): Wi-Fi channel 4.
        CHANNEL_5 (int): Wi-Fi channel 5.
        CHANNEL_6 (int): Wi-Fi channel 6.
        CHANNEL_7 (int): Wi-Fi channel 7.
        CHANNEL_8 (int): Wi-Fi channel 8.
        CHANNEL_9 (int): Wi-Fi channel 9.
        CHANNEL_10 (int): Wi-Fi channel 10.
        CHANNEL_11 (int): Wi-Fi channel 11.
        CHANNEL_12 (int): Wi-Fi channel 12.
        CHANNEL_13 (int): Wi-Fi channel 13.
        CHANNEL_14 (int): Wi-Fi channel 14.
    """
    CHANNEL_1 = 1
    CHANNEL_2 = 2
    CHANNEL_3 = 3
    CHANNEL_4 = 4
    CHANNEL_5 = 5
    CHANNEL_6 = 6
    CHANNEL_7 = 7
    CHANNEL_8 = 8
    CHANNEL_9 = 9
    CHANNEL_10 = 10
    CHANNEL_11 = 11
    CHANNEL_12 = 12
    CHANNEL_13 = 13
    CHANNEL_14 = 14

    @classmethod
    def display_list(cls):
        """
        Returns a list of available Wi-Fi channels.
        """
        return [channel.value for channel in cls]

class WifiPolicy():
    """
    Represents a Wi-Fi policy for network management.

    This class allows you to define and manage Wi-Fi policies based on specific criteria.

    Args:
        wifi_policy_name (str): The name of the Wi-Fi policy.
        negate (bool): If True, the policy will be negated.

    Attributes:
        wifi_policy_name (str): The name of the Wi-Fi policy.
        negate (bool): Indicates whether the policy is negated.
        wifi_policy_status (bool): The status of the Wi-Fi policy (STATUS_OK or STATUS_NOK).

    """

    def __init__(self, wifi_policy_name: str, negate=False):
        """
        Initializes a new Wi-Fi policy with the given parameters.

        Args:
            wifi_policy_name (str): The name of the Wi-Fi policy.
            negate (bool, optional): If True, the policy will be negated (default is False).

        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIFI_POLICY)
        self.log.debug(f"WifiPolicy() -> Wifi-Policy: {wifi_policy_name} -> Negate: {negate}")
        
        self.wifi_db = WifiDB()

        if not self.wifi_db.wifi_policy_exist(wifi_policy_name):
            self.log.debug(f"Wifi-Policy: {wifi_policy_name} does not exist.")
            if self.wifi_db.add_wifi_policy(wifi_policy_name):
                self.log.debug(f"Error Adding wifi-policy: {wifi_policy_name} to DB")
                self._set_status(STATUS_NOK)
            else:
                
                self._set_status(STATUS_OK)

        self.wifi_policy_name = wifi_policy_name
        self.negate = negate

    def add_security_access_group(self, ssid: str, pass_phrase: str, mode: WPAVersion=WPAVersion.WPA2) -> bool:
        """
        Add a security access group with the specified SSID, passphrase, and security mode.

        Args:
        ssid (str): The SSID (Service Set Identifier) for the security access group.
        pass_phrase (str): The security passphrase or key for the security access group.
        mode (WPAVersion): The security mode for the security access group (e.g., WPA, WPA2, WPA3).

        Returns:
        bool: STATUS_OK if the security access group is added successfully, STATUS_NOK if the addition fails.

        Note:
        - This method adds a security access group with the provided SSID, passphrase, and security mode to the database.
        - It returns STATUS_OK if the addition is successful, and STATUS_NOK if there is an error or the addition fails.

        """
        return self.wifi_db.add_wifi_security_access_group(self.wifi_policy_name, ssid, pass_phrase, mode.value)

    def add_security_access_group_default(self, wifi_policy_name: str) -> bool:
        """
        Add a default security access group to the specified wireless Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy to add the default security access group to.

        Returns:
            bool: True if the default security access group is added successfully, False otherwise.

        Note:
        - This method adds a default security access group to the specified wireless Wi-Fi policy.
        - The default security access group typically includes pre-defined settings for SSID, WPA passphrase, and security mode.
        - Returns True if the default security access group is added successfully, and False otherwise.
        """
        return self.wifi_db.add_wifi_security_access_group_default(wifi_policy_name)

    def add_key_management(self, key_managment:WPAkeyManagement) -> bool:
        return STATUS_OK
    
    def add_hardware_mode(self, hardware_mode:HardwareMode) -> bool:
        """
        Add a hardware mode to a wireless Wi-Fi policy.

        Args:
            hardware_mode (HardwareMode): The hardware mode to add to the policy.

        Returns:
            bool: STATUS_OK if the hardware mode was successfully added, STATUS_NOK if it fails.

        Note:
        - This method associates a hardware mode with the specified wireless Wi-Fi policy.
        - It returns STATUS_OK if the association is successful, and STATUS_NOK if it fails.
        """
        return self.wifi_db.add_wifi_hardware_mode(self.wifi_policy_name, hardware_mode.value)
    
    def add_channel(self, wifi_channel: WifiChannel=WifiChannel.CHANNEL_6) -> bool:
        """
        Add a Wi-Fi channel to a wireless Wi-Fi policy.

        Args:
        - wifi_channel (WifiChannel): The Wi-Fi channel to add. Default is CHANNEL_6.

        Returns:
        bool: True if the addition is successful, False if it fails.

        Note:
        - This method associates a Wi-Fi channel with the specified wireless Wi-Fi policy.
        """        
        return self.wifi_db.add_wifi_channel(self.wifi_policy_name, str(wifi_channel.value))

    def del_ssid(self, ssid: str) -> bool:
        """
        Delete a Wi-Fi security access group with the specified SSID from the associated wireless Wi-Fi policy.

        Args:
            ssid (str): The SSID (Service Set Identifier) of the Wi-Fi security access group to delete.

        Returns:
            bool: STATUS_OK if the Wi-Fi security access group is deleted successfully, STATUS_NOK otherwise.

        Note:
        - This method deletes a Wi-Fi security access group with the specified SSID from the associated wireless Wi-Fi policy.
        - Returns True if the deletion is successful, and False otherwise.
        """
        return self.wifi_db.del_wifi_security_access_group(self.wifi_policy_name, ssid)

    def security_access_group_entry_exist(self, wifi_policy_name: str) -> bool:
        # Get the security policies associated with the Wi-Fi policy
        security_policies = self.wifi_db.get_wifi_security_policy(wifi_policy_name)

        # Check if there are any security policies
        if len(security_policies) > 0:
            self.log.debug(f"Security access group entry exists for Wi-Fi policy '{wifi_policy_name}'.")
            return True
        else:
            self.log.debug(f"No security access group entry found for Wi-Fi policy '{wifi_policy_name}'.")
            return False

    def get_ssid_list(self, wifi_policy_name: str) -> list:  
        self.wifi_db.get_wifi_security_policy(wifi_policy_name)
             
    def status(self) -> bool:
        """
        Get the status of the Wi-Fi policy.

        Returns:
            bool: The status of the Wi-Fi policy (STATUS_OK or STATUS_NOK).

        """
        return self.wifi_policy_status

    def _set_status(self, status: bool) -> bool:
        """
        Set the status of the Wi-Fi policy.

        Args:
            status (bool): The status to set (STATUS_OK or STATUS_NOK).

        Returns:
            bool: STATUS_OK if the status is successfully set.

        """
        self.wifi_policy_status = status
        return STATUS_OK

class WifiInterface():
    '''
    Interface level wifi settings
    '''
    
    def __init__(self, wifi_interface_name: str):
        """
        Initialize a WifiInterface instance.

        Parameters:
            interface_name (str): The name of the wireless interface.
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIFI_INTERFACE)
        self.log.debug(f"WifiInterface() -> interface: {wifi_interface_name}")
        
        self.wifi_interface_name = wifi_interface_name
        self.cmd = RunCommand()
        self.wifi_db = WifiDB()
        
        self.is_wifi_interface = self._is_interface_wifi()

    def _is_interface_wifi(self) -> bool:
        """
        Check if the current wireless interface is associated with Wi-Fi.

        Returns:
            bool: True if the current interface is associated with Wi-Fi, False otherwise.
        """
        cmd = ['iw', 'dev', self.wifi_interface_name , 'info']
        
        result = self.cmd.run(cmd)
        
        if result.exit_code:
            self.log.error("Unable to get wireless interface list")
            return False

        output_lines = result.stdout.strip().split('\n')
        interface_names = [line.split()[1] for line in output_lines if line.startswith('Interface')]

        if not interface_names:
            self.log.error("No wireless interfaces found")
            return False

        if self.wifi_interface_name not in interface_names:
            return False

        return True

    def is_interface_wifi(self) -> bool:
        """
        Check if the current interface is associated with Wi-Fi.

        Returns:
            bool: True if the interface is associated with Wi-Fi, False otherwise.
        """
        return self.is_wifi_interface
    
    def scan(self):
        """
        Perform a Wi-Fi scan on the specified interface and return the parsed scan results.

        Returns:
            List[Dict[str, Union[str, int, float]]]: Parsed Wi-Fi scan results as a list
            of dictionaries, where each dictionary represents information about a Wi-Fi network.
        """
        result = self.cmd.run(['iw', 'dev', self.wifi_interface_name, 'scan'])

        if result.exit_code:
            self.log.error(f"Unable to obtain scan from wifi-interface: {self.wifi_interface_name}")
            return []

        try:
            parsed_data = jc.parse('iw_scan', result.stdout)
            return parsed_data
        
        except Exception as e:
            self.log.error(f"Error parsing scan results: {e}")
            return []

    def update_policy_to_wifi_interface(self, wifi_policy_name: str) -> bool:
        """
        Update the Wi-Fi policy for the wireless interface.

        Parameters:
            wifi_policy_name (str): The name of the Wi-Fi policy.

        Returns:
            bool: STATUS_OK if the update is successful, STATUS_NOK otherwise.
        """
        if not self.is_interface_wifi():
            self.log.error(f"Unable to apply wifi-policy: {wifi_policy_name} , due to interface: {self.wifi_interface_name} is not wifi")
            return STATUS_NOK
        
        if not self.wifi_db.wifi_policy_exist(wifi_policy_name):
            self.log.error(f"Unable to apply wifi-policy: {wifi_policy_name} , interface: {self.wifi_interface_name} does not exists")
            return STATUS_NOK
        
        return self.wifi_db.add_wifi_policy_to_wifi_interface(wifi_policy_name, self.wifi_interface_name)
    
    def set_hardware_mode(self, wifi_interface_name:str, hw_mode: HardwareMode) -> bool:
        """
        Set the hardware mode for the wireless interface.

        Parameters:
            hw_mode (HardwareMode): The hardware mode to set.

        Returns:
            bool: STATUS_OK if the set operation is successful, STATUS_NOK otherwise.
        """

        if not self.is_interface_wifi():
            self.log.error(f"Unable to apply hardware-mode: {hw_mode.value} , due to interface: {self.wifi_interface_name} is not wifi")
            return STATUS_NOK
        
        return STATUS_OK
    
    def set_channel(self, wifi_interface_name:str, channel: WifiChannel) -> bool:
        """
        Set the Wi-Fi channel for the wireless interface.

        Parameters:
            channel (WifiChannel): The Wi-Fi channel to set.

        Returns:
            bool: STATUS_OK if the set operation is successful, STATUS_NOK otherwise.
        """
        if not self.is_interface_wifi():
            self.log.error(f"Unable to apply channel: {channel.value} , due to interface: {self.wifi_interface_name} is not wifi")
            return STATUS_NOK   
        
        return STATUS_OK

class Wifi(NetworkManager):
    """Command set for managing wireless networks using the 'iw' command."""

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIFI)

    def wifi_policy_name_exist(self, wifi_policy_name:str) -> bool:
        return True 

    def wifi_interface_exist(self, wifi_interface_name: str) -> bool:
        """
        Check if a Wi-Fi interface exists.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface to check.

        Returns:
            bool: True if the Wi-Fi interface exists, False otherwise.
        """
        output = self.run(['iw', 'dev', wifi_interface_name , 'info'])
        
        if output.exit_code:
            self.log.debug(f"Unable to obtain wifi-interface: {wifi_interface_name} status")
            return False
        return True
            
    def set_ssid(self, wifi_interface_name: str, ssid: str) -> bool:
        """
        Set the SSID (Service Set Identifier) for a Wi-Fi interface.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            ssid (str): The SSID to set.

        Returns:
            bool: STATUS_OK if the SSID was successfully set, STATUS_NOK otherwise.
        """
        output = self.run(['iw', 'dev', wifi_interface_name, 'set', 'ssid', ssid])
        
        if output.exit_code:
            self.log.error(f"Failed to set SSID for {wifi_interface_name}")
            return STATUS_NOK
        
        return STATUS_OK

    def set_wpa_passphrase(self, wifi_interface_name: str, pass_phrase: str) -> bool:
        """
        Set the WPA passphrase for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            pass_phrase (str): The WPA passphrase to set.

        Returns:
            bool: STATUS_OK if the WPA passphrase was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'wpa_passphrase', pass_phrase]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set WPA passphrase for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK
    
    def set_wpa_key_mgmt(self, wifi_interface_name: str, wpa_key_mgmt: WPAkeyManagement) -> bool:
        """
        Set the WPA key management method for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            wpa_key_mgmt (WPAkeyManagement): The key management method to set.

        Returns:
            bool: STATUS_OK if the key management method was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'key_mgmt', wpa_key_mgmt.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set key management method for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_wpa_pairwise(self, wifi_interface_name: str, wpa_pairwise: Pairwise) -> bool:
        """
        Set the WPA pairwise cipher for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            wpa_pairwise (str): The WPA pairwise cipher to set (CCMP, TKIP, etc.).

        Returns:
            bool: STATUS_OK if the WPA pairwise cipher was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'wpa_pairwise', wpa_pairwise.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set WPA pairwise cipher for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_rsn_pairwise(self, wifi_interface_name: str, rsn_pairwise: Pairwise) -> bool:
        """
        Set the RSN pairwise cipher for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            rsn_pairwise (str): The RSN pairwise cipher to set (CCMP, TKIP, etc.).

        Returns:
            bool: STATUS_OK if the RSN pairwise cipher was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'rsn_pairwise', rsn_pairwise.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set RSN pairwise cipher for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK
    
    def set_wifi_mode(self, wifi_interface_name: str, mode: HardwareMode) -> bool:
        """
        Set the Wi-Fi mode for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            mode (str): The Wi-Fi mode to set (a, b, g, ad, ax, any).

        Returns:
            bool: STATUS_OK if the Wi-Fi mode was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'mode', mode.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set Wi-Fi mode for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_wifi_channel(self, wifi_interface_name: str, channel: int) -> bool:
        """
        Set the Wi-Fi channel for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            channel (int): The Wi-Fi channel to set (1, 2, 3, 4, 5, 6, 8, 7, 8, 9, 10, 11).

        Returns:
            bool: STATUS_OK if the Wi-Fi channel was successfully set, STATUS_NOK otherwise.
        """
        if channel < 1 or channel > 11:
            self.log.error("Invalid Wi-Fi channel. The channel must be in the range 1 to 11.")
            return STATUS_NOK

        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'channel', str(channel)]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set Wi-Fi channel for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_auth_algs(self, wifi_interface_name: str, auth_alg: AuthAlgorithms) -> bool:
        """
        Set the authentication algorithms for a Wi-Fi interface using the iw command.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface.
            auth_alg (AuthAlgorithms): The authentication algorithm to set (AuthAlgorithms.OSA or AuthAlgorithms.SKA).

        Returns:
            bool: STATUS_OK if the authentication algorithm was successfully set, STATUS_NOK otherwise.
        """
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'auth-algs', auth_alg.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set authentication algorithm for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

    def set_ieee80211(self, ieee802_support:HostapdIEEE802Config, negate=False) -> bool:
        return STATUS_OK

class WifiAccessPoint(HostapdManager):
    def __init__(self, interface_name: str, wifi_policy_name: str):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIFI_ACCESS_POINT)
        
        self.interface_name = interface_name
        self.wifi_policy_name = wifi_policy_name

        self.hostapd_file_name = f'{interface_name}_{wifi_policy_name}_{HOSTAPD_CONF_FILE}'
        
        HostapdManager().__init__(self.hostapd_file_name)
        


    
        
        