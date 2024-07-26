import json
from tabulate import tabulate
from typing import List, Dict, Any

# Original JSON data
json_data = '''
[{"ifindex":1,"ifname":"lo","flags":["LOOPBACK","UP","LOWER_UP"],"mtu":65536,"qdisc":"noqueue","operstate":"UNKNOWN","group":"default","txqlen":1000,"link_type":"loopback","address":"00:00:00:00:00:00","broadcast":"00:00:00:00:00:00","addr_info":[{"family":"inet","local":"127.0.0.1","prefixlen":8,"scope":"host","label":"lo","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet6","local":"::1","prefixlen":128,"scope":"host","protocol":"kernel_lo","valid_life_time":4294967295,"preferred_life_time":4294967295}]},{"ifindex":2,"ifname":"dummy0","flags":["BROADCAST","NOARP"],"mtu":1500,"qdisc":"noop","operstate":"DOWN","group":"default","txqlen":1000,"link_type":"ether","address":"be:dd:5c:0a:2a:21","broadcast":"ff:ff:ff:ff:ff:ff","addr_info":[]},{"ifindex":3,"ifname":"eth0","flags":["BROADCAST","MULTICAST","UP","LOWER_UP"],"mtu":1500,"qdisc":"mq","operstate":"UP","group":"default","txqlen":1000,"link_type":"ether","address":"20:7c:14:f4:4f:fd","broadcast":"ff:ff:ff:ff:ff:ff","addr_info":[{"family":"inet","local":"192.168.0.100","prefixlen":24,"scope":"global","label":"eth0","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet6","local":"fe80::227c:14ff:fef4:4ffd","prefixlen":64,"scope":"link","protocol":"kernel_ll","valid_life_time":4294967295,"preferred_life_time":4294967295}]},{"ifindex":4,"ifname":"eth1","flags":["BROADCAST","MULTICAST","UP","LOWER_UP"],"mtu":1500,"qdisc":"mq","operstate":"UP","group":"default","txqlen":1000,"link_type":"ether","address":"20:7c:14:f4:4f:fe","broadcast":"ff:ff:ff:ff:ff:ff","addr_info":[{"family":"inet","local":"192.168.1.1","prefixlen":24,"scope":"global","label":"eth1","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet6","local":"fe80::227c:14ff:fef4:4ffe","prefixlen":64,"scope":"link","protocol":"kernel_ll","valid_life_time":4294967295,"preferred_life_time":4294967295}]},{"ifindex":5,"ifname":"eth2","flags":["BROADCAST","MULTICAST"],"mtu":1500,"qdisc":"mq","master":"brlan0","operstate":"DOWN","group":"default","txqlen":1000,"link_type":"ether","address":"20:7c:14:f4:4f:ff","broadcast":"ff:ff:ff:ff:ff:ff","addr_info":[{"family":"inet","local":"172.16.100.1","prefixlen":24,"scope":"global","label":"eth2","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.101.1","prefixlen":24,"scope":"global","label":"eth2","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.102.1","prefixlen":24,"scope":"global","label":"eth2","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.103.1","prefixlen":24,"scope":"global","label":"eth2","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.104.1","prefixlen":24,"scope":"global","label":"eth2","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.105.1","prefixlen":24,"scope":"global","label":"eth2","valid_life_time":4294967295,"preferred_life_time":4294967295}]},{"ifindex":6,"ifname":"eth3","flags":["BROADCAST","MULTICAST","UP","LOWER_UP"],"mtu":1500,"qdisc":"mq","operstate":"UP","group":"default","txqlen":1000,"link_type":"ether","address":"20:7c:14:f4:50:00","broadcast":"ff:ff:ff:ff:ff:ff","addr_info":[{"family":"inet","local":"192.168.1.128","prefixlen":24,"broadcast":"192.168.1.255","scope":"global","label":"eth3","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.0.1","prefixlen":24,"scope":"global","label":"eth3","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.1.1","prefixlen":24,"scope":"global","label":"eth3:sec","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet","local":"172.16.2.1","prefixlen":24,"scope":"global","label":"eth3:sec","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet6","local":"fe80::227c:14ff:fef4:5000","prefixlen":64,"scope":"link","protocol":"kernel_ll","valid_life_time":4294967295,"preferred_life_time":4294967295}]},{"ifindex":7,"ifname":"eth4","flags":["BROADCAST","MULTICAST","UP","LOWER_UP"],"mtu":1500,"qdisc":"mq","operstate":"UP","group":"default","txqlen":1000,"link_type":"ether","address":"20:7c:14:f4:50:01","broadcast":"ff:ff:ff:ff:ff:ff","addr_info":[{"family":"inet","local":"192.168.100.1","prefixlen":24,"scope":"global","label":"eth4","valid_life_time":4294967295,"preferred_life_time":4294967295},{"family":"inet6","local":"fe80::227c:14ff:fef4:5001","prefixlen":64,"scope":"link","protocol":"kernel_ll","valid_life_time":4294967295,"preferred_life_time":4294967295}]},{"ifindex":8,"link":null,"ifname":"sit0","flags":["NOARP"],"mtu":1480,"qdisc":"noop","operstate":"DOWN","group":"default","txqlen":1000,"link_type":"sit","address":"0.0.0.0","broadcast":"0.0.0.0","addr_info":[]},{"ifindex":10,"ifname":"brlan0","flags":["BROADCAST","MULTICAST"],"mtu":1500,"qdisc":"noop","operstate":"DOWN","group":"default","txqlen":1000,"link_type":"ether","address":"20:7c:14:f4:4f:ff","broadcast":"ff:ff:ff:ff:ff:ff","addr_info":[]}]
'''

# Load JSON data
try:
    network_data: List[Dict[str, Any]] = json.loads(json_data)
except json.JSONDecodeError as e:
    print(f"Error loading JSON data: {e}")
    exit()

def bridge_group_interface_table(ip_route_addr_json: List[Dict[str, Any]])) -> List[Dict[str, str]]:
    """
    Extract and format bridge-related information from the raw network data.

    Args:
        data (List[Dict[str, Any]]): The raw network data in JSON format.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the groomed data
        with keys 'Bridge Name', 'Interface', and 'INET Address'.
    """
    bridge_interfaces: List[Dict[str, str]] = []

    for item in ip_route_addr_json:
        # Check if the item has a 'master' key
        if 'master' in item:
            bridge_name = item['master']
            # Collect INET addresses
            inet_addresses = [
                f"{info['local']}/{info['prefixlen']}"
                for info in item.get('addr_info', [])
                if info['family'] == 'inet'
            ]
            bridge_interfaces.append({
                'Bridge Name': bridge_name,
                'Interface': item['ifname'],
                'INET Address': '\n'.join(inet_addresses)
            })
                
    return bridge_interfaces

# Groom the data
groomed_data = groom_data(network_data)

# Print the data in tabulated format
print(tabulate(groomed_data, headers='keys', tablefmt='grid'))

# Print groomed data for inspection
print("\nGroomed Data:")
for entry in groomed_data:
    print(entry)
