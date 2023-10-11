# Bridge and VLAN Configuration

This configuration sets up two bridges (`brlan0` and `brlan1`) and two VLANs (`vlan1000` and `vlan2000`) with assigned ports. The GigabitEthernet ports are associated with their respective bridges and VLANs.

## Enabling Configuration Mode

1. Enter privileged EXEC mode by typing `enable`.

2. Enter global configuration mode with `configure terminal`.

## Bridge Configuration

3. Create and configure `brlan0` and `brlan1` bridges:

   ```config
   bridge brlan0
       no shutdown
   end

   bridge brlan1
       no shutdown
   end
   ```

   These commands create and activate the `brlan0` and `brlan1` bridges.

## VLAN Configuration

4. Create and configure two VLANs, `vlan1000` and `vlan2000`:

   ```config
    vlan 1000
        name vlan1000
    end

    vlan 2000
        name vlan2000
    end
   ```

   These commands create VLANs with the names "vlan1000" and "vlan2000."

## Port Configuration

5. Rename and configure GigabitEthernet ports and associate them with the respective bridges and VLANs:

   - **Gig0** is associated with `brlan0` and `vlan1000`:

     ```config
     flush enx3c8cf8f943a2
     rename if enx3c8cf8f943a2 if-alias Gig0

     interface Gig0
         bridge group brlan0
         switchport access vlan vlan1000
         no shutdown
     end
     ```

   - **Gig1** is associated with `brlan0` and `vlan1000`:

     ```config
     flush enx00249b119cef
     rename if enx00249b119cef if-alias Gig1

     interface Gig1
         bridge group brlan0
         switchport access vlan vlan1000
         no shutdown
     end
     ```

   - **Gig2** is associated with `brlan1` and `vlan2000`:

     ```config
     flush enx9cebe81be18a
     rename if enx9cebe81be18a if-alias Gig2

     interface Gig2
         bridge group brlan1
         switchport access vlan vlan2000
         no shutdown
     end
     ```

   - **Gig3** is associated with `brlan1` and `vlan2000`:

     ```config
     flush enx8cae4cdb5f8e
     rename if enx8cae4cdb5f8e if-alias Gig3

     interface Gig3
         bridge group brlan1
         switchport access vlan vlan2000
         no shutdown
     end
     ```

   These configurations rename the interfaces for clarity and associate them with their respective bridges and VLANs.

## Saving and Exiting Configuration

6. To save your configuration, use the `write memory` or `copy running-config startup-config` command.

7. Exit configuration mode with `exit`.

## Full Configuration

Here's the complete configuration for your reference:

```config
enable
configure terminal

bridge brlan0
    no shutdown
end

bridge brlan1
    no shutdown
end

vlan 1000
    name vlan1000
end

vlan 2000
    name vlan2000
end

flush enx3c8cf8f943a2
rename if enx3c8cf8f943a2 if-alias Gig0

interface Gig0
    bridge group brlan0
    switchport access vlan vlan1000
    no shutdown
end

flush enx00249b119cef
rename if enx00249b119cef if-alias Gig1

interface Gig1
    bridge group brlan0
    switchport access vlan vlan1000
    no shutdown
end

flush enx9cebe81be18a
rename if enx9cebe81be18a if-alias Gig2

interface Gig2
    bridge group brlan1
    switchport access vlan vlan2000
    no shutdown
end

flush enx8cae4cdb5f8e
rename if enx8cae4cdb5f8e if-alias Gig3

interface Gig3
    bridge group brlan1
    switchport access vlan vlan2000
    no shutdown
end
```

This full configuration establishes two bridges, two VLANs, and associates GigabitEthernet ports with their respective bridges and VLANs. Adjust the configuration as needed for your network setup.
