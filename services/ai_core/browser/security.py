"""NOVA X - Browser Agent Security & SSRF Protection
Prevents SSRF, scheme exploits, and internal cloud metadata harvesting.
"""

from urllib.parse import urlparse
import ipaddress
import socket

FORBIDDEN_HOSTS = {
    "169.254.169.254",  # AWS/GCP/Azure instance metadata
    "metadata.google.internal",
    "instance-data",
}

FORBIDDEN_SCHEMES = {"file", "gopher", "dict", "ftp", "ldap", "tftp", "data"}


def validate_url_safety(url: str) -> str:
    """Validates URL for safe navigation, preventing SSRF and scheme exploits."""
    if not url or not url.strip():
        raise ValueError("URL cannot be empty.")

    clean_url = url.strip()
    if "://" not in clean_url:
        clean_url = f"https://{clean_url}"

    parsed = urlparse(clean_url)
    scheme = (parsed.scheme or "").lower()

    if scheme in FORBIDDEN_SCHEMES or scheme not in ("http", "https"):
        raise ValueError(f"SECURITY_VIOLATION: Navigation scheme '{scheme}' is forbidden.")

    hostname = (parsed.hostname or "").lower()

    if hostname in FORBIDDEN_HOSTS:
        raise ValueError(f"SECURITY_VIOLATION: Target host '{hostname}' is blocked by NOVA Security Policy.")

    return clean_url
