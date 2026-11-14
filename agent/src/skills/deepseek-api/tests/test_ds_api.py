"""Tests du client sans reseau, sans cle et sans dependance phonenumbers."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ds_api.py"
spec = importlib.util.spec_from_file_location("btc_lab_ds_api", SCRIPT)
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.transport = patch.object(client, "request", return_value={"status": "completed"})
        self.request = self.transport.start()
        self.addCleanup(self.transport.stop)

    def test_ask_sends_masked_text(self):
        with patch.object(client, "sanitize", return_value=("[EMAIL]", 1)):
            client.execute("ask", "test@example.com")
        path, payload = self.request.call_args.args
        self.assertEqual(path, "/responses")
        self.assertEqual(payload["input"], "[EMAIL]")
        self.assertEqual(payload["model"], "deepseek-flash")

    def test_filter_failure_blocks_request(self):
        with patch.object(client, "sanitize", side_effect=RuntimeError("filter unavailable")):
            with self.assertRaises(RuntimeError):
                client.execute("search", "public query")
        self.request.assert_not_called()

    def test_mutations_refused(self):
        for action in ("upload", "delete"):
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    client.execute("files", action=action)
        self.request.assert_not_called()

    def test_sensitive_url_refused(self):
        with patch.object(client, "sanitize", return_value=("[URL_JETON]", 1)):
            with self.assertRaises(ValueError):
                client.execute("fetch", "https://example.com/?token=test")
        self.request.assert_not_called()

    def test_models(self):
        client.execute("models")
        self.request.assert_called_once_with("/models")

    def test_long_search_refused(self):
        with patch.object(client, "sanitize", return_value=("x" * 129, 0)):
            with self.assertRaises(ValueError):
                client.execute("search", "x" * 129)
        self.request.assert_not_called()

    def test_fim_sensitive_code_refused(self):
        with patch.object(client, "sanitize", return_value=("[CLE_API]", 1)):
            with self.assertRaises(ValueError):
                client.execute("fim", "sensitive fixture")
        self.request.assert_not_called()

    def test_file_metadata(self):
        client.execute("files", action="get", file_id="file-api-example")
        self.request.assert_called_once_with("/files/file-api-example")


if __name__ == "__main__":
    unittest.main()
