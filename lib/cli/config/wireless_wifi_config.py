import cmd2
import argparse
import logging

from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.network_manager import InterfaceType
from lib.network_manager.wireless import Wifi

from lib.common.constants import STATUS_NOK, STATUS_OK

class InvalidWirelessWifiConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class WirelessWifiPolicyConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, Wifi):

    PROMPT_CMD_ALIAS = InterfaceType.WIRELESS_WIFI.value

    def __init__(self, args=None, negate=False):
        
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)
        Wifi.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)

        self.log.debug(f"__init__ > arg -> {args} -> negate={negate}")

        self.args = args
        self.negate = negate
        self.prompt = self.set_prompt()

        if args and not negate:
            self.run_command(args)
        elif args and negate:
            self.run_command(f'no {args}')

    def do_ssid(self, args, negate=False):
        self.log.debug(f"do_ssid() - args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure Service Set Identifier (SSID)",
            epilog="Usage:\n"
            "   ssid <ssid>\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for configuring SSID
        ssid_parser = subparsers.add_parser("configure", help="Configure the SSID")
        ssid_parser.add_argument("ssid_name", help="The name of the SSID")

        # Subparser for displaying the current SSID
        display_parser = subparsers.add_parser("display", help="Display the current SSID")

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        # Implement the logic to handle the parsed arguments, e.g., set or display the SSID based on subcommand

        return

    def do_wpa(self, args, negate=False):
        self.log.debug(f"do_wpa() - args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure Wireless Protected Access (WPA)",
            epilog="Usage:\n"
            "   wpa passphrase <wpa-passphrase>\n"
            "   wpa mode [WPA | WPA2 | WPA3 | MIX-MODE]\n"
            "   wpa key-mgmt [WPA-PSK | WPA-EPA | WPA-EPA-SHA256 | WPA-EPA-TLS]\n"
            "   wpa pairwise [CCMP | TKIP]\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for configuring WPA passphrase
        passphrase_parser = subparsers.add_parser("passphrase", help="Configure the WPA passphrase")
        passphrase_parser.add_argument("wpa_passphrase", help="The WPA passphrase")

        # Subparser for configuring WPA mode
        mode_parser = subparsers.add_parser("mode", help="Configure the WPA mode")
        mode_parser.add_argument("wpa_mode", choices=["WPA", "WPA2", "WPA3", "MIX-MODE"], help="The WPA mode")

        # Subparser for configuring WPA key management
        key_mgmt_parser = subparsers.add_parser("key-mgmt", help="Configure WPA key management")
        key_mgmt_parser.add_argument("wpa_key_mgmt", choices=["WPA-PSK", "WPA-EPA", "WPA-EPA-SHA256", "WPA-EPA-TLS"], help="The WPA key management")

        # Subparser for configuring WPA pairwise
        pairwise_parser = subparsers.add_parser("pairwise", help="Configure WPA pairwise")
        pairwise_parser.add_argument("wpa_pairwise", choices=["CCMP", "TKIP"], help="The WPA pairwise encryption method")

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        # Implement the logic to handle the parsed arguments, e.g., set WPA settings based on subcommand

        return

    def do_mode(self, args, negate=False):
        self.log.debug(f"do_mode() - args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure Hardware Mode",
            epilog="Usage:\n"
            "   mode [ a | b | g | ad | ax | any]\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for configuring hardware mode
        mode_parser = subparsers.add_parser("configure", help="Configure the hardware mode")
        mode_parser.add_argument("mode_option", choices=["a", "b", "g", "ad", "ax", "any"], help="The hardware mode")

        # Subparser for displaying the current hardware mode
        display_parser = subparsers.add_parser("display", help="Display the current hardware mode")

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        # Implement the logic to handle the parsed arguments, e.g., set or display the hardware mode based on subcommand

        return

    def do_channel(self, args, negate=False):
        self.log.debug(f"do_channel() - args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure Channel",
            epilog="Usage:\n"
            "   channel [1 | 2 | 3 | 4 | 5 | 6 | 8 | 7 | 8 | 9 | 10 | 11]\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        # Subparser for configuring the channel
        channel_parser = subparsers.add_parser("configure", help="Configure the channel")
        channel_parser.add_argument("channel_number", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"], help="The channel number")

        # Subparser for displaying the current channel
        display_parser = subparsers.add_parser("display", help="Display the current channel")

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        # Implement the logic to handle the parsed arguments, e.g., set or display the channel based on subcommand

        return
