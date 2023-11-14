# Wireless WiFi Access Point Configuration Guide

## WiFi Policy Full Settings

To configure the WiFi access point with full settings, follow the steps outlined below:

```shell
enable
configure terminal

; wifi-policy full settings
wireless wifi <wifi-policy-name>
    ssid <ssid> pass-phrase <pass-phrase> wpa-mode [WPA | {WPA2} | WPA3 ]
    [no] wpa key-mgmt [WPA-PSK | {WPA-EPA} | WPA-EPA-SHA256 | WPA-EPA-TLS]
    [no] wpa pairwise [CCMP | {TKIP}]
    [no] rsn pairwise [{CCMP} | TKIP]
    [no] mode [ a | b | g | ad | ax | {any}]
    [no] channel [1 | 2 | 3 | 4 | 5 | {6} | 8 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14]
    [no] auth algs [OSA | {SKA}]
    [no] mac acl [{0} | 1 | 2]
    [no] hostapd config-overwrite <hostapd-option> <value>
end
```

This section outlines the steps to enable and configure the WiFi access point with specific settings. Notable configuration parameters include the SSID (Service Set Identifier), passphrase, WPA (Wi-Fi Protected Access) mode, key management options, pairwise encryption algorithms, operating mode, channel selection, authentication algorithms, MAC (Media Access Control) address control lists, and hostapd configuration overwrites.

## WiFi Policy Default Settings

To set default WiFi policy settings, follow the instructions below:

```shell
; wifi-policy default settings
wireless wifi <wifi-policy-name-default>
end
```

This section focuses on establishing default settings for the WiFi access point. By using the "wifi-policy default settings" command, you can define a set of default configurations that will be applied unless overridden. This is useful for maintaining consistent settings across multiple access points or simplifying the configuration process.

# WiFi Interface Configuration

## Rename WiFi Interface

To rename a WiFi interface, use the following commands:

```shell
rename if <wifi-interface> if-alias <wifi-interface-alias>
```

This command allows you to assign a user-friendly alias to a WiFi interface, making it easier to identify and manage.

## Configure WiFi Interface

To configure a WiFi interface, follow these steps:

```shell
interface <wifi-interface | wifi-interface-alias>
    [no] wireless wifi-policy <wifi-policy-name>

    ; Apply mode to wifi-interface, this will overwrite wifi-policy mode setting
    [no] mode [ a | b | g | ad | ax | {any}]

    ; Apply channel to wifi-interface, this will overwrite wifi-policy setting
    [no] channel [1 | 2 | 3 | 4 | 5 | {6} | 8 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14] 
end
```
