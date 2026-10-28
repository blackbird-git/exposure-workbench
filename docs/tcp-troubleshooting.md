
# TCP Connectivity Troubleshooting Lab

## Objective

Practice diagnosing TCP connection failures using Linux networking tools, packet captures, and firewall rules.

The lab demonstrates three possible TCP connection outcomes:

1. Successful connection
2. Connection refused
3. Connection timeout

## Lab Environment

| Component | Details |
|---|---|
| Client | WSL Ubuntu |
| Server | Ubuntu VM |
| Server IP | `192.168.170.128` |
| Client IP (WSL) | `172.29.29.173` |
| Client IP observed by VM | `192.168.170.1` |
| Server interface | `ens33` |
| Firewall | iptables (nf_tables backend) |

The client and server are on different subnets.

The Ubuntu VM observes a different client source address than WSL reports locally, indicating source NAT between the environments.

## Tools Used

| Tool | Purpose |
|---|---|
| `ping` | Verify basic IP reachability |
| `ip route get` | Inspect routing decisions |
| `ss` | Inspect TCP listeners and connections |
| `nc` | Test TCP connectivity |
| `tcpdump` | Capture and inspect TCP packets |
| `iptables` | Inspect and modify firewall rules |

---

## Scenario 1: Successful TCP Connection

### Start a TCP Listener

On the Ubuntu VM:

```bash
nc -lvnp 9090
```

### Capture TCP Traffic

In another terminal on the VM:

```bash
sudo tcpdump -ni any 'tcp port 9090'
```

### Connect from WSL

```bash
nc -v 192.168.170.128 9090
```

The connection succeeded.

### Packet Capture

The capture showed the TCP three-way handshake:

```text
Client → Server   SYN
Server → Client   SYN-ACK
Client → Server   ACK
```

After sending application data:

```text
Client → Server   PSH, ACK
Server → Client   ACK
```

The transmitted payload contained 15 bytes.

### Inspect TCP Socket State

On the Ubuntu VM:

```bash
ss -tnp '( sport = :9090 )'
```

Output:

```text
State  Recv-Q Send-Q Local Address:Port       Peer Address:Port
ESTAB  0      0      192.168.170.128:9090    192.168.170.1:64436
```

The connection was associated with the `nc` process.

### Conclusion

The TCP handshake completed successfully, and application data was transmitted and acknowledged.

This confirms connectivity for that specific connection attempt but does not establish long-term network or application health.

---

## Scenario 2: Connection Refused

### Test a Port Without a Listener

From WSL:

```bash
nc -vz -w 3 192.168.170.128 9091
```

Result:

```text
Connection refused
```

### Capture TCP Traffic

On the Ubuntu VM:

```bash
sudo tcpdump -ni any 'tcp port 9091'
```

Observed:

```text
Client → Server   SYN
Server → Client   RST, ACK
```

Actual packet capture:

```text
192.168.170.1.64438 > 192.168.170.128.9091: Flags [S]
192.168.170.128.9091 > 192.168.170.1.64438: Flags [R.]
```

### Analysis

The SYN reached the destination server.

Because no process was listening on TCP port 9091, the server's TCP stack responded with RST-ACK.

The client immediately reported `Connection refused`.

### Conclusion

A refused connection indicates that the connection attempt was actively rejected.

Common causes include:

- No process listening on the destination port
- Service listening on the wrong interface
- Firewall configured to reject TCP connections

A TCP reset does not necessarily indicate an application failure.

---

## Scenario 3: Connection Timeout

### Objective

Simulate a firewall silently dropping incoming TCP connections.

### Create a Firewall DROP Rule

On the Ubuntu VM:

```bash
sudo iptables -I INPUT 1 -s 192.168.170.1 -p tcp --dport 9092 -j DROP
```

This rule drops incoming TCP traffic to port 9092 from the client's NAT-translated address.

### Verify Firewall Configuration

```bash
sudo iptables -L INPUT -n -v --line-numbers
```

Output:

```text
Chain INPUT (policy ACCEPT)
num  pkts bytes target prot source          destination
1    0    0     DROP   tcp  192.168.170.1   0.0.0.0/0 tcp dpt:9092
```

### Start Packet Capture

On the Ubuntu VM:

```bash
sudo tcpdump -ni any 'tcp port 9092'
```

### Test Connectivity

From WSL:

```bash
nc -vz -w 5 192.168.170.128 9092
```

Result:

```text
Connection timed out
```

### Packet Capture

Five incoming SYN packets were observed:

```text
Client → Server   SYN
Client → Server   SYN
Client → Server   SYN
Client → Server   SYN
Client → Server   SYN
```

No SYN-ACK or RST packets were returned.

All five SYN packets used the same TCP sequence number:

```text
seq 1012368340
```

This indicated retransmissions of the same connection attempt.

### Verify Firewall Counters

```bash
sudo iptables -L INPUT -n -v --line-numbers
```

Output:

```text
num  pkts bytes target prot source          destination
1    5    300   DROP   tcp  192.168.170.1   0.0.0.0/0 tcp dpt:9092
```

The firewall counter showed five matching packets.

### Analysis

The packet capture confirmed that SYN packets reached the Ubuntu VM's network interface.

However, the firewall silently dropped them before they could be processed normally by the TCP stack.

Because the client received no response, it retransmitted SYN packets until the connection attempt timed out.

### Conclusion

A TCP timeout does not necessarily mean packets failed to reach the destination server.

Packets may reach the server's network interface but be discarded by local firewall rules.

Packet captures combined with firewall counters help distinguish this situation from packet loss elsewhere in the network.

---

## Scenario 4: Firewall Cleanup and Recovery

### Remove the DROP Rule

On the Ubuntu VM:

```bash
sudo iptables -D INPUT -s 192.168.170.1 -p tcp --dport 9092 -j DROP
```

### Verify Removal

```bash
sudo iptables -L INPUT -n -v --line-numbers
```

Output:

```text
Chain INPUT (policy ACCEPT)
num  pkts bytes target prot source destination
```

No firewall rules remained in the INPUT chain.

### Retest Connectivity

From WSL:

```bash
nc -vz -w 3 192.168.170.128 9092
```

Result:

```text
Connection refused
```

### Conclusion

Removing the DROP rule restored normal TCP behavior.

Because no service was listening on port 9092, the server again actively refused the connection rather than silently dropping packets.

---

## TCP Connection Outcomes

| Scenario | Packet Behavior | Client Result |
|---|---|---|
| Service listening | SYN → SYN-ACK → ACK | Connected |
| No listener | SYN → RST-ACK | Connection refused |
| Firewall DROP | SYN → No response | Connection timeout |

These behaviors help narrow the possible causes of connectivity failures.

They do not, by themselves, establish the complete root cause.

---

## Troubleshooting Methodology

### 1. Verify Destination

Confirm the correct IP address and TCP port.

```bash
ip route get 192.168.170.128
```

### 2. Verify Listener

On the destination server:

```bash
sudo ss -lntp
```

Confirm the application is listening on the expected port and network interface.

### 3. Test TCP Connectivity

From the client:

```bash
nc -vz -w 3 192.168.170.128 9090
```

Identify whether the connection succeeds, is refused, or times out.

### 4. Capture Traffic at Both Endpoints

On the client:

```bash
sudo tcpdump -ni any 'host 192.168.170.128 and tcp port 9090'
```

On the server:

```bash
sudo tcpdump -ni any 'tcp port 9090'
```

Compare the packet captures to determine where communication breaks down.

### 5. Interpret the Results

- SYN leaves client but never reaches server: investigate routing, intermediate firewalls, and network infrastructure.
- SYN reaches server but no response leaves: investigate local firewall rules and TCP processing.
- SYN reaches server and RST returns: investigate listeners and firewall rejection.
- SYN-ACK leaves server but never reaches client: investigate return routing and intermediate firewalls.
- TCP handshake succeeds but application fails: investigate application logs, authentication, dependencies, and service health.

### 6. Verify Recovery

After making a correction:

1. Repeat the original connectivity test.
2. Verify application-level functionality.
3. Review logs and monitoring.
4. Confirm service recovery with affected users.
5. Document the root cause and corrective action.

---

## Key Takeaways

- TCP connectivity and application health are separate concerns.
- A successful TCP handshake does not prove the application is healthy.
- Connection refused commonly corresponds to a TCP reset.
- Connection timeout means the connection was not established within the allowed time.
- SYN retransmissions indicate that the client has not received an acceptable response.
- Packet captures help identify where communication breaks down.
- Local firewall rules can silently drop packets even when they reach the destination interface.
- Firewall counters provide additional evidence when diagnosing packet filtering.
- NAT can change the source address observed by the destination.
- Effective troubleshooting relies on isolating the fault domain through evidence rather than assumptions.

## Lab Outcome

Successfully reproduced and diagnosed:

- A working TCP connection
- A connection refused by the destination TCP stack
- A connection timeout caused by firewall packet drops
- Recovery after removing the firewall rule

All temporary firewall changes were removed, and normal TCP behavior was verified.
