from enum import Enum
import logging
from lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from lib.common.constants import STATUS_OK, STATUS_NOK
from lib.network_manager.network_operations.hostapd_mgr import HostapdIEEE802Config
from lib.network_manager.network_operations.network_mgr import NetworkManager

class WPAVersion(Enum):
    WPA1 = 1
    WPA2 = 2
    WPA3 = 3
    UNKNOWN = -1
    
class WPAkeyManagement(Enum):
    WPA_PSK = 'WPA-PSK'
    WPA_EPA = 'WPA-EPA'
    WPA_EPA_SHA265 = 'WPA-EPA-SHA265'
    WPA_EPA_TLA = 'WPA-EPA-TLS'   
    
class Pairwise(Enum):
    CCMP = 'CCMP'
    TKIP = 'TKIP'

class HardwareMode(Enum):
    A = 'a'
    B = 'b'
    G = 'g'
    AD = 'ad'
    AX = 'ax'
    ANY = 'any'

class AuthAlgorithms(Enum):
    OSA = 'OSA'
    SKA = 'SKA'

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
        self.log.setLevel(RSLS().WIRELESS_WIFI_POLICY)
        self.log.debug(f"WifiPolicy() -> Wifi-Policy: {wifi_policy_name} -> Negate: {negate}")

        self.wifi = Wifi()

        if not self.wifi.wifi_policy_name_exist(wifi_policy_name):
            self.log.debug(f"Wifi-Policy: {wifi_policy_name} does not exist.")
            self.wifi_policy_status = STATUS_NOK
            return

        self.wifi_policy_name = wifi_policy_name
        self.negate = negate
        self.wifi_policy_status = STATUS_OK

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

           
class Wifi(NetworkManager):
    """Command set for managing wireless networks using the 'iw' command."""

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().WIFI)

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
