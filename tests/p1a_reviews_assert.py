#!/usr/bin/env python3
"""P1a Top pick + Upgrade deep reviews — SoT-only, no Amazon PDP leftover."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P1a deep reviews draft only. "
    "Do not merge. Do not Cloudflare Live deploy. -->"
)

REVIEWS = (
    (
        "dehumidifiers/reviews/waykar-80-pints-2025-energy-star/index.html",
        "B0C9THG48W",
        "/dehumidifiers/best-dehumidifiers-for-basements/",
        "Top pick",
    ),
    (
        "dehumidifiers/reviews/aeocky-5500-sqft-energy-star-most/index.html",
        "B0D1C6HWFF",
        "/dehumidifiers/best-dehumidifiers-for-basements/",
        "Upgrade",
    ),
    (
        "air-purifiers/reviews/levoit-smart-pet-air-purifier-home/index.html",
        "B0GXKSC38S",
        "/air-purifiers/best-air-purifiers-for-pets/",
        "Top pick",
    ),
    (
        "air-purifiers/reviews/dreame-pet-air-purifier-ap10-suck/index.html",
        "B0FS68R44C",
        "/air-purifiers/best-air-purifiers-for-pets/",
        "Upgrade",
    ),
    (
        "robot-vacuums/reviews/eufy-e25-robot-vacuum-mop-combo/index.html",
        "B0FK2HPNCB",
        "/robot-vacuums/pet-homes/",
        "Top pick",
    ),
    (
        "robot-vacuums/reviews/roborock-2026-new-qrevo-s-pro/index.html",
        "B0GGRTD2ZY",
        "/robot-vacuums/pet-homes/",
        "Upgrade",
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
    notes = ROOT / "notes" / "p1a-deep-reviews-2026-10-23.md"
    if not notes.exists():
        errors.append("missing notes/p1a-deep-reviews-2026-10-23.md")
    else:
        blob = notes.read_text(encoding="utf-8")
        if "waiting_for_部署上线" not in blob:
            errors.append("notes missing waiting_for_部署上线")
        for _rel, asin, _hub, _role in REVIEWS:
            if asin not in blob:
                errors.append(f"notes missing ASIN {asin}")

    inv_path = SITE / "data" / "p1a-scene-inventory-2026-10-23.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")

    for rel, asin, hub, role in REVIEWS:
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
        if hub.rstrip("/") not in html and hub not in html:
            tail = hub.rstrip("/").rsplit("/", 1)[-1]
            if tail not in html:
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
        print("p1a_reviews_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p1a_reviews_assert ok (6 P1a deep reviews)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
