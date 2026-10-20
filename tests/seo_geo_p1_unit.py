#!/usr/bin/env python3
"""Unit tests for P1 cite / geo / robots helpers (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import (  # noqa: E402
    ROBOTS_INDEX,
    has_html_class,
    inject_cite_strip,
    inject_geo_anchors,
    inject_rev_hub_geo,
    inject_review_geo,
    mark_answer_first,
    set_robots_meta,
)


def main() -> None:
    errors: list[str] = []
    products = [
        {
            "asin": "B0GLX9TGJV",
            "pick_id": "pick-1",
            "review_slug": "cosori-twinfry-9-qt-double-air",
            "position": 1,
            "name": "COSORI TwinFry",
        }
    ]

    landing = '<section class="landing-pick" id="pick-1"><h2>TwinFry</h2></section>'
    out = inject_geo_anchors(landing, products)
    if 'id="geo-B0GLX9TGJV"' not in out:
        errors.append("landing pick missing geo anchor")

    card = (
        '<article class="product-card" data-asin="B0GLX9TGJV" data-role="" data-position="1"\n'
        '  data-sticky="product-card" data-product-name="COSORI TwinFry">body</article>'
        '<article class="product-card" data-asin="B0DD3QTMV5">other</article>'
    )
    # Comparison products have ASIN but no pick_id (P0 bug: skipped geo ids).
    cmp_products = [{"asin": "B0GLX9TGJV", "position": 1, "name": "COSORI TwinFry"}]
    out = inject_geo_anchors(card, cmp_products)
    if 'id="geo-B0GLX9TGJV"' not in out:
        errors.append("multiline comparison card missing geo id")
    if out.count('id="geo-B0GLX9TGJV"') != 1:
        errors.append("comparison geo id duplicated")

    misplaced = (
        "<main>"
        '<article class="product-card">first</article>'
        '<aside class="geo-cite-strip">old</aside>'
        '<article class="product-card">second</article>'
        "</main><footer></footer>"
    )
    out = inject_cite_strip(misplaced, "Best Air Fryers of 2026", "https://moretop10.com/air-fryers/comparison/", "2026-10-20")
    if out.find("geo-cite-strip") < out.rfind('class="product-card"'):
        errors.append("cite strip still before last product card")
    if "How to cite:" not in out:
        errors.append("cite strip missing How to cite label")
    if out.count("geo-cite-strip") != 1:
        errors.append("cite strip not unique after relocate")

    hub = (
        '<article class="rev-hub-card">'
        "<h2>TwinFry</h2>"
        '<a class="rev-hub-read" href="cosori-twinfry-9-qt-double-air/">Read</a>'
        '<img src="../../assets/img/products/B0GLX9TGJV.jpg" alt=""/>'
        "</article>"
    )
    out = inject_rev_hub_geo(hub, products)
    if 'id="geo-B0GLX9TGJV"' not in out:
        errors.append("reviews hub card missing geo id")

    review = '<main class="product-review-page"><h1>TwinFry</h1></main>'
    out = inject_review_geo(review, "B0GLX9TGJV")
    if 'id="geo-B0GLX9TGJV"' not in out:
        errors.append("review article missing geo anchor")

    robots = set_robots_meta('<head><meta name="robots" content="index,follow"/></head>', ROBOTS_INDEX)
    if ROBOTS_INDEX not in robots:
        errors.append("robots meta not upgraded to max-image-preview")

    # JSON-LD Speakable cssSelector ".geo-answer-first" must not skip the HTML class.
    cmp_html = (
        '<script type="application/ld+json">'
        '{"speakable":{"cssSelector":[".cmp-answer-first",".geo-answer-first"]}}'
        "</script>"
        '<section class="cmp-answer-first prose-block"><p>Quick answer with $129.00.</p></section>'
    )
    out = mark_answer_first(cmp_html, "comparison")
    if not has_html_class(out, "geo-answer-first"):
        errors.append("comparison mark_answer_first skipped HTML class because JSON-LD mentioned it")
    if 'class="cmp-answer-first geo-answer-first' not in out:
        errors.append("comparison Answer-first class not merged onto cmp-answer-first")

    if errors:
        raise SystemExit("seo_geo_p1_unit failed:\n- " + "\n- ".join(errors))
    print("seo_geo_p1_unit ok")


if __name__ == "__main__":
    main()
