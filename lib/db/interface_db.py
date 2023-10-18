import logging


from lib.db.router_shell_db import RouterShellDatabaseConnector as RSDB
from lib.common.cmd2_global import  Cmd2GlobalSettings as CGS
from lib.common.cmd2_global import  RouterShellLoggingGlobalSettings as RSLGS

from lib.common.constants import STATUS_NOK, STATUS_OK


class InterfaceConfigDB:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().INTERFACE_DB)
        
        '''CMD2 DEBUG LOGGING'''
        cls.debug = CGS().DEBUG_INTERFACE_DB
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()  
            
    def exists_interface(cls, interface_name:str) -> bool:
        pass
    
    def add_interface(cls, interface_name: str, interface_type:str, shutdown_status:bool=True) -> bool:
        pass
    
    def del_interface(cls, interface_name:str) -> bool:
        pass
    
    def update_interface_shutdown_status(cls, interface_name:str, shutdown_status:bool) -> bool:
        pass
    
    


