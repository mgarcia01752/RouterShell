import logging

'''
TODO ADD TO CLASS
from lib.common.router_shell_log_control import  RouterShellLoggingGlobalSettings as RSLGS

        self.log.setLevel(RSLGS().BRIDGE_CONFIG)

'''


class RouterShellLoggerSettings():
    '''
        LOGGING LEVELS: INFO WARN ERROR FATAL CRITICAL
    '''

    GLOBAL_DEBUG = False

    TEMPLATE_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    GLOBAL_MODE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ROUTER_SHELL_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    ROUTERCLI = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    CMD_PROMPT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    TELNET_SERVER = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    SYSTEM_CALL = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSTEM_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSTEM_START_UP = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSTEM_INIT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSTEM_RESET = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSTEM_SHUT_DOWN = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSTEM_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSTEM_SERVICE_CTRL = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    LINUX_SYSTEM = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    COPY = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    COPY_START_RUN = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    COPY_MODE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    CONFIGURE_MODE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    CONFIGURE_PROMPT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    CLEAR_MODE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SHOW_MODE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    CONFIGURE_CMD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    BRIDGE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_INTERFACE_FACTORY = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    BRIDGE_CONFIG_CMD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    DHCPD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    DHCP_CLIENT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CLIENT_FACTORY = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CLIENT_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_SUPPORTED_CLIENTS_ABC = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CLIENT_UDHCPC = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CLIENT_UDHCPC6 = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CLIENT_DHCPCD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_CLIENT_DHCLIENT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    
    DHCP_INTERFACE_CLIENT = logging.DEBUG if GLOBAL_DEBUG else logging.DEBUG

    DHCP_SERVER = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_SERVER_MANAGER = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_SERVER_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_POOL_FACTORY = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_SERVER_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    DHCP_SERVER_SERVICE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_SERVER_SERVICE_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    DNSMASQ_SERVICE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DNSMASQ_GLOBAL_SERVICE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DNSMASQ_INTERFACE_SERVICE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DNSMASQ_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    INTERFACE_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    IF_SHOW = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    ROUTE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    IP_ROUTE_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    NAT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    NAT_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    NAT_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    HARDWARE_NETWORK = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    VLAN                        = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    VLAN_DB                     = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    VLAN_CONFIG_CMD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    VLAN_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    VLAN_MGT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    VLAN_SWITCHPORT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    ARP = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ARP_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    WIFI = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    WIFI_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    WIFI_POLICY = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    WIFI_INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    WIFI_POLICY_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    WIFI_ACCESS_POINT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    WL_CELL = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    ROUTER_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ROUTER_CONFIG_DB = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    ROUTER_PROMPT = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    PROMPT_FEEDER = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    CREATE_LB_INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    NETWORK_INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    NET_INTERFACE_FACTORY = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    NETWORK_MANAGER = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    INET = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    MAC = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    PHY = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    RUN = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    SYSCTL = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    OS_CHECKER = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    ##########################
    # HIGH LEVEL API LOGGING #
    ##########################

    DHCP_POOL_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    DHCP_POOL_CONFIG_CMD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    LOOPBACK_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    LOOPBACK_CONFIG_CMD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    LOOPBACK_INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    ETHERNET_CONFIG_CMD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ETHERNET_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    ETHERNET_INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    SYSTEM = logging.DEBUG if GLOBAL_DEBUG else logging.INFO

    WIRELESS_WIFI_CONFIG_CMD = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    WIRELESS_WIFI_CONFIG = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
    WIRELESS_WIFI_INTERFACE = logging.DEBUG if GLOBAL_DEBUG else logging.INFO
