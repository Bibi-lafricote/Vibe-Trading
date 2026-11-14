"""Controle local d'URL. Ne garantit pas la resolution DNS du service distant."""
import ipaddress
import socket
import urllib.parse


def validate_url(value):
    if not isinstance(value, str) or not value or any(ord(c) <= 32 or ord(c) == 127 for c in value) or "\\" in value:
        raise ValueError("URL invalide")
    url = urllib.parse.urlsplit(value)
    if url.scheme != "https" or not url.hostname or url.username is not None or url.password is not None or url.port not in (None, 443):
        raise ValueError("HTTPS sans identifiants, port 443 exige")
    host = url.hostname.rstrip(".").encode("idna").decode("ascii").lower()
    if "%" in host or host == "localhost" or host.endswith((".localhost", ".local", ".internal", ".home.arpa")) or ("." not in host and ":" not in host):
        raise ValueError("Hote local refuse")
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            rows = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError("Resolution impossible") from exc
        addresses = [ipaddress.ip_address(row[4][0]) for row in rows]
    if not addresses or any(not address.is_global or address.is_multicast or address.is_unspecified for address in addresses):
        raise ValueError("Adresse non publique refusee")
    return value
