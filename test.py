
import logging
from lib.db.vlan_db import VlanDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/log/routershell.log')
    ]
)

if VlanDatabase().add_interface_to_vlan(1, 'enx0'):
    print(f'Did not add Interface to Vlan')

