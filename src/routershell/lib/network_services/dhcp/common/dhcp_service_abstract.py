from abc import ABC, abstractmethod

from routershell.lib.common.types import StatusResult


class DHCPServerAbstract(ABC):
    
    @abstractmethod
    def status(self) -> StatusResult:
        pass
    
    @abstractmethod
    def restart(self) -> StatusResult:
        pass
    
    @abstractmethod
    def start(self) -> StatusResult:
        pass

    @abstractmethod
    def stop(self) -> StatusResult:
        pass
    