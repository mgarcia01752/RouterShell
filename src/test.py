#!/usr/bin/env python3

from lib.network_manager.interface import Interface


print(Interface().get_interface_type_via_db('wlan0'))
