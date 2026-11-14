"""Integration client/politique URL avec filtre et transport simules."""
import importlib.util
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ds_api.py"
spec = importlib.util.spec_from_file_location("btc_lab_fetch_client", SCRIPT)
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class FetchPolicyIntegrationTests(unittest.TestCase):
    def test_localhost_never_reaches_transport(self):
        url = "https://localhost/private"
        with patch.object(client, "sanitize", return_value=(url, 0)), patch.object(client, "request") as transport:
            with self.assertRaises(ValueError):
                client.execute("fetch", url)
            transport.assert_not_called()

    def test_private_ip_never_reaches_transport(self):
        url = "https://10.0.0.1/private"
        with patch.object(client, "sanitize", return_value=(url, 0)), patch.object(client, "request") as transport:
            with self.assertRaises(ValueError):
                client.execute("fetch", url)
            transport.assert_not_called()

    def test_private_dns_never_reaches_transport(self):
        url = "https://example.com/private"
        rows = [(2, 1, 6, "", ("10.0.0.1", 443))]
        with patch.object(client, "sanitize", return_value=(url, 0)), patch.object(client, "request") as transport, patch.object(socket, "getaddrinfo", return_value=rows):
            with self.assertRaises(ValueError):
                client.execute("fetch", url)
            transport.assert_not_called()

    def test_public_dns_reaches_mock_transport(self):
        url = "https://example.com/page"
        rows = [(2, 1, 6, "", ("8.8.8.8", 443))]
        with patch.object(client, "sanitize", return_value=(url, 0)), patch.object(client, "request", return_value={}) as transport, patch.object(socket, "getaddrinfo", return_value=rows):
            client.execute("fetch", url)
            transport.assert_called_once_with("/v1/tools/fetch", {"url": url})


if __name__ == "__main__":
    unittest.main()
