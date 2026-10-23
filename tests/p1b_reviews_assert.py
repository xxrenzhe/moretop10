#!/usr/bin/env python3
"""P1b Top pick + Upgrade deep reviews — SoT-only, no Amazon PDP leftover."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P1b deep reviews draft only. "
    "Do not merge. Do not Cloudflare Live deploy. -->"
)

# Unique review files (10). 16 hub slots share these paths.
REVIEWS = (
    (
        "air-purifiers/reviews/levoit-smart-pet-air-purifier-home/index.html",
        "B0GXKSC38S",
        "Top pick",
        (
            "/air-purifiers/best-air-purifiers-for-allergies/",
            "/air-purifiers/best-air-purifiers-for-smoke/",
        ),
    ),
    (
        "air-purifiers/reviews/levoit-air-purifier-home-bedroom-small/index.html",
        "B07X25BNBR",
        "Top pick",
        (
            "/air-purifiers/best-air-purifiers-for-bedrooms/",
            "/air-purifiers/best-air-purifiers-for-dust/",
            "/air-purifiers/best-air-purifiers-for-allergies/",
        ),
    ),
    (
        "air-purifiers/reviews/mooka-air-purifier-home-bedroom-large/index.html",
        "B0CXJ97TV1",
        "Top pick",
        (
            "/air-purifiers/best-air-purifiers-for-mold/",
            "/air-purifiers/best-air-purifiers-for-large-rooms/",
            "/air-purifiers/best-air-purifiers-for-bedrooms/",
        ),
    ),
    (
        "air-purifiers/reviews/dreame-air-purifier-pm20-home-large/index.html",
        "B0F32TGRMR",
        "Upgrade",
        (
            "/air-purifiers/best-air-purifiers-for-mold/",
            "/air-purifiers/best-air-purifiers-for-large-rooms/",
        ),
    ),
    (
        "air-purifiers/reviews/dreame-pet-air-purifier-ap10-suck/index.html",
        "B0FS68R44C",
        "Upgrade",
        ("/air-purifiers/best-air-purifiers-for-dust/",),
    ),
    (
        "air-purifiers/reviews/dreame-smart-air-purifier-pm10-home/index.html",
        "B0F2G5DPJN",
        "Top pick",
        ("/air-purifiers/best-air-purifiers-for-smoke/",),
    ),
    (
        "humidifiers/reviews/homvana-36l-cool-mist-humidifiers-bedroom/index.html",
        "B0DF567NW8",
        "Top pick",
        ("/humidifiers/best-humidifiers-for-babies/",),
    ),
    (
        "humidifiers/reviews/homvana-humidifier-large-room-7l-807ft/index.html",
        "B0C369CCDY",
        "Upgrade",
        ("/humidifiers/best-humidifiers-for-babies/",),
    ),
    (
        "standing-desks/reviews/fezibo-60-x-30-inch-standing/index.html",
        "B0B68QSN6Y",
        "Top pick",
        ("/standing-desks/best-standing-desks-for-home-office/",),
    ),
    (
        "standing-desks/reviews/fezibo-63-x-37-inch-large/index.html",
        "B0GD75Y6SC",
        "Upgrade",
        ("/standing-desks/best-standing-desks-for-home-office/",),
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
    "[MistIQ",
)

NEEDLE_H2 = (
    "who should skip",
    "day-two",
    "faq",
)


def _plain(html: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", html))


def _sentences(text: str) -> int:
    parts = [p for p in re.split(r"(?<=[.!?])\s+", text.strip()) if p]
    return len(parts)


def main() -> int:
    errors: list[str] = []
    notes = ROOT / "notes" / "p1b-deep-reviews-2026-10-23.md"
    if not notes.exists():
        errors.append("missing notes/p1b-deep-reviews-2026-10-23.md")
    else:
        blob = notes.read_text(encoding="utf-8")
        if "waiting_for_部署上线" not in blob:
            errors.append("notes missing waiting_for_部署上线")
        if "## Skips" not in blob:
            errors.append("notes missing Skips section")
        for _rel, asin, _role, hubs in REVIEWS:
            if asin not in blob:
                errors.append(f"notes missing ASIN {asin}")
            for hub in hubs:
                if hub not in blob:
                    errors.append(f"notes missing hub {hub}")

    inv_path = SITE / "data" / "p1b-scene-inventory-2026-10-23.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")
    if inv.get("deep_reviews") != "p1b_top_pick_upgrade_only":
        errors.append("inventory missing deep_reviews flag")

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
            block = re.search(
                r'aria-label="Key insights".*?</section>', html, re.S
            )
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
            if nq < 3 or nq > 5:
                errors.append(f"{rel} FAQ count {nq} (want 3–5)")
        for bad in FORBIDDEN:
            if bad in html:
                errors.append(f"{rel} still has {bad!r}")
        if "was-price" in html or "original_price" in html:
            errors.append(f"{rel} invented was-price field")
        if "pboost.me" not in html:
            errors.append(f"{rel} missing live track")

    if errors:
        print("p1b_reviews_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p1b_reviews_assert ok (10 unique P1b deep reviews / 16 slots)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
