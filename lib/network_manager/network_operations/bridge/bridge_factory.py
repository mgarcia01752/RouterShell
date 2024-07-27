
import logging
from lib.common.constants import STATUS_OK
from lib.network_manager.network_operations.bridge.bridge import STP_STATE, Bridge, BridgeProtocol
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS


class BridgeConfigFactory:
    def __init__(self, bridge_name:str):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG_FACTORY)        
        self.bridge_name = bridge_name
        
class BridgeConfigCommands:
    def __init__(self, bridge_name:str):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(RSLGS().BRIDGE_CONFIG_COMMANDS)
        self.bridge_name = bridge_name
    
    def does_bridge_exist(self) -> bool:
        if Bridge().does_bridge_exist_os(self.bridge_name):
            self.log.debug(f'does_bridge_exist_os() -> {self.bridge_name} does not exisit on OS')
            return False
            
        if Bridge().does_bridge_exists_db(self.bridge_name):
            self.log.debug(f'does_bridge_exist_os() -> {self.bridge_name} does not exisit on DB')
            return False
        
        return True
    
    def create_bridge_interface(self) -> bool:
        
        if not self.does_bridge_exist():    
            # Add Bridge to OS
            
            # Add Bridge to DB
            Bridge().add_bridge_db(self.bridge_name)
            
            return STATUS_OK
        
        return STATUS_OK
    
    def set_inet(self, inet:str) -> bool:
        if self.does_bridge_exist():
            # check for inet address
            # set inet address OS
            # set inet address DB
            return STATUS_OK
        return STATUS_OK
    
    def set_shutdown_status(self, negate:bool) -> bool:
        if self.does_bridge_exist():
            # check for shutdown status
            # set shutdown status OS
            # set shutdown status DB
            return STATUS_OK    
        return STATUS_OK
    
    def set_stp(self, stp:STP_STATE) -> bool:
        if self.does_bridge_exist():
            # check for stp status
            # set STP OS
            # set STP DB
            return STATUS_OK
        return STATUS_OK
    
    def set_bridge_protocol(self, protocol:BridgeProtocol) -> bool:
        if self.does_bridge_exist():
            # check for bridge protocol
            # set bridge protocol OS
            # set bridge protocol DB
            return STATUS_OK
        return STATUS_OK
    
            
    
    
    
    
    
    
    
        