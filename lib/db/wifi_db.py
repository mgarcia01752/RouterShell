import logging
from typing import List

from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB, Result
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK

class WifiDB:
    
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WL_WIFI_DB)
            
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


    def add_wifi_policy(cls, wifi_policy_name: str) -> bool:
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
        return RSDB().insert_wifi_policy(wifi_policy_name).status

    def add_wifi_security_access_group(cls, wifi_policy_name: str, ssid: str, pass_phrase: str, mode: str) -> bool:
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
        cls.log.debug(f"{wifi_policy_name}, {ssid}, {pass_phrase}, {mode}")
        return RSDB().insert_wifi_access_security_group(wifi_policy_name, ssid, pass_phrase, mode).status
    
    def add_wifi_key_management(cls, wifi_policy_name:str, key_management:str) -> bool:
        return STATUS_OK
    
    def add_wifi_hardware_mode(cls, wifi_policy_name:str, mode:str) -> bool:
        return RSDB()
