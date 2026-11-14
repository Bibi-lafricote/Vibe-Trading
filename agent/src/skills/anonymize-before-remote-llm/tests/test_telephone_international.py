"""Tests hors reseau ; phonenumbers requis. Non executes lors de la preparation."""
import importlib.util
from pathlib import Path
import unittest
import phonenumbers

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "telephone_international.py"
spec = importlib.util.spec_from_file_location("btc_lab_phones", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InternationalTests(unittest.TestCase):
    def test_international_examples(self):
        for country in ("FR", "IN", "GB", "DE", "US", "JP", "AU", "BR"):
            with self.subTest(country=country):
                number = phonenumbers.example_number(country)
                self.assertIsNotNone(number)
                text = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                self.assertEqual(module.masquer_telephones("Contact : " + text), ("Contact : [TEL]", 1))

    def test_following_price(self):
        self.assertEqual(module.masquer_telephones("+33 6 12 34 56 78 64000"), ("[TEL] 64000", 1))

    def test_national_region(self):
        self.assertEqual(module.masquer_telephones("06 12 34 56 78", "FR"), ("[TEL]", 1))

    def test_market_text(self):
        text = "BTC 64 000 dollars ; IBIT 12 500 000 euros ; 15 decembre 2026."
        self.assertEqual(module.masquer_telephones(text), (text, 0))

    def test_invalid_region(self):
        with self.assertRaises(ValueError):
            module.masquer_telephones("test", "XX")


if __name__ == "__main__":
    unittest.main()
