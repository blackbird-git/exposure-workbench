#!/usr/bin/env bash

file="${1:-/opt/exposure-demo/index.html}"

printf 'File: %s\n' "$file"

if stat -c 'Owner: %U | Group: %G | Permissions: %a' "$file"; then
    printf '\nPath permissions:\n'
    namei -l "$file"
else
    printf 'Unable to inspect path: %s\n' "$file" >&2
    exit 1
fi