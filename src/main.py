#!/usr/bin/env python3

from lib.router_cli import RouterCLI

import platform
import subprocess

if __name__ == '__main__':
    
    # Check if the program is running on a Linux system
    if platform.system() != 'Linux':
        print("This program is intended to run on a Linux system.")
    else:
        RouterCLI().cmdloop()