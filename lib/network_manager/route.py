import ipaddress
import logging

from tabulate import tabulate
from lib.network_manager.network_manager import NetworkManager
from lib.sysctl import SysCtl
from lib.constants import STATUS_NOK, STATUS_OK

class Route(NetworkManager):

    def __init__(self, arg=None):
        """
        Initialize the Route class.

        Args:
            arg: An optional argument (default is None).

        Returns:
            None
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg

    def set_default_gateway(self, gateway_ip) -> bool:
        """
        Configure the default gateway using the 'ip' command.

        Args:
            gateway_ip (str): The IP address of the default gateway.

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if self.run(["ip", "route", "add", "default", "via", gateway_ip]).exit_code:
            self.log.error(f"Unable to add static default route -> {gateway_ip}")
            return STATUS_NOK
        
        return STATUS_OK

    def set_classless_routing(self, enable=True) -> bool:
        """
        Enable or disable classless routing using the 'sysctl' command.

        Args:
            negate (bool): True to disable classless routing, False to enable it (default).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if enable:
            enable_stat = 1
        else:
            enable_stat = 0
        
        if SysCtl().write_sysctl('net.ipv4.ip_forward', enable):
            self.log.error(f"Unable to set classless routing -> net.ipv4.ip_forward -> {enable}")
            return STATUS_NOK
        
        return STATUS_OK

    def set_src_net_route(self, src_net, dest_net:str="0.0.0.0" , negate=False) -> bool:
        """
        Configure or remove the default network using the 'ip' command.

        Args:
            network_ip (str): The IP address of the default network.
            negate (bool): True to remove the route, False to add it (default).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if negate:
            add_del = 'del'
        else:
            add_del = 'add'
        
        if self.run(["ip", "route", add_del, src_net, "via", dest_net]).exit_code:
            self.log.error(f"Unable to {'remove' if negate else 'add'} static default route -> {src_net}")
            return STATUS_NOK
        
        return STATUS_OK

    def add_route(self, destination_ip_mask, next_hop, metric: int = 100, negate=False) -> bool:
        """
        Add or delete a route to/from the routing table using the 'ip' command.

        Args:
            destination_ip_mask (str): The destination IP address and mask of the route.
            next_hop (str): The next hop IP address or interface name.
            metric (int): 0 to 4294967295, 32-bit unsigned integer.
            negate (bool): True to delete the route, False to add it (default).

        Returns:
            bool: STATUS_OK if the operation was successful, STATUS_NOK otherwise.
        """
        if negate:
            add_del = 'del'
        else:
            add_del = 'add'

        route_command = ["ip", "route", add_del, destination_ip_mask]

        # Check if next_hop is an IP address
        try:
            ipaddress.IPv4Address(next_hop)  # Validate if it's a valid IP address
            route_command.extend(["via", next_hop])
        except ValueError:
            # If next_hop is not a valid IP address, assume it's an interface
            route_command.extend(["dev", next_hop])

        route_command.extend(["metric", str(metric)])

        self.log.debug(f"Route CMD: {route_command}")

        if self.run(route_command).exit_code:
            self.log.error(f"Unable to {'delete' if negate else 'add'} static route -> {route_command}")
            return STATUS_NOK

        return STATUS_OK

    def _get_route(self, destination_ip):
        """
        Get the route (interface) for a given destination IP address using the 'ip' command.

        Args:
            destination_ip (str): The destination IP address.

        Returns:
            str: The interface for the route, or None if no matching route is found.
        """
        try:
            route_info = subprocess.check_output(["ip", "route", "get", destination_ip], stderr=subprocess.DEVNULL, universal_newlines=True)
            lines = route_info.splitlines()
            for line in lines:
                if "dev" in line:
                    parts = line.split()
                    if "via" not in parts:
                        return parts[2]
        except subprocess.CalledProcessError:
            pass
        return None

    def get_route(self, arg=None):
        try:
            # Run the 'ip route' command to retrieve IPv4 routes
            route_info = self.run(["ip", "route", "show"])

            # Check if the command ran successfully
            if route_info.exit_code != 0:
                raise Exception(f"Error running 'ip route show'. Exit code: {route_info.exit_code}")

            # Parse the 'ip route' output to extract relevant IPv4 routes
            routes = route_info.stdout.splitlines()

            # Create a list of dictionaries containing route information
            route_data = []

            for route in routes:
                self.log.debug(f"Line: {route}")
                parts = route.split()
                self.log.debug(f"Parts: {parts}")
                if len(parts) >= 5:
                    destination = parts[0]
                    via = parts[2]
                    dev = parts[4]
                    route_data.append([destination, via, dev])  # Use a list instead of a dictionary

            if route_data:
                headers = ["Destination", "Via", "Device"]
                route_table = tabulate(route_data, headers, tablefmt="simple")
                print(route_table)
            else:
                print("No IPv4 routes found.")

            return route_data

        except Exception as e:
            self.log.error(f"An error occurred: {str(e)}")
            return []