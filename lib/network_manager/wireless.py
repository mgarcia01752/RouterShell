import subprocess
from enum import Enum
import logging
from lib.network_manager.network_manager import NetworkManager
from lib.common.router_shell_log_control import RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_OK, STATUS_NOK

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

class Wifi(NetworkManager):
    """Command set for managing wireless networks using the 'iw' command."""

    def __init__(self):
        super().__init()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIRELESS_WIFI)

    def wifi_interface_exist(self, wifi_interface_name: str) -> bool:
        """
        Check if a Wi-Fi interface exists.

        Args:
            wifi_interface_name (str): The name of the Wi-Fi interface to check.

        Returns:
            bool: True if the Wi-Fi interface exists, False otherwise.
        """

        # Use 'iw' command to show the list of Wi-Fi interfaces.
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
        # Use 'iw' command to set the SSID.
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
        # Use 'iw' command to set the key management method.
        cmd = ['iw', 'dev', wifi_interface_name, 'set', 'key_mgmt', wpa_key_mgmt.value]
        output = self.run(cmd)

        if output.exit_code:
            self.log.error(f"Failed to set key management method for {wifi_interface_name}")
            return STATUS_NOK

        return STATUS_OK

 
    