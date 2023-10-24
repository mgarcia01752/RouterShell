DROP TABLE IF EXISTS Interfaces;
CREATE TABLE IF NOT EXISTS Interfaces (
    ID INTEGER PRIMARY KEY,
    IfName VARCHAR(100) UNIQUE,
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
    CONSTRAINT FK_InterfaceSubOptions_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

DROP TABLE IF EXISTS InterfaceSubOptions;
CREATE TABLE IF NOT EXISTS InterfaceSubOptions (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    MacAddress VARCHAR(17),             -- MAC address format: xx:xx:xx:xx:xx:xx
    Duplex VARCHAR(4),                  -- Duplex [half | full | auto]
    Speed VARCHAR(5),                   -- Speed [10 | 100 | 1000 | 10000 | auto]
    ProxyArp BOOLEAN,
    DropGratuitousArp BOOLEAN,
    CONSTRAINT FK_InterfaceSubOptions_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

DROP TABLE IF EXISTS InterfaceStaticArp;
CREATE TABLE IF NOT EXISTS InterfaceStaticArp (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    IpAddress VARCHAR(45),              -- IPv4 | IPv6 Address/Mask Prefix (adjust length as needed)              
    MacAddress VARCHAR(17),             -- MAC address format: xx:xx:xx:xx:xx:xx
    Encapsulation VARCHAR(10),          -- arpa | TBD
    CONSTRAINT FK_InterfaceStaticArp_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

DROP TABLE IF EXISTS InterfaceIpAddress;
CREATE TABLE IF NOT EXISTS InterfaceIpAddress (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    IpAddress VARCHAR(45),              -- IPv4 | IPv6 Address/Mask Prefix (adjust length as needed)
    SecondaryIp BOOLEAN,                -- True = Secondary
    CONSTRAINT FK_InterfaceIpAddress_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

DROP TABLE IF EXISTS BridgeGroups;
CREATE TABLE IF NOT EXISTS BridgeGroups (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT UNIQUE,
    BridgeGroups_FK INT DEFAULT -1,
    CONSTRAINT FK_BridgeGroups_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID),
    CONSTRAINT FK_Bridges_Interfaces FOREIGN KEY (BridgeGroups_FK) REFERENCES Bridges(ID)
);

DROP TABLE IF EXISTS Bridges;
CREATE TABLE IF NOT EXISTS Bridges (
    ID INTEGER PRIMARY KEY,
    BridgeGroups_FK INT DEFAULT -1,
    BridgeName VARCHAR(50),
    Protocol VARCHAR(15),                -- Bridge Protocol
    StpStatus BOOLEAN,                   -- STB STATUS ENABLE = 1 , DISABLE = 0
    ShutdownStatus BOOLEAN DEFAULT TRUE, -- TRUE should be in uppercase
    CONSTRAINT FK_Bridges_BridgeGroups FOREIGN KEY (BridgeGroups_FK) REFERENCES BridgeGroups(ID)
);

DROP TABLE IF EXISTS Vlans;
CREATE TABLE IF NOT EXISTS Vlans (
    ID INTEGER PRIMARY KEY,
    VlanID INT UNIQUE,
    VlanInterfaces_FK INT DEFAULT -1,
    VlanName VARCHAR(20) UNIQUE,
    VlanDescription VARCHAR(50),
    CONSTRAINT FK_Vlans_VlanInterfaces FOREIGN KEY (VlanInterfaces_FK) REFERENCES VlanInterfaces(ID)
);

DROP TABLE IF EXISTS VlanInterfaces;
CREATE TABLE IF NOT EXISTS VlanInterfaces (
    ID INTEGER PRIMARY KEY,
    VlanName VARCHAR(20),
    Interface_FK INT DEFAULT -1,
    Bridge_FK INT DEFAULT -1,
    CONSTRAINT FK_VLANs_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID),
    CONSTRAINT FK_VLANs_Bridges FOREIGN KEY (Bridge_FK) REFERENCES Bridges(ID)
);

DROP TABLE IF EXISTS Nats;
CREATE TABLE IF NOT EXISTS Nats (
    ID INTEGER PRIMARY KEY,
    NatPoolName VARCHAR(50) UNIQUE
);

DROP TABLE IF EXISTS NatDirections;
CREATE TABLE IF NOT EXISTS NatDirections (
    ID INTEGER PRIMARY KEY,
    NAT_FK INT DEFAULT -1,
    Interface_FK INT UNIQUE,                -- Only 1 direction per interface                                             
    Direction VARCHAR(7),                   -- Direction inside | outside -> NATDirection()
    CONSTRAINT FK_NatDirections_Nats FOREIGN KEY (NAT_FK) REFERENCES Nats(ID),
    CONSTRAINT FK_NatDirections_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

DROP TABLE IF EXISTS DHCP;
CREATE TABLE IF NOT EXISTS DHCP (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT DEFAULT -1,
    DhcpPoolname VARCHAR(50) UNIQUE,
    CONSTRAINT FK_DHCP_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

DROP TABLE IF EXISTS Subnet;
CREATE TABLE IF NOT EXISTS Subnet (
    ID INTEGER PRIMARY KEY,
    DHCP_FK INT DEFAULT -1,
    IpSubnet VARCHAR(45),
    CONSTRAINT FK_Subnet_DHCP FOREIGN KEY (DHCP_FK) REFERENCES DHCP(ID)
);

DROP TABLE IF EXISTS Pools;
CREATE TABLE IF NOT EXISTS Pools (
    ID INTEGER PRIMARY KEY,
    Subnet_FK INT DEFAULT -1,
    IpAddressStart VARCHAR(45),
    IpAddressEnd VARCHAR(45),
    IpSubnet VARCHAR(45),
    CONSTRAINT FK_Pools_Subnet FOREIGN KEY (Subnet_FK) REFERENCES Subnet(ID)
);

DROP TABLE IF EXISTS Reservations;
CREATE TABLE IF NOT EXISTS Reservations (
    ID INTEGER PRIMARY KEY,
    Subnet_FK INT DEFAULT -1,
    MacAddress VARCHAR(12),
    IPAddress VARCHAR(45),
    CONSTRAINT FK_Reservations_Subnet FOREIGN KEY (Subnet_FK) REFERENCES Subnet(ID)
);

DROP TABLE IF EXISTS Options;
CREATE TABLE IF NOT EXISTS Options (
    ID INTEGER PRIMARY KEY,
    DhcpOptions VARCHAR(20),
    DhcpValue VARCHAR(50),
    Pools_FK INT DEFAULT -1,
    DHCP_FK INT DEFAULT -1,
    Reservations_FK INT,
    CONSTRAINT FK_Options_Pools FOREIGN KEY (Pools_FK) REFERENCES Pools(ID),
    CONSTRAINT FK_Options_DHCP FOREIGN KEY (DHCP_FK) REFERENCES DHCP(ID),
    CONSTRAINT FK_Options_Reservations FOREIGN KEY (Reservations_FK) REFERENCES Reservations(ID)
);

DROP TABLE IF EXISTS FireWallPolicies;
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
    CONSTRAINT FK_FirewallRules_FWPolicies FOREIGN KEY (FireWallPolicy_FK) REFERENCES FireWallPolicies(ID)
);

DROP TABLE IF EXISTS FirewallRules;
CREATE TABLE IF NOT EXISTS FirewallRules (
    ID INTEGER PRIMARY KEY,
    Description VARCHAR(255),               -- Description of the rule
    FireWallPolicy_FK INT,                  -- Foreign key to link with FirewallPolicies
    SourceIP VARCHAR(45),                   -- Source IP or network
    SourcePort INT,                         -- Source port (optional)
    DestinationIP VARCHAR(45),              -- Destination IP or network
    DestinationPort INT,                    -- Destination port (optional)
    Protocol VARCHAR(10),                   -- Protocol (e.g., TCP, UDP, ICMP, any)
    Action VARCHAR(10),                     -- Action (allow, deny)
    CONSTRAINT FK_FirewallRules_FWPolicies FOREIGN KEY (FireWallPolicy_FK) REFERENCES FireWallPolicies(ID)
);
