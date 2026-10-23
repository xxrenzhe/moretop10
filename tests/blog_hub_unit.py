#!/usr/bin/env python3
"""Unit tests for /blog/ article-index classifier and ordering (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from build_blog import (  # noqa: E402
    classify_editorial,
    render_feed_row,
    site_rel_to_href,
    sort_articles,
)


INCLUDE = {
    "tv/index.html": ("guide", "tv"),
    "tv/remove-smart-tv-ads/index.html": ("how-to", "tv"),
    "tv/smart-tv-ad-alternatives/index.html": ("alternatives", "tv"),
    "tv/best-tv-for-privacy/index.html": ("best-of", "tv"),
    "tv/samsung-smart-tv-ads/index.html": ("guide", "tv"),
    "kids-bikes/how-to-choose-a-kids-bike/index.html": ("how-to", "kids-bikes"),
    "kids-bikes/royalbaby-ez-vs-dual-handbrake/index.html": ("versus", "kids-bikes"),
    "kids-bikes/premium-kids-bike-alternatives/index.html": ("alternatives", "kids-bikes"),
    "kids-bikes/best-balance-to-pedal-kids-bikes/index.html": ("best-of", "kids-bikes"),
    "humidifiers/best-humidifiers-for-bedrooms/index.html": ("best-of", "humidifiers"),
    "espresso-machines/premium-espresso-machine-alternatives/index.html": (
        "alternatives",
        "espresso-machines",
    ),
    "robot-vacuums/top-reads/index.html": ("top-reads", "robot-vacuums"),
    "blog/how-to-read-a-shortlist/index.html": ("article", "blog"),
}

EXCLUDE = (
    "index.html",
    "robot-vacuums/index.html",
    "robot-vacuums/comparison/index.html",
    "robot-vacuums/reviews/index.html",
    "robot-vacuums/reviews/eufy-e25-robot-vacuum-mop-combo/index.html",
    "blog/index.html",
    "blog/how-we-pick-products/index.html",
    "about-us/index.html",
    "authors/priya-nair/index.html",
    "contact/index.html",
    "privacy-policy/index.html",
    "robot-vacuums-match/index.html",
    # In-flight scene / niche PRs — do not treat as Articles rows.
    "robot-vacuums/pet-homes/index.html",
    "dehumidifiers/basement/index.html",
    "litter-boxes/pets/index.html",
)


def main() -> int:
    errors: list[str] = []

    for rel, expected in INCLUDE.items():
        got = classify_editorial(rel)
        if got != expected:
            errors.append(f"include {rel}: expected {expected}, got {got}")

    for rel in EXCLUDE:
        got = classify_editorial(rel)
        if got is not None:
            errors.append(f"exclude {rel}: expected None, got {got}")

    if site_rel_to_href("kids-bikes/how-to-choose-a-kids-bike/index.html") != (
        "../kids-bikes/how-to-choose-a-kids-bike/"
    ):
        errors.append("href resolve how-to")
    if site_rel_to_href("tv/index.html") != "../tv/":
        errors.append("href resolve tv hub")

    ordered = sort_articles(
        [
            {
                "title": "Older how-to",
                "date": "2026-10-01",
                "kind": "how-to",
            },
            {
                "title": "Zebra later",
                "date": "2026-10-23",
                "kind": "best-of",
            },
            {
                "title": "Alpha later",
                "date": "2026-10-23",
                "kind": "how-to",
            },
            {
                "title": "Undated",
                "date": "",
                "kind": "guide",
            },
        ]
    )
    titles = [a["title"] for a in ordered]
    if titles != ["Alpha later", "Zebra later", "Older how-to", "Undated"]:
        errors.append(f"sort order {titles}")

    row = render_feed_row(
        {
            "href": "../tv/remove-smart-tv-ads/",
            "title": "How to remove smart TV ads",
            "excerpt": "Software first.",
            "date": "2026-10-23",
            "kind": "how-to",
            "kind_label": "How-to",
            "category": "tv",
            "category_label": "Smart TV ads",
        },
        thumb_src="../assets/img/lifestyle/devices-mockup.jpg",
    )
    if 'class="feed-row"' not in row:
        errors.append("row missing feed-row")
    if 'class="feed-thumb"' not in row or "<img " not in row:
        errors.append("row missing thumb wrapper")
    if "author-post-thumb" in row:
        errors.append("blog row should not use author-post-thumb")
    if "object-fit" in row:
        errors.append("object-fit belongs in CSS, not markup")

    if errors:
        print("blog_hub_unit failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("blog_hub_unit ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
