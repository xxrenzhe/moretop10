#!/usr/bin/env python3
"""P2 L1 fill — honest 6/8/8/0, no leftover bedroom chrome, no invented gallery."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p2_greenfield import (  # noqa: E402
    CATS,
    DRAFT_COMMENT,
    EXPECTED_DENSITY,
    PACK_PATH,
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


def _asins(picks: list[dict]) -> list[str]:
    return [p["asin"] for p in picks]


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
    if not PACK_PATH.exists():
        errors.append("missing L1 fill pack")
        print("p2_greenfield_assert failed:\n- " + "\n- ".join(errors))
        return 1
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    html_map = (SITE / "sitemap" / "index.html").read_text(encoding="utf-8")
    for loc in SITEMAP_LOCS:
        if f"https://moretop10.com{loc}" not in sitemap:
            errors.append(f"sitemap missing {loc}")
    for cat in CATS:
        if f'href="../{cat["slug"]}/"' not in html_map:
            errors.append(f"sitemap/index.html missing /{cat['slug']}/")

    inv_by_path = {row.get("path"): row for row in inv.get("pages") or []}

    for cat in CATS:
        slug = cat["slug"]
        expected = EXPECTED_DENSITY[slug]
        scene_blob = (pack.get("scenes") or {}).get(cat["scene_path"]) or {}
        pack_asins = [p["asin"] for p in scene_blob.get("products") or []]
        if len(pack_asins) != expected:
            errors.append(f"{slug} pack count {len(pack_asins)} != expected {expected}")

        shortlist = json.loads((SITE / "data" / f"shortlist-{slug}.json").read_text(encoding="utf-8"))
        if shortlist.get("density") != expected:
            errors.append(f"{slug} shortlist density {shortlist.get('density')} != {expected}")
        if expected < 10 and not shortlist.get("density_shortfall"):
            errors.append(f"{slug} shortlist must keep density_shortfall")
        if shortlist.get("waiting_for_部署上线") != "yes":
            errors.append(f"{slug} shortlist missing waiting_for_部署上线")
        got_asins = _asins(shortlist.get("picks") or [])
        if set(got_asins) != set(pack_asins):
            errors.append(f"{slug} shortlist ASINs drifted from pack")
        for pick in shortlist.get("picks") or []:
            track = healthy_track(pick.get("affiliate_link"))
            if not track:
                errors.append(f"{slug} {pick.get('asin')} missing healthy fromsll track")
            if pick.get("image"):
                errors.append(f"{slug} {pick.get('asin')} invented gallery")
            if pick.get("list_price"):
                errors.append(f"{slug} {pick.get('asin')} invented list_price")

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
            if "m.media-amazon.com" in html:
                errors.append(f"{rel} invented Amazon gallery")

        landing = SITE / slug / "index.html"
        if landing.exists():
            html = landing.read_text(encoding="utf-8")
            if f"Top {expected} Best {cat['name']}" not in html:
                errors.append(f"{slug} landing H1 must stay honest Top {expected}")
            for needed in (f"{cat['scene_path']}/", "comparison/", "reviews/"):
                if needed not in html:
                    errors.append(f"{slug} landing related-cluster missing {needed}")
            if expected == 0:
                if html.count('class="product-card"') > 0:
                    errors.append(f"{slug} landing unexpectedly has product cards")
                if '"@type":"Product"' in html or '"@type": "Product"' in html:
                    errors.append(f"{slug} landing invented Product schema")
                if 'class="best-widget-name"' in html:
                    errors.append(f"{slug} landing invented Best-widget names")
            else:
                for asin in pack_asins:
                    if f"id=\"geo-{asin}\"" not in html:
                        errors.append(f"{slug} landing missing #geo-{asin}")

        cmp = SITE / slug / "comparison" / "index.html"
        if cmp.exists():
            html = cmp.read_text(encoding="utf-8")
            cards = html.count('class="product-card"')
            if cards != expected:
                errors.append(f"{slug} comparison cards={cards} (need {expected})")

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
        visits = html.count('class="bestof-visit-card"')
        if visits != expected:
            errors.append(f"{rel} visit cards={visits} (need {expected})")
        inline_need = min(3, expected)
        if html.count('class="inline-pick-card"') != inline_need:
            errors.append(f"{rel} inline picks != {inline_need}")
        if "10%" in html or "12%" in html:
            errors.append(f"{rel} leaked was/%")
        if "m.media-amazon.com" in html:
            errors.append(f"{rel} invented Amazon gallery")
        if expected == 0:
            if "density is honest at 0" not in html.lower() and "Density is honest at 0" not in html:
                errors.append(f"{rel} missing honest density copy")
        else:
            if f"Density is honest at {expected}" not in html and f"density is honest at {expected}" not in html.lower():
                errors.append(f"{rel} missing honest density {expected} copy")
            for asin in pack_asins:
                if asin not in html:
                    errors.append(f"{rel} missing pack ASIN {asin}")
            if re.search(r"was-price|list.price|save \d+%", html, re.I):
                errors.append(f"{rel} invented was/% copy")

        inv_row = inv_by_path.get(f"/{slug}/{cat['scene_path']}/")
        if not inv_row or inv_row.get("density") != expected:
            errors.append(f"{slug} inventory density != {expected}")
        if expected == 0 and inv_row and inv_row.get("shortfall") != "no_healthy_pb_fromsll":
            errors.append(f"{slug} inventory must keep water-flosser shortfall")

    if errors:
        print("p2_greenfield_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p2_greenfield_assert ok (pillows 6 / mattresses 8 / office-chairs 8 / water-flossers 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
