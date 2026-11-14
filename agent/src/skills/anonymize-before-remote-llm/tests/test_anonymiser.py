"""Integration du vrai filtre ; dependance phonenumbers requise ; fixtures fictives."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
import io

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("btc_lab_complete_anonymizer", SCRIPTS / "anonymiser.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AnonymizerTests(unittest.TestCase):
    def test_public_market_data_unchanged(self):
        text = "Michael Saylor : BTC 64 000 dollars ; IBIT 12 500 000 euros ; 15 decembre 2026."
        self.assertEqual(module.anonymiser(text), (text, 0))

    def test_phone_preserves_following_price(self):
        self.assertEqual(module.anonymiser("+33 6 12 34 56 78 64000"), ("[TEL] 64000", 1))

    def test_email_and_api_key(self):
        masked, count = module.anonymiser("test@example.com ; sk-FAKEONLY12345678901234567890")
        self.assertEqual(masked, "[EMAIL] ; [CLE_API]")
        self.assertEqual(count, 2)

    def test_birth_social_and_plate(self):
        masked, count = module.anonymiser("Ne le 12/03/1985 ; 1 85 03 75 123 456 78 ; AB-123-CD")
        self.assertEqual(masked, "[NAISSANCE] ; [SECU] ; [PLAQUE]")
        self.assertEqual(count, 3)

    def test_card(self):
        self.assertEqual(module.anonymiser("Carte: 4532 0151 1283 0366."), ("Carte: [CARTE].", 1))

    def test_original_preserved_and_exclusive_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "fixture.txt"
            source.write_text("test@example.com", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                module.main([str(source)])
            self.assertEqual(source.read_text(encoding="utf-8"), "test@example.com")
            self.assertEqual(source.with_name("fixture.anonymise.txt").read_text(encoding="utf-8"), "[EMAIL]")
            with self.assertRaises(FileExistsError), redirect_stdout(io.StringIO()):
                module.main([str(source)])


if __name__ == "__main__":
    unittest.main()
