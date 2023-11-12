from typing import Any
import cmd2
import argparse
import logging

from lib.cli.base.global_operation import GlobalUserCommand
from lib.cli.common.cmd2_global import Cmd2GlobalSettings
from lib.cli.common.router_prompt import RouterPrompt, ExecMode
from lib.network_manager.network_manager import InterfaceType
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

from lib.network_manager.wireless_wifi import HardwareMode, Pairwise, WPAVersion, WPAkeyManagement, WifiChannel, WifiPolicy

from lib.common.constants import STATUS_NOK, STATUS_OK

class InvalidWirelessWifiConfig(Exception):
    def __init__(self, message):
        super().__init__(message)

class WirelessWifiPolicyConfig(cmd2.Cmd, GlobalUserCommand, RouterPrompt, WifiPolicy):

    PROMPT_CMD_ALIAS = InterfaceType.WIRELESS_WIFI.value

    def __init__(self, wifi_policy_name, negate=False):
        
        super().__init__()
        GlobalUserCommand.__init__(self)
        RouterPrompt.__init__(self, ExecMode.CONFIG_MODE, self.PROMPT_CMD_ALIAS)

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().WL_WIFI_POLICY_CONFIG)
        self.log.debug(f"__init__ > arg -> {wifi_policy_name} -> negate={negate}")
        self.debug = Cmd2GlobalSettings().DEBUG_WIFI_CONFIG

        WifiPolicy.__init__(self, wifi_policy_name)        

        self.wifi_policy_name = wifi_policy_name
        self.negate = negate
        self.prompt = self.set_prompt()

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

    def do_ssid(self, args, negate=False):
        """
        Configure the Service Set Identifier (SSID), passphrase, and optional security mode.

        Usage:
            ssid <ssid> passphrase <passphrase> [mode [WPA | WPA2 | WPA3]]

        Args:
            args (str): The input arguments containing SSID, passphrase, and optional mode.
            negate (bool): True if the command is a negation (e.g., 'no ssid ...'), False otherwise.

        Arguments:
            ssid (str): The SSID of the Wi-Fi network.
            passphrase (str, optional): The passphrase for the SSID (up to 64 characters).
            mode (str, optional): The security mode (WPA, WPA2, or WPA3).

        """
        self.log.debug(f"do_ssid() - args: {args}")
        
        args = f'ssid  {args}'
         
        parser = argparse.ArgumentParser(
            description="Configure Service Set Identifier (SSID), passphrase, and optional security mode.",
            epilog="Usage:\n"
                   "   ssid <ssid> passphrase <passphrase> [mode [WPA | \{WPA2\} | WPA3]]\n"
                   "\n"
                   "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")
        ssid_parser = subparsers.add_parser("ssid", help="Configure the SSID")
        ssid_parser.add_argument("ssid_name", help="SSID of the Wi-Fi network")
        ssid_parser.add_argument("passphrase", help="pass-phrase", nargs='?', choices=["pass-phrase"])
        ssid_parser.add_argument("pass_phrase", help="Passphrase (up to 64 characters)")
        ssid_parser.add_argument("wpa_mode", help="wpa-mode", nargs='?', choices=['wpa-mode'])
        ssid_parser.add_argument("wpa_mode_type", help=f"Security mode (WPA, WP2, WPA3)", nargs='?', choices=['WPA', 'WPA2', 'WPA3'])

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        if args.subcommand == "ssid":
            ssid_name = args.ssid_name
            pass_phrase = args.pass_phrase
            wpa_mode_type = args.wpa_mode_type
            
            if not wpa_mode_type:
                wpa_mode_type = WPAVersion.WPA2
            else:
                wpa_mode_type = WPAVersion[wpa_mode_type]
            
            self.log.debug(f"SSID Name: {ssid_name}, Passphrase: {pass_phrase}, WPA-Mode: {wpa_mode_type}")
            
            if self.add_security_access_group(ssid_name, pass_phrase, wpa_mode_type):
                self.log.error(f"Unable to add Security Access Group SSID Name: {ssid_name}, Passphrase: {pass_phrase}, WPA-Mode: {wpa_mode_type} to DB")
                
    def do_wpa(self, args, negate=False):
        self.log.debug(f"do_wpa() - args: {args}")

        parser = argparse.ArgumentParser(
            description="Configure Wireless Protected Access (WPA)",
            epilog="Usage:\n"
            "   wpa key-mgmt [WPA-PSK | WPA-EPA | WPA-EPA-SHA256 | WPA-EPA-TLS]\n"
            "   wpa pairwise [CCMP | TKIP]\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        key_mgmt_parser = subparsers.add_parser("key-mgmt", help="Configure WPA key management")

        key_mgmt_parser.add_argument("wpa_key_mgmt", choices=WPAkeyManagement.display_list(), 
                                     help="The WPA key management")

        pairwise_parser = subparsers.add_parser("pairwise", help="Configure WPA pairwise")
        pairwise_parser.add_argument("wpa_pairwise", choices=Pairwise.display_list(), help="The WPA pairwise encryption method")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

    def do_mode(self, args, negate=False):
        self.log.info(f"do_mode() - args: {args} -> negate: {negate}")
        
        args = f'mode  {args}'
        
        parser = argparse.ArgumentParser(
            description="Configure Hardware Mode",
            epilog="Usage:\n"
            f"   mode [{HardwareMode.display_list()}]\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")
        mode_parser = subparsers.add_parser("mode", help="Configure the hardware mode")
        mode_parser.add_argument("mode_option", help="The hardware mode")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        if args.subcommand == "mode":
            mode_option = args.mode_option
            self.log.info(f"do_mode() - mode_option: {mode_option}")
            
            if self.add_hardware_mode(HardwareMode[mode_option.upper()]):
                self.log.error(f"Unable to add hardware-mode: {mode_option} to wifi-policy: {self.wifi_policy_name}")

    def do_channel(self, args, negate=False):
        self.log.debug(f"do_channel() - args: {args}")
        args = f'channel  {args}'
        parser = argparse.ArgumentParser(
            description="Configure Channel",
            epilog="Usage:\n"
            "   channel [1 | 2 | 3 | 4 | 5 | 6 | 8 | 7 | 8 | 9 | 10 | 11]\n"
            "\n"
            "   <suboption> --help                           Get help for specific suboptions."
        )

        subparsers = parser.add_subparsers(dest="subcommand")

        channel_parser = subparsers.add_parser("configure", help="Configure the channel")
        channel_parser.add_argument("channel_number", choices=WifiChannel.display_list(), help="The channel number")

        try:
            if not isinstance(args, list):
                args = parser.parse_args(args.split())
            else:
                args = parser.parse_args(args)
        except SystemExit:
            return

        if args.subcommand == "channel":
            self.add_channel(WifiChannel[args.channel_number])
    
    def do_ieee80211(self, args: str, negate: bool = False):
        parser = argparse.ArgumentParser(
            description="Configure IEEE802.11 Support",
            epilog="Usage:\n"
                   "[no] ieee80211 [d | h | ac | ax | be | x | n | w]\n"
        )

        subparsers = parser.add_subparsers(dest="subcommand")
        ieee80211_parser = subparsers.add_parser("ieee80211", 
                                                 choices=["d", "h", "ac", "ax", "be", "x", "w", 'n'],
                                                 help="Configure IEEE802.11 support")
        
        parsed_args = parser.parse_args(args)
                
        return

    def do_end(self, _: Any) -> None:

        if not self.security_access_group_entry_exist(self.wifi_policy_name):
            self.add_security_access_group_default(self.wifi_policy_name)
            
        super().do_end()
        