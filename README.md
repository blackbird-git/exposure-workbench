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