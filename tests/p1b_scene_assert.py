#!/usr/bin/env python3
"""P1b scenario best-of draft pages — no leftover bedroom chrome, live tracks only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p1b_scene_pages import (  # noqa: E402
    CLUSTER_LINKS,
    DRAFT_COMMENT,
    SCENE_ASINS,
    TEMPLATE_LEFTOVER,
    healthy_track,
    load_category,
)

PAGES = (
    (
        "air-purifiers/best-air-purifiers-for-allergies/index.html",
        "air-purifiers-allergies",
        "air-purifiers",
        "/air-purifiers/best-air-purifiers-for-allergies/",
    ),
    (
        "air-purifiers/best-air-purifiers-for-mold/index.html",
        "air-purifiers-mold",
        "air-purifiers",
        "/air-purifiers/best-air-purifiers-for-mold/",
    ),
    (
        "air-purifiers/best-air-purifiers-for-bedrooms/index.html",
        "air-purifiers-bedrooms",
        "air-purifiers",
        "/air-purifiers/best-air-purifiers-for-bedrooms/",
    ),
    (
        "air-purifiers/best-air-purifiers-for-dust/index.html",
        "air-purifiers-dust",
        "air-purifiers",
        "/air-purifiers/best-air-purifiers-for-dust/",
    ),
    (
        "air-purifiers/best-air-purifiers-for-smoke/index.html",
        "air-purifiers-smoke",
        "air-purifiers",
        "/air-purifiers/best-air-purifiers-for-smoke/",
    ),
    (
        "air-purifiers/best-air-purifiers-for-large-rooms/index.html",
        "air-purifiers-large-rooms",
        "air-purifiers",
        "/air-purifiers/best-air-purifiers-for-large-rooms/",
    ),
    (
        "humidifiers/best-humidifiers-for-babies/index.html",
        "humidifiers-babies",
        "humidifiers",
        "/humidifiers/best-humidifiers-for-babies/",
    ),
    (
        "standing-desks/best-standing-desks-for-home-office/index.html",
        "standing-desks-home-office",
        "standing-desks",
        "/standing-desks/best-standing-desks-for-home-office/",
    ),
)


def main() -> int:
    errors: list[str] = []
    inv_path = SITE / "data" / "p1b-scene-inventory-2026-10-23.json"
    if not inv_path.exists():
        errors.append("missing inventory json")
        print("p1b_scene_assert failed:\n- " + "\n- ".join(errors))
        return 1
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")
    if not (SITE / "data" / "p1b-scene-inventory-2026-10-23.md").exists():
        errors.append("missing inventory markdown")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    seen_orders: dict[str, tuple[str, ...]] = {}

    for rel, scene_key, slug, url_path in PAGES:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if DRAFT_COMMENT not in html:
            errors.append(f"{rel} missing draft comment")
        if 'name="robots" content="index,follow' not in html:
            errors.append(f"{rel} robots is not index,follow")
        for leak in TEMPLATE_LEFTOVER:
            if leak in html:
                errors.append(f"{rel} leftover {leak!r}")
        if html.count('class="bestof-visit-card"') != 10:
            errors.append(f"{rel} visit cards != 10")
        loc = f"https://moretop10.com{url_path}"
        loc_at = sitemap.find(f"<loc>{loc}</loc>")
        if loc_at < 0:
            errors.append(f"sitemap missing {url_path}")
        else:
            block = sitemap[loc_at : loc_at + 180]
            if "2026-10-23" not in block:
                errors.append(f"sitemap lastmod not bumped for {url_path}")

        cmp, _land = load_category(slug)
        cmp_order = list(cmp)
        scene_order = SCENE_ASINS[scene_key]
        seen_orders[scene_key] = tuple(scene_order)
        if scene_order == cmp_order[:10]:
            errors.append(f"{rel} pasted comparison order")
        if len(scene_order) != 10 or len(set(scene_order)) != 10:
            errors.append(f"{rel} scene order is not 10 unique ASINs")
        for asin in scene_order:
            if asin not in cmp:
                errors.append(f"{rel} ASIN {asin} not on live comparison")
                continue
            track = healthy_track(cmp[asin].get("cta"))
            if not track:
                errors.append(f"{rel} unhealthy track {asin}")
            elif "pboost.me" not in track or "uid=fromsll" not in track:
                errors.append(f"{rel} track is not healthy PB uid=fromsll {asin}")

        landing = (SITE / slug / "index.html").read_text(encoding="utf-8")
        tail = url_path.rstrip("/").rsplit("/", 1)[-1]
        if tail not in landing:
            errors.append(f"{slug} landing missing cluster link {url_path}")

        # Reviews: Top/Upgrade reuse only — do not require new review files.
        page_row = next((p for p in inv.get("pages", []) if p.get("path") == url_path), None)
        if page_row:
            if page_row.get("new_reviews"):
                errors.append(f"{rel} inventory lists new reviews")
            for role in ("top_pick", "upgrade"):
                rec = page_row.get(role) or {}
                if not rec.get("review_exists"):
                    errors.append(f"{rel} {role} review missing")
                if rec.get("track_ok") is not True:
                    errors.append(f"{rel} {role} track not ok")

    ap_orders = [v for k, v in seen_orders.items() if k.startswith("air-purifiers-")]
    if len(set(ap_orders)) != len(ap_orders):
        errors.append("two air-purifier scenes share the same ASIN order")

    for slug, href, label in CLUSTER_LINKS:
        landing = (SITE / slug / "index.html").read_text(encoding="utf-8")
        if href not in landing and label not in landing:
            errors.append(f"{slug} landing missing {label}")

    if errors:
        print("p1b_scene_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p1b_scene_assert ok (8 draft scene pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
