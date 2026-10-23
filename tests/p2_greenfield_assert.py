#!/usr/bin/env python3
"""P2 greenfield draft pages — honest density 0, no leftover bedroom chrome."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p2_greenfield import (  # noqa: E402
    CATS,
    DRAFT_COMMENT,
    TEMPLATE_LEFTOVER,
    healthy_track,
)

SITEMAP_LOCS = []
for cat in CATS:
    SITEMAP_LOCS.extend(
        [
            f"/{cat['slug']}/",
            f"/{cat['slug']}/comparison/",
            f"/{cat['slug']}/reviews/",
            f"/{cat['slug']}/{cat['scene_path']}/",
        ]
    )


def main() -> int:
    errors: list[str] = []
    inv_path = SITE / "data" / "p2-greenfield-inventory-2026-10-23.json"
    if not inv_path.exists():
        errors.append("missing inventory json")
        print("p2_greenfield_assert failed:\n- " + "\n- ".join(errors))
        return 1
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    html_map = (SITE / "sitemap" / "index.html").read_text(encoding="utf-8")
    for loc in SITEMAP_LOCS:
        if f"https://moretop10.com{loc}" not in sitemap:
            errors.append(f"sitemap missing {loc}")
    for cat in CATS:
        if f'href="../{cat["slug"]}/"' not in html_map:
            errors.append(f"sitemap/index.html missing /{cat['slug']}/")

    forbidden_touch = (
        "site/blog/index.html",
        "site/ceramic-space-heaters/index.html",
        "site/scripts/bake_p1c_ceramic.py",
        "site/data/p1c-ceramic-inventory-2026-10-23.json",
        "tests/p1c_ceramic_assert.py",
    )
    for rel in forbidden_touch:
        # Coexistence only: these #40 / blog files must stay absent on this branch.
        if (ROOT / rel).exists() and "ceramic" in rel:
            errors.append(f"must not add ceramic P1c file {rel} on the P2 branch")

    for cat in CATS:
        slug = cat["slug"]
        shortlist = json.loads((SITE / "data" / f"shortlist-{slug}.json").read_text(encoding="utf-8"))
        if shortlist.get("density") != 0 or not shortlist.get("density_shortfall"):
            errors.append(f"{slug} shortlist must stay honest density 0")
        if shortlist.get("waiting_for_部署上线") != "yes":
            errors.append(f"{slug} shortlist missing waiting_for_部署上线")
        if shortlist.get("picks"):
            errors.append(f"{slug} invented picks")

        hubs = (
            f"{slug}/index.html",
            f"{slug}/comparison/index.html",
            f"{slug}/reviews/index.html",
        )
        for rel in hubs:
            path = SITE / rel
            if not path.exists():
                errors.append(f"missing {rel}")
                continue
            html = path.read_text(encoding="utf-8")
            if DRAFT_COMMENT not in html:
                errors.append(f"{rel} missing draft comment")
            if "10%" in html or "12%" in html:
                errors.append(f"{rel} leaked was/%")

        landing = SITE / slug / "index.html"
        if landing.exists():
            html = landing.read_text(encoding="utf-8")
            if f"Top 0 Best {cat['name']}" not in html:
                errors.append(f"{slug} landing H1 must stay honest Top 0")
            for needed in (f"{cat['scene_path']}/", "comparison/", "reviews/"):
                if needed not in html:
                    errors.append(f"{slug} landing related-cluster missing {needed}")
            if html.count('class="product-card"') > 0:
                errors.append(f"{slug} landing unexpectedly has product cards")
            if '"@type":"Product"' in html or '"@type": "Product"' in html:
                errors.append(f"{slug} landing invented Product schema")
            if 'class="best-widget-name"' in html:
                errors.append(f"{slug} landing invented Best-widget names")

        cmp = SITE / slug / "comparison" / "index.html"
        if cmp.exists():
            html = cmp.read_text(encoding="utf-8")
            if html.count('class="product-card"') != 0:
                errors.append(f"{slug} comparison invented cards")

        review_articles = list((SITE / slug / "reviews").glob("*/index.html"))
        if review_articles:
            errors.append(f"{slug} new review articles exist: {[p.parent.name for p in review_articles]}")

        rel = f"{slug}/{cat['scene_path']}/index.html"
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
        if html.count('class="bestof-visit-card"') != 0:
            errors.append(f"{rel} invented visit cards")
        if html.count('class="inline-pick-card"') != 0:
            errors.append(f"{rel} invented inline picks")
        if "10%" in html or "12%" in html:
            errors.append(f"{rel} leaked was/%")
        if "density is honest at 0" not in html.lower() and "Density is honest at 0" not in html:
            errors.append(f"{rel} missing honest density copy")

    if errors:
        print("p2_greenfield_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p2_greenfield_assert ok (4 plural categories + 4 draft scene pages, density 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
