import logging
from typing import List

from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB, Result
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK

class WifiPolicyNotFoundError(Exception):
    """
    Exception raised when a Wi-Fi policy is not found.
    """

    def __init__(self, message="Wi-Fi policy not found."):
        self.message = message
        super().__init__(self.message)


class WifiDB:
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WIFI_DB)
            
    def wifi_policy_exist(self, wifi_policy_name: str) -> bool:
        """
        Check if a wireless Wi-Fi policy with the given name exists in the database.

        Args:
        wifi_policy_name (str): The name of the wireless Wi-Fi policy to check for existence.

        Returns:
        bool: True if the policy exists, False if it doesn't.

        Note:
        - This method checks the database for the existence of a wireless Wi-Fi policy with the provided name.
        - It returns True if the policy exists, and False if it doesn't.

        """
        return RSDB().wifi_policy_exist(wifi_policy_name).status

    def add_wifi_policy(self, wifi_policy_name: str) -> bool:
        """
        Insert a new wireless Wi-Fi policy into the database.

        Args:
        wifi_policy_name (str): The name of the wireless Wi-Fi policy to insert.

        Returns:
        bool: True if the insertion is successful, False if it fails.

        Note:
        - This method inserts a new wireless Wi-Fi policy with the provided name into the database.
        - It returns STATUS_Ok if the insertion is successful, and STATUS_NOK if it fails.

        """
        
        sql_result = RSDB().insert_wifi_policy(wifi_policy_name)
        
        if sql_result.status:
            self.log.error(f"Unable to add wifi-policy: {wifi_policy_name} -> Reason: {sql_result.reason}")
            return STATUS_NOK
                
        return STATUS_OK 

    def add_wifi_security_access_group(self, wifi_policy_name: str, ssid: str, pass_phrase: str, mode: str) -> bool:
        """
        Insert a new Wi-Fi security group into the database associated with a wireless Wi-Fi policy.

        Args:
        wifi_policy_name (str): The name of the wireless Wi-Fi policy to associate the security group with.
        ssid (str): The SSID (Service Set Identifier) for the security group.
        pass_phrase (str): The security passphrase or key for the security group.
        mode (str): The security mode for the security group (e.g., WPA2, WPA3).

        Returns:
        bool: True if the security group is successfully inserted, False if the insertion fails.

        Note:
        - This method inserts a new Wi-Fi security group associated with the specified wireless Wi-Fi policy.
        - It returns True if the insertion is successful, and False if there is an error or the insertion fails.

        """
        self.log.debug(f"{wifi_policy_name}, {ssid}, {pass_phrase}, {mode}")
        return RSDB().insert_wifi_access_security_group(wifi_policy_name, ssid, pass_phrase, mode).status

    def add_wifi_security_access_group_default(self, wifi_policy_name: str) -> bool:
        """
        Add a default Wi-Fi security access group to the specified wireless Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy to add the default security access group to.

        Returns:
            bool: True if the default Wi-Fi security access group is added successfully, False otherwise.

        Note:
        - This method adds a default Wi-Fi security access group to the specified wireless Wi-Fi policy.
        - The default Wi-Fi security access group typically includes pre-defined settings for SSID, WPA passphrase, and security mode.
        - Returns True if the default Wi-Fi security access group is added successfully, and False otherwise.
        """
        self.log.debug(f"Adding default Wi-Fi security access group to policy '{wifi_policy_name}'")
        return RSDB().insert_wifi_access_security_group_default(wifi_policy_name).status
  
    def add_wifi_key_management(self, wifi_policy_name:str, key_management:str) -> bool:
        return STATUS_OK

    def add_wifi_hardware_mode(self, wifi_policy_name:str, hardware_mode: str) -> bool:
        """
        Add/update a hardware mode to a wireless Wi-Fi policy.

        Args:
            - wifi_policy_name (str): The name of the wireless Wi-Fi policy.
            - hardware_mode (str): The hardware mode to add.

        Returns:
            bool: True if the addition is successful, False if it fails.

        Raises:
            - Wi-FiPolicyNotFoundError: If the specified Wi-Fi policy is not found.
            - InvalidHardwareModeError: If the provided hardware mode is not valid.

        Note:
            - This method associates a hardware mode with the specified wireless Wi-Fi policy.
            - When a Wifi-policy name is create, a hardware-mode default of any is set
            - The hardware mode should be a valid mode from the HardwareMode enum.
            - If the Wi-Fi policy or hardware mode is not found, respective errors will be raised.
        """
        sql_result = RSDB().update_wifi_hardware_mode(wifi_policy_name, hardware_mode)
        if sql_result.status:
            self.log.error(f"Unable update wifi-hardware-mode: {hardware_mode} -> Reason: {sql_result.reason}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_wifi_policy_to_wifi_interface(self, wifi_policy_name: str, wifi_interface_name: str) -> bool:
        """
        Add a wireless Wi-Fi policy to a Wi-Fi interface.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy to associate with the Wi-Fi interface.
            wifi_interface_name (str): The name of the Wi-Fi interface to which the policy should be added.

        Returns:
            bool: STATUS_OK if the association is successful, STATUS_NOK if it fails.

        Note:
            - If the Wi-Fi policy or Wi-Fi interface is not found, respective errors will be logged.
        """
        # Check if the Wi-Fi policy exists
        if not self.wifi_policy_exist(wifi_policy_name):
            self.log.error(f"Wi-Fi policy '{wifi_policy_name}' not found.")
            return STATUS_NOK

        # Check if the Wi-Fi interface exists
        if not RSDB().interface_exists(wifi_interface_name):
            self.log.error(f"Wi-Fi interface '{wifi_interface_name}' not found.")
            return STATUS_NOK

        # Associate the Wi-Fi policy with the Wi-Fi interface
        sql_result = RSDB().insert_wifi_policy_to_wifi_interface(wifi_policy_name, wifi_interface_name)

        if sql_result.status:
            self.log.error(f"Unable to associate wifi-policy '{wifi_policy_name}' with wifi-interface '{wifi_interface_name}' -> Reason: {sql_result.reason}")
            return STATUS_NOK

        return STATUS_OK

    def add_wifi_channel(self, wifi_policy_name: str, channel: str) -> bool:
        """
        Add a Wi-Fi channel to a wireless Wi-Fi policy.

        Args:
        - wifi_policy_name (str): The name of the wireless Wi-Fi policy.
        - channel (str): The Wi-Fi channel to add.

        Returns:
        bool: STATUS_OK if the addition is successful, STATUS_NOK if it fails.

        Note:
        - This method associates a Wi-Fi channel with the specified wireless Wi-Fi policy.
        """
        return RSDB().insert_wifi_channel(wifi_policy_name, channel).status

    def get_wifi_security_policy(self, wifi_policy_name: str) -> List[dict]:
        """
        Get a list of security policies associated with a specific Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the Wi-Fi policy.

        Returns:
            List[dict]: A list of dictionaries containing security policy information.
        """
        return Result.sql_result_to_value_list(RSDB().select_wifi_security_policy(wifi_policy_name))

    def del_wifi_security_access_group(self, wifi_policy_name: str, ssid: str) -> bool:
        """
        Delete a Wi-Fi security access group with the specified SSID from the wireless Wi-Fi policy.

        Args:
            wifi_policy_name (str): The name of the wireless Wi-Fi policy from which to delete the security access group.
            ssid (str): The SSID (Service Set Identifier) of the Wi-Fi security access group to delete.

        Returns:
            bool: STATUS_OK if the Wi-Fi security access group is deleted successfully, STATUS_NOK otherwise.

        Note:
        - This method deletes a Wi-Fi security access group with the specified SSID from the wireless Wi-Fi policy.
        - Returns True if the deletion is successful, and False otherwise.
        """
        return RSDB().delete_wifi_ssid(wifi_policy_name, ssid).status

