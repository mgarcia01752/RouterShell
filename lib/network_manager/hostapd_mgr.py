from enum import Enum
from lib.common.constants import STATUS_NOK, STATUS_OK

from lib.network_manager.common.run_commands import RunCommand

class HostapdIEEE802Config(Enum):
    IEEE80211AC = "ieee80211ac"
    IEEE80211AX = "ieee80211ax"
    IEEE80211BE = "ieee80211be"
    IEEE80211D = "ieee80211d"
    IEEE80211H = "ieee80211h"
    IEEE80211N = "ieee80211n"
    IEEE8021X = "ieee8021x"
    IEEE80211W = "ieee80211w"

class HostapdConfigGenerator():
    def __init__(self):
        """
        Initialize the HostapdConfigGenerator.

        The constructor sets up an empty list to store the Hostapd configuration lines.
        """
        self.config = []

    def generate_config(self):
        """
        Generate the Hostapd configuration.

        Returns:
            List[str]: A list of configuration lines for the Hostapd configuration.
        """
        return self.config

    def add_wmm(self, value: int):
        """
        Set the Wireless Multimedia (WMM) support.

        Args:
            value (int): The value to set for WMM (1 for enabled, 0 for disabled).
        """
        if value in [0, 1]:
            self.config.append(f'wmm_enabled={value}')
        else:
            print("Invalid WMM value. Use 1 for enabled or 0 for disabled.")

    def add_ieee802(self, option: HostapdIEEE802Config, value: int):
        """
        Set the IEEE802 configuration option to the specified value.

        Args:
            option (HostapdIEEE802Config): The IEEE802 configuration option to set.
            value (int): The value to set for the option (0 or 1).
        """
        if option.value in ["ieee80211d","ieee80211d", "ieee80211h", "ieee80211ac", "ieee80211ax", "ieee80211be", "ieee8021x", "ieee80211w"]:
            self.config.append(f'{option.value}={value}')
        else:
            print(f"Invalid IEEE802 option: {option.value}")
            
    def add_bss(self, bss_name: str):
        """
        Add a BSS (Basic Service Set) configuration to the Hostapd config.

        Args:
            bss_name (str): The name of the BSS.
        """
        self.config.append(f'\n# BSS configuration for {bss_name}')
        self.config.append(f'bss={bss_name}')

    def add_interface(self, interface_name: str):
        """
        Add interface configuration to the BSS.

        Args:
            interface_name (str): The name of the interface.
        """
        self.config.append(f'interface={interface_name}')

    def add_bridge(self, bridge_name: str):
        """
        Add bridge configuration to the BSS.

        Args:
            bridge_name (str): The name of the bridge.
        """
        self.config.append(f'bridge={bridge_name}')

    def add_ssid(self, ssid: str):
        """
        Add SSID (Service Set Identifier) configuration to the BSS.

        Args:
            ssid (str): The SSID to set.
        """
        self.config.append(f'ssid={ssid}')

    def add_channel(self, channel: int):
        """
        Add channel configuration to the Hostapd configuration.

        Args:
            channel (int): The channel number to set.
        """
        self.config.append(f'channel={channel}')

    def add_hw_mode(self, mode: str):
        """
        Add operation mode configuration to the Hostapd configuration.

        Args:
            mode (str): The operation mode to set (e.g., 'a', 'b', 'g', 'ad').
        """
        valid_modes = ['a', 'b', 'g', 'ad']

        if mode in valid_modes:
            self.config.append(f'hw_mode={mode}')
        else:
            print(f"Invalid operation mode: {mode}. Use one of {valid_modes}")

    def add_auth_algs(self, value: int):
        """
        Set the allowed authentication algorithms in the Hostapd configuration.

        Args:
            value (int): Bit-field of allowed authentication algorithms.
                         Bit 0 = Open System Authentication
                         Bit 1 = Shared Key Authentication (requires WEP)
        """
        if 0 <= value <= 3:
            self.config.append(f'auth_algs={value}')
        else:
            print("Invalid value for auth_algs. Use a bit-field value between 0 and 3.")

    def add_wpa(self, wpa_version: int):
        """
        Add WPA version configuration to the BSS.

        Args:
            wpa_version (int): Set to 2 for WPA2, 3 for WPA3.
        """
        self.config.append(f'wpa={wpa_version}')

    def add_wpa_psk(self, psk: str):
        """
        Add WPA PSK (Pre-Shared Key) configuration to the BSS.

        Args:
            psk (str): The WPA PSK to set.
        """
        self.config.append(f'wpa_psk={psk}')

    def add_wpa_passphrase(self, passphrase: str):
        """
        Add WPA passphrase configuration to the BSS.

        Args:
            passphrase (str): The WPA passphrase to set.
        """
        self.config.append(f'wpa_passphrase={passphrase}')

    def add_wpa_psk_file(self, psk_file: str):
        """
        Add WPA PSK file configuration to the BSS.

        Args:
            psk_file (str): The path to the WPA PSK file.
        """
        self.config.append(f'wpa_psk_file={psk_file}')

    def add_wpa_psk_radius(self, psk_radius: str):
        """
        Add WPA PSK radius configuration to the BSS.

        Args:
            psk_radius (str): The WPA PSK radius setting.
        """
        self.config.append(f'wpa_psk_radius={psk_radius}')

    def add_wpa_key_mgmt(self, key_mgmt: str):
        """
        Add WPA key management configuration to the BSS.

        Args:
            key_mgmt (str): The WPA key management options.
        """
        self.config.append(f'wpa_key_mgmt={key_mgmt}')

    def add_wpa_pairwise(self, pairwise: str):
        """
        Add WPA pairwise configuration to the BSS.

        Args:
            pairwise (str): The WPA pairwise options.
        """
        self.config.append(f'wpa_pairwise={pairwise}')

    def add_wpa_group_rekey(self, rekey_interval: int):
        """
        Add WPA group rekey configuration to the BSS.

        Args:
            rekey_interval (int): The rekey interval in seconds.
        """
        self.config.append(f'wpa_group_rekey={rekey_interval}')

    def add_wpa_strict_rekey(self, strict_rekey: int):
        """
        Add WPA strict rekey configuration to the BSS.

        Args:
            strict_rekey (int): Set to 1 to enable strict rekeying, 0 to disable.
        """
        self.config.append(f'wpa_strict_rekey={strict_rekey}')

    def add_ap_max_inactivity(self, max_inactivity: int):
        """
        Add maximum inactivity timeout for stations.

        Args:
            max_inactivity (int): Maximum inactivity timeout in seconds.
        """
        self.config.append(f'ap_max_inactivity={max_inactivity}')

    def add_ap_isolate(self, enable_isolate: int):
        """
        Add AP isolation configuration.

        Args:
            enable_isolate (int): Set to 1 to enable AP isolation, 0 to disable.
        """
        self.config.append(f'ap_isolate={enable_isolate}')

    def add_eap_message(self, eap_message: str):
        """
        Add EAP message configuration.

        Args:
            eap_message (str): EAP message to include in the configuration.
        """
        self.config.append(f'eap_message={eap_message}')

    def add_eap_reauth_period(self, reauth_period: int):
        """
        Add EAP reauthentication period.

        Args:
            reauth_period (int): EAP reauthentication period in seconds.
        """
        self.config.append(f'eap_reauth_period={reauth_period}')

    def add_eap_user_file(self, user_file: str):
        """
        Add EAP user file configuration.

        Args:
            user_file (str): Path to the EAP user file.
        """
        self.config.append(f'eap_user_file={user_file}')

    def add_eap_sim_db(self, sim_db: str):
        """
        Add EAP-SIM database configuration.

        Args:
            sim_db (str): EAP-SIM database configuration.
        """
        self.config.append(f'eap_sim_db={sim_db}')

    def add_eap_sim_db_timeout(self, timeout: int):
        """
        Add EAP-SIM database timeout configuration.

        Args:
            timeout (int): EAP-SIM database timeout in seconds.
        """
        self.config.append(f'eap_sim_db_timeout={timeout}')

    def add_eap_fast_a_id(self, a_id: str):
        """
        Add EAP-FAST A-ID configuration.

        Args:
            a_id (str): EAP-FAST A-ID.
        """
        self.config.append(f'eap_fast_a_id={a_id}')

    def add_eap_fast_a_id_info(self, a_id_info: str):
        """
        Add EAP-FAST A-ID-Info configuration.

        Args:
            a_id_info (str): EAP-FAST A-ID-Info.
        """
        self.config.append(f'eap_fast_a_id_info={a_id_info}')

    def add_eap_fast_prov(self, prov: int):
        """
        Add EAP-FAST provisioning configuration.

        Args:
            prov (int): EAP-FAST provisioning option.
        """
        self.config.append(f'eap_fast_prov={prov}')

    def add_eap_teap_auth(self, enable_teap_auth: int):
        """
        Add EAP-TEAP authentication configuration.

        Args:
            enable_teap_auth (int): Set to 1 to enable EAP-TEAP, 0 to disable.
        """
        self.config.append(f'eap_teap_auth={enable_teap_auth}')

    def add_eap_teap_pac_no_inner(self, enable_pac_no_inner: int):
        """
        Add EAP-TEAP PAC without inner method configuration.

        Args:
            enable_pac_no_inner (int): Set to 1 to enable PAC without inner method, 0 to disable.
        """
        self.config.append(f'eap_teap_pac_no_inner={enable_pac_no_inner}')

    def add_eap_teap_separate_result(self, enable_separate_result: int):
        """
        Add EAP-TEAP separate result configuration.

        Args:
            enable_separate_result (int): Set to 1 to enable separate result, 0 to disable.
        """
        self.config.append(f'eap_teap_separate_result={enable_separate_result}')

    def add_eap_teap_id(self, teap_id: int):
        """
        Add EAP-TEAP ID configuration.

        Args:
            teap_id (int): EAP-TEAP ID.
        """
        self.config.append(f'eap_teap_id={teap_id}')

    def add_eap_sim_aka_result_ind(self, result_ind: int):
        """
        Add EAP-SIM-AKA result indication configuration.

        Args:
            result_ind (int): Set to 1 to enable result indication, 0 to disable.
        """
        self.config.append(f'eap_sim_aka_result_ind={result_ind}')

    def add_eap_sim_id(self, sim_id: int):
        """
        Add EAP-SIM ID configuration.

        Args:
            sim_id (int): EAP-SIM ID.
        """
        self.config.append(f'eap_sim_id={sim_id}')

    def add_eap_sim_aka_fast_reauth_limit(self, limit: int):
        """
        Add EAP-SIM-AKA fast reauthentication limit configuration.

        Args:
            limit (int): EAP-SIM-AKA fast reauthentication limit.
        """
        self.config.append(f'eap_sim_aka_fast_reauth_limit={limit}')

    def add_eap_server_erp(self, enable_erp: int):
        """
        Add EAP server ERP configuration.

        Args:
            enable_erp (int): Set to 1 to enable EAP server ERP, 0 to disable.
        """
        self.config.append(f'eap_server_erp={enable_erp}')

    def add_ap_table_max_size(self, max_size: int):
        """
        Add maximum AP table size configuration.

        Args:
            max_size (int): Maximum AP table size.
        """
        self.config.append(f'ap_table_max_size={max_size}')

    def add_ap_table_expiration_time(self, expiration_time: int):
        """
        Add AP table expiration time configuration.

        Args:
            expiration_time (int): AP table expiration time in seconds.
        """
        self.config.append(f'ap_table_expiration_time={expiration_time}')

    def add_ap_setup_locked(self, setup_locked: int):
        """
        Add AP setup locked configuration.

        Args:
            setup_locked (int): Set to 1 to lock AP setup, 0 to unlock.
        """
        self.config.append(f'ap_setup_locked={setup_locked}')

    def add_ap_pin(self, pin: str):
        """
        Add AP PIN configuration.

        Args:
            pin (str): AP PIN.
        """
        self.config.append(f'ap_pin={pin}')

    def add_ap_settings(self, ap_settings: str):
        """
        Add AP settings configuration.

        Args:
            ap_settings (str): AP settings.
        """
        self.config.append(f'ap_settings={ap_settings}')

    def add_multi_ap_backhaul_ssid(self, backhaul_ssid: str):
        """
        Add Multi-AP backhaul SSID configuration.

        Args:
            backhaul_ssid (str): Multi-AP backhaul SSID.
        """
        self.config.append(f'multi_ap_backhaul_ssid={backhaul_ssid}')

    def add_multi_ap_backhaul_wpa_psk(self, backhaul_wpa_psk: str):
        """
        Add Multi-AP backhaul WPA PSK configuration.

        Args:
            backhaul_wpa_psk (str): Multi-AP backhaul WPA PSK.
        """
        self.config.append(f'multi_ap_backhaul_wpa_psk={backhaul_wpa_psk}')

    def add_multi_ap_backhaul_wpa_passphrase(self, backhaul_passphrase: str):
        """
        Add Multi-AP backhaul WPA passphrase configuration.

        Args:
            backhaul_passphrase (str): Multi-AP backhaul WPA passphrase.
        """
        self.config.append(f'multi_ap_backhaul_wpa_passphrase={backhaul_passphrase}')

    def add_qos_map_set(self, qos_map_set: str):
        """
        Add QoS map set configuration.

        Args:
            qos_map_set (str): QoS map set configuration.
        """
        self.config.append(f'qos_map_set={qos_map_set}')

    def add_dynamic_vlan(self, dynamic_vlan: int):
        """
        Add dynamic VLAN configuration to the BSS.

        Args:
            dynamic_vlan (int): Set to 1 to enable dynamic VLAN support, 0 to disable.
        """
        self.config.append(f'dynamic_vlan={dynamic_vlan}')

    def add_vlan_file(self, vlan_file: str):
        """
        Add the VLAN configuration file path to the BSS.

        Args:
            vlan_file (str): Path to the VLAN configuration file.
        """
        self.config.append(f'vlan_file={vlan_file}')

    def add_vlan_tagged_interface(self, tagged_interface: str):
        """
        Add the tagged interface for VLANs to the BSS.

        Args:
            tagged_interface (str): Name of the tagged interface (e.g., "eth0").
        """
        self.config.append(f'vlan_tagged_interface={tagged_interface}')

    def add_vlan_bridge(self, vlan_bridge: str):
        """
        Add the VLAN bridge to the BSS.

        Args:
            vlan_bridge (str): Name of the VLAN bridge (e.g., "brvlan").
        """
        self.config.append(f'vlan_bridge={vlan_bridge}')

class HostapdManager(RunCommand, HostapdConfigGenerator):
    def __init__(self):
        """
        Initializes the HostapdManager, inheriting from RunCommand and HostapdConfigGenerator.
        """
        super().__init__()

    def start(self) -> bool:
        """
        Start the hostapd service.

        Returns:
            bool: STATUS_OK if the service starts successfully, STATUS_NOK otherwise.
        """
        try:
            # Run the 'service hostapd start' command
            result = self.run_command(["service", "hostapd", "start"])
            return STATUS_OK if result.exit_code == STATUS_OK else STATUS_NOK

        except Exception as e:
            # Log and handle the exception
            self.log.error(f"Failed to start hostapd service: {e}")
            return STATUS_NOK

    def restart(self) -> bool:
        """
        Restart the hostapd service.

        Returns:
            bool: STATUS_OK if the service restarts successfully, STATUS_NOK otherwise.
        """
        try:
            # Run the 'service hostapd restart' command
            result = self.run_command(["service", "hostapd", "restart"])
            return STATUS_OK if result.exit_code == STATUS_OK else STATUS_NOK

        except Exception as e:
            # Log and handle the exception
            self.log.error(f"Failed to restart hostapd service: {e}")
            return STATUS_NOK

    def stop(self) -> bool:
        """
        Stop the hostapd service.

        Returns:
            bool: STATUS_OK if the service stops successfully, STATUS_NOK otherwise.
        """
        try:
            # Run the 'service hostapd stop' command
            result = self.run_command(["service", "hostapd", "stop"])
            return STATUS_OK if result.exit_code == STATUS_OK else STATUS_NOK

        except Exception as e:
            # Log and handle the exception
            self.log.error(f"Failed to stop hostapd service: {e}")
            return STATUS_NOK

    def load(self) -> bool:
        """
        Load the Hostapd configuration.

        Returns:
            bool: STATUS_OK if the configuration is loaded successfully, STATUS_NOK otherwise.
        """
        try:
            # Generate Hostapd configuration
            config_lines = self.generate_config()

            # Write the configuration to the hostapd.conf file
            with open("/etc/hostapd/hostapd.conf", "w") as file:
                file.write("\n".join(config_lines))

            # Restart the hostapd service to apply the new configuration
            restart_result = self.restart()

            return restart_result

        except Exception as e:
            # Log and handle the exception
            self.log.error(f"Failed to load Hostapd configuration: {e}")
            return STATUS_NOK

