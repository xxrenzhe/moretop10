"""Affiliate CTA URL rules for MoreTop10 Check price links.

Hard lock (2026-10-22):
  - PartnerBoost (`pboost.me`): keep ensuring `uid=fromsll`.
  - YeahPromos / Amazon maas / any non-pboost track: pass through **unchanged**.
    Never append `uid`, `subid`, or site params.
  - Refuse a bake only when the track is empty or the host is unusable.
    Missing uid is **not** a refuse reason (YP tracks have no uid).
"""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

PB_UID = "fromsll"
PB_HOSTS = frozenset({"pboost.me", "www.pboost.me"})
YP_HOSTS = frozenset(
    {
        "yeahpromos.com",
        "www.yeahpromos.com",
        "maas.yeahpromos.com",
    }
)
AMAZON_MAAS_HOSTS = frozenset(
    {
        "www.amazon.com",
        "amazon.com",
        "amzn.to",
        "www.amzn.to",
        "smile.amazon.com",
    }
)

# Hosts we will bake a Check price CTA for. Empty / relative / unknown = no CTA
# (never invent a hop). Wrong-host refuse is for bake validators, not uid.
ALLOWED_TRACK_HOSTS = PB_HOSTS | YP_HOSTS | AMAZON_MAAS_HOSTS


class AffiliateTrackError(ValueError):
    """Track is empty or the host is not a usable affiliate hop."""


def _host(url: str) -> str:
    return (urlparse(url).netloc or "").lower()


def classify_network(url: str, network: str | None = None) -> str:
    """Return `pb` or `yp` (yp = any non-pboost track we pass through)."""
    hint = (network or "").strip().lower()
    if hint in {"pb", "partnerboost"}:
        return "pb"
    if hint in {"yp", "yeahpromos", "maas"}:
        return "yp"
    host = _host(url)
    if host in PB_HOSTS or host.endswith(".pboost.me"):
        return "pb"
    return "yp"


def is_empty_track(url: str | None) -> bool:
    raw = (url or "").strip()
    return raw in {"", "#", "about:blank", "javascript:void(0)"}


def is_allowed_track_host(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = (parsed.netloc or "").lower()
    if host in ALLOWED_TRACK_HOSTS:
        return True
    if host.endswith(".pboost.me") or host.endswith(".yeahpromos.com"):
        return True
    return False


def ensure_affiliate_uid(url: str, network: str | None = None) -> str:
    """Apply uid only on PartnerBoost pboost.me hops.

    YP / Amazon maas / any other allowed track is returned byte-for-byte.
    """
    if is_empty_track(url):
        raise AffiliateTrackError("empty track")
    raw = url.strip()
    if not is_allowed_track_host(raw):
        raise AffiliateTrackError(f"wrong-host track: {_host(raw) or '(none)'}")

    if classify_network(raw, network) != "pb":
        return raw

    parsed = urlparse(raw)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    filtered = [(k, v) for k, v in pairs if k.lower() != "uid"]
    filtered.append(("uid", PB_UID))
    new_query = urlencode(filtered)
    return urlunparse(parsed._replace(query=new_query))


def prepare_affiliate_link(url: str | None, network: str | None = None) -> str | None:
    """CTA href or None when the slot should stay empty (no fake Check price)."""
    if is_empty_track(url):
        return None
    return ensure_affiliate_uid(url or "", network)
