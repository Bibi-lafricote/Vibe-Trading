"""Client DeepSeek btc-lab. Integration preparatoire ; aucun outil de courtier."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.deepseek.com"


def sanitize(text, region=None):
    folder = Path(__file__).resolve().parents[2] / "anonymize-before-remote-llm" / "scripts"
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
    from anonymiser import anonymiser
    return anonymiser(text, region)


def validate_fetch_url(text):
    path = Path(__file__).resolve().with_name("public_url.py")
    spec = importlib.util.spec_from_file_location("btc_lab_url_policy", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Politique URL indisponible")
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    return policy.validate_url(text)


def api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        path = Path.home() / ".openclaw" / "deepseek.key"
        if path.is_symlink():
            raise RuntimeError("Fichier de cle symbolique refuse")
        if not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise RuntimeError("Cle absente ou permissions trop ouvertes ; fichier local exige en 600")
        key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError("Cle DeepSeek absente")
    return key


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Redirection HTTP refusee")


def request(path, payload=None):
    # Aucun endpoint libre ni serveur configurable dans ce client.
    allowed = {"/models", "/user/balance", "/v1/tools/search", "/v1/tools/fetch", "/responses", "/beta/completions", "/files?limit=20&order=desc"}
    if path not in allowed and not (path.startswith("/files/") and path[7:].startswith("file-")):
        raise ValueError("Endpoint refuse")
    req = urllib.request.Request(BASE + path,
        data=None if payload is None else json.dumps(payload).encode("utf-8"),
        headers={"Authorization": "Bearer " + api_key(), "Content-Type": "application/json"},
        method="GET" if payload is None else "POST")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("Erreur HTTP %s ; corps masque" % exc.code) from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("Erreur reseau ; details masques") from None
    if not isinstance(result, dict):
        raise RuntimeError("Reponse API inattendue")
    if result.get("error") or result.get("status") == "failed":
        raise RuntimeError("Echec API ; details masques")
    return result


def execute(command, text="", region=None, count=5, action="list", file_id=None):
    if command == "files":
        if action not in {"list", "get"}:
            raise ValueError("Envoi et suppression de fichiers desactives")
        if action == "list":
            return request("/files?limit=20&order=desc")
        if not file_id or not file_id.startswith("file-"):
            raise ValueError("Identifiant fichier invalide")
        return request("/files/" + urllib.parse.quote(file_id, safe=""))
    if command in {"models", "balance"}:
        return request("/models" if command == "models" else "/user/balance")
    if command not in {"search", "fetch", "ask", "fim"}:
        raise ValueError("Commande inconnue")
    clean, masked = sanitize(text, region)
    if not clean.strip():
        raise ValueError("Texte vide")
    if command == "search":
        if len(clean) > 128 or not 1 <= count <= 50:
            raise ValueError("Recherche : 128 caracteres maximum, count entre 1 et 50")
        return request("/v1/tools/search", {"query": clean, "count": count})
    if command == "fetch":
        if masked:
            raise ValueError("URL sensible refusee")
        validated = validate_fetch_url(text)
        return request("/v1/tools/fetch", {"url": validated})
    if command == "fim":
        if masked:
            raise ValueError("Code contenant des donnees sensibles : revision locale requise")
        return request("/beta/completions", {"model": "deepseek-flash", "prompt": clean, "max_tokens": 128})
    return request("/responses", {"model": "deepseek-flash", "input": clean,
        "tools": [{"type": "deepseek_web_search"}, {"type": "deepseek_read_url"}],
        "reasoning": {"effort": "low"}, "max_output_tokens": 1200})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["search", "fetch", "ask", "models", "balance", "fim", "files"])
    parser.add_argument("text", nargs="?", default="")
    parser.add_argument("--region")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--id", dest="file_id")
    args = parser.parse_args(argv)
    try:
        result = execute(args.command, args.text, args.region, args.count,
            action=args.text or "list", file_id=args.file_id)
    except (RuntimeError, ValueError, OSError, ImportError):
        print("Echec local ou distant ; aucune nouvelle tentative automatique. Verifier localement sans journaliser les secrets.", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
