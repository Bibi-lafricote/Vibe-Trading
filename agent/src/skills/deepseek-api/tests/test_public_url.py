"""Tests de politique URL avec DNS simule ; aucun acces reseau."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "public_url.py"
spec = importlib.util.spec_from_file_location("btc_lab_public_url", SCRIPT)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class PublicUrlTests(unittest.TestCase):
    def test_rejected_urls(self):
        urls = [
            "https://localhost/private", "https://127.0.0.1/",
            "https://10.0.0.1/", "https://[::1]/", "https://[fe80::1]/",
            "https://router.local/", "https://a:b@example.com/",
            "http://example.com/", "https://example.com:8443/",
            "https://example.com/\nprivate",
        ]
        for url in urls:
            with self.subTest(url=url), self.assertRaises(ValueError):
                policy.validate_url(url)

    def test_public_dns(self):
        rows = [(2, 1, 6, "", ("8.8.8.8", 443))]
        with patch.object(policy.socket, "getaddrinfo", return_value=rows):
            self.assertEqual(policy.validate_url("https://example.com/page"), "https://example.com/page")

    def test_mixed_dns(self):
        rows = [(2, 1, 6, "", ("8.8.8.8", 443)), (2, 1, 6, "", ("10.0.0.1", 443))]
        with patch.object(policy.socket, "getaddrinfo", return_value=rows):
            with self.assertRaises(ValueError):
                policy.validate_url("https://example.com/")

    def test_dns_failure(self):
        with patch.object(policy.socket, "getaddrinfo", side_effect=OSError("fixture")):
            with self.assertRaises(ValueError):
                policy.validate_url("https://example.com/")


if __name__ == "__main__":
    unittest.main()
