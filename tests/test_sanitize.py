import unittest

from ai.sanitize import sanitize_report


class TestReportSanitizer(unittest.TestCase):

    def test_private_ipv4(self):
        report = (
            "Target: admin@192.168.1.10\n"
            "Server: 192.168.1.10\n"
        )
        result = sanitize_report(report)

        self.assertNotIn("192.168.1.10", result)
        self.assertEqual(result.count("<IPv4_1>"), 2)

    def test_preserve_network_semantics(self):
        report = (
            "LISTEN 127.0.0.1:8080\n"
            "LISTEN 0.0.0.0:22\n"
            "LISTEN [::1]:8080\n"
        )
        result = sanitize_report(report)

        self.assertIn("127.0.0.1:8080", result)
        self.assertIn("0.0.0.0:22", result)
        self.assertIn("[::1]:8080", result)

    def test_credentials(self):
        report = (
            "password=supersecret\n"
            "api_key: abc123\n"
            "token=xyz789\n"
        )
        result = sanitize_report(report)

        for secret in ("supersecret", "abc123", "xyz789"):
            self.assertNotIn(secret, result)

        self.assertEqual(result.count("<REDACTED>"), 3)

    def test_email(self):
        result = sanitize_report(
            "Contact: admin@example.com"
        )
        self.assertNotIn("admin@example.com", result)
        self.assertIn("<EMAIL_REDACTED>", result)

    def test_ipv6_link_local(self):
        result = sanitize_report(
            "Address: fe80::20c:29ff:fed1:a59b"
        )
        self.assertNotIn(
            "fe80::20c:29ff:fed1:a59b", result
        )
        self.assertIn("<IPv6_1>", result)

    def test_username(self):
        result = sanitize_report(
            "Target: ilyam@10.0.0.5\n"
            "Configured user: serviceuser\n"
        )
        self.assertNotIn("ilyam@", result)
        self.assertNotIn("serviceuser", result)

    def test_empty_report(self):
        self.assertEqual(sanitize_report(""), "")


if __name__ == "__main__":
    unittest.main()
