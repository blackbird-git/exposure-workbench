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

From the project root, run:

```bash
bash scripts/collect-report.sh
```

The collector defaults to the lab VM. To specify another SSH target:

```bash
bash scripts/collect-report.sh user@host
```

The target must be accessible over SSH. The service and file checks
still use the demo service and path unless those scripts are changed.

The collector runs the service, file, and network checks over SSH and
writes the results to `report.txt`. It continues after an individual
check fails and returns a nonzero exit status if any check failed.

The current target is configured in the script. Each run replaces the
previous report. Generated reports are excluded from Git.