#!/usr/bin/env python3
"""Sanitize infrastructure reports before AI-assisted analysis.

This is a defense-in-depth tool, not a guarantee of anonymization.
Review sanitized reports before sharing them externally.
"""

import argparse
import ipaddress
import re
from pathlib import Path


IPV4_PATTERN = re.compile(
    r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])"
)

IPV6_PATTERN = re.compile(
    r"(?<![\w:])(?:[0-9a-fA-F]{0,4}:){2,}"
    r"[0-9a-fA-F:.%]*"
)

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

SECRET_PATTERN = re.compile(
    r"(?im)^(\s*(?:password|passwd|token|api[_-]?key|"
    r"secret|authorization|access[_-]?key)\s*[:=]\s*)"
    r"(.+)$"
)

TARGET_PATTERN = re.compile(
    r"(?m)^(\s*Target:\s*)([A-Za-z_][\w.-]*)@"
)

USER_PATTERN = re.compile(
    r"(?m)^(\s*Configured user:\s*)(\S+)"
)

HOSTNAME_PATTERN = re.compile(
    r"(?im)^(\s*(?:hostname|host name|fqdn)\s*[:=]\s*)(\S+)"
)


class ReportSanitizer:
    def __init__(self):
        self.addresses = {}
        self.users = {}
        self.hostnames = {}

    def sanitize_ip(self, address):
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return address

        # These addresses carry important diagnostic meaning.
        if ip.is_loopback or ip.is_unspecified:
            return address

        # Preserve public addresses for now, but flag this limitation
        # in documentation and review before external transmission.
        if ip.is_global:
            return address

        key = str(ip)

        if key not in self.addresses:
            family = "IPv4" if ip.version == 4 else "IPv6"
            count = sum(
                1 for value in self.addresses.values()
                if value.startswith(f"<{family}_")
            )
            self.addresses[key] = f"<{family}_{count + 1}>"

        return self.addresses[key]

    def sanitize_user(self, username):
        if username in {"root", "nobody"}:
            return username

        if username not in self.users:
            self.users[username] = f"<USER_{len(self.users) + 1}>"

        return self.users[username]

    def sanitize_hostname(self, hostname):
        if hostname in {"localhost", "localhost.localdomain"}:
            return hostname

        if hostname not in self.hostnames:
            self.hostnames[hostname] = (
                f"<HOST_{len(self.hostnames) + 1}>"
            )

        return self.hostnames[hostname]

    def sanitize(self, report):
        # Redact secrets before processing other content.
        report = SECRET_PATTERN.sub(
            lambda m: m.group(1) + "<REDACTED>",
            report,
        )

        report = EMAIL_PATTERN.sub("<EMAIL_REDACTED>", report)

        report = TARGET_PATTERN.sub(
            lambda m: m.group(1)
            + self.sanitize_user(m.group(2))
            + "@",
            report,
        )

        report = USER_PATTERN.sub(
            lambda m: m.group(1)
            + self.sanitize_user(m.group(2)),
            report,
        )

        report = HOSTNAME_PATTERN.sub(
            lambda m: m.group(1)
            + self.sanitize_hostname(m.group(2)),
            report,
        )

        report = IPV4_PATTERN.sub(
            lambda m: self.sanitize_ip(m.group()),
            report,
        )

        report = IPV6_PATTERN.sub(
            lambda m: self.sanitize_ip(m.group()),
            report,
        )

        return report


def sanitize_report(report):
    return ReportSanitizer().sanitize(report)


def main():
    parser = argparse.ArgumentParser(
        description="Sanitize infrastructure diagnostic reports"
    )
    parser.add_argument("report", help="Path to diagnostic report")
    args = parser.parse_args()

    try:
        report = Path(args.report).read_text(encoding="utf-8")
        if not report.strip():
            raise ValueError("Empty report")
    except (OSError, UnicodeError, ValueError):
        parser.exit(1, "Unable to read a valid report.\n")

    print(sanitize_report(report), end="")


if __name__ == "__main__":
    main()
