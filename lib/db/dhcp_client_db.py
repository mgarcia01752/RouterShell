import logging
from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.network_manager.dhcp_client import DHCPVersion

class DHCPClientDatabase:

    rsdb = RSDB()
    log = logging.getLogger(__name__)

    def add_db_dhcp_client(cls, interface_name: str, dhcp_version: DHCPVersion) -> bool:
        return cls.rsdb.insert_interface_dhcp_client(interface_name, dhcp_version.value).status
    
    def update_db_dhcp_client(cls, interface_name: str, dhcp_version: DHCPVersion) -> bool:
        return cls.rsdb.update_interface_dhcp_client(interface_name, dhcp_version.value).status
    
    def remove_db_dhcp_client(cls, interface_name: str, dhcp_version: DHCPVersion) -> bool:
        return cls.rsdb.remove_interface_dhcp_client(interface_name, dhcp_version.value).status