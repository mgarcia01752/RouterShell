import json
import logging

from tabulate import tabulate
from lib.network_manager.interface import Interface
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.cli.common.cmd2_global import Cmd2GlobalSettings as CGS


class InterfaceShow(Interface):
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().IF_SHOW)
        self.debug = CGS.DEBUG_SHOW_INTERFACE
        self.arg = arg
        
    def is_secondary_address(self, interface, address):
        for addr_info in interface["addr_info"]:
            if addr_info["family"] in ["inet", "inet6"] and addr_info["local"] == address:
                if "label" in addr_info and "secondary" in addr_info["label"]:
                    return True
        return False


    def show_ip_interface_brief(self):
        ip_info_json = self.get_ip_addr_info()
        
        table = []
        for interface in ip_info_json:
            interface_name = interface["ifname"]
            mac = interface.get("address", "N/A")
            inet_addresses = []
            inet6_addresses = []
            for addr_info in interface["addr_info"]:
                if addr_info["family"] == "inet":
                    address = addr_info["local"]
                    if self.is_secondary_address(interface, address):
                        address += " (s)"
                    inet_addresses.append(address)
                elif addr_info["family"] == "inet6":
                    inet6_addresses.append(addr_info["local"])

            inet_str = "\n".join(inet_addresses) if inet_addresses else "unassigned"
            inet6_str = "\n".join(inet6_addresses) if inet6_addresses else "unassigned"

            state = interface.get("operstate", "N/A")
            protocol = interface.get("link_type", "N/A")

            table.append([interface_name, mac, inet_str, inet6_str, state, protocol])

        headers = ["Interface", "mac", "inet", "inet6", "method", "state", "protocol"]
        print(tabulate(table, headers, tablefmt="simple"))





