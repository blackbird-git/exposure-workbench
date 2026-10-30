#!/usr/bin/env python3

from pathlib import Path
import argparse

REQUIRED_SECTIONS = [
    "=== Service ===",
    "=== File permissions ===",
    "=== Network listeners ===",
]


def analyze_report(report_path):
    path = Path(report_path)

    if not path.is_file():
        raise FileNotFoundError(f"Report not found: {path}")

    report = path.read_text(encoding="utf-8")

    if not report.strip():
        raise ValueError("Report is empty")

    print("AI Infrastructure Operations Lab")
    print("=" * 35)
    print(f"Report: {path}")
    print(f"Size: {len(report)} characters")

    print("\nDiagnostic sections:")

    for section in REQUIRED_SECTIONS:
        status = "FOUND" if section in report else "MISSING"
        print(f"  [{status}] {section}")

    print("\nReport loaded successfully.")
    print("No commands executed. No data sent externally.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Read and validate infrastructure diagnostic reports"
    )
    parser.add_argument("report", help="Path to diagnostic report")

    args = parser.parse_args()
    analyze_report(args.report)
