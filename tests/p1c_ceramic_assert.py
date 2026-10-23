#!/usr/bin/env python3
"""P1c ceramic space heaters draft pages — honest density 4, no leftover bedroom chrome."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p1c_ceramic import (  # noqa: E402
    CMP_ORDER,
    DRAFT_COMMENT,
    SCENE_ASINS,
    SLUG,
    TEMPLATE_LEFTOVER,
    healthy_track,
)

PAGES = (
    (
        "ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/index.html",
        "ceramic-large-rooms",
        "/ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/",
    ),
    (
        "ceramic-space-heaters/best-ceramic-space-heaters-for-garages/index.html",
        "ceramic-garages",
        "/ceramic-space-heaters/best-ceramic-space-heaters-for-garages/",
    ),
)
HUBS = (
    "ceramic-space-heaters/index.html",
    "ceramic-space-heaters/comparison/index.html",
    "ceramic-space-heaters/reviews/index.html",
)
SITEMAP_LOCS = (
    "/ceramic-space-heaters/",
    "/ceramic-space-heaters/comparison/",
    "/ceramic-space-heaters/reviews/",
    "/ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/",
    "/ceramic-space-heaters/best-ceramic-space-heaters-for-garages/",
)


def main() -> int:
    errors: list[str] = []
    inv_path = SITE / "data" / "p1c-ceramic-inventory-2026-10-23.json"
    if not inv_path.exists():
        errors.append("missing inventory json")
        print("p1c_ceramic_assert failed:\n- " + "\n- ".join(errors))
        return 1
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")

    shortlist = json.loads((SITE / "data" / f"shortlist-{SLUG}.json").read_text(encoding="utf-8"))
    if shortlist.get("density") != 4 or not shortlist.get("density_shortfall"):
        errors.append("shortlist must stay honest density 4")
    if shortlist.get("waiting_for_部署上线") != "yes":
        errors.append("shortlist missing waiting_for_部署上线")
    if [p["asin"] for p in shortlist.get("picks") or []] != CMP_ORDER:
        errors.append("shortlist comparison order drifted")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    for loc in SITEMAP_LOCS:
        if f"https://moretop10.com{loc}" not in sitemap:
            errors.append(f"sitemap missing {loc}")

    for rel in HUBS:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if DRAFT_COMMENT not in html:
            errors.append(f"{rel} missing draft comment")
        if "10%" in html or "12%" in html or "$49.99" in html or "$74.99" in html:
            errors.append(f"{rel} leaked was/%")

    landing = SITE / SLUG / "index.html"
    if landing.exists():
        html = landing.read_text(encoding="utf-8")
        if "Top 4 Best Ceramic Space Heaters" not in html:
            errors.append("landing H1 must stay honest Top 4")
        for needed in (
            "best-ceramic-space-heaters-for-large-rooms/",
            "best-ceramic-space-heaters-for-garages/",
            "comparison/",
            "reviews/",
        ):
            if needed not in html:
                errors.append(f"landing related-cluster missing {needed}")
        if html.count('class="product-card"') > 10:
            errors.append("landing unexpectedly has product cards")

    cmp = SITE / SLUG / "comparison" / "index.html"
    if cmp.exists():
        html = cmp.read_text(encoding="utf-8")
        n_cards = html.count('class="product-card"')
        if n_cards != 4:
            errors.append(f"comparison cards={n_cards} (need 4)")
        for asin in CMP_ORDER:
            if f'data-asin="{asin}"' not in html:
                errors.append(f"comparison missing {asin}")
            if f"id=\"geo-{asin}\"" not in html and f'id="geo-{asin}"' not in html:
                errors.append(f"comparison missing #geo-{asin}")

    review_articles = list((SITE / SLUG / "reviews").glob("*/index.html"))
    if review_articles:
        errors.append(f"new review articles exist: {[p.name for p in review_articles]}")

    for rel, scene_key, url_path in PAGES:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if DRAFT_COMMENT not in html:
            errors.append(f"{rel} missing draft comment")
        for leak in TEMPLATE_LEFTOVER:
            if leak in html:
                errors.append(f"{rel} leftover {leak!r}")
        if html.count('class="bestof-visit-card"') != 4:
            errors.append(f"{rel} visit cards != 4")
        if html.count('class="inline-pick-card"') != 3:
            errors.append(f"{rel} inline picks != 3")
        if url_path not in sitemap and f"https://moretop10.com{url_path}" not in sitemap:
            errors.append(f"sitemap missing {url_path}")
        scene_order = SCENE_ASINS[scene_key]
        if scene_order == CMP_ORDER:
            errors.append(f"{rel} pasted comparison order")
        for asin in scene_order:
            row = next(p for p in shortlist["picks"] if p["asin"] == asin)
            track = healthy_track(row.get("affiliate_link"))
            if not track:
                errors.append(f"{rel} unhealthy track {asin}")
            elif track not in html and track.replace("&", "&amp;") not in html:
                errors.append(f"{rel} missing track {asin}")
        if "10%" in html or "12%" in html or "$49.99" in html or "$74.99" in html:
            errors.append(f"{rel} leaked was/%")

    if errors:
        print("p1c_ceramic_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p1c_ceramic_assert ok (plural category + 2 draft scene pages, density 4)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
