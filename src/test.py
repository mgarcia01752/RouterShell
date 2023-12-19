#!/usr/bin/env python3

from lib.network_manager.hostapd_mgr import HostapdManager


hm = HostapdManager()



interface='wlx80afca061616'
driver='nl80211'
ssid='MyTestSSID'
hw_mode='g'
channel='6'
auth_algs='1'
wpa='2'
wpa_key_mgmt='WPA-PSK'
wpa_passphrase='YourPassword'

hm.add_interface("wlan0")  # Change the interface name if needed
hm.add_driver("nl80211")
hm.add_ssid("YourSSID")  # Replace with your desired SSID
hm.add_hw_mode("g")
hm.add_channel(6)  # Set your desired channel number
hm.add_auth_algs(1)
hm.add_wpa(2)
hm.add_wpa_key_mgmt("WPA-PSK")
hm.add_wpa_passphrase("YourPassword")  # Replace with your desired WPA passphrase

    



