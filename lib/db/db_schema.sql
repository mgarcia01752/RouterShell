DROP TABLE IF EXISTS InterfaceAlias;
CREATE TABLE IF NOT EXISTS InterfaceAlias (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT UNIQUE,
    IfName VARCHAR(100) UNIQUE,
    IfNameAlias VARCHAR(100) UNIQUE
);


DROP TABLE IF EXISTS Interfaces;
CREATE TABLE IF NOT EXISTS Interfaces (
    ID INTEGER PRIMARY KEY,
    InterfaceName VARCHAR(100) UNIQUE,
    InterfaceType VARCHAR(100),         -- Interface Type (ethernet, loopback, wireless wifi, wireless cell)
    ShutdownStatus BOOLEAN              -- True = interface is shutdown
);

DROP TABLE IF EXISTS InterfaceSubOptions;
CREATE TABLE IF NOT EXISTS InterfaceSubOptions (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    MacAddress VARCHAR(17),             -- MAC address format: xx:xx:xx:xx:xx:xx
    Duplex VARCHAR(4) DEFAULT 'auto',   -- Duplex [half | full | auto]
    Speed VARCHAR(5) DEFAULT 'auto',    -- Speed [10 | 100 | 1000 | 10000 | auto]
    ProxyArp BOOLEAN,
    DropGratuitousArp BOOLEAN,
    CONSTRAINT FK_InterfaceSubOptions_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS InterfaceStaticArp;
CREATE TABLE IF NOT EXISTS InterfaceStaticArp (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    IpAddress VARCHAR(45),              -- IPv4 | IPv6 Address/Mask Prefix (adjust length as needed)              
    MacAddress VARCHAR(17),             -- MAC address format: xx:xx:xx:xx:xx:xx
    Encapsulation VARCHAR(10),          -- arpa | TBD
    CONSTRAINT FK_InterfaceStaticArp_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS InterfaceIpAddress;
CREATE TABLE IF NOT EXISTS InterfaceIpAddress (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    IpAddress VARCHAR(45),              -- IPv4 | IPv6 Address/Mask Prefix (adjust length as needed)
    SecondaryIp BOOLEAN,                -- True = Secondary
    CONSTRAINT FK_InterfaceIpAddress_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS InterfaceBlackList;
CREATE TABLE IF NOT EXISTS InterfaceBlackList (
    ID INTEGER PRIMARY KEY,
    InterfaceName VARCHAR(50)           -- Interface to be excluded from Routershell configurations
);

DROP TABLE IF EXISTS BridgeGroups;
CREATE TABLE IF NOT EXISTS BridgeGroups (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT UNIQUE,
    BridgeGroups_FK INT DEFAULT -1,
    CONSTRAINT FK_BridgeGroups_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE,
    CONSTRAINT FK_Bridges_Interfaces FOREIGN KEY (BridgeGroups_FK) REFERENCES Bridges(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Bridges;
CREATE TABLE IF NOT EXISTS Bridges (
    ID INTEGER PRIMARY KEY,
    BridgeGroups_FK INT,
    BridgeName VARCHAR(50) UNIQUE,
    Protocol VARCHAR(15),                -- Bridge Protocol
    StpStatus BOOLEAN,                   -- STB STATUS ENABLE = 1 , DISABLE = 0
    ShutdownStatus BOOLEAN DEFAULT TRUE,
    CONSTRAINT FK_Bridges_BridgeGroups FOREIGN KEY (BridgeGroups_FK) REFERENCES BridgeGroups(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Vlans;
CREATE TABLE IF NOT EXISTS Vlans (
    ID INTEGER PRIMARY KEY,
    VlanID INT UNIQUE,
    VlanInterfaces_FK INT DEFAULT -1,
    VlanName VARCHAR(20) UNIQUE,
    VlanDescription VARCHAR(50),
    CONSTRAINT FK_Vlans_VlanInterfaces FOREIGN KEY (VlanInterfaces_FK) REFERENCES VlanInterfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS VlanInterfaces;
CREATE TABLE IF NOT EXISTS VlanInterfaces (
    ID INTEGER PRIMARY KEY,
    VlanName VARCHAR(20),
    Interface_FK INT DEFAULT -1,
    Bridge_FK INT DEFAULT -1,
    CONSTRAINT FK_VLANs_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE,
    CONSTRAINT FK_VLANs_Bridges FOREIGN KEY (Bridge_FK) REFERENCES Bridges(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Nats;
CREATE TABLE IF NOT EXISTS Nats (
    ID INTEGER PRIMARY KEY,
    NatPoolName VARCHAR(50) UNIQUE
);

DROP TABLE IF EXISTS NatDirections;
CREATE TABLE IF NOT EXISTS NatDirections (
    ID INTEGER PRIMARY KEY,
    NAT_FK INT ,
    Interface_FK INT UNIQUE,                -- Only 1 direction per interface                                             
    Direction VARCHAR(7),                   -- Direction inside | outside -> NATDirection()
    CONSTRAINT FK_NatDirections_Nats FOREIGN KEY (NAT_FK) REFERENCES Nats(ID) ON DELETE CASCADE,
    CONSTRAINT FK_NatDirections_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPClient;
CREATE TABLE IF NOT EXISTS DHCPClient (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    DHCPVersion VARCHAR(6),                 -- DHCPVersion:dhcpv4 | dhcpv6
    CONSTRAINT FK_DHCPClient_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPServer;
CREATE TABLE IF NOT EXISTS DHCPServer (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT,
    DhcpPoolname VARCHAR(50) UNIQUE,
    CONSTRAINT FK_DHCP_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPSubnet;
CREATE TABLE IF NOT EXISTS DHCPSubnet (
    ID INTEGER PRIMARY KEY,
    DHCPServer_FK INT ,              
    InetSubnet VARCHAR(45) UNIQUE,
    CONSTRAINT FK_Subnet_DHCP FOREIGN KEY (DHCPServer_FK) REFERENCES DHCPServer(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPSubnetPools;
CREATE TABLE IF NOT EXISTS DHCPSubnetPools (
    ID INTEGER PRIMARY KEY,
    DHCPSubnet_FK INT,
    InetAddressStart VARCHAR(45),
    InetAddressEnd VARCHAR(45),
    InetSubnet VARCHAR(45),
    CONSTRAINT FK_DHCPSubnetPools_DHCPSubnet FOREIGN KEY (DHCPSubnet_FK) REFERENCES DHCPSubnet(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPSubnetReservations;
CREATE TABLE IF NOT EXISTS DHCPSubnetReservations (
    ID INTEGER PRIMARY KEY,
    DHCPSubnet_FK INT,
    MacAddress VARCHAR(12),
    InetAddress VARCHAR(45),
    CONSTRAINT FK_DHCPSubnetReservations_DHCPSubnet FOREIGN KEY (DHCPSubnet_FK) REFERENCES DHCPSubnet(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPOptions;
CREATE TABLE IF NOT EXISTS DHCPOptions (
    ID INTEGER PRIMARY KEY,
    DhcpOption VARCHAR(20),
    DhcpValue VARCHAR(50),
    DHCPSubnetPools_FK INT,
    DHCPSubnetReservations_FK INT,
    CONSTRAINT FK_DHCPOptions_DHCPSubnetPools FOREIGN KEY (DHCPSubnetPools_FK) REFERENCES DHCPSubnetPools(ID) ON DELETE CASCADE,
    CONSTRAINT FK_DHCPOptions_DHCPSubnetReservations FOREIGN KEY (DHCPSubnetReservations_FK) REFERENCES DHCPSubnetReservations(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS FirewallPolicies;
CREATE TABLE IF NOT EXISTS FireWallPolicies (
    ID INTEGER PRIMARY KEY,
    Description VARCHAR(255)                -- Description of the policy
);

DROP TABLE IF EXISTS FWDirectionInterfaces;
CREATE TABLE IF NOT EXISTS FWDirectionInterfaces (
    ID INTEGER PRIMARY KEY,
    FirewallPolicy_FK INT,                  -- Foreign key to link with FirewallPolicies
    Interface_FK INT,
    Direction VARCHAR(8),                   -- Direction (inbound or outbound)
    CONSTRAINT FK_FirewallRules_FWPolicies FOREIGN KEY (FirewallPolicy_FK) REFERENCES FirewallPolicies(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS FirewallRules;
CREATE TABLE IF NOT EXISTS FirewallRules (
    ID INTEGER PRIMARY KEY,
    Description VARCHAR(255),               -- Description of the rule
    FirewallPolicy_FK INT,                  -- Foreign key to link with FirewallPolicies
    SourceIP VARCHAR(45),                   -- Source IP or network
    SourcePort INT,                         -- Source port (optional)
    DestinationIP VARCHAR(45),              -- Destination IP or network
    DestinationPort INT,                    -- Destination port (optional)
    Protocol VARCHAR(10),                   -- Protocol (e.g., TCP, UDP, ICMP, any)
    Action VARCHAR(10),                     -- Action (allow, deny)
    CONSTRAINT FK_FirewallRules_FWPolicies FOREIGN KEY (FirewallPolicy_FK) REFERENCES FirewallPolicies(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS RenameInterface;
CREATE TABLE IF NOT EXISTS RenameInterface (
    ID INTEGER PRIMARY KEY,
    InitialInterface VARCHAR(50) UNIQUE,
    AliasInterface VARCHAR(50) UNIQUE
);

DROP TABLE IF EXISTS WirelessWifiPolicy;
CREATE TABLE IF NOT EXISTS WirelessWifiPolicy (
    ID INTEGER PRIMARY KEY,
    Ssid VARCHAR(32),
    WpaPassPhrase VARCHAR(63),
    WpaVersion INTEGER,             -- WPA = 1, WPA2 = 2, WPA3 = 3
    

);