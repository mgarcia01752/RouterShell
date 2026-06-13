from abc import ABC, abstractmethod

class DHCPServerAbstract(ABC):
    
    @abstractmethod
    def status(self) -> bool:
        pass
    
    @abstractmethod
    def restart(self) -> bool:
        pass
    
    @abstractmethod
    def start(self) -> bool:
        pass

    @abstractmethod
    def stop(self) -> bool:
        pass
    