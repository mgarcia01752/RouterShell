import logging
import textwrap
from typing import Dict, Tuple

from lib.db.sqlite_db.router_shell_db import RouterShellDB as RSDB
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

from lib.common.constants import STATUS_NOK, STATUS_OK

class SystemDatabase:

    rsdb = RSDB()
    
    def __init__(cls):
        cls.log = logging.getLogger(cls.__class__.__name__)
        cls.log.setLevel(RSLGS().SYSTEM_DB)
        
        if not cls.rsdb:
            cls.log.debug(f"Connecting RouterShell Database")
            cls.rsdb = RSDB()
    
    def set_banner_motd(cls, motd_banner:str) -> bool:
        """
        Set the banner Message of the Day (Motd) in the RouterShell configuration.

        Args:
            cls: The RouterShellDB class.
            motd_banner (str): The new banner text.

        Returns:
            bool: STATUS_OK if the banner is successfully set, STATUS_NOK otherwise.
        """        
        return cls.rsdb.update_banner_motd(motd_banner).status
    
    def get_banner_motd(cls) -> Tuple[bool, str]:
        """
        Retrieve the banner Message of the Day (Motd) from the RouterShell configuration.

        Args:
            cls: The RouterShellDB class

        Returns:
            Tuple[bool, str]: A tuple containing the status (STATUS_OK | STATUS_NOK) of the operation and the formatted banner text with lines
        """
        result = cls.rsdb.select_banner_motd()

        return result.status, result.result.get('BannerMotd')



        
        