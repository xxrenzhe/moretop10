#!/usr/bin/env python3
"""P1a scene best-of / niche draft pages — no leftover bedroom chrome, live tracks only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p1a_scene_pages import (  # noqa: E402
    DRAFT_COMMENT,
    SCENE_ASINS,
    TEMPLATE_LEFTOVER,
    healthy_track,
    load_category,
)

PAGES = (
    (
        "dehumidifiers/best-dehumidifiers-for-basements/index.html",
        "dehumidifiers-basements",
        "dehumidifiers",
        "/dehumidifiers/best-dehumidifiers-for-basements/",
    ),
    (
        "air-purifiers/best-air-purifiers-for-pets/index.html",
        "air-purifiers-pets",
        "air-purifiers",
        "/air-purifiers/best-air-purifiers-for-pets/",
    ),
    (
        "robot-vacuums/pet-homes/index.html",
        "robot-vacuums-pet-homes",
        "robot-vacuums",
        "/robot-vacuums/pet-homes/",
    ),
)


def main() -> int:
    errors: list[str] = []
    inv_path = SITE / "data" / "p1a-scene-inventory-2026-10-23.json"
    if not inv_path.exists():
        errors.append("missing inventory json")
        print("p1a_scene_assert failed:\n- " + "\n- ".join(errors))
        return 1
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")

    for rel, scene_key, slug, url_path in PAGES:
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
        if html.count('class="bestof-visit-card"') != 10:
            errors.append(f"{rel} visit cards != 10")
        if url_path not in sitemap and f"https://moretop10.com{url_path}" not in sitemap:
            errors.append(f"sitemap missing {url_path}")

        cmp, _land = load_category(slug)
        cmp_order = list(cmp)
        scene_order = SCENE_ASINS[scene_key]
        if scene_order == cmp_order[:10]:
            errors.append(f"{rel} pasted comparison order")
        for asin in scene_order:
            if asin not in cmp:
                errors.append(f"{rel} ASIN {asin} not on live comparison")
                continue
            track = healthy_track(cmp[asin].get("cta"))
            if not track:
                errors.append(f"{rel} unhealthy track {asin}")

        landing = (SITE / slug / "index.html").read_text(encoding="utf-8")
        if url_path.rstrip("/") not in landing and url_path not in landing:
            # landings use ../{slug}/{scene}/
            tail = url_path.rstrip("/").split("/", 2)[-1]
            if tail not in landing:
                errors.append(f"{slug} landing missing cluster link {url_path}")

    if errors:
        print("p1a_scene_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p1a_scene_assert ok (3 draft scene pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
