# System Configuration

This guide provides instructions for configuring Telnet and SSH servers on your system. Telnet and SSH are protocols used to establish remote connections to your devices. While Telnet is often used for basic remote access and network device configuration, SSH is preferred for secure connections due to its encryption capabilities.

## Telnet

Telnet allows you to remotely connect to and manage devices over a network using plain text communication. Due to its lack of encryption, Telnet is generally used in controlled or secure environments.

### Configuration Steps:

1. **Enter Configuration Mode**:
    - Access the device's configuration terminal.
    ```shell
    configure terminal
    ```

2. **Enable Telnet Server**:
    - Configure the Telnet server to listen on the default port (23). This step enables the Telnet service on the specified port.
    ```shell
    system telnet-server port 23
    ```

3. **Disable Telnet Server**:
    - If you want to disable the Telnet server, you can use the `no` option to turn it off.
    ```shell
    no system telnet-server
    ```

4. **Exit Configuration Mode**:
    - Save the configuration and exit the terminal.
    ```shell
    end
    ```

The complete configuration looks like this for enabling:
```shell
configure terminal
 system telnet-server port 23
end
```

To disable the Telnet server:
```shell
configure terminal
 no system telnet-server
end
```

### Important Notes:
- **Security**: Telnet transmits data in plain text, making it vulnerable to interception. Use it only in trusted networks or environments.
- **Firewall**: Ensure that your firewall allows traffic on port 23.

## Secure Shell (SSH)

SSH provides a secure channel over an unsecured network by encrypting the data transferred between the client and server. It is the preferred method for secure remote access and management of devices.

### Configuration Steps:

1. **Enter Configuration Mode**:
    - Access the device's configuration terminal.
    ```shell
    configure terminal
    ```

2. **Enable SSH Server**:
    - Configure the SSH server to listen on the default port (22). This step enables the SSH service on the specified port.
    ```shell
    system ssh-server port 22
    ```

3. **Disable SSH Server**:
    - If you want to disable the SSH server, you can use the `no` option to turn it off.
    ```shell
    no system ssh-server
    ```

4. **Exit Configuration Mode**:
    - Save the configuration and exit the terminal.
    
    ```shell
    end
    ```

    - The complete configuration looks like this for enabling:
    
    ```shell
    configure terminal
    system ssh-server port 22
    end
    ```

    - To disable the SSH server:
    
    ```shell
    configure terminal
    no system ssh-server
    end
```
