import argparse
import ipaddress
import cmd2
import logging

from lib.cli.base.global_operation import GlobalUserCommand

from lib.cli.common.router_prompt import RouterPrompt, ExecMode
from lib.common.router_shell_log_control import  RouterShellLoggerSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.network_manager.network_operations.nat import NATDirection, Nat

class InvalidNatConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class NatConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Nat):

    PROMPT_CMD_ALIAS = "nat"

    def __init__(self, arg=None, negate=False):
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE)
        Nat.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().NAT_CONFIG)

        self.log.debug(f"__init__ -> (negate={negate}) -> arg -> {arg}")

        self.arg = arg
        self.prompt = self.set_prompt()

        if arg and not negate:
            self.run_command(arg)
        elif arg and negate:
            self.run_command(f'no {arg}')

    def run_command(self, cli: str, negate=False):
        self.log.debug(f"run_command() -> cli: {cli} -> negate: {negate}")

        if not isinstance(cli, list):
            cli = cli.strip().split()
            self.log.debug(f"convert cli to a list: {cli}")

        self.command = cli[0]

        cli = ' '.join([item for item in cli[1:]])

        do_method_name = f"do_{self.command}"

        self.log.debug(f"run_command({self.command}) -> {do_method_name}() -> Args: {cli}, negate={negate}")

        if hasattr(self, do_method_name) and callable(getattr(self, do_method_name)):
            getattr(self, do_method_name)(cli, negate)
        else:
            print(f"Command '{self.command}' not recognized.")

    def do_nat(self, args, negate=False):
        self.log.debug(f"do_nat() - args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure Network Address Translation (NAT)",
            epilog="Usage:\n"
            "   [no] nat pool <pool-name>\n"
            "   [no] nat pool <pool-name> <pool-ip-start> <pool-ip-end> netmask <pool-netmask>\n"
            "   [no] nat pool <pool-name> [inside|outside] source list <access-control-list-id>\n"
            "\n"
            "  <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for "nat pool <pool-name>"
        pool_parser = subparsers.add_parser("pool", help="Configure NAT pool parameters")
        pool_parser.add_argument("pool_name", help="Set pool name")

        # Subparser for "nat pool <pool-name> <pool-ip-start> <pool-ip-end> netmask <pool-netmask>"
        pool_ip_parser = subparsers.add_parser("pool_ip", help="Configure NAT pool IP range")
        pool_ip_parser.add_argument("pool_name", help="NAT pool name")
        pool_ip_parser.add_argument("pool_ip_start", help="Set pool ip address range start")
        pool_ip_parser.add_argument("pool_ip_end", help="Set pool ip address range end")
        pool_ip_parser.add_argument("pool_netmask", help="Set pool ip netmask")

        # Subparser for "nat pool <pool-name> [inside|outside] source list <access-control-list-id>"
        source_list_parser = subparsers.add_parser("domain", help="Configure NAT Access Control Parameters")
        source_list_parser.add_argument("pool_name", help="NAT pool name")
        source_list_parser.add_argument("direction", type=NATDirection, choices=list(NATDirection), help="Specify direction (inside or outside)")
        source_list_parser.add_argument("acl_id", help="Access Control List ID")

        # Parse the arguments
        parsed_args = parser.parse_args(args.split())  # Use split to convert the string to a list

        # Determine the subcommand and take appropriate actions
        if parsed_args.subcommand == "pool":
            # Handle "nat pool <pool-name>"
            self._handle_nat_pool(parsed_args.pool_name)
        elif parsed_args.subcommand == "pool_ip":
            # Handle "nat pool <pool-name> <pool-ip-start> <pool-ip-end> netmask <pool-netmask>"
            self._handle_nat_pool_ip_range(parsed_args.pool_name, parsed_args.pool_ip_start, parsed_args.pool_ip_end, parsed_args.pool_netmask)
        elif parsed_args.subcommand == "domain":
            # Handle "nat pool <pool-name> [inside|outside] source list <access-control-list-id>"
            self._handle_nat_access_control(parsed_args.pool_name, parsed_args.direction, parsed_args.acl_id)
        else:
            print("Invalid command")

    def _handle_nat_pool(self, pool_name):
        self.log.debug(f"do_nat() -> create_nat_ip_poolConfiguring NAT pool: {pool_name}")
        if Nat().create_nat_pool(pool_name):
            self.log.debug(f"Unable to create NAT Pool ({pool_name})")
            return STATUS_NOK
            
    def _handle_nat_pool_ip_range(self, pool_name, pool_ip_start, pool_ip_end, pool_netmask):
        self.log.debug(f"Configuring NAT pool IP range for {pool_name}: {pool_ip_start} - {pool_ip_end} (Netmask: {pool_netmask})")

    def _handle_nat_access_control(self, pool_name, direction, acl_id):
        self.log.debug(f"Configuring NAT Access Control for {pool_name} ({direction}): ACL ID {acl_id}")


