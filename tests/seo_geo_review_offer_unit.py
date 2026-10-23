#!/usr/bin/env python3
"""Review Article Offer.price must come from a real snapshot/catalog amount.

GSC Rich Results: “should specify price or priceSpecification.price (in offers)”.
Never invent prices — omit a price-less Offer when SoT has no amount.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import apply_review_article, review_snapshot_price  # noqa: E402

RV_CAT = {"slug": "robot-vacuums", "name": "Robot Vacuums & Mops"}
BIKE_CAT = {"slug": "kids-bikes", "name": "Kids Bikes"}

ARTICLE_OFFER_NO_PRICE = (
    '{"@context":"https://schema.org","@type":"Article","headline":"Q10 Review",'
    '"mainEntity":{"@type":"Product","name":"Q10","sku":"B0DWXBCQVP",'
    '"offers":{"@type":"Offer","url":"https://pboost.me/y5piG3lw?uid=fromsll",'
    '"availability":"https://schema.org/InStock"}},'
    '"url":"https://moretop10.com/robot-vacuums/reviews/roborock-q10-s5-robot-vacuum-mop/"}'
)

SNAPSHOT_BAR = (
    '<div class="review-fact"><strong>Price snapshot</strong>'
    '<span>$279.98<span class="review-price-checked"> · checked 2026-10-20</span></span>'
    "</div>"
)


def _page(ld: str, body: str) -> str:
    return (
        "<html><head><title>Q10 Review</title>"
        f'<script type="application/ld+json">{ld}</script>'
        "</head><body>"
        f'<main class="product-review-page"><h1>Q10</h1>{body}</main>'
        "</body></html>"
    )


def _ld_by_type(html: str, type_name: str) -> dict | None:
    for blob in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    ):
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue
        if data.get("@type") == type_name:
            return data
    return None


def _article_offer(html: str) -> dict | None:
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
            offer = entity.get("offers")
            if offer is None:
                return None
            if isinstance(offer, list):
                return offer[0] if offer else None
            return offer if isinstance(offer, dict) else None
    raise AssertionError("no Article/Product JSON-LD")


def main() -> None:
    errors: list[str] = []

    priced = apply_review_article(
        _page(ARTICLE_OFFER_NO_PRICE, SNAPSHOT_BAR),
        RV_CAT,
        "roborock-q10-s5-robot-vacuum-mop",
        [],
    )
    offer = _article_offer(priced)
    if not offer:
        errors.append("snapshot page dropped Offer despite real $279.98")
    else:
        if offer.get("price") != "279.98":
            errors.append(f"snapshot Offer.price={offer.get('price')!r} want '279.98'")
        if offer.get("priceCurrency") != "USD":
            errors.append(f"snapshot priceCurrency={offer.get('priceCurrency')!r}")
        if offer.get("url") != "https://pboost.me/y5piG3lw?uid=fromsll":
            errors.append("snapshot rewrite invented or dropped Offer.url")
        if offer.get("availability") != "https://schema.org/InStock":
            errors.append("snapshot rewrite dropped existing availability")
        if not isinstance(offer.get("price"), str):
            errors.append("Offer.price must be a string of the number")

    no_sot = apply_review_article(
        _page(ARTICLE_OFFER_NO_PRICE, "<p>No snapshot on this page.</p>"),
        RV_CAT,
        "roborock-q10-s5-robot-vacuum-mop",
        [],
    )
    if _article_offer(no_sot) is not None:
        errors.append("no-price page must omit price-less Offer (do not invent)")

    catalog_only = apply_review_article(
        _page(ARTICLE_OFFER_NO_PRICE, "<p>Facts bar missing.</p>"),
        RV_CAT,
        "roborock-q10-s5-robot-vacuum-mop",
        [
            {
                "review_slug": "roborock-q10-s5-robot-vacuum-mop",
                "name": "Q10",
                "price": "279.98",
                "asin": "B0DWXBCQVP",
            }
        ],
    )
    offer = _article_offer(catalog_only)
    if not offer or offer.get("price") != "279.98":
        errors.append("catalog comparison price was not used when snapshot missing")

    bogus = apply_review_article(
        _page(ARTICLE_OFFER_NO_PRICE, "<p>No snapshot.</p>"),
        RV_CAT,
        "roborock-q10-s5-robot-vacuum-mop",
        [
            {
                "review_slug": "roborock-q10-s5-robot-vacuum-mop",
                "name": "Q10",
                "price": "N/A",
            }
        ],
    )
    if _article_offer(bogus) is not None:
        errors.append("non-numeric catalog price must not emit Offer.price")

    zero = apply_review_article(
        _page(
            ARTICLE_OFFER_NO_PRICE,
            '<div class="review-fact"><strong>Price snapshot</strong><span>$0.00</span></div>',
        ),
        RV_CAT,
        "roborock-q10-s5-robot-vacuum-mop",
        [],
    )
    if _article_offer(zero) is not None:
        errors.append("$0.00 snapshot must not become a priced Offer")

    # Real committed pages (in-memory only — no bake, no HTML write).
    samples = [
        (
            SITE
            / "robot-vacuums"
            / "reviews"
            / "roborock-q10-s5-robot-vacuum-mop"
            / "index.html",
            RV_CAT,
            "roborock-q10-s5-robot-vacuum-mop",
            "279.98",
            "B0DWXBCQVP",
        ),
        (
            SITE
            / "kids-bikes"
            / "reviews"
            / "royalbaby-ez-kids-bike-12-20-inch"
            / "index.html",
            BIKE_CAT,
            "royalbaby-ez-kids-bike-12-20-inch",
            "189.99",
            "B0D1Q49LN7",
        ),
        (
            SITE
            / "air-fryers"
            / "reviews"
            / "cosori-twinfry-9-qt-double-air"
            / "index.html",
            {"slug": "air-fryers", "name": "Air Fryers"},
            "cosori-twinfry-9-qt-double-air",
            None,
            "B0GLX9TGJV",
        ),
    ]
    for path, cat, slug, expect_price, asin in samples:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
            continue
        raw = path.read_text(encoding="utf-8")
        before = _article_offer(raw)
        if before and before.get("price"):
            errors.append(f"{path.relative_to(SITE)} already has Offer.price (fixture drift)")
        out = apply_review_article(raw, cat, slug, [])
        offer = _article_offer(out)
        if expect_price is None:
            # Cosori sample: discover snapshot from the page itself.
            snap = re.search(
                r"<strong>Price snapshot</strong>\s*<span>\$([0-9][0-9,]*(?:\.[0-9]{2})?)",
                raw,
            )
            expect_price = snap.group(1).replace(",", "") if snap else None
        if expect_price:
            if not offer or offer.get("price") != expect_price:
                errors.append(
                    f"{path.relative_to(SITE)} Offer.price={None if not offer else offer.get('price')!r} "
                    f"want {expect_price!r}"
                )
            elif offer.get("priceCurrency") != "USD":
                errors.append(f"{path.relative_to(SITE)} missing USD")
        elif offer is not None:
            errors.append(f"{path.relative_to(SITE)} invented Offer without snapshot")
        if "AggregateRating" in out:
            errors.append(f"{path.relative_to(SITE)} leaked AggregateRating")
        if asin and f'id="geo-{asin}"' not in out:
            errors.append(f"{path.relative_to(SITE)} lost #geo-{asin}")

        # Visitor-copy / marketing paths must stay untouched by this pass.
        if "completeness gate" in out or "inventory-blocked" in out or "PartnerBoost" in out:
            errors.append(f"{path.relative_to(SITE)} visitor-copy jargon appeared")
        faq_before = _ld_by_type(raw, "FAQPage")
        faq_after = _ld_by_type(out, "FAQPage")
        if faq_before != faq_after:
            errors.append(f"{path.relative_to(SITE)} FAQ JSON-LD changed (copy-scrub collision)")
        if SNAPSHOT_BAR[:40] in raw and SNAPSHOT_BAR[:40] not in out:
            errors.append(f"{path.relative_to(SITE)} visible Price snapshot markup changed")

    extra_listed = [
        (
            SITE / "hair-dryers" / "reviews" / "laifen-se-2-diffuser-hair-dryer" / "index.html",
            {"slug": "hair-dryers", "name": "Hair Dryers"},
            "laifen-se-2-diffuser-hair-dryer",
        ),
        (
            SITE / "standing-desks" / "reviews" / "fezibo-63-x-37-inch-large" / "index.html",
            {"slug": "standing-desks", "name": "Standing Desks"},
            "fezibo-63-x-37-inch-large",
        ),
    ]
    for path, cat, slug in extra_listed:
        if not path.exists():
            errors.append(f"missing listed URL {path.relative_to(SITE)}")
            continue
        raw = path.read_text(encoding="utf-8")
        snap = review_snapshot_price(raw)
        out = apply_review_article(raw, cat, slug, [])
        offer = _article_offer(out)
        if snap and (not offer or offer.get("price") != snap):
            errors.append(f"{path.relative_to(SITE)} listed URL Offer.price want {snap!r}")
        if not snap and offer is not None:
            errors.append(f"{path.relative_to(SITE)} listed URL invented Offer")

    if errors:
        raise SystemExit("seo_geo_review_offer_unit failed:\n- " + "\n- ".join(errors))
    print("seo_geo_review_offer_unit ok")


if __name__ == "__main__":
    main()
