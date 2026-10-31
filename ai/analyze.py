#!/usr/bin/env python3
"""Validate infrastructure reports and optionally request local AI analysis."""

import argparse
import json
from pathlib import Path

try:
    from .ollama_client import OllamaError, analyze_with_ollama
    from .sanitize import sanitize_report
except ImportError:
    from ollama_client import OllamaError, analyze_with_ollama
    from sanitize import sanitize_report

REQUIRED_SECTIONS = [
    "=== Service ===",
    "=== File permissions ===",
    "=== Network listeners ===",
]


def analyze_report(report_path, *, ai=False, model="qwen3:4b", json_output=False):
    path = Path(report_path)
    if not path.is_file():
        raise FileNotFoundError(f"Report not found: {path}")
    report = path.read_text(encoding="utf-8")
    if not report.strip():
        raise ValueError("Report is empty")
    missing = [section for section in REQUIRED_SECTIONS if section not in report]

    if not json_output:
        print("AI Infrastructure Operations Lab")
        print("=" * 35)
        print(f"Report: {path}")
        print(f"Size: {len(report)} characters")
        print("\nDiagnostic sections:")
        for section in REQUIRED_SECTIONS:
            print(f"  [{'MISSING' if section in missing else 'FOUND'}] {section}")

    if not ai:
        if json_output:
            print(json.dumps({"report": str(path), "missing_sections": missing}, indent=2))
        else:
            print("\nReport loaded successfully.")
            print("No commands executed. No data sent externally.")
        return None

    if missing:
        raise ValueError("AI analysis requires all diagnostic sections; missing: " + ", ".join(missing))

    sanitized = sanitize_report(report)
    findings = analyze_with_ollama(sanitized, model=model)
    if json_output:
        print(json.dumps(findings, indent=2))
    else:
        print("\nLocal AI analysis (advisory; verify before acting)")
        print("=" * 47)
        print(findings["summary"])
        for i, item in enumerate(findings["findings"], 1):
            print(f"\n{i}. {item['title']} [{item['severity']}; confidence: {item['confidence']}]")
            print(f"   Evidence: {item['evidence']}")
            print(f"   Interpretation: {item['interpretation']}")
            for step in item["verification_steps"]:
                print(f"   Verify: {step}")
        print("\nNo commands executed. Report sent only to local Ollama.")
    return findings


def main():
    parser = argparse.ArgumentParser(description="Validate diagnostic reports and optionally analyze them with local Ollama")
    parser.add_argument("report", help="Path to diagnostic report")
    parser.add_argument("--ai", action="store_true", help="Analyze report with local Ollama")
    parser.add_argument("--model", default="qwen3:4b", help="Installed Ollama model (default: qwen3:4b)")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()
    try:
        analyze_report(args.report, ai=args.ai, model=args.model, json_output=args.json)
    except (OSError, UnicodeError, ValueError, OllamaError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
