#!/usr/bin/env python3
"""Assert the baked /blog/ hub is a real editorial article index."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BLOG = SITE / "blog" / "index.html"
CSS = SITE / "assets" / "css" / "site.css"

_FEED_HREF_RE = re.compile(
    r'<article class="feed-row"[^>]*>.*?<h2 class="feed-title"><a href="([^"]+)"',
    re.S,
)
_SKU_REVIEW_RE = re.compile(r"/reviews/[^\"/]+/")
_COMPARISON_RE = re.compile(r"/comparison/")


def collect_errors(site: Path = SITE) -> list[str]:
    errors: list[str] = []
    blog = site / "blog" / "index.html"
    css = site / "assets" / "css" / "site.css"
    if not blog.is_file() or blog.stat().st_size < 400:
        errors.append("missing or empty blog/index.html")
        return errors
    html = blog.read_text(encoding="utf-8")

    if "<h1>Articles</h1>" not in html:
        errors.append("blog hub H1 should be Articles")
    if 'href="../blog/">Articles</a>' not in html and ">Articles</a>" not in html:
        errors.append("blog hub lost Articles nav")
    if 'class="feed-list"' not in html or "data-blog-feed" not in html:
        errors.append("blog hub missing feed-list")
    rows = html.count('class="feed-row"')
    if rows < 8:
        errors.append(f"blog hub expected a multi-item feed, found {rows} rows")
    hrefs = _FEED_HREF_RE.findall(html)
    if any(_SKU_REVIEW_RE.search(h) for h in hrefs):
        errors.append("blog feed includes a SKU review URL")
    if any(_COMPARISON_RE.search(h) for h in hrefs):
        errors.append("blog feed includes a comparison-chart URL")
    if any(h.rstrip("/").endswith("/pet-homes") for h in hrefs):
        errors.append("blog feed includes a niche/scene page")
    if "how-we-pick-products/" not in html:
        errors.append("blog hub missing How we pick sidebar link")
    if 'class="must-reads-widget"' not in html:
        errors.append("blog hub missing methodology sidebar")
    if "how-we-pick-products/" in "".join(hrefs):
        errors.append("methodology post should stay in the sidebar, not the feed")
    if "CollectionPage" not in html:
        errors.append("blog hub missing CollectionPage JSON-LD")
    if 'rel="canonical" href="https://moretop10.com/blog/"' not in html:
        errors.append("blog hub canonical should stay /blog/")
    if "We may earn a commission" not in html:
        errors.append("blog hub lost affiliate disclosure")
    if "object-fit:cover" in html:
        errors.append("blog hub should not inline object-fit on thumbs")

    if not css.is_file():
        errors.append("missing assets/css/site.css")
        return errors
    css_text = css.read_text(encoding="utf-8")
    if ".blog-hub-page .feed-thumb img" not in css_text:
        errors.append("site.css missing blog-hub thumb img rule")
    thumb_block = css_text.split(".blog-hub-page .feed-thumb img", 1)
    if len(thumb_block) > 1 and "object-fit:cover" not in thumb_block[1][:180]:
        errors.append("blog-hub thumbs must use object-fit:cover")
    return errors


def main() -> int:
    errors = collect_errors(SITE)
    if errors:
        print("blog_hub_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("blog_hub_assert ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
