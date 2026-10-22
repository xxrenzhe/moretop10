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
]
FORBIDDEN = [
    "tv/cleanyourtv/index.html",
    "tv/cleanyourtv/supported-models/index.html",
    "tv/cleanyourtv-alternatives/index.html",
    "tv/cleanyourtv/not-working/index.html",
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

    launcher = (SITE / "tv/best-launcher-for-android-tv/index.html").read_text(encoding="utf-8")
    if "yeahpromos.com" in launcher or "pboost.me" in launcher:
        errors.append("launcher page must not carry affiliate SKUs")

    home = (SITE / "index.html").read_text(encoding="utf-8")
    if 'data-editorial-cluster="tv"' not in home:
        errors.append("home missing /tv/ tile")
    footer = (SITE / "about-us" / "index.html").read_text(encoding="utf-8").split("<footer", 1)[-1]
    if "tv/" not in footer:
        errors.append("about footer missing /tv/")
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    if "https://moretop10.com/tv/" not in sitemap:
        errors.append("sitemap missing /tv/")
    if "https://moretop10.com/tv/cleanyourtv/" in sitemap:
        errors.append("sitemap lists a forbidden branded path")

    if errors:
        raise SystemExit("tv_cluster_assert failed:\n- " + "\n- ".join(errors))
    print("tv_cluster_assert ok")


if __name__ == "__main__":
    main()
