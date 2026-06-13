import logging

from routershell.lib.cli.base.copy_start_run import CopyStartRun
from routershell.lib.common.router_shell_log_control import RouterShellLoggerSettings as RSLS
from routershell.lib.db.sqlite_db.router_shell_db import RouterShellDB
from routershell.lib.network_manager.common.run_commands import RunCommand
from routershell.lib.network_manager.network_operations.interface import Interface
from routershell.lib.system.system_call import SystemCall


class SystemStartUp(Interface):
    """
    Class for managing system startup procedures.

    Inherits from Interface.
    """
    def __init__(self):
        """
        Initializes the SystemStartUp class.
        """
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_START_UP)

        if not self.fetch_db_interface_names():
            self.update_interface_db_from_os()
            
        SystemCall().seed_hostname_db_from_os()
            
        self.set_os_rename_interface()
        
        self.log.debug('Loading........')
        CopyStartRun().read_start_config()
            
class SystemShutDown(RunCommand):    
    """
    Class for managing system shutdown procedures.

    Inherits from RunCommand.
    """
    def __init__(self):
        """
        Initializes the SystemShutDown class.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_START_UP)
            
class SystemReset(Interface):
    """
    Class for resetting system settings.

    Inherits from Interface.
    """
    def __init__(self):
        """
        Initializes the SystemReset class.
        """
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_RESET)
        
    def database(self):
        """
        Resets the system database.

        Reverts some settings in the OS when clearing the database.
        """
        # Flush interfaces
        Interface().flush_interfaces()
                
        # Revert Interfaces back to the original interface name
        Interface().set_os_rename_interface(reverse=True)

class SystemFactoryReset:
    def __init__(self):
        """
        Initializes the SystemFactoryReset class.
        """
        super().__init__()
        
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLS().SYSTEM_INIT)

        RouterShellDB().reset_database()
        
        #Build Initial DB Entries based on Interface found on system
        Interface().update_interface_db_from_os()
        
        #Take factory-startup-config and configure router    
        CopyStartRun().read_start_config('factory-startup.cfg')
