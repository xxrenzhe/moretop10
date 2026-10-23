#!/usr/bin/env python3
"""P0 SEO/GEO assertions against baked site/ HTML (no network, no deploy)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = ROOT / "site" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from site_config import ALL_CATS  # noqa: E402


def ld_types(html: str) -> set[str]:
    types: set[str] = set()
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue

        def walk(x: object) -> None:
            if isinstance(x, dict):
                t = x.get("@type")
                if isinstance(t, list):
                    types.update(str(i) for i in t)
                elif t:
                    types.add(str(t))
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for i in x:
                    walk(i)

        walk(data)
    return types


def main() -> None:
    errors: list[str] = []
    for cat in ALL_CATS:
        path = SITE / cat["slug"] / "index.html"
        if not path.exists():
            errors.append(f"missing hub {cat['slug']}")
            continue
        html = path.read_text(encoding="utf-8")
        types = ld_types(html)
        for needed in ("CollectionPage", "ItemList"):
            if needed not in types:
                errors.append(f"{cat['slug']} hub missing {needed}")
        if "AggregateRating" in types:
            errors.append(f"{cat['slug']} hub has AggregateRating")
        n = re.search(r'"numberOfItems":(\d+)', html)
        item_count = int(n.group(1)) if n else None
        if item_count is not None and item_count > 10:
            errors.append(f"{cat['slug']} numberOfItems={n.group(1)} > 10")
        # Honest empty drafts (density 0) must not invent Product schema.
        if (item_count or 0) > 0 and "Product" not in types:
            errors.append(f"{cat['slug']} hub missing Product")

    authors = SITE / "authors" / "index.html"
    if not authors.exists():
        errors.append("missing authors hub")
    else:
        html = authors.read_text(encoding="utf-8")
        if "Our editors" not in html:
            errors.append("authors hub H1")
        if "priya-nair/" not in html:
            errors.append("authors hub missing priya-nair")

    llms = (SITE / "llms.txt").read_text(encoding="utf-8")
    well = (SITE / ".well-known" / "llms.txt").read_text(encoding="utf-8")
    if llms != well:
        errors.append("llms.txt dual-path mismatch")
    if "#geo-" not in llms:
        errors.append("llms.txt missing #geo-")
    if "aff_pb_autoads" in llms:
        errors.append("llms backend jargon")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    if "https://moretop10.com/authors/" not in sitemap:
        errors.append("sitemap missing authors hub")
    if "robot-vacuums-match" in sitemap:
        errors.append("sitemap still has match orphan")

    match = (SITE / "robot-vacuums-match" / "index.html").read_text(encoding="utf-8")
    if "noindex,follow" not in match:
        errors.append("match not noindex")

    if errors:
        raise SystemExit("seo_geo_p0_assert failed:\n- " + "\n- ".join(errors))
    print("seo_geo_p0_assert ok")


if __name__ == "__main__":
    main()
