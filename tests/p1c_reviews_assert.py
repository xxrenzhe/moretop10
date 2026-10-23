#!/usr/bin/env python3
"""P1c Top pick + Upgrade deep reviews — SoT-only, no Amazon PDP leftover."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P1c deep reviews draft only. "
    "Do not merge. Do not Cloudflare Live deploy. -->"
)

# Unique review files (3). 6 hub slots share these paths.
REVIEWS = (
    (
        "ceramic-space-heaters/reviews/dreo-space-heater-portable-electric-remote/index.html",
        "B0C6FFK1GV",
        "Top pick",
        ("/ceramic-space-heaters/",),
    ),
    (
        "ceramic-space-heaters/reviews/dreo-atom-one-space-heater-thermostat/index.html",
        "B097RG67QB",
        "Upgrade",
        (
            "/ceramic-space-heaters/",
            "/ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/",
            "/ceramic-space-heaters/best-ceramic-space-heaters-for-garages/",
        ),
    ),
    (
        "ceramic-space-heaters/reviews/dreo-space-heaters-indoor-thermostat-1500w/index.html",
        "B095PP1GZR",
        "Top pick",
        (
            "/ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/",
            "/ceramic-space-heaters/best-ceramic-space-heaters-for-garages/",
        ),
    ),
)

HUB_WIRES = (
    (
        "ceramic-space-heaters/index.html",
        (
            "reviews/dreo-space-heater-portable-electric-remote/",
            "reviews/dreo-atom-one-space-heater-thermostat/",
        ),
    ),
    (
        "ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/index.html",
        (
            "dreo-space-heaters-indoor-thermostat-1500w",
            "dreo-atom-one-space-heater-thermostat",
        ),
    ),
    (
        "ceramic-space-heaters/best-ceramic-space-heaters-for-garages/index.html",
        (
            "dreo-atom-one-space-heater-thermostat",
            "dreo-space-heaters-indoor-thermostat-1500w",
        ),
    ),
)

FORBIDDEN = (
    "【",
    "Do you run lab tests?",
    "hardwood and alternatives guides",
    "RHEA-001",
    "PartnerBoost",
    "Mac L2",
    "fromsll track",
    "DEDICATED CUSTOMER SUPPORT",
    "[FAST COMFORT",
    "royalbaby",
    "B0C6FCKQML",
)

NEEDLE_H2 = (
    "who should skip",
    "day-two",
    "faq",
)

TRACKS = (
    "https://pboost.me/C5qeREta?uid=fromsll",
    "https://pboost.me/O5qeSat9?uid=fromsll",
    "https://pboost.me/N5qe9P4ta?uid=fromsll",
)


def _plain(html: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", html))


def _sentences(text: str) -> int:
    parts = [p for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p]
    return len(parts)


def main() -> int:
    errors: list[str] = []
    notes = ROOT / "notes" / "p1c-deep-reviews-2026-10-23.md"
    if not notes.exists():
        errors.append("missing notes/p1c-deep-reviews-2026-10-23.md")
    else:
        blob = notes.read_text(encoding="utf-8")
        if "waiting_for_部署上线" not in blob:
            errors.append("notes missing waiting_for_部署上线")
        if "## Skips" not in blob:
            errors.append("notes missing Skips section")
        if "B0C6FCKQML" not in blob:
            errors.append("notes must name skipped Gold ASIN")
        for _rel, asin, _role, hubs in REVIEWS:
            if asin not in blob:
                errors.append(f"notes missing ASIN {asin}")
            for hub in hubs:
                if hub not in blob:
                    errors.append(f"notes missing hub {hub}")

    inv_path = SITE / "data" / "p1c-ceramic-inventory-2026-10-23.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")
    if inv.get("deep_reviews") != "p1c_top_pick_upgrade_only":
        errors.append("inventory missing deep_reviews flag")

    gold = list((SITE / "ceramic-space-heaters" / "reviews").glob("*/index.html"))
    slugs = {p.parent.name for p in gold}
    expected = {rel.split("/")[2] for rel, *_ in REVIEWS}
    if slugs != expected:
        errors.append(f"review slugs={sorted(slugs)} (want {sorted(expected)})")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    for rel, _asin, _role, _hubs in REVIEWS:
        loc = "/" + rel.replace("index.html", "")
        if f"https://moretop10.com{loc}" not in sitemap:
            errors.append(f"sitemap missing {loc}")

    for rel, asin, role, hubs in REVIEWS:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if DRAFT_COMMENT not in html:
            errors.append(f"{rel} missing draft comment")
        if f'id="geo-{asin}"' not in html:
            errors.append(f"{rel} missing geo-{asin}")
        if f'<p class="badge">{role}</p>' not in html:
            errors.append(f"{rel} badge is not {role}")
        if 'class="review-summary"' not in html:
            errors.append(f"{rel} missing answer-first summary")
        else:
            sm = re.search(r'<p class="review-summary">(.*?)</p>', html, re.S)
            n = _sentences(_plain(sm.group(1))) if sm else 0
            if n < 2 or n > 4:
                errors.append(f"{rel} summary has {n} sentences (want 2–4)")
        if 'aria-label="Key insights"' not in html:
            errors.append(f"{rel} missing Key insights")
        else:
            block = re.search(r'aria-label="Key insights".*?</section>', html, re.S)
            n_facts = len(re.findall(r"<li>", block.group(0))) if block else 0
            if n_facts < 5 or n_facts > 8:
                errors.append(f"{rel} Key insights has {n_facts} facts (want 5–8)")
        low = html.lower()
        for needle in NEEDLE_H2:
            if needle not in low:
                errors.append(f"{rel} missing {needle!r}")
        for hub in hubs:
            tail = hub.rstrip("/").rsplit("/", 1)[-1]
            if hub.rstrip("/") not in html and hub not in html and tail not in html:
                errors.append(f"{rel} missing cluster link {hub}")
        faqs = re.findall(
            r'<section class="review-section review-faq">.*?</section>', html, re.S
        )
        if not faqs:
            errors.append(f"{rel} missing review FAQ")
        else:
            nq = len(re.findall(r"<summary>", faqs[0]))
            if nq != 4:
                errors.append(f"{rel} FAQ count {nq} (want 4)")
        for bad in FORBIDDEN:
            if bad in html:
                errors.append(f"{rel} still has {bad!r}")
        if "was-price" in html or "original_price" in html:
            errors.append(f"{rel} invented was-price field")
        if "pboost.me" not in html:
            errors.append(f"{rel} missing live track")
        if "10%" in html or "12%" in html:
            errors.append(f"{rel} leaked was/%")
        if "Best Humidifiers for Bedrooms" in html:
            errors.append(f"{rel} leftover humidifier schema")
        if "how-to-choose-a-humidifier" in html:
            errors.append(f"{rel} leftover humidifier chrome")
        if 'href="../../favicon' in html or 'href="../../assets/css/' in html:
            errors.append(f"{rel} leftover depth-2 head assets")
        if 'src="../../assets/img/symbol-color.svg"' in html:
            errors.append(f"{rel} leftover depth-2 logo")
        if 'href="../../../favicon.ico"' not in html:
            errors.append(f"{rel} missing depth-3 favicon")
        if 'href="../../comparison/"' not in html:
            errors.append(f"{rel} missing review-main comparison link")

    for rel, needles in HUB_WIRES:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing hub {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in html:
                errors.append(f"{rel} missing recommend-slot link {needle}")

    hub = SITE / "ceramic-space-heaters" / "reviews" / "index.html"
    if hub.exists():
        html = hub.read_text(encoding="utf-8")
        if "dreo-space-heater-portable-electric-remote/" not in html:
            errors.append("reviews hub missing white remote path")
        if "dreo-atom-one-space-heater-thermostat/" not in html:
            errors.append("reviews hub missing Atom One path")
        if "dreo-space-heaters-indoor-thermostat-1500w/" not in html:
            errors.append("reviews hub missing Premium path")
        if "royalbaby" in html.lower():
            errors.append("reviews hub still has kids-bike leftover")
        if "B0C6FCKQML" in html and 'href="dreo-' in html:
            gold_card = re.search(r'id="geo-B0C6FCKQML".*?</article>', html, re.S)
            if gold_card and "rev-hub-read" in gold_card.group(0):
                errors.append("reviews hub invented a Gold deep-review link")

    cmp = SITE / "ceramic-space-heaters" / "comparison" / "index.html"
    if cmp.exists():
        html = cmp.read_text(encoding="utf-8")
        for slug in (
            "dreo-space-heater-portable-electric-remote",
            "dreo-atom-one-space-heater-thermostat",
            "dreo-space-heaters-indoor-thermostat-1500w",
        ):
            if f"reviews/{slug}/" not in html:
                errors.append(f"comparison missing review link {slug}")

    for track in TRACKS:
        found = False
        for rel, *_rest in REVIEWS:
            if track in (SITE / rel).read_text(encoding="utf-8"):
                found = True
                break
        if not found:
            errors.append(f"missing live track {track}")

    if errors:
        print("p1c_reviews_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p1c_reviews_assert ok (3 unique P1c deep reviews / 6 slots)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
