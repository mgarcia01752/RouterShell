#! /usr/bin/env python3

from lib.cli.router_main_cli import RouterCLI
import logging

def main():
    cli = RouterCLI()
    cli.run()

if __name__ == "__main__":
    main()
