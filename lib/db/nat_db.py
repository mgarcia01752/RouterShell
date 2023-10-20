import logging

from lib.common.constants import STATUS_NOK, STATUS_OK
from lib.db.sqlite_db.router_shell_db import RouterShellDatabaseConnector as RSDB, Result

from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS


class NatDB:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().NAT_DB)
        
        '''CMD2 DEBUG LOGGING'''
        cls.debug = CGS().DEBUG_NAT_DB
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()  

    def pool_name_exists(cls, pool_name: str) -> bool:


    
    def create_global_pool_name(cls, pool_name: str) -> bool:
        pass
    
    def delete_global_pool_name(cls, pool_name: str) -> bool:
        pass

    def get_global_pool_names(cls):
        '''return list of pool names'''
        pass

    def add_inside_interface(self, pool_name: str, interface_name: str) -> bool:
        pass

    def delete_inside_interface(self, pool_name: str, interface_name: str) -> bool:
        pass
    
    def add_outside_interface(self, pool_name: str, interface_name: str) -> bool:
        pass
                    
    def delete_outside_interface(cls, pool_name: str, interface_name: str) -> str:
        pass
    