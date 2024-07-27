from enum import Enum, auto

class BridgeProtocol(Enum):
    """
    Enumeration for different bridge protocols used in network bridging.

    Attributes:
        IEEE_802_1D: IEEE 802.1D STP - The original Spanning Tree Protocol with relatively slow convergence times.
        IEEE_802_1W: IEEE 802.1W RSTP - Rapid Spanning Tree Protocol with faster convergence, currently not supported.
        IEEE_802_1S: IEEE 802.1S MSTP - Multiple Spanning Tree Protocol for efficient loop prevention in multi-VLAN environments, currently not supported.
    """
    
    IEEE_802_1D = auto()
    '''
    IEEE 802.1D STP: STP is the original Spanning Tree Protocol, and it was designed 
    to prevent loops in bridged networks. However, it has relatively slow convergence times. 
    When a network topology change occurs (e.g., a link failure or recovery), 
    STP can take several seconds or even longer to recompute the spanning tree 
    and re-converge the network. During this time, some network segments may be blocked, 
    leading to suboptimal network performance.
    '''
    
    IEEE_802_1W = auto()
    '''
    !!!!!!!!Currently not Supported!!!!!!!!

    IEEE 802.1W RSTP: Rapid Spanning Tree Protocol is designed to provide rapid convergence. 
    It improves upon the slow convergence of STP. RSTP is much faster at detecting network 
    topology changes and re-converging the network. In many cases, RSTP can converge within 
    a few seconds or less. This rapid convergence is achieved by introducing new port states 
    and mechanisms to minimize the time it takes to transition to a new topology.
    '''
    
    IEEE_802_1S = auto()
    '''
    !!!!!!!!Currently not Supported!!!!!!!!

    IEEE 802.1S is a network standard that defines the Multiple Spanning Tree Protocol (MSTP). 
    MSTP is an extension of the original Spanning Tree Protocol (STP) defined in IEEE 802.1D 
    and is designed to improve the efficiency of loop prevention in Ethernet networks, 
    especially in environments with multiple VLANs (Virtual LANs).
    '''

class STP_STATE(Enum):
    """
    Enumeration for the Spanning Tree Protocol (STP) states.

    Attributes:
        STP_DISABLE: STP is disabled.
        STP_ENABLE: STP is enabled.
    """
    
    STP_DISABLE = '0'
    '''
    STP_DISABLE: Disables Spanning Tree Protocol. In this state, no spanning tree computation 
    is performed, and network loops may occur if there are multiple active paths.
    '''
    
    STP_ENABLE = '1'
    '''
    STP_ENABLE: Enables Spanning Tree Protocol. In this state, STP will actively compute 
    and manage spanning trees to prevent network loops.
    '''
