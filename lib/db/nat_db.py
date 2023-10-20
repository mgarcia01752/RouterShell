import json

class NatDB:

    def create_global_nat_pool(cls, pool_name: str) -> bool:
        pass
    
    def delete_global_nat_pool(cls, pool_name: str) -> bool:
        pass

    def get_pool(cls, pool_name: str):
        pass

    def add_inside_interface(self, pool_name: str, interface_name: str) -> bool:
        pass
    
    def set_outside_interface(self, pool_name: str, interface_name: str) -> bool:
        pass
    
    def delete_inside_interface(self, pool_name: str, interface_name: str) -> bool:
        pass
                
    def get_outside_interface(cls, pool_name: str) -> str:
        pass
    
    def __str__(self) -> str:
        return f"Name: {self.name}, Inside Interfaces: {self.inside_interfaces}, Outside Interface: {self.outside_interface}"
