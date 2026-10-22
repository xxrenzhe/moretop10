#!/usr/bin/env python3
"""Baked-site assert: author feed thumbs follow per-page cover SoT."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import (  # noqa: E402
    author_feed_cover_errors,
    author_href_to_site_rel,
    canonical_cover_url,
    iter_author_posts,
)


def main() -> None:
    errors = author_feed_cover_errors(SITE)

    marcus = SITE / "authors" / "marcus-webb" / "index.html"
    if not marcus.exists():
        errors.append("missing authors/marcus-webb/")
    else:
        html = marcus.read_text(encoding="utf-8")
        posts = iter_author_posts(html)
        if len(posts) < 10:
            errors.append(f"marcus-webb expected 10+ posts, got {len(posts)}")

        by_group: dict[str, list[tuple[str, str]]] = {}
        for post in posts:
            href = post["href"]
            thumb = canonical_cover_url(post["thumb"], "authors/marcus-webb/index.html")
            site_rel = author_href_to_site_rel(href)
            group = site_rel.split("/", 1)[0]
            by_group.setdefault(group, []).append((href, thumb))

        for group in ("security-cameras", "video-doorbells", "dash-cams"):
            rows = by_group.get(group, [])
            if len(rows) < 2:
                errors.append(f"marcus-webb missing {group} posts")
                continue
            thumbs = {thumb for _href, thumb in rows}
            hrefs = [href for href, _thumb in rows]
            if any("cmp-hero-" in t for t in thumbs):
                errors.append(f"marcus-webb {group} still uses category cmp-hero")
            if len(thumbs) != len(hrefs):
                errors.append(
                    f"marcus-webb {group} thumbs not unique: {len(thumbs)} covers for {len(hrefs)} posts"
                )

    if errors:
        raise SystemExit("author_feed_covers_assert failed:\n- " + "\n- ".join(errors))
    print("author_feed_covers_assert ok")


if __name__ == "__main__":
    main()
