class HostapdConfigGenerator:
    def __init__(self):
        self.config = []

    def add_bss(self, bss_name):
        """
        Add a BSS (Basic Service Set) configuration to the Hostapd config.
        Args:
            bss_name (str): The name of the BSS.
        """
        self.config.append(f'\n# BSS configuration for {bss_name}')
        self.config.append(f'bss={bss_name}')

    def add_interface(self, interface_name):
        """
        Add interface configuration to the BSS.
        Args:
            interface_name (str): The name of the interface.
        """
        self.config.append(f'interface={interface_name}')

    def add_bridge(self, bridge_name):
        """
        Add bridge configuration to the BSS.
        Args:
            bridge_name (str): The name of the bridge.
        """
        self.config.append(f'bridge={bridge_name}')

    def add_ssid(self, ssid):
        """
        Add SSID (Service Set Identifier) configuration to the BSS.
        Args:
            ssid (str): The SSID to set.
        """
        self.config.append(f'ssid={ssid}')

    def add_wpa(self, wpa_version):
        """
        Add WPA version configuration to the BSS.
        Args:
            wpa_version (int): Set to 2 for WPA2, 3 for WPA3.
        """
        self.config.append(f'wpa={wpa_version}')

    def add_wpa_psk(self, psk):
        """
        Add WPA PSK (Pre-Shared Key) configuration to the BSS.
        Args:
            psk (str): The WPA PSK to set.
        """
        self.config.append(f'wpa_psk={psk}')

    def add_wpa_passphrase(self, passphrase):
        """
        Add WPA passphrase configuration to the BSS.
        Args:
            passphrase (str): The WPA passphrase to set.
        """
        self.config.append(f'wpa_passphrase={passphrase}')

    def add_wpa_psk_file(self, psk_file):
        """
        Add WPA PSK file configuration to the BSS.
        Args:
            psk_file (str): The path to the WPA PSK file.
        """
        self.config.append(f'wpa_psk_file={psk_file}')

    def add_wpa_psk_radius(self, psk_radius):
        """
        Add WPA PSK radius configuration to the BSS.
        Args:
            psk_radius (str): The WPA PSK radius setting.
        """
        self.config.append(f'wpa_psk_radius={psk_radius}')

    def add_wpa_key_mgmt(self, key_mgmt):
        """
        Add WPA key management configuration to the BSS.
        Args:
            key_mgmt (str): The WPA key management options.
        """
        self.config.append(f'wpa_key_mgmt={key_mgmt}')

    def add_wpa_pairwise(self, pairwise):
        """
        Add WPA pairwise configuration to the BSS.
        Args:
            pairwise (str): The WPA pairwise options.
        """
        self.config.append(f'wpa_pairwise={pairwise}')

    def add_wpa_group_rekey(self, rekey_interval):
        """
        Add WPA group rekey configuration to the BSS.
        Args:
            rekey_interval (int): The rekey interval in seconds.
        """
        self.config.append(f'wpa_group_rekey={rekey_interval}')

    def add_wpa_strict_rekey(self, strict_rekey):
        """
        Add WPA strict rekey configuration to the BSS.
        Args:
            strict_rekey (int): Set to 1 to enable strict rekeying, 0 to disable.
        """
        self.config.append(f'wpa_strict_rekey={strict_rekey}')

    def add_ap_max_inactivity(self, max_inactivity):
        """
        Add maximum inactivity timeout for stations.
        Args:
            max_inactivity (int): Maximum inactivity timeout in seconds.
        """
        self.config.append(f'ap_max_inactivity={max_inactivity}')

    def add_ap_isolate(self, enable_isolate):
        """
        Add AP isolation configuration.
        Args:
            enable_isolate (int): Set to 1 to enable AP isolation, 0 to disable.
        """
        self.config.append(f'ap_isolate={enable_isolate}')

    def add_eap_message(self, eap_message):
        """
        Add EAP message configuration.
        Args:
            eap_message (str): EAP message to include in the configuration.
        """
        self.config.append(f'eap_message={eap_message}')

    def add_eap_reauth_period(self, reauth_period):
        """
        Add EAP reauthentication period.
        Args:
            reauth_period (int): EAP reauthentication period in seconds.
        """
        self.config.append(f'eap_reauth_period={reauth_period}')

    def add_eap_user_file(self, user_file):
        """
        Add EAP user file configuration.
        Args:
            user_file (str): Path to the EAP user file.
        """
        self.config.append(f'eap_user_file={user_file}')

    def add_eap_sim_db(self, sim_db):
        """
        Add EAP-SIM database configuration.
        Args:
            sim_db (str): EAP-SIM database configuration.
        """
        self.config.append(f'eap_sim_db={sim_db}')

    def add_eap_sim_db_timeout(self, timeout):
        """
        Add EAP-SIM database timeout configuration.
        Args:
            timeout (int): EAP-SIM database timeout in seconds.
        """
        self.config.append(f'eap_sim_db_timeout={timeout}')

    def add_eap_fast_a_id(self, a_id):
        """
        Add EAP-FAST A-ID configuration.
        Args:
            a_id (str): EAP-FAST A-ID.
        """
        self.config.append(f'eap_fast_a_id={a_id}')

    def add_eap_fast_a_id_info(self, a_id_info):
        """
        Add EAP-FAST A-ID-Info configuration.
        Args:
            a_id_info (str): EAP-FAST A-ID-Info.
        """
        self.config.append(f'eap_fast_a_id_info={a_id_info}')

    def add_eap_fast_prov(self, prov):
        """
        Add EAP-FAST provisioning configuration.
        Args:
            prov (int): EAP-FAST provisioning option.
        """
        self.config.append(f'eap_fast_prov={prov}')

    def add_eap_teap_auth(self, enable_teap_auth):
        """
        Add EAP-TEAP authentication configuration.
        Args:
            enable_teap_auth (int): Set to 1 to enable EAP-TEAP, 0 to disable.
        """
        self.config.append(f'eap_teap_auth={enable_teap_auth}')

    def add_eap_teap_pac_no_inner(self, enable_pac_no_inner):
        """
        Add EAP-TEAP PAC without inner method configuration.
        Args:
            enable_pac_no_inner (int): Set to 1 to enable PAC without inner method, 0 to disable.
        """
        self.config.append(f'eap_teap_pac_no_inner={enable_pac_no_inner}')

    def add_eap_teap_separate_result(self, enable_separate_result):
        """
        Add EAP-TEAP separate result configuration.
        Args:
            enable_separate_result (int): Set to 1 to enable separate result, 0 to disable.
        """
        self.config.append(f'eap_teap_separate_result={enable_separate_result}')

    def add_eap_teap_id(self, teap_id):
        """
        Add EAP-TEAP ID configuration.
        Args:
            teap_id (int): EAP-TEAP ID.
        """
        self.config.append(f'eap_teap_id={teap_id}')

    def add_eap_sim_aka_result_ind(self, result_ind):
        """
        Add EAP-SIM-AKA result indication configuration.
        Args:
            result_ind (int): Set to 1 to enable result indication, 0 to disable.
        """
        self.config.append(f'eap_sim_aka_result_ind={result_ind}')

    def add_eap_sim_id(self, sim_id):
        """
        Add EAP-SIM ID configuration.
        Args:
            sim_id (int): EAP-SIM ID.
        """
        self.config.append(f'eap_sim_id={sim_id}')

    def add_eap_sim_aka_fast_reauth_limit(self, limit):
        """
        Add EAP-SIM-AKA fast reauthentication limit configuration.
        Args:
            limit (int): EAP-SIM-AKA fast reauthentication limit.
        """
        self.config.append(f'eap_sim_aka_fast_reauth_limit={limit}')

    def add_eap_server_erp(self, enable_erp):
        """
        Add EAP server ERP configuration.
        Args:
            enable_erp (int): Set to 1 to enable EAP server ERP, 0 to disable.
        """
        self.config.append(f'eap_server_erp={enable_erp}')

    def add_ap_table_max_size(self, max_size):
        """
        Add maximum AP table size configuration.
        Args:
            max_size (int): Maximum AP table size.
        """
        self.config.append(f'ap_table_max_size={max_size}')

    def add_ap_table_expiration_time(self, expiration_time):
        """
        Add AP table expiration time configuration.
        Args:
            expiration_time (int): AP table expiration time in seconds.
        """
        self.config.append(f'ap_table_expiration_time={expiration_time}')

    def add_ap_setup_locked(self, setup_locked):
        """
        Add AP setup locked configuration.
        Args:
            setup_locked (int): Set to 1 to lock AP setup, 0 to unlock.
        """
        self.config.append(f'ap_setup_locked={setup_locked}')

    def add_ap_pin(self, pin):
        """
        Add AP PIN configuration.
        Args:
            pin (str): AP PIN.
        """
        self.config.append(f'ap_pin={pin}')

    def add_ap_settings(self, ap_settings):
        """
        Add AP settings configuration.
        Args:
            ap_settings (str): AP settings.
        """
        self.config.append(f'ap_settings={ap_settings}')

    def add_multi_ap_backhaul_ssid(self, backhaul_ssid):
        """
        Add Multi-AP backhaul SSID configuration.
        Args:
            backhaul_ssid (str): Multi-AP backhaul SSID.
        """
        self.config.append(f'multi_ap_backhaul_ssid={backhaul_ssid}')

    def add_multi_ap_backhaul_wpa_psk(self, backhaul_wpa_psk):
        """
        Add Multi-AP backhaul WPA PSK configuration.
        Args:
            backhaul_wpa_psk (str): Multi-AP backhaul WPA PSK.
        """
        self.config.append(f'multi_ap_backhaul_wpa_psk={backhaul_wpa_psk}')

    def add_multi_ap_backhaul_wpa_passphrase(self, backhaul_passphrase):
        """
        Add Multi-AP backhaul WPA passphrase configuration.
        Args:
            backhaul_passphrase (str): Multi-AP backhaul WPA passphrase.
        """
        self.config.append(f'multi_ap_backhaul_wpa_passphrase={backhaul_passphrase}')

    def add_qos_map_set(self, qos_map_set):
        """
        Add QoS map set configuration.
        Args:
            qos_map_set (str): QoS map set configuration.
        """
        self.config.append(f'qos_map_set={qos_map_set}')

    def add_dynamic_vlan(self, dynamic_vlan):
        """
        Add dynamic VLAN configuration to the BSS.
        Args:
            dynamic_vlan (int): Set to 1 to enable dynamic VLAN support, 0 to disable.
        """
        self.config.append(f'dynamic_vlan={dynamic_vlan}')

    def add_vlan_file(self, vlan_file):
        """
        Add the VLAN configuration file path to the BSS.
        Args:
            vlan_file (str): Path to the VLAN configuration file.
        """
        self.config.append(f'vlan_file={vlan_file}')

    def add_vlan_tagged_interface(self, tagged_interface):
        """
        Add the tagged interface for VLANs to the BSS.
        Args:
            tagged_interface (str): Name of the tagged interface (e.g., "eth0").
        """
        self.config.append(f'vlan_tagged_interface={tagged_interface}')

    def add_vlan_bridge(self, vlan_bridge):
        """
        Add the VLAN bridge to the BSS.
        Args:
            vlan_bridge (str): Name of the VLAN bridge (e.g., "brvlan").
        """
        self.config.append(f'vlan_bridge={vlan_bridge}')

    def add_vlan_naming(self, vlan_naming):
        """
        Add VLAN naming configuration to the BSS.
        Args:
            vlan_naming (int): Set to 1 to enable VLAN naming, 0 to disable.
        """
        self.config.append(f'vlan_naming={vlan_naming}')

    def add_wps_state(self, wps_state):
        """
        Add WPS state configuration to the BSS.
        Args:
            wps_state (int): WPS state (1 for enabled, 2 for disabled, 0 for unset).
        """
        self.config.append(f'wps_state={wps_state}')

    def add_wps_independent(self, wps_independent):
        """
        Add WPS independent configuration to the BSS.
        Args:
            wps_independent (int): Set to 1 to enable independent WPS, 0 to disable.
        """
        self.config.append(f'wps_independent={wps_independent}')

    def add_wps_pin_requests(self, pin_requests_file):
        """
        Add WPS PIN requests configuration to the BSS.
        Args:
            pin_requests_file (str): Path to the WPS PIN requests file.
        """
        self.config.append(f'wps_pin_requests={pin_requests_file}')

    def add_wps_cred_processing(self, cred_processing):
        """
        Add WPS credential processing configuration to the BSS.
        Args:
            cred_processing (int): Set to 1 to enable credential processing, 0 to disable.
        """
        self.config.append(f'wps_cred_processing={cred_processing}')

    def add_wps_cred_add_sae(self, cred_add_sae):
        """
        Add WPS credential adding SAE configuration to the BSS.
        Args:
            cred_add_sae (int): Set to 1 to enable adding SAE with credentials, 0 to disable.
        """
        self.config.append(f'wps_cred_add_sae={cred_add_sae}')

    def add_wps_rf_bands(self, rf_bands):
        """
        Add WPS RF bands configuration to the BSS.
        Args:
            rf_bands (str): WPS RF bands (e.g., "a", "g").
        """
        self.config.append(f'wps_rf_bands={rf_bands}')

    def add_wps_application_ext(self, application_ext_hexdump):
        """
        Add WPS application extension configuration to the BSS.
        Args:
            application_ext_hexdump (str): Hexdump of the WPS application extension.
        """
        self.config.append(f'wps_application_ext={application_ext_hexdump}')

    def generate_config(self):
        return self.config

