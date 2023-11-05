import logging
from typing import List

from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB, Result
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS
from lib.common.constants import STATUS_NOK, STATUS_OK

class WifiDB:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().WIRELESS_WIFI_DB)
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()
    
    def wifi_interface_exist_db(self, wifi_interface_name:str) -> bool:
        return True
    