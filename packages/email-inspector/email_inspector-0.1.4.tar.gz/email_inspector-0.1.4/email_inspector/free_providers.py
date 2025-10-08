# email_inspector/free_providers.py
from __future__ import annotations
import json
import os
import re
from functools import lru_cache
from typing import Optional, Dict, Any
from pathlib import Path
import logging

log = logging.getLogger(__name__)

# optional dependency for MX lookups
try:
    import dns.resolver
except Exception:
    dns = None  # MX fallback will be disabled if dnspython not installed

_EMAIL_RE = re.compile(r"^[^@]+@([^@]+\.[^@]+)$")


def _parse_json_text(text: str) -> Dict[str, Any]:
    """
    Parse loaded JSON text and normalize to a dict mapping domain -> provider.
    The upstream list may be an object {domain:provider} or an array ["domain", ...].
    """
    data = json.loads(text)
    if isinstance(data, dict):
        # normalize keys and values
        return {k.lower(): (v if v is not None else k).lower() for k, v in data.items()}
    elif isinstance(data, list):
        return {str(item).lower(): str(item).lower() for item in data}
    else:
        raise ValueError("Unexpected JSON structure for free_providers.json")


def _load_resource_via_importlib_resources() -> Optional[Dict[str, Any]]:
    """Try stdlib importlib.resources (modern and older APIs)."""
    try:
        import importlib.resources as resources  # stdlib
    except Exception as e:
        log.debug("importlib.resources not available: %s", e)
        return None

    # modern API: resources.files(...)
    try:
        data_file = resources.files("email_inspector").joinpath("data").joinpath("free_providers.json")
        if data_file.is_file():
            text = data_file.read_text(encoding="utf-8")
            return _parse_json_text(text)
    except Exception as e:
        log.debug("importlib.resources.files() failed: %s", e)

    # older API: resources.read_text(package, resource)
    try:
        text = resources.read_text("email_inspector.data", "free_providers.json")
        return _parse_json_text(text)
    except Exception as e:
        log.debug("importlib.resources.read_text() failed: %s", e)

    return None


def _load_resource_via_backport() -> Optional[Dict[str, Any]]:
    """Try importlib_resources backport if installed (for older Pythons)."""
    try:
        import importlib_resources as resources  # backport
    except Exception as e:
        log.debug("importlib_resources backport not installed: %s", e)
        return None

    try:
        data_file = resources.files("email_inspector").joinpath("data").joinpath("free_providers.json")
        if data_file.is_file():
            text = data_file.read_text(encoding="utf-8")
            return _parse_json_text(text)
    except Exception as e:
        log.debug("importlib_resources.files() failed: %s", e)

    try:
        text = resources.read_text("email_inspector.data", "free_providers.json")
        return _parse_json_text(text)
    except Exception as e:
        log.debug("importlib_resources.read_text() failed: %s", e)

    return None


def _load_resource_via_pkgutil() -> Optional[Dict[str, Any]]:
    """Try pkgutil.get_data which works for zipped packages."""
    try:
        import pkgutil
        raw = pkgutil.get_data("email_inspector", "data/free_providers.json")
        if raw:
            return _parse_json_text(raw.decode("utf-8"))
    except Exception as e:
        log.debug("pkgutil.get_data failed: %s", e)
    return None


def _load_resource_via_filesystem() -> Optional[Dict[str, Any]]:
    """Direct filesystem fallback using the installed package location."""
    try:
        import email_inspector as pkg
        pkg_root = Path(pkg.__file__).resolve().parent
        candidate = pkg_root / "data" / "free_providers.json"
        if candidate.is_file():
            return _parse_json_text(candidate.read_text(encoding="utf-8"))

        # Extra fallback for odd install layouts
        candidate2 = Path(pkg.__file__).resolve().parent.parent / "email_inspector" / "data" / "free_providers.json"
        if candidate2.is_file():
            return _parse_json_text(candidate2.read_text(encoding="utf-8"))
    except Exception as e:
        log.debug("filesystem fallback failed: %s", e)
    return None


@lru_cache(maxsize=1)
def _load_free_domains() -> Dict[str, str]:
    """
    Load mapping {domain: provider_name} from packaged JSON file using robust fallbacks.
    Returns normalized dict with lowercase keys and provider names.
    Raises FileNotFoundError if resource not found.
    """
    loaders = (
        _load_resource_via_importlib_resources,
        _load_resource_via_backport,
        _load_resource_via_pkgutil,
        _load_resource_via_filesystem,
    )

    for loader in loaders:
        try:
            result = loader()
            if result:
                # ensure values are strings and lowercase
                normalized = {str(k).lower(): str(v).lower() for k, v in result.items()}
                return normalized
        except Exception as e:
            log.debug("loader %s raised error: %s", loader.__name__, e)

    # If all loaders failed, raise informative error
    raise FileNotFoundError(
        "free_providers.json resource not found for email_inspector. "
        "Tried importlib.resources, importlib_resources backport, pkgutil.get_data, and filesystem checks. "
        "Ensure package was built with include-package-data and that email_inspector/data/free_providers.json exists in the installed package."
    )


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
    return domain in _load_free_domains()


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
        if mx.endswith("gmail-smtp-in.l.google.com") or "google" in mx:
            return True
        if "outlook" in mx or "office365" in mx or "microsoft" in mx:
            return True
        if "yandex" in mx or "yahoo" in mx or "gmx" in mx:
            return True
    return False
