-- Drop the Interfaces table if it exists
DROP TABLE IF EXISTS Interfaces;

-- Create the Interface table if it doesn't exist
CREATE TABLE IF NOT EXISTS Interfaces (
    ID INT PRIMARY KEY,
    IfName VARCHAR(100),
    InterfaceType VARCHAR(100)
);

-- Drop the Bridges table if it exists
DROP TABLE IF EXISTS Bridges;

-- Create the Bridge table if it doesn't exist
CREATE TABLE IF NOT EXISTS Bridges (
    ID INT PRIMARY KEY,
    Interface_FK INT,
    BridgeName VARCHAR(50),
    CONSTRAINT FK_Bridges_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

-- Drop the Vlans table if it exists
DROP TABLE IF EXISTS Vlans;

-- Create the Vlan table if it doesn't exist
CREATE TABLE IF NOT EXISTS Vlans (
    ID INT PRIMARY KEY,
    VlanInterfaces_FK INT,
    VlanName VARCHAR(20),
    VlanDescription VARCHAR(50),
    CONSTRAINT FK_Vlans_VlanInterfaces FOREIGN KEY (VlanInterfaces_FK) REFERENCES VlanInterfaces(ID)
);

-- Drop the VlanInterfaces table if it exists
DROP TABLE IF EXISTS VlanInterfaces;

-- Create the VLANs table
CREATE TABLE IF NOT EXISTS VlanInterfaces (
    ID INT PRIMARY KEY,
    VlanName VARCHAR(20),
    Interface_FK INT, -- Connection to an interface (optional)
    Bridge_FK INT,    -- Connection to a bridge (optional)
    CONSTRAINT FK_VLANs_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID),
    CONSTRAINT FK_VLANs_Bridges FOREIGN KEY (Bridge_FK) REFERENCES Bridges(ID)
);

-- Drop the Nats table if it exists
DROP TABLE IF EXISTS Nats;

-- Create the Nats table if it doesn't exist
CREATE TABLE IF NOT EXISTS Nats (
    ID INT PRIMARY KEY,
    NatPoolName VARCHAR(50),
    Interface_FK INT,  -- Add the missing column
    CONSTRAINT FK_Nats_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

-- Drop the NatDirections table if it exists
DROP TABLE IF EXISTS NatDirections;

-- Create the NatDirection table if it doesn't exist
CREATE TABLE IF NOT EXISTS NatDirections (
    ID INT PRIMARY KEY,
    NAT_FK INT,
    INTERFACE_FK INT,
    Direction INT,
    CONSTRAINT FK_NatDirections_Nats FOREIGN KEY (NAT_FK) REFERENCES Nats(ID)
);

-- Drop the DHCP table if it exists
DROP TABLE IF EXISTS DHCP;

-- Create the DHCP table if it doesn't exist
CREATE TABLE IF NOT EXISTS DHCP (
    id INT PRIMARY KEY,
    Interface_FK INT,
    DhcpPoolname VARCHAR(50),
    CONSTRAINT fk_DHCP_Interfaces FOREIGN KEY (Interface_FK) REFERENCES Interfaces(ID)
);

-- Drop the Subnet table if it exists
DROP TABLE IF EXISTS Subnet;

-- Create the Subnet table if it doesn't exist
CREATE TABLE IF NOT EXISTS Subnet (
    id INT PRIMARY KEY,
    DHCP_FK INT,
    IpSubnet VARCHAR(45),
    CONSTRAINT fk_Subnet_DHCP FOREIGN KEY (DHCP_FK) REFERENCES DHCP(id)
);

-- Drop the Pools table if it exists
DROP TABLE IF EXISTS Pools;

-- Create the Pools table if it doesn't exist
CREATE TABLE IF NOT EXISTS Pools (
    id INT PRIMARY KEY,
    Subnet_FK INT,
    IpAddressStart VARCHAR(45),
    IpAddressEnd VARCHAR(45),
    IpSubnet VARCHAR(45),
    CONSTRAINT fk_Pools_Subnet FOREIGN KEY (Subnet_FK) REFERENCES Subnet(id)
);

-- Drop the Options table if it exists
DROP TABLE IF EXISTS Options;

-- Create the Options table if it doesn't exist
CREATE TABLE IF NOT EXISTS Options (
    id INT PRIMARY KEY,
    DhcpOptions VARCHAR(20),
    DhcpValue VARCHAR(50),
    Pools_FK INT, -- Connection to Pools
    DHCP_FK INT, -- Connection to DHCP
    Reservations_FK INT, -- Connection to Reservations
    CONSTRAINT fk_Options_Pools FOREIGN KEY (Pools_FK) REFERENCES Pools(id),
    CONSTRAINT fk_Options_DHCP FOREIGN KEY (DHCP_FK) REFERENCES DHCP(id),
    CONSTRAINT fk_Options_Reservations FOREIGN KEY (Reservations_FK) REFERENCES Reservations(id)
);

