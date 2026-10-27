#!/usr/bin/env bash


printf 'Note: process details may be incomplete without elevated privileges.\n'

printf '\nNetwork interfaces:\n'
ip -br address

printf 'TCP:\n'
ss -ltnp

printf '\nUDP:\n'
ss -lunp