from enum import Enum, auto

class DHCPStatus(Enum):
    """An enumeration of DHCP client statuses."""
    STOP = auto()
    START = auto()
    RESTART = auto()

class DHCPStackVersion(Enum):
    """An enumeration of DHCP stack versions."""
    DHCP_V4 = 'DHCPv4'
    DHCP_V6 = 'DHCPv6'
    DHCP_DUAL_STACK = 'DHCPv4v6'
    