#!/usr/bin/env python3
"""Editorial /tv/ cluster: intent routes, YP as-is, density exception."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from site_config import ALL_CATS, EDITORIAL_CLUSTERS  # noqa: E402

REQUIRED = [
    "tv/index.html",
    "tv/remove-smart-tv-ads/index.html",
    "tv/supported-android-tv-models/index.html",
    "tv/smart-tv-ad-alternatives/index.html",
    "tv/best-launcher-for-android-tv/index.html",
    "tv/adb-debloat-not-working/index.html",
    "tv/best-non-smart-tv/index.html",
    "tv/best-tv-for-privacy/index.html",
]
P2 = [
    "tv/best-launcher-for-android-tv/index.html",
    "tv/adb-debloat-not-working/index.html",
]
P3 = [
    "tv/best-non-smart-tv/index.html",
    "tv/best-tv-for-privacy/index.html",
]
CONTENT_ONLY = [
    "tv/best-launcher-for-android-tv/index.html",
    "tv/adb-debloat-not-working/index.html",
    "tv/best-non-smart-tv/index.html",
    "tv/best-tv-for-privacy/index.html",
]
STUB_PHRASES = (
    "when we publish scores",
    "ranking note",
    "p2 stub",
    "coming soon",
    "placeholder",
    "thin stub",
)
MIN_P2_WORDS = 400
MIN_P2_H2 = 5
P2_REQUIRED_HEADINGS = {
    "tv/best-launcher-for-android-tv/index.html": (
        "What a launcher can and cannot do",
        "How we rank (validation, not scores)",
        "After you install",
        "When to leave this page",
        "No product list",
    ),
    "tv/adb-debloat-not-working/index.html": (
        "Confirm the platform first",
        "Network and ADB over IP",
        "Honest next steps",
        "No product list",
    ),
}


def legal_body_html(html: str) -> str:
    match = re.search(r'<div class="legal-body">(.*)</div>\s*</div>\s*</main>', html, re.S)
    return match.group(1) if match else ""


def visible_words(html_chunk: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", html_chunk)
    text = unescape(text)
    return [w for w in re.split(r"\s+", text) if w]
FORBIDDEN = [
    "tv/cleanyourtv/index.html",
    "tv/cleanyourtv/supported-models/index.html",
    "tv/cleanyourtv-alternatives/index.html",
    "tv/cleanyourtv/not-working/index.html",
    "tv/cleanyourtv-best-non-smart/index.html",
    "tv/cleanyourtv/privacy/index.html",
]
DO_NOT_HERO = {"B0DGHZ1C8V", "B0FHGNWZXT", "B0FMK1B4LW", "B0HGXYM1WD"}


def main() -> None:
    errors: list[str] = []
    if any(c["slug"] == "tv" for c in ALL_CATS):
        errors.append("tv registered in ALL_CATS (density-10 shortlist) — forbidden")
    if not any(c["slug"] == "tv" for c in EDITORIAL_CLUSTERS):
        errors.append("EDITORIAL_CLUSTERS missing tv")

    sl = json.loads((SITE / "data" / "shortlist-tv.json").read_text(encoding="utf-8"))
    hero = sl.get("hero_google_tv") or []
    fire = sl.get("honest_fire_tv") or []
    if len(hero) != 9:
        errors.append(f"hero_google_tv expected 9, got {len(hero)}")
    if len(fire) != 20:
        errors.append(f"honest_fire_tv expected 20, got {len(fire)}")
    oos_asins = {item.get("asin") for item in hero + fire if item.get("oos")}
    if "B0GV4Q9XSF" not in oos_asins:
        errors.append("B0GV4Q9XSF should be marked oos in shortlist")
    for item in hero + fire:
        link = item.get("affiliate_link") or ""
        if item.get("affiliate_network") != "yp":
            errors.append(f"{item.get('asin')} network {item.get('affiliate_network')}")
        if not link.startswith("https://yeahpromos.com/"):
            errors.append(f"{item.get('asin')} track host is not yeahpromos.com")
        if "uid=" in link or "subid=" in link:
            errors.append(f"{item.get('asin')} track has uid/subid")
        if item.get("asin") in DO_NOT_HERO:
            errors.append(f"do_not_hero ASIN in shortlist products {item.get('asin')}")

    for rel in REQUIRED:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if "data-tv-disclosure" not in html:
            errors.append(f"{rel} missing unofficial disclosure")
        if "geo-answer-first" not in html:
            errors.append(f"{rel} missing answer-first")
        if re.search(r"uid=", html):
            errors.append(f"{rel} contains uid=")
        if "PartnerBoost" in html or "YeahPromos" in html:
            errors.append(f"{rel} visitor jargon")

    for rel in FORBIDDEN:
        if (SITE / rel).exists():
            errors.append(f"forbidden path exists {rel}")

    alt = (SITE / "tv/smart-tv-ad-alternatives/index.html").read_text(encoding="utf-8")
    alt_hrefs = unescape(alt)
    for item in hero:
        if item.get("oos"):
            if item["affiliate_link"] in alt_hrefs:
                errors.append(f"OOS hero {item['asin']} still has Check price")
            continue
        if item["affiliate_link"] not in alt_hrefs:
            errors.append(f"L2 missing hero track {item['asin']}")
        if item["asin"] not in alt:
            errors.append(f"L2 missing hero ASIN {item['asin']}")
    oos_row = re.search(r'<tr[^>]*id="geo-B0GV4Q9XSF"[\s\S]*?</tr>', alt)
    if not oos_row:
        errors.append("honest table missing OOS B0GV4Q9XSF")
    elif "Check price" in oos_row.group(0) or "yeahpromos.com" in oos_row.group(0):
        errors.append("OOS B0GV4Q9XSF still has a Check price CTA")
    elif "Currently unavailable" not in oos_row.group(0):
        errors.append("OOS B0GV4Q9XSF missing unavailable label")
    if "$1299.99" not in alt:
        errors.append("L2 price $1299.99 (B0GHZXKT1T) not baked")
    if "$2497.99" not in alt:
        errors.append("L2 price $2497.99 (B0GR9C4H3H) not baked")
    for asin in DO_NOT_HERO:
        if asin in alt:
            errors.append(f"L2 includes do_not_hero {asin}")
    if "Primary recommendations — Google TV" not in alt:
        errors.append("L2 missing Google TV hero heading")
    if "Fire TV panels — honest section" not in alt:
        errors.append("L2 missing honest Fire section")
    if "No retailer link yet" not in alt and "stay empty" not in alt.lower():
        errors.append("L2 missing empty-slot honesty")

    hub = (SITE / "tv/index.html").read_text(encoding="utf-8")
    if "tv/best-non-smart-tv/" not in hub:
        errors.append("hub missing /tv/best-non-smart-tv/ G-IL")
    if "tv/best-tv-for-privacy/" not in hub:
        errors.append("hub missing /tv/best-tv-for-privacy/ G-IL")
    if "tv/best-launcher-for-android-tv/" not in hub:
        errors.append("hub missing /tv/best-launcher-for-android-tv/ G-IL")
    if "tv/adb-debloat-not-working/" not in hub:
        errors.append("hub missing /tv/adb-debloat-not-working/ G-IL")
    if "ranking notes" in hub.lower() or "p2 stub" in hub.lower():
        errors.append("hub still labels P2 pages as stubs / ranking notes")

    for rel in CONTENT_ONLY:
        html = (SITE / rel).read_text(encoding="utf-8")
        if "yeahpromos.com" in html or "pboost.me" in html or "btn-cta-yellow" in html:
            errors.append(f"{rel} invented a Check price CTA on an empty product zone")
        if "cleanyourtv" in rel.replace("\\", "/").lower():
            errors.append(f"forbidden cleanyourtv path {rel}")

    for rel in P2:
        html = (SITE / rel).read_text(encoding="utf-8")
        body = legal_body_html(html)
        words = visible_words(body)
        h2s = re.findall(r"<h2>[^<]+</h2>", body)
        if len(words) < MIN_P2_WORDS:
            errors.append(f"{rel} still stub-thin ({len(words)} words, need {MIN_P2_WORDS}+)")
        if len(h2s) < MIN_P2_H2:
            errors.append(f"{rel} still stub-thin ({len(h2s)} h2, need {MIN_P2_H2}+)")
        lowered = body.lower()
        for phrase in STUB_PHRASES:
            if phrase in lowered:
                errors.append(f"{rel} still has stub phrase {phrase!r}")
        if re.search(r'href="[^"]*tv/"', html) is None:
            errors.append(f"{rel} missing hub /tv/ back-link")
        if "tv/remove-smart-tv-ads/" not in html:
            errors.append(f"{rel} missing L1 /tv/remove-smart-tv-ads/ back-link")
        if "tv/smart-tv-ad-alternatives/" not in html:
            errors.append(f"{rel} missing L2 /tv/smart-tv-ad-alternatives/ back-link")
        if "tv/best-non-smart-tv/" not in html:
            errors.append(f"{rel} missing P3 /tv/best-non-smart-tv/ link")
        if "tv/best-tv-for-privacy/" not in html:
            errors.append(f"{rel} missing P3 /tv/best-tv-for-privacy/ link")
        for heading in P2_REQUIRED_HEADINGS[rel]:
            if heading not in body:
                errors.append(f"{rel} missing first-class heading {heading!r}")
        if "Fire Stick" in html and not re.search(
            r"(will not|never|not)[^.]*Fire Stick|Fire Stick[^.]*not",
            html,
            re.I,
        ):
            errors.append(f"{rel} mentions Fire Stick outside a prohibition")

    for rel in P3:
        html = (SITE / rel).read_text(encoding="utf-8")
        if re.search(r'href="[^"]*tv/"', html) is None:
            errors.append(f"{rel} missing hub /tv/ back-link")
        if "tv/remove-smart-tv-ads/" not in html:
            errors.append(f"{rel} missing L1 /tv/remove-smart-tv-ads/ back-link")
        if "tv/smart-tv-ad-alternatives/" not in html:
            errors.append(f"{rel} missing L2 /tv/smart-tv-ad-alternatives/ back-link")
        zone = re.search(r'<div class="tv-empty"[^>]*data-tv-empty-products[\s\S]*?</div>', html)
        if not zone:
            errors.append(f"{rel} missing honest empty product zone")
        elif "<a " in zone.group(0) or "btn-cta" in zone.group(0):
            errors.append(f"{rel} empty product zone has a checkout link")
        if "No affiliate-tracked" not in html:
            errors.append(f"{rel} missing empty-feed honesty copy")
        if "Fire Stick" in html and not re.search(
            r"(will not|never|not)[^.]*Fire Stick|Fire Stick[^.]*not",
            html,
            re.I,
        ):
            errors.append(f"{rel} mentions Fire Stick outside a prohibition")

    home = (SITE / "index.html").read_text(encoding="utf-8")
    if 'data-editorial-cluster="tv"' not in home:
        errors.append("home missing /tv/ tile")
    footer = (SITE / "about-us" / "index.html").read_text(encoding="utf-8").split("<footer", 1)[-1]
    if "tv/" not in footer:
        errors.append("about footer missing /tv/")
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    if "https://moretop10.com/tv/" not in sitemap:
        errors.append("sitemap missing /tv/")
    if "https://moretop10.com/tv/best-launcher-for-android-tv/" not in sitemap:
        errors.append("sitemap missing P2 /tv/best-launcher-for-android-tv/")
    if "https://moretop10.com/tv/adb-debloat-not-working/" not in sitemap:
        errors.append("sitemap missing P2 /tv/adb-debloat-not-working/")
    if "https://moretop10.com/tv/best-non-smart-tv/" not in sitemap:
        errors.append("sitemap missing P3 /tv/best-non-smart-tv/")
    if "https://moretop10.com/tv/best-tv-for-privacy/" not in sitemap:
        errors.append("sitemap missing P3 /tv/best-tv-for-privacy/")
    if "https://moretop10.com/tv/cleanyourtv/" in sitemap:
        errors.append("sitemap lists a forbidden branded path")
    if "cleanyourtv" in sitemap:
        errors.append("sitemap contains cleanyourtv")

    llms = (SITE / "llms.txt").read_text(encoding="utf-8")
    if "https://moretop10.com/tv/best-launcher-for-android-tv/" not in llms:
        errors.append("llms.txt missing P2 /tv/best-launcher-for-android-tv/")
    if "https://moretop10.com/tv/adb-debloat-not-working/" not in llms:
        errors.append("llms.txt missing P2 /tv/adb-debloat-not-working/")
    if "https://moretop10.com/tv/best-non-smart-tv/" not in llms:
        errors.append("llms.txt missing P3 /tv/best-non-smart-tv/")
    if "https://moretop10.com/tv/best-tv-for-privacy/" not in llms:
        errors.append("llms.txt missing P3 /tv/best-tv-for-privacy/")

    if errors:
        raise SystemExit("tv_cluster_assert failed:\n- " + "\n- ".join(errors))
    print("tv_cluster_assert ok")


if __name__ == "__main__":
    main()
