import logging

from lib.network_manager.network_operations.route import Route

class RouteShow(Route):
    
    def __init__(self, arg=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.arg = arg        

    def route(self, args=None):
            self.get_route()