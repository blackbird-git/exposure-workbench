"""Tests for local AI report analysis; no Ollama service required."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ai.analyze import REQUIRED_SECTIONS, analyze_report
from ai.ollama_client import OllamaError, analyze_with_ollama, validate_findings, validate_local_url

SAMPLE_REPORT = "\n".join(REQUIRED_SECTIONS) + "\nTarget: alice@192.168.1.10\nLISTEN 127.0.0.1:8080\n"
RESULT = {
    "summary": "Loopback listener observed; remote access requirements unknown.",
    "findings": [{
        "title": "Loopback binding", "severity": "info", "confidence": "high",
        "evidence": "127.0.0.1:8080", "interpretation": "Accessible locally; may be intentional.",
        "verification_steps": ["ss -ltn", "curl -I http://127.0.0.1:8080"],
    }],
}


class LocalAITests(unittest.TestCase):
    def test_local_url(self):
        self.assertEqual(validate_local_url("http://127.0.0.1:11434"), "http://127.0.0.1:11434")
        for url in ("https://127.0.0.1:11434", "http://localhost:11434", "http://8.8.8.8:11434", "http://127.0.0.1:11434/evil"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_local_url(url)

    def test_schema_validation(self):
        self.assertEqual(validate_findings(RESULT), RESULT)
        with self.assertRaises(OllamaError):
            validate_findings({"summary": "x", "findings": [{"title": "missing fields"}]})

    def test_sanitized_before_request(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.txt"
            report_path.write_text(SAMPLE_REPORT, encoding="utf-8")
            with patch("ai.analyze.analyze_with_ollama", return_value=RESULT) as mocked:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(analyze_report(report_path, ai=True), RESULT)
            sent = mocked.call_args.args[0]
            self.assertNotIn("192.168.1.10", sent)
            self.assertIn("127.0.0.1:8080", sent)

    def test_default_mode_does_not_call_ai(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.txt"
            report_path.write_text(SAMPLE_REPORT, encoding="utf-8")
            with patch("ai.analyze.analyze_with_ollama") as mocked:
                with contextlib.redirect_stdout(io.StringIO()):
                    analyze_report(report_path)
            mocked.assert_not_called()

    def test_missing_sections_block_ai(self):
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory) / "report.txt"
            report_path.write_text("=== Service ===\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                analyze_report(report_path, ai=True, json_output=True)

    def test_api_request_uses_structured_output(self):
        response = json.dumps({"message": {"content": json.dumps(RESULT)}}).encode()
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self, *_): return response
        class FakeOpener:
            def open(self, request, timeout):
                payload = json.loads(request.data)
                self_test.assertFalse(payload["stream"])
                self_test.assertFalse(payload["think"])
                self_test.assertIn("format", payload)
                return FakeResponse()
        self_test = self
        with patch("ai.ollama_client.urllib.request.build_opener", return_value=FakeOpener()):
            self.assertEqual(analyze_with_ollama(SAMPLE_REPORT), RESULT)

    def test_malformed_response(self):
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self, *_): return b"not-json"
        class FakeOpener:
            def open(self, request, timeout): return FakeResponse()
        with patch("ai.ollama_client.urllib.request.build_opener", return_value=FakeOpener()):
            with self.assertRaises(OllamaError):
                analyze_with_ollama(SAMPLE_REPORT)


if __name__ == "__main__":
    unittest.main()
