#!/usr/bin/env python3

from lib.network_manager.hostapd_mgr import HostapdManager

config_generator = HostapdManager()

interface_name = 'wlx80afca061616'
driver = 'nl80211'
ssid = 'MyTestSSID'
hw_mode = 'g'
channel = '6'
auth_algs = '1'
wpa_version = '2'
wpa_key_mgmt = 'WPA-PSK'
wpa_passphrase = 'YourPassword'

# Create an instance of HostapdConfigGenerator

# Set the configuration variables
config_generator.add_interface(interface_name)
# config_generator.add_driver(driver)
config_generator.add_ssid(ssid)
config_generator.add_hw_mode(hw_mode)
config_generator.add_channel(int(channel))  # Assuming channel is an integer
# Assuming auth_algs is an integer
config_generator.add_auth_algs(int(auth_algs))
# Assuming wpa_version is an integer
config_generator.add_wpa(int(wpa_version))
config_generator.add_wpa_key_mgmt(wpa_key_mgmt)
config_generator.add_wpa_passphrase(wpa_passphrase)

# Load the configuration
config_generator.load()
