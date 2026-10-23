#!/usr/bin/env python3
"""Review/product JSON-LD: remaining GSC Product + Merchant fields.

Emit only from SoT already on the page. Never invent stock, stars, quotes,
return windows, or shipping.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import (  # noqa: E402
    apply_review_article,
    extract_comparison_products,
    product_node,
)

RV_CAT = {"slug": "robot-vacuums", "name": "Robot Vacuums & Mops"}

LONG_NAME = (
    "Dreame Pocket Pro Hair Dryer, Dual Voltage Travel Blow Dryer with Diffuser, "
    "1300W Professional HighSpeed Ionic Hair Blower, Fast Drying, Low Noise, "
    "Lightweight, No Heat Damage, Global Travel 120V/240V"
)

ARTICLE_LD = (
    '{"@context":"https://schema.org","@type":"Article","headline":"Q10 Review",'
    '"mainEntity":{"@type":"Product","name":'
    + json.dumps(LONG_NAME)
    + ',"sku":"B0DWXBCQVP",'
    '"offers":{"@type":"Offer","url":"https://pboost.me/y5piG3lw?uid=fromsll",'
    '"availability":"https://schema.org/InStock"}},'
    '"url":"https://moretop10.com/robot-vacuums/reviews/roborock-q10-s5-robot-vacuum-mop/"}'
)

BODY = """
<div class="meta-row"><span class="stars" aria-label="4.0 out of 5">★★★★☆</span></div>
<div class="review-fact"><strong>Price snapshot</strong><span>$279.98</span></div>
<div class="review-fact"><strong>Retailer reviews</strong><span>20609 reviews</span></div>
<p class="review-summary">Buy the roborock Q10 S5+ if you want high-powered 10,000 Pa suction.</p>
"""


def _page(ld: str, body: str) -> str:
    return (
        "<html><head><title>Q10 Review</title>"
        f'<script type="application/ld+json">{ld}</script>'
        "</head><body>"
        f'<main class="product-review-page"><h1>Q10</h1>{body}</main>'
        "</body></html>"
    )


def _article_product(html: str) -> dict:
    for blob in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    ):
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if data.get("@type") != "Article":
            continue
        entity = data.get("mainEntity")
        if isinstance(entity, dict) and entity.get("@type") == "Product":
            return entity
    raise AssertionError("no Article/Product JSON-LD")


def main() -> None:
    errors: list[str] = []

    out = apply_review_article(
        _page(ARTICLE_LD, BODY),
        RV_CAT,
        "roborock-q10-s5-robot-vacuum-mop",
        [],
    )
    product = _article_product(out)
    offer = product.get("offers")
    if not isinstance(offer, dict):
        errors.append("priced snapshot lost Offer")
        offer = {}

    if offer.get("price") != "279.98" or offer.get("priceCurrency") != "USD":
        errors.append(f"price/currency missing: {offer}")
    if "availability" in offer:
        errors.append("kept InStock without a catalog stock signal")
    if offer.get("hasMerchantReturnPolicy") or offer.get("shippingDetails"):
        errors.append("invented merchant return/shipping")

    rating = product.get("aggregateRating")
    if not isinstance(rating, dict):
        errors.append("missing retailer AggregateRating")
    else:
        if str(rating.get("ratingValue")) != "4.0":
            errors.append(f"ratingValue={rating.get('ratingValue')!r} want 4.0")
        if int(str(rating.get("ratingCount") or 0)) != 20609:
            errors.append(f"ratingCount={rating.get('ratingCount')!r} want 20609")
        if str(rating.get("bestRating") or "5") != "5":
            errors.append("bestRating should be 5 (retailer stars)")

    review = product.get("review")
    if isinstance(review, list):
        review = review[0] if review else None
    if not isinstance(review, dict) or review.get("@type") != "Review":
        errors.append("missing editorial Review from review-summary")
    else:
        body = review.get("reviewBody") or ""
        if "10,000 Pa" not in body:
            errors.append("Review.reviewBody not from review-summary")
        if review.get("reviewRating"):
            errors.append("invented Review.reviewRating stars")
        author = review.get("author") or {}
        if author.get("name") != "MoreTop10":
            errors.append("Review.author should be MoreTop10")

    if "10,000 Pa" not in (product.get("description") or ""):
        errors.append("Product.description not from review-summary")
    if len(product.get("name") or "") > 150:
        errors.append(f"Product.name length {len(product['name'])} > 150")
    if not (product.get("name") or "").startswith("Dreame Pocket Pro"):
        errors.append("name truncate invented a new title")

    no_rating = apply_review_article(
        _page(
            ARTICLE_LD,
            '<div class="review-fact"><strong>Price snapshot</strong><span>$279.98</span></div>'
            "<p>No stars or retailer count.</p>",
        ),
        RV_CAT,
        "roborock-q10-s5-robot-vacuum-mop",
        [],
    )
    bare = _article_product(no_rating)
    if bare.get("aggregateRating"):
        errors.append("invented aggregateRating without retailer stars+count")
    if bare.get("review"):
        errors.append("invented Review without review-summary")

    # Real committed pages (in-memory).
    samples = [
        (
            SITE
            / "robot-vacuums"
            / "reviews"
            / "roborock-q10-s5-robot-vacuum-mop"
            / "index.html",
            RV_CAT,
            "roborock-q10-s5-robot-vacuum-mop",
            "4.0",
            20609,
        ),
        (
            SITE
            / "kids-bikes"
            / "reviews"
            / "royalbaby-ez-kids-bike-12-20-inch"
            / "index.html",
            {"slug": "kids-bikes", "name": "Kids Bikes"},
            "royalbaby-ez-kids-bike-12-20-inch",
            "4.6",
            3000,
        ),
        (
            SITE
            / "air-fryers"
            / "reviews"
            / "cosori-twinfry-9-qt-double-air"
            / "index.html",
            {"slug": "air-fryers", "name": "Air Fryers"},
            "cosori-twinfry-9-qt-double-air",
            "4.7",
            1061,
        ),
    ]
    for path, cat, slug, stars, count in samples:
        raw = path.read_text(encoding="utf-8")
        product = _article_product(apply_review_article(raw, cat, slug, []))
        offer = product.get("offers") or {}
        if offer.get("availability"):
            errors.append(f"{path.relative_to(SITE)} still has unbacked availability")
        if offer.get("hasMerchantReturnPolicy") or offer.get("shippingDetails"):
            errors.append(f"{path.relative_to(SITE)} invented return/shipping")
        rating = product.get("aggregateRating") or {}
        if str(rating.get("ratingValue")) != stars:
            errors.append(f"{path.relative_to(SITE)} ratingValue={rating.get('ratingValue')!r}")
        if int(str(rating.get("ratingCount") or 0)) != count:
            errors.append(f"{path.relative_to(SITE)} ratingCount={rating.get('ratingCount')!r}")
        if not (product.get("description") or "").strip():
            errors.append(f"{path.relative_to(SITE)} missing description")
        review = product.get("review")
        if isinstance(review, list):
            review = review[0] if review else None
        if not isinstance(review, dict) or not review.get("reviewBody"):
            errors.append(f"{path.relative_to(SITE)} missing editorial Review")
        elif review.get("reviewRating"):
            errors.append(f"{path.relative_to(SITE)} invented reviewRating")
        if len(product.get("name") or "") > 150:
            errors.append(f"{path.relative_to(SITE)} name still {len(product['name'])} chars")

    card = (
        '<article class="product-card" data-asin="B0DX1DQKMD" data-position="1" '
        'data-product-name="Roborock Qrevo CurvX Robot Vacuum and Mop, 22,000Pa">'
        '<div class="pc-name">Roborock Qrevo CurvX</div>'
        '<a class="pc-reviews-link" href="../reviews/roborock-qrevo-curvx-robot-vacuum-mop/">'
        "5,629 reviews</a>"
        "<p class='pc-tagline'>With 22000Pa HyperForce suction and Zero-Tangling Design…</p>"
        '<span class="stars" aria-label="4.2 out of 5">★★★★☆</span>'
        '<span class="pc-price-value">$1199.99</span>'
        "</article>"
    )
    extracted = extract_comparison_products(card, "robot-vacuums")
    if not extracted:
        errors.append("extract_comparison_products returned no card")
    else:
        row = extracted[0]
        if row.get("rating_value") != "4.2" or row.get("rating_count") != 5629:
            errors.append(f"card rating SoT not extracted: {row}")
        if "22000Pa" not in (row.get("description") or ""):
            errors.append("card tagline not extracted as description")
        node = product_node(row, "robot-vacuums", "https://moretop10.com/robot-vacuums/comparison/")
        if (node.get("aggregateRating") or {}).get("ratingValue") != "4.2":
            errors.append("product_node missing retailer aggregateRating")
        if "22000Pa" not in (node.get("description") or ""):
            errors.append("product_node missing card description")
        offer = node.get("offers") or {}
        if offer.get("availability"):
            errors.append("product_node invented availability")
        if node.get("review"):
            errors.append("product_node invented Review without editorial body")

    if errors:
        raise SystemExit("seo_geo_review_merchant_unit failed:\n- " + "\n- ".join(errors))
    print("seo_geo_review_merchant_unit ok")


if __name__ == "__main__":
    main()
