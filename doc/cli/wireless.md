
# Wireless WiFi Access Point Configuration Guide

```config
cls
clear router-db
yes

configure terminal 

wireless wifi wifi-guest-network
    ssid GuestNetwork pass-phrase FBI wpa-mode WPA2
    
    mode any
    channel 6
end

wireless wifi wifi-default-check
end

rename -if wlx80afca061616 -ifalias wlan0

interface wlan0
    ip address 172.16.0.1/24
    wireless wifi-policy wifi-guest-network
end


```

```config
enable
configure terminal

wireless wifi <wifi-policy-name>
    ssid <ssid> pass-phrase <pass-phrase> wpa-mode [WPA | {WPA2} | WPA3 | Mixed-Mode]
    [no] wpa key-mgmt [WPA-PSK | {WPA-EPA} | WPA-EPA-SHA256 | WPA-EPA-TLS]
    [no] wpa pairwise [CCMP | {TKIP}]
    [no] rsn pairwise [{CCMP} | TKIP]
    [no] mode [ a | b | g | ad | ax | {any}]
    [no] channel [1 | 2 | 3 | 4 | 5 | {6} | 8 | 7 | 8 | 9 | 10 | 11]
    [no] auth-algs [OSA | {SKA}]
    [no] macaddr-acl [{0} | 1 | 2]
    [no] hostapd-conf-overwrite <hostapd-option> <value>
end

rename if <os-announced-interface> if-alias <wireless-interface-alias>

interface <wireless-interface-alias>
    ip address <ip-address> <subnet-mask>
    [no] wireless wifi-policy <wifi-policy-name>
    no shutdown
end

```

```config
enable
configure terminal

wireless cell <wireless-policy-name>
end

wireless wifi <wireless-policy-name>
    ssid ""
    wpa-passphrase ""
    [no] auth-algs [OSA | SKA]
    [no] wpa [WPA | WPA2 | WPA3 | Mixed-Mode]
    [no] wpa-key-mgmt [WPA-PSK | WPA-EPA | WPA-EPA-SHA256 | WPA-EPA-TLS]
    [no] wpa-pairwise [CCMP | TKIP]
    [no] rsn-pairwise [CCMP | TKIP]
    [no] mode [ a | b | g | ad | ax | any]
    [no] channel [1 | 2 | 3 | 4 | 5 | 6 | 8 | 7 | 8 | 9 | 10 | 11]
    [no] macaddr-acl [0 | 1 | 2]
    [no] hostapd-conf-overwrite <hostapd-option> <value>
end

rename if <os-announced-interface> if-alias <wireless-interface-alias>

interface <wireless-interface-alias>
    ip address <ip-address> <subnet-mask>
    wireless-policy <wireless-policy-name>
    no shutdown
end

```