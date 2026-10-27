#!/usr/bin/env bash

# Collect the configured user and current process for the demo service.
service="${1:-exposure-demo.service}"

load_state=$(systemctl show "$service" --property=LoadState --value)

if [ "$load_state" = "not-found" ]; then
    printf 'Error: service %s was not found.\n' "$service" >&2
    exit 1
fi

configured_user=$(systemctl show "$service" --property=User --value)
service_state=$(systemctl show "$service" --property=ActiveState --value)
service_pid=$(systemctl show "$service" --property=MainPID --value)

printf 'Service: %s\n' "$service"
if [ -z "$configured_user" ]; then
    printf 'Configured user: not explicitly set\n'
else
    printf 'Configured user: %s\n' "$configured_user"
fi

printf 'Active state: %s\n' "$service_state"

printf 'Main PID: %s\n' "$service_pid"

if [ "$service_pid" = "0" ]; then
    printf 'No main process is currently recorded for this service.\n'
else
    ps -p "$service_pid" -o user:20,pid,args
fi