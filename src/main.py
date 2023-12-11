#!/usr/bin/env python3

import os
from lib.cli.router_main_cli import RouterCLI

import platform

if __name__ == '__main__':
    
    # Check if the program is running on a Linux system
    if platform.system() != 'Linux':
        print("This program is intended to run on a Linux system.")
    else:
        router_shell_log_dir = '/tmp/log'
        if not os.path.exists(router_shell_log_dir):
            os.makedirs(router_shell_log_dir)
            
        RouterCLI().cmdloop()