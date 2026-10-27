#!/usr/bin/env bash

target="${1:-ilyam@192.168.170.128}"
service="${2:-exposure-demo.service}"
file="${3:-/opt/exposure-demo/index.html}"
report="report.txt"
failed=0

run_check() {
    local title="$1"
    local script="$2"
    local argument="${3:-}"

    printf '\n=== %s ===\n' "$title"

    if [[ -n "$argument" && ! "$argument" =~ ^[a-zA-Z0-9_./@:-]+$ ]]; then
        printf 'WARNING: unsupported characters in check argument.\n'
        failed=1
        return
    fi

    if ssh "$target" "bash -s -- $argument" < "$script"; then
        printf 'Check completed.\n'
    else
        printf 'WARNING: check failed.\n'
        failed=1
    fi
}

{
    printf 'Target: %s\n' "$target"
    printf 'Service requested: %s\n' "$service"
    printf 'Path requested: %s\n' "$file"
    run_check "Service" "scripts/check-service.sh" "$service"
    run_check "File permissions" "scripts/check-file.sh" "$file"
    run_check "Network listeners" "scripts/check-listeners.sh"

    if [ "$failed" -eq 0 ]; then
        printf '\nAll checks completed.\n'
    else
        printf '\nOne or more checks failed; review the report.\n'
    fi
} > "$report" 2>&1

printf 'Report saved to %s\n' "$report"
exit "$failed"