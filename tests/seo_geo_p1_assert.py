#!/usr/bin/env python3
"""P1 SEO/GEO assertions against baked site/ HTML (no network, no deploy)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = ROOT / "site" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from seo_geo import ROBOTS_INDEX  # noqa: E402
from site_config import ALL_CATS  # noqa: E402

JARGON = re.compile(
    r"completeness gate|card checklist|publishable|inventory-blocked|"
    r"PartnerBoost|YeahPromos|Mac CDP|Mac L2",
    re.I,
)


def main() -> None:
    errors: list[str] = []

    indexable = [
        SITE / "index.html",
        SITE / "about-us" / "index.html",
        SITE / "authors" / "index.html",
    ]
    for cat in ALL_CATS:
        indexable.append(SITE / cat["slug"] / "index.html")
        indexable.append(SITE / cat["slug"] / "comparison" / "index.html")
        indexable.append(SITE / cat["slug"] / "reviews" / "index.html")

    for path in indexable:
        if not path.exists():
            errors.append(f"missing {path.relative_to(SITE)}")
            continue
        html = path.read_text(encoding="utf-8")
        if ROBOTS_INDEX not in html:
            errors.append(f"{path.relative_to(SITE)} missing {ROBOTS_INDEX}")

    match = (SITE / "robot-vacuums-match" / "index.html").read_text(encoding="utf-8")
    if 'content="noindex,follow"' not in match:
        errors.append("match page lost noindex,follow")

    for cat in ALL_CATS:
        landing = SITE / cat["slug"] / "index.html"
        html = landing.read_text(encoding="utf-8")
        if "geo-cite-strip" not in html or "How to cite:" not in html:
            errors.append(f"{cat['slug']} hub missing How to cite strip")
        n = re.search(r'"numberOfItems":(\d+)', html)
        item_count = int(n.group(1)) if n else 0
        # Honest empty drafts have no ASINs — do not invent #geo- anchors.
        if item_count > 0 and 'id="geo-' not in html:
            errors.append(f"{cat['slug']} hub missing #geo-ASIN")

        cmp = SITE / cat["slug"] / "comparison" / "index.html"
        html = cmp.read_text(encoding="utf-8")
        if "How to cite:" not in html:
            errors.append(f"{cat['slug']} comparison missing How to cite")
        cite_at = html.find('class="geo-cite-strip"')
        last_card = html.rfind('class="product-card"')
        if cite_at != -1 and last_card != -1 and cite_at < last_card:
            errors.append(f"{cat['slug']} comparison cite still inside product stack")
        if 'class="product-card"' in html and 'id="geo-' not in html:
            errors.append(f"{cat['slug']} comparison cards missing #geo-ASIN")
        n_cards = html.count('class="product-card"')
        if n_cards > 10:
            errors.append(f"{cat['slug']} comparison has {n_cards} cards (>10)")

        rev_hub = SITE / cat["slug"] / "reviews" / "index.html"
        html = rev_hub.read_text(encoding="utf-8")
        if "How to cite:" not in html:
            errors.append(f"{cat['slug']} reviews hub missing How to cite")
        if 'class="rev-hub-card"' in html and 'id="geo-' not in html:
            # Kids / thin hubs may lack ASINs; only flag when packshots encode an ASIN.
            if re.search(r"/products/B0[0-9A-Z]{8}", html):
                errors.append(f"{cat['slug']} reviews hub has ASIN packshots but no #geo-")

    sample = SITE / "air-fryers" / "reviews" / "cosori-twinfry-9-qt-double-air" / "index.html"
    if not sample.exists():
        errors.append("missing sample review article")
    else:
        html = sample.read_text(encoding="utf-8")
        if ROBOTS_INDEX not in html:
            errors.append("sample review missing robots preview")
        if "How to cite:" not in html:
            errors.append("sample review missing How to cite")
        if 'id="geo-B0GLX9TGJV"' not in html:
            errors.append("sample review missing #geo-B0GLX9TGJV")
        if JARGON.search(html):
            errors.append("sample review still has visitor jargon")
        if "AggregateRating" in html:
            errors.append("sample review leaked AggregateRating")

    review_pages = list((SITE).glob("*/reviews/*/index.html"))
    if len(review_pages) < 50:
        errors.append(f"expected dozens of baked review articles, found {len(review_pages)}")
    geo_ok = 0
    for path in review_pages:
        html = path.read_text(encoding="utf-8")
        if ROBOTS_INDEX not in html:
            errors.append(f"{path.relative_to(SITE)} missing robots preview")
        if "How to cite:" not in html:
            errors.append(f"{path.relative_to(SITE)} missing How to cite")
        if 'id="geo-' in html:
            geo_ok += 1
        if "AggregateRating" in html:
            errors.append(f"{path.relative_to(SITE)} leaked AggregateRating")
    if review_pages and geo_ok == 0:
        errors.append("no review article received a #geo-ASIN anchor")

    if errors:
        raise SystemExit("seo_geo_p1_assert failed:\n- " + "\n- ".join(errors[:40]))
    print("seo_geo_p1_assert ok")
    print(f"  review articles: {len(review_pages)} (geo={geo_ok})")
    print(f"  cats: {len(ALL_CATS)}")


if __name__ == "__main__":
    main()
