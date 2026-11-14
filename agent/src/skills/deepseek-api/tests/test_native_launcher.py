"""Controle local du lanceur ; aucun import de la CLI native ni appel API."""
import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[5]
spec = importlib.util.spec_from_file_location("btc_lab_launcher", ROOT / "btc-lab" / "start.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class NativeLauncherTests(unittest.TestCase):
    def test_check_reports_flash_without_reading_key(self):
        output = io.StringIO()
        with patch.object(launcher.importlib.util, "find_spec", return_value=object()), patch.object(launcher, "load_key") as key, redirect_stdout(output):
            self.assertEqual(launcher.main(["--check"]), 0)
            key.assert_not_called()
        data = json.loads(output.getvalue())
        self.assertEqual(data["settings"]["LANGCHAIN_MODEL_NAME"], "deepseek-flash")
        self.assertFalse(data["api_called"])

    def test_check_does_not_change_provider(self):
        with patch.dict(os.environ, {"LANGCHAIN_PROVIDER": "fixture"}), patch.object(launcher.importlib.util, "find_spec", return_value=object()), redirect_stdout(io.StringIO()):
            launcher.main(["--check"])
            self.assertEqual(os.environ["LANGCHAIN_PROVIDER"], "fixture")

    def test_missing_dependencies_block_start_before_key(self):
        with patch.object(launcher.importlib.util, "find_spec", return_value=None), patch.object(launcher, "load_key") as key, redirect_stderr(io.StringIO()):
            self.assertEqual(launcher.main(["--start"]), 1)
            key.assert_not_called()

    def test_key_error_not_exposed(self):
        output = io.StringIO()
        with patch.object(launcher.importlib.util, "find_spec", return_value=object()), patch.object(launcher, "load_key", side_effect=RuntimeError("PRIVATE_FIXTURE")), redirect_stderr(output):
            self.assertEqual(launcher.main(["--start"]), 1)
        self.assertNotIn("PRIVATE_FIXTURE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
