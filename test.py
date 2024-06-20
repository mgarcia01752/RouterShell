#!/usr/bin/env python3

from lib.network_manager.network_operations.interface import Interface

print(f'Next Looopback Address: {Interface().get_next_loopback_address()}')

