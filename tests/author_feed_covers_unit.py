#!/usr/bin/env python3
"""Unit tests for author-feed per-page cover resolution (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import (  # noqa: E402
    apply_hub_page,
    author_href_to_site_rel,
    canonical_cover_url,
    cover_to_thumb_src,
    resolve_page_cover,
    rewrite_author_feed_thumbs,
)


def _page(og: str, extra: str = "") -> str:
    return (
        f'<meta property="og:image" content="{og}"/>'
        f"<main>{extra}</main>"
    )


def main() -> None:
    errors: list[str] = []

    product_og = _page(
        "https://moretop10.com/assets/img/products/B0BZ55JZ4S.jpg",
        '<img class="lifestyle-photo" src="../assets/img/lifestyle/cmp-hero-security-cameras.jpg"/>',
    )
    cover = resolve_page_cover(product_og, "security-cameras/index.html")
    if cover != "/assets/img/products/B0BZ55JZ4S.jpg":
        errors.append(f"product og lost to lifestyle: {cover}")

    cmp_og = _page("https://moretop10.com/assets/img/products/B0FF426P7D.jpg")
    if resolve_page_cover(cmp_og, "security-cameras/comparison/index.html") != (
        "/assets/img/products/B0FF426P7D.jpg"
    ):
        errors.append("comparison og not used")

    amazon = _page("https://m.media-amazon.com/images/I/71eXAGbsOjL._AC_SL1500_.jpg")
    if resolve_page_cover(amazon) != (
        "https://m.media-amazon.com/images/I/71eXAGbsOjL._AC_SL1500_.jpg"
    ):
        errors.append("amazon og not kept")

    icon_only = _page(
        "https://moretop10.com/icon-512.png",
        '<img class="review-hero-img" src="../../../assets/img/products/B0CD7NT4Y9.jpg"/>',
    )
    if resolve_page_cover(icon_only, "video-doorbells/reviews/e340/index.html") != (
        "/assets/img/products/B0CD7NT4Y9.jpg"
    ):
        errors.append("icon og should fall through to review-hero packshot")

    lifestyle_only = (
        '<meta property="og:image" content="https://moretop10.com/icon-512.png"/>'
        '<section class="cmp-hero" style="--cmp-hero-bg: url(\'../../assets/img/lifestyle/cmp-hero-dash-cams.jpg\')"></section>'
        "<main><p>no packshot</p></main>"
    )
    if resolve_page_cover(lifestyle_only, "dash-cams/comparison/index.html") != (
        "/assets/img/lifestyle/cmp-hero-dash-cams.jpg"
    ):
        errors.append("lifestyle hero should be last-resort fallback")

    if author_href_to_site_rel("../../security-cameras/comparison/") != (
        "security-cameras/comparison/index.html"
    ):
        errors.append("href resolve comparison")
    if author_href_to_site_rel("../../security-cameras/reviews/eufy-s220/") != (
        "security-cameras/reviews/eufy-s220/index.html"
    ):
        errors.append("href resolve review")

    if cover_to_thumb_src("/assets/img/products/B0BZ55JZ4S.jpg", "../../") != (
        "../../assets/img/products/B0BZ55JZ4S.jpg"
    ):
        errors.append("thumb src site asset")
    if cover_to_thumb_src(
        "https://m.media-amazon.com/images/I/71eXAGbsOjL._AC_SL1500_.jpg", "../../"
    ) != "https://m.media-amazon.com/images/I/71eXAGbsOjL._AC_SL1500_.jpg":
        errors.append("thumb src amazon stays absolute")

    if canonical_cover_url(
        "../../assets/img/products/B0BZ55JZ4S.jpg", "authors/marcus-webb/index.html"
    ) != "/assets/img/products/B0BZ55JZ4S.jpg":
        errors.append("canonical thumb from author page")

    tmp = Path("/tmp/author-feed-cover-unit")
    (tmp / "security-cameras").mkdir(parents=True, exist_ok=True)
    (tmp / "security-cameras" / "comparison").mkdir(parents=True, exist_ok=True)
    (tmp / "security-cameras" / "index.html").write_text(
        _page("https://moretop10.com/assets/img/products/B0BZ55JZ4S.jpg"),
        encoding="utf-8",
    )
    (tmp / "security-cameras" / "comparison" / "index.html").write_text(
        _page("https://moretop10.com/assets/img/products/B0FF426P7D.jpg"),
        encoding="utf-8",
    )
    feed = (
        '<div class="author-posts" data-author-posts>'
        '<article class="author-post-row feed-row" data-author-post>'
        '<div class="author-post-copy"><h3 class="feed-title">'
        '<a href="../../security-cameras/">Hub</a></h3></div>'
        '<a class="author-post-thumb-link" href="../../security-cameras/">'
        '<img class="author-post-thumb feed-thumb" '
        'src="../../assets/img/lifestyle/cmp-hero-security-cameras.jpg" alt=""/>'
        "</a></article>"
        '<article class="author-post-row feed-row" data-author-post>'
        '<div class="author-post-copy"><h3 class="feed-title">'
        '<a href="../../security-cameras/comparison/">Compare</a></h3></div>'
        '<a class="author-post-thumb-link" href="../../security-cameras/comparison/">'
        '<img class="author-post-thumb feed-thumb" '
        'src="../../assets/img/lifestyle/cmp-hero-security-cameras.jpg" alt="" '
        'srcset="../../assets/img/lifestyle/cmp-hero-security-cameras.jpg 231w"/>'
        "</a></article></div>"
    )
    out = rewrite_author_feed_thumbs(feed, site_root=tmp, prefix="../../")
    if "cmp-hero-security-cameras.jpg" in out:
        errors.append("rewrite left category lifestyle thumbs")
    if out.count("../../assets/img/products/B0BZ55JZ4S.jpg") != 1:
        errors.append("hub thumb not set to hub og packshot")
    if out.count("../../assets/img/products/B0FF426P7D.jpg") != 1:
        errors.append("comparison thumb not set to comparison og packshot")
    if "srcset=" in out:
        errors.append("stale srcset should be dropped when src changes")

    applied = apply_hub_page(
        feed,
        kind="author",
        cat=None,
        cmp_html=None,
        prefix="../../",
        site_root=tmp,
    )
    if "B0BZ55JZ4S.jpg" not in applied or "B0FF426P7D.jpg" not in applied:
        errors.append("apply_hub_page author kind did not rewrite thumbs")

    if errors:
        raise SystemExit("author_feed_covers_unit failed:\n- " + "\n- ".join(errors))
    print("author_feed_covers_unit ok")


if __name__ == "__main__":
    main()
