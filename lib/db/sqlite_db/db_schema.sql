DROP TABLE IF EXISTS SystemConfiguration;
CREATE TABLE IF NOT EXISTS SystemConfiguration (
    ID INTEGER PRIMARY KEY NOT NULL,
    BannerMotd TEXT DEFAULT '',
    Hostname VARCHAR(255) DEFAULT '',
    TelnetServer_FK INT,
    SshServer_FK INT
);
INSERT INTO SystemConfiguration DEFAULT VALUES;

DROP TABLE IF EXISTS TelnetServer;
CREATE TABLE IF NOT EXISTS TelnetServer (
    ID INTEGER PRIMARY KEY NOT NULL,
    Enable BOOLEAN DEFAULT FALSE,
    Port INTEGER DEFAULT 23,
    CONSTRAINT FK_TelnetServer_SystemConfiguration FOREIGN KEY (ID) REFERENCES SystemConfiguration(TelnetServer_FK) ON DELETE CASCADE
);
INSERT INTO TelnetServer DEFAULT VALUES;

DROP TABLE IF EXISTS SshServer;
CREATE TABLE IF NOT EXISTS SshServer (
    ID INTEGER PRIMARY KEY NOT NULL,
    Enable BOOLEAN DEFAULT FALSE,
    Port INTEGER DEFAULT 22,
    CONSTRAINT FK_SshServer_SystemConfiguration FOREIGN KEY (ID) REFERENCES SystemConfiguration(SshServer_FK) ON DELETE CASCADE
);
INSERT INTO SshServer DEFAULT VALUES;

DROP TABLE IF EXISTS InterfaceAlias;
CREATE TABLE IF NOT EXISTS InterfaceAlias (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT UNIQUE,
    IfName VARCHAR(100) UNIQUE,
    IfNameAlias VARCHAR(100) UNIQUE
);

DROP TABLE IF EXISTS Interfaces;
CREATE TABLE IF NOT EXISTS Interfaces (
    ID INTEGER PRIMARY KEY NOT NULL,
    InterfaceName VARCHAR(100) UNIQUE,
    InterfaceType VARCHAR(100),                         -- Interface Type (ethernet, loopback, wireless wifi, wireless cell)
    ShutdownStatus BOOLEAN DEFAULT TRUE,                -- True = interface is shutdown
    Description VARCHAR(100)
);

DROP TABLE IF EXISTS RenameInterface;
CREATE TABLE IF NOT EXISTS RenameInterface (
    ID INTEGER PRIMARY KEY NOT NULL,
    BusInfo VARCHAR(30) UNIQUE,
    InitialInterface VARCHAR(50) UNIQUE,
    AliasInterface VARCHAR(50) UNIQUE, 
    CONSTRAINT FK_RenameInterface_Interfaces FOREIGN KEY (AliasInterface) REFERENCES Interfaces(InterfaceName) ON DELETE CASCADE
);

DROP TABLE IF EXISTS InterfaceSubOptions;
CREATE TABLE IF NOT EXISTS InterfaceSubOptions (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT DEFAULT -1,
    MacAddress VARCHAR(17),                             -- MAC address format: xx:xx:xx:xx:xx:xx
    Duplex VARCHAR(4) DEFAULT 'auto',                   -- Duplex [half | full | auto]
    Speed VARCHAR(5) DEFAULT 'auto',                    -- Speed [10 | 100 | 1000 | 10000 | auto]
    ProxyArp BOOLEAN DEFAULT TRUE,
    DropGratuitousArp BOOLEAN DEFAULT TRUE,
    CONSTRAINT FK_InterfaceSubOptions_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS InterfaceStaticArp;
CREATE TABLE IF NOT EXISTS InterfaceStaticArp (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT DEFAULT -1,
    IpAddress VARCHAR(45),                              -- IPv4 | IPv6 Address/Mask Prefix (adjust length as needed)              
    MacAddress VARCHAR(17),                             -- MAC address format: xx:xx:xx:xx:xx:xx
    Encapsulation VARCHAR(10) DEFAULT 'arpa',           -- arpa | TBD
    CONSTRAINT FK_InterfaceStaticArp_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS InterfaceIpAddress;
CREATE TABLE IF NOT EXISTS InterfaceIpAddress (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT DEFAULT -1,
    IpAddress VARCHAR(45),              -- IPv4 | IPv6 Address/Mask Prefix (adjust length as needed)
    SecondaryIp BOOLEAN DEFAULT FALSE,  -- True = Secondary
    CONSTRAINT FK_InterfaceIpAddress_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS InterfaceBlackList;
CREATE TABLE IF NOT EXISTS InterfaceBlackList (
    ID INTEGER PRIMARY KEY NOT NULL,
    InterfaceName VARCHAR(50)           -- Interface to be excluded from Routershell configurations
);

DROP TABLE IF EXISTS BridgeGroups;
CREATE TABLE IF NOT EXISTS BridgeGroups (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT UNIQUE,
    BridgeGroups_FK INT DEFAULT -1,
    CONSTRAINT FK_BridgeGroups_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE,
    CONSTRAINT FK_Bridges_Interfaces FOREIGN KEY (BridgeGroups_FK) REFERENCES Bridges(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Bridges;
CREATE TABLE IF NOT EXISTS Bridges (
    ID INTEGER PRIMARY KEY NOT NULL,
    BridgeGroups_FK INT,
    BridgeName VARCHAR(50) UNIQUE,
    Protocol VARCHAR(15),                -- Bridge Protocol
    StpStatus BOOLEAN,                   -- STB STATUS ENABLE = 1 , DISABLE = 0
    ShutdownStatus BOOLEAN DEFAULT TRUE,
    CONSTRAINT FK_Bridges_BridgeGroups FOREIGN KEY (BridgeGroups_FK) REFERENCES BridgeGroups(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Vlans;
CREATE TABLE IF NOT EXISTS Vlans (
    ID INTEGER PRIMARY KEY NOT NULL,
    VlanID INT UNIQUE,
    VlanInterfaces_FK INT DEFAULT -1,
    VlanName VARCHAR(20) UNIQUE,
    VlanDescription VARCHAR(50),
    CONSTRAINT FK_Vlans_VlanInterfaces FOREIGN KEY (VlanInterfaces_FK) REFERENCES VlanInterfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS VlanInterfaces;
CREATE TABLE IF NOT EXISTS VlanInterfaces (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT DEFAULT 0,
    Bridge_FK INT DEFAULT 0,
    CONSTRAINT FK_VLANs_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE,
    CONSTRAINT FK_VLANs_Bridges FOREIGN KEY (Bridge_FK) REFERENCES Bridges(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS Nats;
CREATE TABLE IF NOT EXISTS Nats (
    ID INTEGER PRIMARY KEY NOT NULL,
    NatPoolName VARCHAR(50) UNIQUE
);

DROP TABLE IF EXISTS NatDirections;
CREATE TABLE IF NOT EXISTS NatDirections (
    ID INTEGER PRIMARY KEY NOT NULL,
    NAT_FK INT ,
    Interface_FK INT UNIQUE,                -- Only 1 direction per interface                                             
    Direction VARCHAR(7),                   -- Direction inside | outside -> NATDirection()
    CONSTRAINT FK_NatDirections_Nats FOREIGN KEY (NAT_FK) REFERENCES Nats(ID) ON DELETE CASCADE,
    CONSTRAINT FK_NatDirections_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPClient;
CREATE TABLE IF NOT EXISTS DHCPClient (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT DEFAULT -1,
    DHCPVersion VARCHAR(6),                 -- DHCPVersion:dhcpv4 | dhcpv6
    CONSTRAINT FK_DHCPClient_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPServer;
CREATE TABLE IF NOT EXISTS DHCPServer (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INT,
    DhcpPoolname VARCHAR(50) UNIQUE,
    CONSTRAINT FK_DHCP_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPSubnet;
CREATE TABLE IF NOT EXISTS DHCPSubnet (
    ID INTEGER PRIMARY KEY NOT NULL,
    DHCPServer_FK INT ,              
    InetSubnet VARCHAR(45) UNIQUE,
    CONSTRAINT FK_Subnet_DHCP FOREIGN KEY (DHCPServer_FK) REFERENCES DHCPServer(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPVersionServerOptions;
CREATE TABLE IF NOT EXISTS DHCPVersionServerOptions (
    ID INTEGER PRIMARY KEY NOT NULL,
    DHCPSubnet_FK INT UNIQUE,              
    DHCPv4ServerOption_FK INT,
    DHCPv6ServerOption_FK INT,    
    CONSTRAINT FK_DHCPVersionServerOptions_DHCPSubnet FOREIGN KEY (DHCPSubnet_FK) REFERENCES DHCPSubnet(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPv4ServerOption;
CREATE TABLE IF NOT EXISTS DHCPv4ServerOption (
    ID INTEGER PRIMARY KEY NOT NULL,
    DHCPVersionServerOptions_FK INT,
    CONSTRAINT FK_DHCPv4ServerOption_DHCPVersionServerOptions FOREIGN KEY (DHCPVersionServerOptions_FK) REFERENCES DHCPVersionServerOptions(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPv6ServerOption;
CREATE TABLE IF NOT EXISTS DHCPv6ServerOption (
    ID INTEGER PRIMARY KEY NOT NULL,
    DHCPVersionServerOptions_FK INT,
    Constructor TEXT,               -- (Interface Name) Apply IPv6 Range to an interface
    Mode TEXT DEFAULT 'slaac',      -- ra-only, slaac, ra-names, ra-stateless, ra-advrouter, off-link    
    CONSTRAINT FK_DHCPv6ServerOption_DHCPVersionServerOptions FOREIGN KEY (DHCPVersionServerOptions_FK) REFERENCES DHCPVersionServerOptions(ID) ON DELETE CASCADE
);


DROP TRIGGER IF EXISTS insert_dhcp_option_ipv6;
CREATE TRIGGER  IF NOT EXISTS insert_dhcp_option_ipv6
    AFTER INSERT ON DHCPSubnet
    WHEN NEW.InetSubnet LIKE '%:%'
BEGIN

    INSERT INTO DHCPVersionServerOptions (DHCPSubnet_FK) VALUES (NEW.ID);
    INSERT INTO DHCPv6ServerOption (DHCPVersionServerOptions_FK) VALUES ((SELECT ID FROM DHCPVersionServerOptions ORDER BY ID DESC LIMIT 1));
    UPDATE DHCPv6ServerOption
        SET DHCPVersionServerOptions_FK = (SELECT ID FROM DHCPVersionServerOptions ORDER BY ID DESC LIMIT 1)
        WHERE ID = (SELECT ID FROM DHCPv6ServerOption ORDER BY ID DESC LIMIT 1);

    UPDATE DHCPVersionServerOptions 
        SET DHCPv6ServerOption_FK = (SELECT ID FROM DHCPv6ServerOption ORDER BY ID DESC LIMIT 1)
        WHERE ID = (SELECT ID FROM DHCPVersionServerOptions ORDER BY ID DESC LIMIT 1);
END;

DROP TRIGGER IF EXISTS insert_dhcp_option_ipv4;
CREATE TRIGGER IF NOT EXISTS insert_dhcp_option_ipv4
    AFTER INSERT ON DHCPSubnet
    WHEN NEW.InetSubnet LIKE '%.%'
BEGIN
    INSERT INTO DHCPVersionServerOptions (DHCPSubnet_FK) VALUES (NEW.ID);
    INSERT INTO DHCPv4ServerOption (DHCPVersionServerOptions_FK) VALUES ((SELECT ID FROM DHCPVersionServerOptions ORDER BY ID DESC LIMIT 1));

    UPDATE DHCPv4ServerOption
        SET DHCPVersionServerOptions_FK = (SELECT ID FROM DHCPVersionServerOptions ORDER BY ID DESC LIMIT 1)
        WHERE ID = (SELECT ID FROM DHCPv4ServerOption ORDER BY ID DESC LIMIT 1);

    UPDATE DHCPVersionServerOptions 
        SET DHCPv4ServerOption_FK = (SELECT ID FROM DHCPv4ServerOption ORDER BY ID DESC LIMIT 1)
        WHERE ID = (SELECT ID FROM DHCPVersionServerOptions ORDER BY ID DESC LIMIT 1);
END;

DROP TABLE IF EXISTS DHCPSubnetPools;
CREATE TABLE IF NOT EXISTS DHCPSubnetPools (
    ID INTEGER PRIMARY KEY NOT NULL,
    DHCPSubnet_FK INT,
    InetAddressStart VARCHAR(45),
    InetAddressEnd VARCHAR(45),
    InetSubnet VARCHAR(45),
    CONSTRAINT FK_DHCPSubnetPools_DHCPSubnet FOREIGN KEY (DHCPSubnet_FK) REFERENCES DHCPSubnet(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPSubnetReservations;
CREATE TABLE IF NOT EXISTS DHCPSubnetReservations (
    ID INTEGER PRIMARY KEY NOT NULL,
    DHCPSubnet_FK INT,
    MacAddress VARCHAR(12),
    InetAddress VARCHAR(45),
    CONSTRAINT FK_DHCPSubnetReservations_DHCPSubnet FOREIGN KEY (DHCPSubnet_FK) REFERENCES DHCPSubnet(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS DHCPOptions;
CREATE TABLE IF NOT EXISTS DHCPOptions (
    ID INTEGER PRIMARY KEY NOT NULL,
    DhcpOption VARCHAR(20),
    DhcpValue VARCHAR(50),
    DHCPSubnetPools_FK INT,
    DHCPSubnetReservations_FK INT,
    CONSTRAINT FK_DHCPOptions_DHCPSubnetPools FOREIGN KEY (DHCPSubnetPools_FK) REFERENCES DHCPSubnetPools(ID) ON DELETE CASCADE,
    CONSTRAINT FK_DHCPOptions_DHCPSubnetReservations FOREIGN KEY (DHCPSubnetReservations_FK) REFERENCES DHCPSubnetReservations(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS FirewallPolicies;
CREATE TABLE IF NOT EXISTS FireWallPolicies (
    ID INTEGER PRIMARY KEY NOT NULL,
    Description VARCHAR(255)                -- Description of the policy
);

DROP TABLE IF EXISTS FWDirectionInterfaces;
CREATE TABLE IF NOT EXISTS FWDirectionInterfaces (
    ID INTEGER PRIMARY KEY NOT NULL,
    FirewallPolicy_FK INT,                  -- Foreign key to link with FirewallPolicies
    Interface_FK INT,
    Direction VARCHAR(8),                   -- Direction (inbound or outbound)
    CONSTRAINT FK_FirewallRules_FWPolicies FOREIGN KEY (FirewallPolicy_FK) REFERENCES FirewallPolicies(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS FirewallRules;
CREATE TABLE IF NOT EXISTS FirewallRules (
    ID INTEGER PRIMARY KEY NOT NULL,
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

DROP TABLE IF EXISTS WifiInterface;
CREATE TABLE IF NOT EXISTS WifiInterface (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INTEGER UNIQUE,
    Channel INT DEFAULT 6,                                      -- Channel 1 - 11 
    HardwareMode VARCHAR(5) DEFAULT 'any',                      -- Mode: a, b, g, ad, ax, any            
    CONSTRAINT FK_WifiInterface_Interface FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS WirelessWifiPolicyInterface;
CREATE TABLE IF NOT EXISTS WirelessWifiPolicyInterface (
    ID INTEGER PRIMARY KEY NOT NULL,
    Interface_FK INTEGER ,               
    WirelessWifiPolicy_FK INTEGER,                              -- 1 : MANY INTERFACES 
    CONSTRAINT FK_WirelessWifiPolicyInterface_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS WirelessWifiPolicy;
CREATE TABLE IF NOT EXISTS WirelessWifiPolicy (
    ID INTEGER PRIMARY KEY NOT NULL,
    WirelessWifiPolicyInterface_FK INTEGER,
    WifiPolicyName VARCHAR(50) UNIQUE,                          -- Only one Policy
    Channel INT DEFAULT 6,                                      -- Channel 1 - 11 
    HardwareMode VARCHAR(5) DEFAULT 'any',                      -- Mode: a, b, g, ad, ax, any           
    CONSTRAINT FK_WirelessWifiPolicy_WirelessWifiPolicyInterface FOREIGN KEY (WirelessWifiPolicyInterface_FK) REFERENCES WirelessWifiPolicyInterface(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS WirelessWifiSecurityPolicy;
CREATE TABLE IF NOT EXISTS WirelessWifiSecurityPolicy (
    ID INTEGER PRIMARY KEY NOT NULL,
    WirelessWifiPolicy_FK INTEGER,
    Ssid VARCHAR(32) DEFAULT 'Guest-WiFi',                           -- 
    WpaPassPhrase VARCHAR(63) DEFAULT 'password',
    WpaVersion INTEGER DEFAULT 2,                                       -- WPA = 1, WPA2 = 2, WPA3 = 3
    WpaKeyManagment VARCHAR(20) DEFAULT 'WPA-Personal',
    WpaPairwise VARCHAR(20) DEFAULT 'TKIP CCMP',
    CONSTRAINT FK_WirelessWifiSecurityPolicy_WirelessWifiPolicy FOREIGN KEY (WirelessWifiPolicy_FK) REFERENCES WirelessWifiPolicy(ID) ON DELETE CASCADE
);

DROP TABLE IF EXISTS WirelessWifiHostapdOptions;
CREATE TABLE IF NOT EXISTS WirelessWifiHostapdOptions (
    ID INTEGER PRIMARY KEY NOT NULL,
    WirelessWifiPolicy_FK INTEGER,
    OptionName VARCHAR(255),
    OptionValue VARCHAR(255),
    CONSTRAINT FK_WirelessWifiHostapdOptions_Interfaces FOREIGN KEY (WirelessWifiPolicy_FK) REFERENCES WirelessWifiPolicy(ID) ON DELETE CASCADE
);



