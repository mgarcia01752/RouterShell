from enum import Enum, auto

class BridgeProtocol(Enum):
    
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
    It improves upon the slow convergence of STP.  RSTP is much faster at detecting network 
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
    STP_DISABLE='0'
    STP_ENABLE='1'