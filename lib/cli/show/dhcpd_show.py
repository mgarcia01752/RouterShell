import logging


class DHCPServerShow():
    """Command set for showing DHCPServer-Show-Command"""

    def __init__(self, args=None):
        super().__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.args = args