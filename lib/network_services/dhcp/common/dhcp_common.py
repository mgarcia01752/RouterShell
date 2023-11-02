from enum import Enum

class DHCPVersion(Enum):
    DHCP_V4 = 'DHCPv4'
    DHCP_V6 = 'DHCPv6'

class DHCPOptionLookup:
    
    def __init__(self):
        pass
        
    '''https://kea.readthedocs.io/en/latest/arm/dhcp4-srv.html#id2'''
        
    dhcpv4_option_lookup = {
        2: {"Name": "time-offset", "Type": "int32", "Array": False, "Returned if not requested": False},
        3: {"Name": "routers", "Type": "ipv4-address", "Array": True, "Returned if not requested": True},
        4: {"Name": "time-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        5: {"Name": "name-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        6: {"Name": "domain-name-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": True},
        7: {"Name": "log-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        8: {"Name": "cookie-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        9: {"Name": "lpr-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        10: {"Name": "impress-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        11: {"Name": "resource-location-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        13: {"Name": "boot-size", "Type": "uint16", "Array": False, "Returned if not requested": False},
        14: {"Name": "merit-dump", "Type": "string", "Array": False, "Returned if not requested": False},
        15: {"Name": "domain-name", "Type": "fqdn", "Array": False, "Returned if not requested": True},
        16: {"Name": "swap-server", "Type": "ipv4-address", "Array": False, "Returned if not requested": False},
        17: {"Name": "root-path", "Type": "string", "Array": False, "Returned if not requested": False},
        18: {"Name": "extensions-path", "Type": "string", "Array": False, "Returned if not requested": False},
        19: {"Name": "ip-forwarding", "Type": "boolean", "Array": False, "Returned if not requested": False},
        20: {"Name": "non-local-source-routing", "Type": "boolean", "Array": False, "Returned if not requested": False},
        21: {"Name": "policy-filter", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        22: {"Name": "max-dgram-reassembly", "Type": "uint16", "Array": False, "Returned if not requested": False},
        23: {"Name": "default-ip-ttl", "Type": "uint8", "Array": False, "Returned if not requested": False},
        24: {"Name": "path-mtu-aging-timeout", "Type": "uint32", "Array": False, "Returned if not requested": False},
        25: {"Name": "path-mtu-plateau-table", "Type": "uint16", "Array": True, "Returned if not requested": False},
        26: {"Name": "interface-mtu", "Type": "uint16", "Array": False, "Returned if not requested": False},
        27: {"Name": "all-subnets-local", "Type": "boolean", "Array": False, "Returned if not requested": False},
        28: {"Name": "broadcast-address", "Type": "ipv4-address", "Array": False, "Returned if not requested": False},
        29: {"Name": "perform-mask-discovery", "Type": "boolean", "Array": False, "Returned if not requested": False},
        30: {"Name": "mask-supplier", "Type": "boolean", "Array": False, "Returned if not requested": False},
        31: {"Name": "router-discovery", "Type": "boolean", "Array": False, "Returned if not requested": False},
        32: {"Name": "router-solicitation-address", "Type": "ipv4-address", "Array": False, "Returned if not requested": False},
        33: {"Name": "static-routes", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        34: {"Name": "trailer-encapsulation", "Type": "boolean", "Array": False, "Returned if not requested": False},
        35: {"Name": "arp-cache-timeout", "Type": "uint32", "Array": False, "Returned if not requested": False},
        36: {"Name": "ieee802-3-encapsulation", "Type": "boolean", "Array": False, "Returned if not requested": False},
        37: {"Name": "default-tcp-ttl", "Type": "uint8", "Array": False, "Returned if not requested": False},
        38: {"Name": "tcp-keepalive-interval", "Type": "uint32", "Array": False, "Returned if not requested": False},
        39: {"Name": "tcp-keepalive-garbage", "Type": "boolean", "Array": False, "Returned if not requested": False},
        40: {"Name": "nis-domain", "Type": "string", "Array": False, "Returned if not requested": False},
        41: {"Name": "nis-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        42: {"Name": "ntp-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        43: {"Name": "vendor-encapsulated-options", "Type": "empty", "Array": False, "Returned if not requested": False},
        44: {"Name": "netbios-name-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        45: {"Name": "netbios-dd-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        46: {"Name": "netbios-node-type", "Type": "uint8", "Array": False, "Returned if not requested": False},
        47: {"Name": "netbios-scope", "Type": "string", "Array": False, "Returned if not requested": False},
        48: {"Name": "font-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        49: {"Name": "x-display-manager", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        52: {"Name": "dhcp-option-overload", "Type": "uint8", "Array": False, "Returned if not requested": False},
        54: {"Name": "dhcp-server-identifier", "Type": "ipv4-address", "Array": False, "Returned if not requested": True},
        56: {"Name": "dhcp-message", "Type": "string", "Array": False, "Returned if not requested": False},
        57: {"Name": "dhcp-max-message-size", "Type": "uint16", "Array": False, "Returned if not requested": False},
        60: {"Name": "vendor-class-identifier", "Type": "string", "Array": False, "Returned if not requested": False},
        62: {"Name": "nwip-domain-name", "Type": "string", "Array": False, "Returned if not requested": False},
        63: {"Name": "nwip-suboptions", "Type": "binary", "Array": False, "Returned if not requested": False},
        64: {"Name": "nisplus-domain-name", "Type": "string", "Array": False, "Returned if not requested": False},
        65: {"Name": "nisplus-servers", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        66: {"Name": "tftp-server-name", "Type": "string", "Array": False, "Returned if not requested": False},
        67: {"Name": "boot-file-name", "Type": "string", "Array": False, "Returned if not requested": False},
        68: {"Name": "mobile-ip-home-agent", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        69: {"Name": "smtp-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        70: {"Name": "pop-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        71: {"Name": "nntp-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        72: {"Name": "www-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        73: {"Name": "finger-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        74: {"Name": "irc-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        75: {"Name": "streettalk-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        76: {"Name": "streettalk-directory-assistance-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        77: {"Name": "user-class", "Type": "binary", "Array": False, "Returned if not requested": False},
        78: {"Name": "slp-directory-agent", "Type": "record (boolean, ipv4-address)", "Array": True, "Returned if not requested": False},
        79: {"Name": "slp-service-scope", "Type": "record (boolean, string)", "Array": False, "Returned if not requested": False},
        85: {"Name": "nds-server", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        86: {"Name": "nds-tree-name", "Type": "string", "Array": False, "Returned if not requested": False},
        87: {"Name": "nds-context", "Type": "string", "Array": False, "Returned if not requested": False},
        88: {"Name": "bcms-controller-names", "Type": "fqdn", "Array": True, "Returned if not requested": False},
        89: {"Name": "bcms-controller-address", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        93: {"Name": "client-system", "Type": "uint16", "Array": True, "Returned if not requested": False},
        94: {"Name": "client-ndi", "Type": "record (uint8, uint8, uint8)", "Array": False, "Returned if not requested": False},
        97: {"Name": "uuid-guid", "Type": "record (uint8, binary)", "Array": False, "Returned if not requested": False},
        98: {"Name": "uap-servers", "Type": "string", "Array": False, "Returned if not requested": False},
        99: {"Name": "geoconf-civic", "Type": "binary", "Array": False, "Returned if not requested": False},
        100: {"Name": "pcode", "Type": "string", "Array": False, "Returned if not requested": False},
        101: {"Name": "tcode", "Type": "string", "Array": False, "Returned if not requested": False},
        108: {"Name": "v6-only-preferred", "Type": "uint32", "Array": False, "Returned if not requested": False},
        112: {"Name": "netinfo-server-address", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        113: {"Name": "netinfo-server-tag", "Type": "string", "Array": False, "Returned if not requested": False},
        114: {"Name": "v4-captive-portal", "Type": "string", "Array": False, "Returned if not requested": False},
        116: {"Name": "auto-config", "Type": "uint8", "Array": False, "Returned if not requested": False},
        117: {"Name": "name-service-search", "Type": "uint16", "Array": True, "Returned if not requested": False},
        119: {"Name": "domain-search", "Type": "fqdn", "Array": True, "Returned if not requested": False},
        124: {"Name": "vivco-suboptions", "Type": "record (uint32, binary)", "Array": False, "Returned if not requested": False},
        125: {"Name": "vivso-suboptions", "Type": "uint32", "Array": False, "Returned if not requested": False},
        136: {"Name": "pana-agent", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        137: {"Name": "v4-lost", "Type": "fqdn", "Array": False, "Returned if not requested": False},
        138: {"Name": "capwap-ac-v4", "Type": "ipv4-address", "Array": True, "Returned if not requested": False},
        141: {"Name": "sip-ua-cs-domains", "Type": "fqdn", "Array": True, "Returned if not requested": False},
        143: {"Name": "v4-sztp-redirect", "Type": "tuple", "Array": True, "Returned if not requested": False},
        146: {"Name": "rdnss-selection", "Type": "record (uint8, ipv4-address, ipv4-address, fqdn)", "Array": True, "Returned if not requested": False},
        159: {"Name": "v4-portparams", "Type": "record (uint8, psid)", "Array": False, "Returned if not requested": False},
        162: {"Name": "v4-dnr", "Type": "record (uint16, uint16, uint8, fqdn, binary)", "Array": False, "Returned if not requested": False},
        212: {"Name": "option-6rd", "Type": "record (uint8, uint8, ipv6-address, ipv4-address)", "Array": True, "Returned if not requested": False},
        213: {"Name": "v4-access-domain", "Type": "fqdn", "Array": False, "Returned if not requested": False}
    }

    '''https://kea.readthedocs.io/en/latest/arm/dhcp6-srv.html#id2'''
    dhcpv6_option_lookup = {
        7: {"Name": "preference", "Type": "uint8", "Array": False},
        12: {"Name": "unicast", "Type": "ipv6-address", "Array": False},
        21: {"Name": "sip-server-dns", "Type": "fqdn", "Array": True},
        22: {"Name": "sip-server-addr", "Type": "ipv6-address", "Array": True},
        23: {"Name": "dns-servers", "Type": "ipv6-address", "Array": True},
        24: {"Name": "domain-search", "Type": "fqdn", "Array": True},
        27: {"Name": "nis-servers", "Type": "ipv6-address", "Array": True},
        28: {"Name": "nisp-servers", "Type": "ipv6-address", "Array": True},
        29: {"Name": "nis-domain-name", "Type": "fqdn", "Array": True},
        30: {"Name": "nisp-domain-name", "Type": "fqdn", "Array": True},
        31: {"Name": "sntp-servers", "Type": "ipv6-address", "Array": True},
        32: {"Name": "information-refresh-time", "Type": "uint32", "Array": False},
        33: {"Name": "bcmcs-server-dns", "Type": "fqdn", "Array": True},
        34: {"Name": "bcmcs-server-addr", "Type": "ipv6-address", "Array": True},
        36: {"Name": "geoconf-civic", "Type": "record (uint8, uint16, binary)", "Array": False},
        37: {"Name": "remote-id", "Type": "record (uint32, binary)", "Array": False},
        38: {"Name": "subscriber-id", "Type": "binary", "Array": False},
        39: {"Name": "client-fqdn", "Type": "record (uint8, fqdn)", "Array": False},
        40: {"Name": "pana-agent", "Type": "ipv6-address", "Array": True},
        41: {"Name": "new-posix-timezone", "Type": "string", "Array": False},
        42: {"Name": "new-tzdb-timezone", "Type": "string", "Array": False},
        43: {"Name": "ero", "Type": "uint16", "Array": True},
        44: {"Name": "lq-query (1)", "Type": "record (uint8, ipv6-address)", "Array": False},
        45: {"Name": "client-data (1)", "Type": "empty", "Array": False},
        46: {"Name": "clt-time (1)", "Type": "uint32", "Array": False},
        47: {"Name": "lq-relay-data (1)", "Type": "record (ipv6-address, binary)", "Array": False},
        48: {"Name": "lq-client-link (1)", "Type": "ipv6-address", "Array": True},
        51: {"Name": "v6-lost", "Type": "fqdn", "Array": False},
        52: {"Name": "capwap-ac-v6", "Type": "ipv6-address", "Array": True},
        53: {"Name": "relay-id", "Type": "binary", "Array": False},
        57: {"Name": "v6-access-domain", "Type": "fqdn", "Array": False},
        58: {"Name": "sip-ua-cs-list", "Type": "fqdn", "Array": True},
        59: {"Name": "bootfile-url", "Type": "string", "Array": False},
        60: {"Name": "bootfile-param", "Type": "tuple", "Array": True},
        61: {"Name": "client-arch-type", "Type": "uint16", "Array": True},
        62: {"Name": "nii", "Type": "record (uint8, uint8, uint8)", "Array": False},
        64: {"Name": "aftr-name", "Type": "fqdn", "Array": False},
        65: {"Name": "erp-local-domain-name", "Type": "fqdn", "Array": False},
        66: {"Name": "rsoo", "Type": "empty", "Array": False},
        67: {"Name": "pd-exclude", "Type": "binary", "Array": False},
        74: {"Name": "rdnss-selection", "Type": "record (ipv6-address, uint8, fqdn)", "Array": True},
        79: {"Name": "client-linklayer-addr", "Type": "binary", "Array": False},
        80: {"Name": "link-address", "Type": "ipv6-address", "Array": False},
        82: {"Name": "solmax-rt", "Type": "uint32", "Array": False},
        83: {"Name": "inf-max-rt", "Type": "uint32", "Array": False},
        88: {"Name": "dhcp4o6-server-addr", "Type": "ipv6-address", "Array": True},
        89: {"Name": "s46-rule", "Type": "record (uint8, uint8, uint8, ipv4-address, ipv6-prefix)", "Array": False},
        90: {"Name": "s46-br", "Type": "ipv6-address", "Array": False},
        91: {"Name": "s46-dmr", "Type": "ipv6-prefix", "Array": False},
        92: {"Name": "s46-v4v6bind", "Type": "record (ipv4-address, ipv6-prefix)", "Array": False},
        93: {"Name": "s46-portparams", "Type": "record(uint8, psid)", "Array": False},
        94: {"Name": "s46-cont-mape", "Type": "empty", "Array": False},
        95: {"Name": "s46-cont-mapt", "Type": "empty", "Array": False},
        96: {"Name": "s46-cont-lw", "Type": "empty", "Array": False},
        103: {"Name": "v6-captive-portal", "Type": "string", "Array": False},
        136: {"Name": "v6-sztp-redirect", "Type": "tuple", "Array": True},
        143: {"Name": "ipv6-address-andsf", "Type": "ipv6-address", "Array": True},
        144: {"Name": "v6-dnr", "Type": "record (uint16, uint16, fqdn, binary)", "Array": False},
    }

    def lookup_dhcpv4_option(self, option_code):
        """
        Lookup a DHCPv4 option by its option code.

        Args:
            option_code (int): The option code to look up.

        Returns:
            dict or None: A dictionary representing the DHCPv4 option information, or None if not found.
        """
        return self.dhcpv4_option_lookup.get(option_code)

    def lookup_dhcpv6_option(self, option_code):
        """
        Lookup a DHCPv6 option by its option code.

        Args:
            option_code (int): The option code to look up.

        Returns:
            dict or None: A dictionary representing the DHCPv6 option information, or None if not found.
        """
        return self.dhcpv6_option_lookup.get(option_code)

    def get_dhcpv4_option_code(self, option_name):
        """
        Get the DHCPv4 option code by providing the option name.

        Args:
            option_name (str): The name of the DHCPv4 option.

        Returns:
            int or None: The option code for the specified option name, or None if not found.
        """
        for code, option_info in self.dhcpv4_option_lookup.items():
            if option_info["Name"] == option_name:
                return code
        return None

    def get_dhcpv6_option_code(self, option_name):
        """
        Get the DHCPv6 option code by providing the option name.

        Args:
            option_name (str): The name of the DHCPv6 option.

        Returns:
            int or None: The option code for the specified option name, or None if not found.
        """
        for code, option_info in self.dhcpv6_option_lookup.items():
            if option_info["Name"] == option_name:
                return code
        return None
