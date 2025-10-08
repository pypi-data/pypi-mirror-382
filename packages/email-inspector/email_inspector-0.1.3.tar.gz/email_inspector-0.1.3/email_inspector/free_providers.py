# email_inspector/free_providers.py
from __future__ import annotations
import json
import os
import re
from functools import lru_cache
from typing import Optional
from importlib import resources


try:
    # optional dependency for MX lookups
    import dns.resolver
except Exception:
    dns = None  # MX fallback will be disabled if dnspython not installed

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "free_providers.json")

_EMAIL_RE = re.compile(r"^[^@]+@([^@]+\.[^@]+)$")

@lru_cache(maxsize=4096)
def _load_free_domains() -> dict:
    """Load mapping {domain: provider_name} from packaged JSON file."""
    with resources.open_text("email_inspector.data", "free_providers.json") as f:
        return json.load(f)
    # ensure lowercase keys
    return {k.lower(): v for k, v in data.items()}

def _extract_domain(email_or_domain: str) -> Optional[str]:
    m = _EMAIL_RE.match(email_or_domain)
    if m:
        return m.group(1).lower()
    # if it looks like a domain already, normalize
    if "." in email_or_domain and " " not in email_or_domain:
        return email_or_domain.strip().lower()
    return None

def is_free_domain(domain: str) -> bool:
    """Return True if domain is in the bundled free-provider list."""
    domain = _extract_domain(domain)
    if not domain:
        return False
    return domain in _load_free_domains()

def is_free_email(email: str) -> bool:
    """Return True if the email belongs to a known free/public provider."""
    domain = _extract_domain(email)
    if not domain:
        return False
    if domain in _load_free_domains():
        return True
    return False

def get_provider(domain_or_email: str) -> Optional[str]:
    """Return provider name for domain (e.g. 'gmail') or None if unknown."""
    domain = _extract_domain(domain_or_email)
    if not domain:
        return None
    return _load_free_domains().get(domain)

def mx_indicates_free(domain_or_email: str) -> bool:
    """
    Optional fallback: perform an MX lookup and try to infer if mail is hosted
    by a consumer provider (Google, Microsoft, Yandex, etc.). Requires dnspython.
    """
    if dns is None:
        raise RuntimeError("dnspython is required for MX checks (pip install dnspython)")

    domain = _extract_domain(domain_or_email)
    if not domain:
        return False
    try:
        answers = dns.resolver.resolve(domain, "MX")
    except Exception:
        return False
    for r in answers:
        mx = str(r.exchange).lower()
        # simple heuristics
        if mx.endswith("gmail-smtp-in.l.google.com"):
            return True
        if "outlook" in mx or "office365" in mx or "microsoft" in mx:
            return True
        if "yandex" in mx or "yahoo" in mx or "gmx" in mx:
            return True
    return False
