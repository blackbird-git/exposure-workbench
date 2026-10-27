#!/usr/bin/env bash

target="ilyam@192.168.170.128"
report="report.txt"
failed=0

run_check() {
    title="$1"
    script="$2"

    printf '\n=== %s ===\n' "$title"

    if ssh "$target" 'bash -s' < "$script"; then
        printf 'Check completed.\n'
    else
        printf 'WARNING: check failed.\n'
        failed=1
    fi
}

{
    run_check "Service" "scripts/check-service.sh"
    run_check "File permissions" "scripts/check-file.sh"
    run_check "Network listeners" "scripts/check-listeners.sh"

    if [ "$failed" -eq 0 ]; then
        printf '\nAll checks completed.\n'
    else
        printf '\nOne or more checks failed; review the report.\n'
    fi
} > "$report" 2>&1

printf 'Report saved to %s\n' "$report"
exit "$failed"