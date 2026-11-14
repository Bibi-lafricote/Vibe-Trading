"""Lancement natif Vibe-Trading avec DeepSeek. Controle local par defaut."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

SETTINGS = {
    "LANGCHAIN_PROVIDER": "deepseek",
    "LANGCHAIN_MODEL_NAME": "deepseek-flash",
    "DEEPSEEK_BASE_URL": "https://api.deepseek.com/v1",
    "VIBE_TRADING_DEEPSEEK_ADAPTER": "native",
}


def load_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    path = Path.home() / ".openclaw" / "deepseek.key"
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("Cle locale absente ou fichier symbolique refuse")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise RuntimeError("Permissions de cle trop ouvertes")
    key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError("Cle vide")
    return key


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--start", action="store_true")
    args, remaining = parser.parse_known_args(argv)
    if remaining[:1] == ["--"]:
        remaining = remaining[1:]
    dependencies = {
        name: importlib.util.find_spec(name) is not None
        for name in ("cli", "langchain_deepseek", "phonenumbers")
    }
    if not args.start:
        if remaining:
            parser.error("arguments natifs autorises seulement avec --start")
        print(json.dumps({"mode": "local_check", "settings": SETTINGS,
            "dependencies": dependencies, "api_called": False}, indent=2))
        return 0 if all(dependencies.values()) else 1
    if not all(dependencies.values()):
        print("Dependances manquantes ; suivre btc-lab/README.fr.md", file=sys.stderr)
        return 1
    try:
        key = load_key()
    except (RuntimeError, OSError):
        print("Cle locale indisponible ; aucun secret affiche.", file=sys.stderr)
        return 1
    os.environ.update(SETTINGS)
    os.environ["DEEPSEEK_API_KEY"] = key
    # Pas de filtre de registre : fonctionnement natif conserve.
    sys.argv = ["vibe-trading", *remaining]
    from cli import main as native_main
    return native_main()


if __name__ == "__main__":
    raise SystemExit(main())
