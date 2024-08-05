def process_args(args):
    if 'option1' in args:
        # Handle option1
        print("Handling option1")
    elif 'option2' in args:
        # Handle option2
        print("Handling option2")
    elif args[:3] == ['switchport', 'access', 'vlan']:
        # Handle the switchport access vlan case
        vlan_id = args[3] if len(args) > 3 else None
        print(f"Handling switchport access vlan with VLAN ID {vlan_id}")
    else:
        # Handle other cases
        print("Handling other cases")

# Example usage
args = ['switchport', 'access', 'vlan', '1000']
process_args(args)
