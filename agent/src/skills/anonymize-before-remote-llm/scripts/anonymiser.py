"""Masquage heuristique local. Ne garantit pas une anonymisation exhaustive."""
import argparse
import re
from pathlib import Path
from telephone_international import masquer_telephones

RULES = [
    ("URL_JETON", r"https?://[^\s]*(?:token|key=|secret|sig=|api_key=)[^\s]*", re.I),
    ("EMAIL", r"[\w.+-]+@[\w-]+\.[\w.]{2,}", 0),
    ("CLE_API", r"\b(?:sk-|pk_live_|sk_live_|ghp_|github_pat_|xox[baprs]-|AKIA)[A-Za-z0-9_-]{10,}", 0),
    ("MOT_DE_PASSE", r"(?:mot\s+de\s+passe|password|passwd)\s*[:=]\s*\S+", re.I),
    ("NAISSANCE", r"(?:n[eé]e?\s+le|date\s+de\s+naissance)\s*:?\s*\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}", re.I),
    ("SECU", r"(?<!\d)[12][ .-]?\d{2}[ .-]?\d{2}[ .-]?\d{2}[ .-]?\d{3}[ .-]?\d{3}(?:[ .-]?\d{2})?(?!\d)", 0),
    ("PLAQUE", r"\b[A-Z]{2}[- ]\d{3}[- ][A-Z]{2}\b", 0),
    ("IBAN", r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b", 0),
    ("IP", r"\b(?:\d{1,3}\.){3}\d{1,3}\b", 0),
    ("CHEMIN", r"/(?:Users|home)/[A-Za-z0-9._-]+(?:/[^\s]*)?", 0),
    ("ADRESSE", r"\b\d{1,4} +(?:rue|avenue|boulevard|impasse|chemin|all[ée]e) +[A-Za-zÀ-ſ' -]{3,40}", re.I),
]
COMPILED = [(name, re.compile(pattern, flags)) for name, pattern, flags in RULES]
CARD = re.compile(r"(?<!\d)\d(?:[\d -]*\d)?(?!\d)")


def _luhn(digits):
    total = 0
    for index, digit in enumerate(reversed(digits)):
        value = int(digit)
        if index % 2:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def anonymiser(texte, region=None):
    if not isinstance(texte, str):
        raise TypeError("texte doit etre une chaine")
    total = 0
    for name, pattern in COMPILED:
        texte, count = pattern.subn("[" + name + "]", texte)
        total += count
    texte, count = masquer_telephones(texte, region)
    total += count

    def replace_card(match):
        nonlocal total
        digits = re.sub(r"\D", "", match.group())
        if 13 <= len(digits) <= 16 and len(set(digits)) > 1 and _luhn(digits):
            total += 1
            return "[CARTE]"
        return match.group()

    return CARD.sub(replace_card, texte), total


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--region", default=None, help="Pays des numeros nationaux, ex. FR ou IN")
    args = parser.parse_args(argv)
    source = args.source.expanduser()
    if source.name.endswith(".anonymise.txt"):
        parser.error("refus de retraiter une copie anonymisee")
    text, count = anonymiser(source.read_text(encoding="utf-8"), args.region)
    destination = source.with_name(source.stem + ".anonymise.txt")
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(text)
    print("masquages :", count)
    print("fichier :", destination.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
