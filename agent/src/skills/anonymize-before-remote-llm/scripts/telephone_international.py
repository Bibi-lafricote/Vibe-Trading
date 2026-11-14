"""Masquage local des telephones ; pas une anonymisation exhaustive."""


def masquer_telephones(texte, region=None):
    """Retourne (texte masque, nombre). Aucun repli silencieux sans dependance."""
    try:
        import phonenumbers
    except ImportError as exc:
        raise RuntimeError("Installer phonenumbers avant tout envoi distant.") from exc
    if not isinstance(texte, str):
        raise TypeError("texte doit etre une chaine")
    if region is not None:
        region = region.strip().upper()
        if region not in phonenumbers.SUPPORTED_REGIONS:
            raise ValueError("region telephonique non reconnue")
    matches = list(phonenumbers.PhoneNumberMatcher(
        texte, region, leniency=phonenumbers.Leniency.VALID, max_tries=1000
    ))
    for match in reversed(matches):
        texte = texte[:match.start] + "[TEL]" + texte[match.end:]
    return texte, len(matches)
