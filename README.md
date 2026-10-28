# Exposure and Remediation Workbench

A defensive infrastructure project for assessing Linux configuration
weaknesses, documenting evidence, and verifying remediation without
breaking application functionality.

## Completed work

- Created a dedicated Ubuntu Server VM on a host-only network.
- Demonstrated unnecessary root execution in a static web service.
- Moved the service to a dedicated nonlogin account.
- Enabled systemd NoNewPrivileges.
- Verified the process identity and successful HTTP response after remediation.
- Examined SSH privilege separation as an example of legitimate root usage.
- Investigated a file-permission change that prevented the running service
  from serving its page, then restored access and verified the response.
- Built a read-only service assessment script that reports systemd state,
  the configured user, and the main process owner.
- Built a read-only file assessment script that reports ownership,
  numeric permissions, and permissions along the full path.
- Built a read-only network inventory script that reports interface
  addresses and TCP and UDP listeners.
- Built a collector that runs the checks over SSH, saves a local report,
  and continues collecting evidence when an individual check fails.

## Current scope

The first scenario was assessed and remediated manually.
Automated assessment and reporting are the next milestone.

The target VM was installed without applying package updates.
It contains only lab content and no production credentials.

The scenarios have been investigated manually.
Automated assessment and reporting are the next milestone.

## Scenarios

- [Service privileges](scenarios/service-privileges/README.md)
- [File permissions](scenarios/file-permissions/README.md)

## Service assessment script

Run the script from WSL against the lab VM:

```bash
ssh ilyam@192.168.170.128 'bash -s' < scripts/check-service.sh
```

The script defaults to `exposure-demo.service`. To check another service,
pass its name as an argument:

```bash
ssh ilyam@192.168.170.128 'bash -s -- ssh.service' < scripts/check-service.sh
```

The script collects evidence; it does not determine whether a service's
privileges are appropriate. It reports when the unit is not found or
when systemd has no main process recorded.

## File assessment script

From the project root, run the script against the lab VM:

```bash
ssh ilyam@192.168.170.128 'bash -s' < scripts/check-file.sh
```

The script defaults to `/opt/exposure-demo/index.html`. To inspect
another path on the VM, pass it as an argument:

```bash
ssh ilyam@192.168.170.128 \
  'bash -s -- /opt/exposure-demo' < scripts/check-file.sh
```

The script reports ownership and permissions. Assessing whether those
permissions are appropriate requires context about the file and its use.

## Network listener inventory

From the project root, run the script against the lab VM:

```bash
ssh ilyam@192.168.170.128 'bash -s' < scripts/check-listeners.sh
```

The script reports interface addresses and listening TCP and UDP
sockets. Process details may be incomplete when run without elevated
privileges. A listener alone does not establish external reachability;
routing, firewalls, and network configuration also matter.

## Collect an evidence report

From the project root, run with the lab defaults:

```bash
bash scripts/collect-report.sh
```

Or specify the SSH target, systemd service, and remote path:

```bash
bash scripts/collect-report.sh user@host ssh.service /tmp
```

Arguments are positional: target first, service second, and path third.
The collector accepts simple service names and paths containing letters,
numbers, underscores, periods, slashes, `@`, colons, and hyphens. Paths
containing spaces are not currently supported.

The collector saves output to `report.txt`, replacing the previous report.
It continues after an individual check fails and returns a nonzero exit
status if any check failed. Generated reports are excluded from Git.


## Networking Troubleshooting Lab

Completed a hands-on TCP connectivity troubleshooting lab using WSL Ubuntu and an Ubuntu VM.

Practiced:

- Inspecting TCP listeners and established connections with `ss`
- Capturing TCP handshakes and retransmissions using `tcpdump`
- Testing connectivity with `nc`
- Diagnosing connection refusals versus timeouts
- Creating and removing temporary firewall DROP rules using `iptables`
- Correlating packet captures with firewall counters
- Investigating routing and NAT behavior

Successfully reproduced and diagnosed three TCP connection outcomes: successful connection, connection refused, and connection timeout.

See [TCP Connectivity Troubleshooting Lab](docs/tcp-troubleshooting.md) for commands, observations, and troubleshooting methodology.
