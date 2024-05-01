#!/usr/bin/env python3

def parse_iptables_output(iptables_output):
    # Split the input by lines
    iptables_lines = iptables_output.split('\n')
    
    # Initialize a dictionary to store chains and their rules
    iptables_dict = {}

    # Parse each line
    current_chain = None
    for line in iptables_lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Check for a new chain
        if line.startswith('Chain'):
            current_chain = line.split()[1]
            iptables_dict[current_chain] = {'policy': None, 'rules': []}
        else:
            # Check for the policy line
            if 'policy' in line:
                iptables_dict[current_chain]['policy'] = line.strip()
            else:
                # Add rule to the current chain
                iptables_dict[current_chain]['rules'].append(line.strip())

    return iptables_dict


def print_readable_iptables(iptables_dict):
    # Print the formatted iptables configuration
    for chain, details in iptables_dict.items():
        print(f"Chain {chain} ({details['policy']})")
        for rule in details['rules']:
            print(rule)
        print('\n')


# Example usage with your iptables output
iptables_output = """
Chain PREROUTING (policy ACCEPT)
target  prot  opt  source     destination         
DNAT    all   --   anywhere  anywhere     to:172.16.1.1

Chain INPUT (policy ACCEPT)
target  prot  opt  source     destination         

Chain OUTPUT (policy ACCEPT)
target  prot  opt  source     destination         

Chain POSTROUTING (policy ACCEPT)
target     prot   opt  source     destination         
MASQUERADE  all   --   anywhere  anywhere 
"""

parsed_iptables = parse_iptables_output(iptables_output)
print_readable_iptables(parsed_iptables)

