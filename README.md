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

## Current scope

The first scenario was assessed and remediated manually.
Automated assessment and reporting are the next milestone.

The target VM was installed without applying package updates.
It contains only lab content and no production credentials.

## Scenarios

- [Service privileges](scenarios/service-privileges/README.md)
