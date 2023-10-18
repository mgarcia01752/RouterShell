-- Drop the Interfaces table if it exists
DROP TABLE IF EXISTS Interfaces;

-- Create the Interface table if it doesn't exist
-- Columns are the minimum entries needed to establish an interface
CREATE TABLE IF NOT EXISTS Interfaces (
    ID INTEGER PRIMARY KEY,
    IfName VARCHAR(100) UNIQUE,
    InterfaceType VARCHAR(100),         -- Interface Type (ethernet, loopback, wireless-wifi, wireless-cell)
    ShutdownStatus BOOLEAN              -- True = interface is shutdown
);

CREATE TABLE IF NOT EXISTS InterfaceSubOptions (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT,
    MacAddress VARCHAR(17),             -- MAC address format: xx:xx:xx:xx:xx:xx
    Duplex INT,                         -- Duplex [half | full | auto]
    Speed VARCHAR(5),                   -- Speed [10 | 100 | 1000 | 10000 | auto]
    CONSTRAINT FK_InterfaceSubOptions_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

CREATE TABLE IF NOT EXISTS InterfaceIpAddress (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT,
    IpAddress VARCHAR(45),              -- IPv4 | IPv6 Address/Mask-Prefix (adjust length as needed)
    SecondaryIp BOOLEAN,                -- True = Secondary
    CONSTRAINT FK_InterfaceIpAddress_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

-- Drop the Bridges table if it exists
DROP TABLE IF EXISTS Bridges;

-- Create the Bridge table if it doesn't exist
CREATE TABLE IF NOT EXISTS Bridges (
    ID INTEGER PRIMARY KEY,
    Interface_FK INT,
    BridgeName VARCHAR(50),
    Protocol VARCHAR(15),               -- Bridge Protocol
    StpStatus BOOLEAN,                  -- STB STATUS ENABLE = 1 , DISABLE = 0 
    CONSTRAINT FK_Bridges_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

-- Drop the Vlans table if it exists
DROP TABLE IF EXISTS Vlans;

-- Create the Vlan table if it doesn't exist
CREATE TABLE IF NOT EXISTS Vlans (
    ID INTEGER PRIMARY KEY,
    VlanID INT UNIQUE,
    VlanInterfaces_FK INT,
    VlanName VARCHAR(20) UNIQUE,
    VlanDescription VARCHAR(50),
    CONSTRAINT FK_Vlans_VlanInterfaces FOREIGN KEY (VlanInterfaces_FK) REFERENCES VlanInterfaces(ID)
);

-- Drop the VlanInterfaces table if it exists
DROP TABLE IF EXISTS VlanInterfaces;

-- Create the VLANs table
CREATE TABLE IF NOT EXISTS VlanInterfaces (
    ID INTEGER PRIMARY KEY,
    VlanName VARCHAR(20),
    Interface_FK INT,
    Bridge_FK INT,
    CONSTRAINT FK_VLANs_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID),
    CONSTRAINT FK_VLANs_Bridges FOREIGN KEY (Bridge_FK) REFERENCES Bridges(ID)
);

-- Drop the Nats table if it exists
DROP TABLE IF EXISTS Nats;

-- Create the Nats table if it doesn't exist
CREATE TABLE IF NOT EXISTS Nats (
    ID INTEGER PRIMARY KEY,
    NatPoolName VARCHAR(50) UNIQUE,
    Interface_FK INT,  -- Add the missing column
    CONSTRAINT FK_Nats_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

-- Drop the NatDirections table if it exists
DROP TABLE IF EXISTS NatDirections;

-- Create the NatDirection table if it doesn't exist
CREATE TABLE IF NOT EXISTS NatDirections (
    ID INTEGER PRIMARY KEY,
    NAT_FK INT,
    INTERFACE_FK INT,
    Direction INT,
    CONSTRAINT FK_NatDirections_Nats FOREIGN KEY (NAT_FK) REFERENCES Nats(ID)
);

-- Drop the DHCP table if it exists
DROP TABLE IF EXISTS DHCP;

-- Create the DHCP table if it doesn't exist
CREATE TABLE IF NOT EXISTS DHCP (
    id INTEGER PRIMARY KEY,
    Interface_FK INT,
    DhcpPoolname VARCHAR(50) UNIQUE,
    CONSTRAINT FK_DHCP_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

-- Drop the Subnet table if it exists
DROP TABLE IF EXISTS Subnet;

-- Create the Subnet table if it doesn't exist
CREATE TABLE IF NOT EXISTS Subnet (
    id INTEGER PRIMARY KEY,
    DHCP_FK INT,
    IpSubnet VARCHAR(45),
    CONSTRAINT FK_Subnet_DHCP FOREIGN KEY (DHCP_FK) REFERENCES DHCP(id)
);

-- Drop the Pools table if it exists
DROP TABLE IF EXISTS Pools;

-- Create the Pools table if it doesn't exist
CREATE TABLE IF NOT EXISTS Pools (
    id INTEGER PRIMARY KEY,
    Subnet_FK INT,
    IpAddressStart VARCHAR(45),
    IpAddressEnd VARCHAR(45),
    IpSubnet VARCHAR(45),
    CONSTRAINT FK_Pools_Subnet FOREIGN KEY (Subnet_FK) REFERENCES Subnet(id)
);

-- Drop the Options table if it exists
DROP TABLE IF EXISTS Reservations;

-- Create the Reservations table
CREATE TABLE IF NOT EXISTS Reservations (
    id INT PRIMARY KEY,
    Subnet_FK INT,
    MacAddress VARCHAR(12),
    IPAddress VARCHAR(45),
    CONSTRAINT FK_Reservations_Subnet FOREIGN KEY (Subnet_FK) REFERENCES Subnet(id)
);

-- Drop the Options table if it exists
DROP TABLE IF EXISTS Options;

-- Create the Options table if it doesn't exist
CREATE TABLE IF NOT EXISTS Options (
    id INTEGER PRIMARY KEY,
    DhcpOptions VARCHAR(20),
    DhcpValue VARCHAR(50),
    Pools_FK INT,
    DHCP_FK INT,
    Reservations_FK INT,
    CONSTRAINT FK_Options_Pools FOREIGN KEY (Pools_FK) REFERENCES Pools(id),
    CONSTRAINT FK_Options_DHCP FOREIGN KEY (DHCP_FK) REFERENCES DHCP(id),
    CONSTRAINT FK_Options_Reservations FOREIGN KEY (Reservations_FK) REFERENCES Reservations(id)
);

