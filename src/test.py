#!/usr/bin/env python3

from lib.network_manager.wireless_wifi import WifiInterface

w_if = 'wlx80afca061616'

wi = WifiInterface(w_if)

print(wi.get_wifi_interfaces())

print(wi.scan(w_if))

