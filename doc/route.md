**IPv4 Static Route**:

1. **Static IPv4 Route to a Network**:
   
   ```shell
   ip route 192.168.2.0 255.255.255.0 10.0.0.1
   ```

   This command adds a static route for the `192.168.2.0/24` network via the next-hop gateway `10.0.0.1`.

2. **Static Default Route**:

   ```shell
   ip route 0.0.0.0 0.0.0.0 10.0.0.1
   ```

   This command configures a static default route, which forwards all traffic to the next-hop gateway `10.0.0.1`.

**IPv6 Static Route**:

3. **Static IPv6 Route to a Network**:

   ```shell
   ipv6 route 2001:db8:abcd:1::/64 GigabitEthernet0/0/0 2001:db8:1234:5678::1
   ```

   This command adds a static route for the `2001:db8:abcd:1::/64` IPv6 network via the interface `GigabitEthernet0/0/0` and the next-hop IPv6 address `2001:db8:1234:5678::1`.

4. **Static IPv6 Default Route**:

   ```shell
   ipv6 route ::/0 GigabitEthernet0/0/0 2001:db8:1234:5678::1
   ```

   This command configures a static default IPv6 route, which forwards all IPv6 traffic to the next-hop gateway `2001:db8:1234:5678::1` via `GigabitEthernet0/0/0`.

**IPv4 and IPv6 Dual Stack Route**:

5. **Dual Stack Default Routes**:

   ```shell
   ip route 0.0.0.0 0.0.0.0 10.0.0.1
   ipv6 route ::/0 GigabitEthernet0/0/0 2001:db8:1234:5678::1
   ```

   This configuration sets up both an IPv4 and an IPv6 default route. IPv4 traffic is forwarded via `10.0.0.1`, and IPv6 traffic is forwarded via `2001:db8:1234:5678::1` through the `GigabitEthernet0/0/0` interface.

These are basic examples of router route configurations. Be sure to adapt these configurations to your specific network setup and adjust IP addresses, subnet masks, interface names, and next-hop gateway addresses as needed.
