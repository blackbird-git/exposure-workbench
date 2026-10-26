# Scenario 001: Unnecessary Root Execution

## Target

Ubuntu VM: exposure-target-01

Service: exposure-demo.service

Application: Python static HTTP server serving /opt/exposure-demo
on 127.0.0.1:8080.

## Finding and evidence

The original systemd unit omitted User=, defaulting to root.
Process inspection confirmed the application ran as root.

This service only needed to read static content and bind to
unprivileged port 8080. Root privileges were unnecessary.

Loopback binding limited network exposure but did not remove
the excessive process privilege.

## Remediation

Created the system account exposure-demo with no home directory
and a nologin shell.

Kept application files owned by root and readable by the service.

Added a systemd override:

    [Service]
    User=exposure-demo
    Group=exposure-demo
    NoNewPrivileges=true

Reloaded systemd and restarted the service.

## Verification

Observed:

- User=exposure-demo
- Group=exposure-demo
- NoNewPrivileges=yes
- ActiveState=active
- Application process owned by exposure-demo
- HTTP 200 from http://127.0.0.1:8080/

The first request immediately after restart was refused; a subsequent
request succeeded. This was consistent with startup timing.
ActiveState=active alone does not establish application readiness.

## False-positive consideration

SSH also had root-owned processes, but its privileged listener and
session privilege separation serve legitimate purposes.

Root execution alone is an observation, not sufficient evidence
of a vulnerability. Findings need service-specific context.

## Limitations

This verifies reduced execution privilege and basic HTTP functionality.
It does not establish that the application or host is fully secure.
