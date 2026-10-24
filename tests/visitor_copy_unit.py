#!/usr/bin/env python3
"""Visitor-copy jargon / US-English rewrites (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import (  # noqa: E402
    AMAZON_DISCLAIMER,
    EDITORIAL_ONLY,
    PUBLISH_RULE,
    RETAILER_CONFIRM,
    UNPUBLISHED_UNTIL_TEN,
    VISITOR_LEAK_RE,
    html_without_ld_json,
    rewrite_visible_jargon,
    scrub_jargon,
)


def main() -> int:
    errors: list[str] = []

    cases = [
        (
            "We only publish products that clear our completeness gate: "
            "title, gallery, price snapshot, and a healthy affiliate CTA.",
            PUBLISH_RULE,
        ),
        (
            "We only publish products that clear our card checklist: "
            "title, gallery, price snapshot, and a healthy affiliate CTA.",
            PUBLISH_RULE,
        ),
        (
            "A category that cannot fill ten stays inventory-blocked—we do not ship a short chart.",
            UNPUBLISHED_UNTIL_TEN,
        ),
        (
            "A category that cannot fill ten stays held—we do not ship a short chart.",
            UNPUBLISHED_UNTIL_TEN,
        ),
        (
            "Draft card from PartnerBoost L1 — Mac L2 required before publish.",
            RETAILER_CONFIRM,
        ),
        (
            "RoyalBaby EZ balance-to-pedal replacement after Mac CDP blocked the prior chart #1 variant.",
            RETAILER_CONFIRM,
        ),
        (
            "the newly upgraded pads offer twice the anti-stick performance, whilst the waterproof material helps",
            "the newly upgraded pads offer twice the anti-stick performance, while the waterproof material helps",
        ),
        (
            "worth pushing your budget towards $300",
            "worth pushing your budget toward $300",
        ),
        (
            "Utilize double ducts to provide fast symptom relief",
            "Use double ducts to provide fast symptom relief",
        ),
        (
            "Confirm size on the retailer page. Snapshot $23.99.",
            "Confirm size on the retailer page. $23.99.",
        ),
        (
            "No healthy track in current PB∪YP feed. Decision-tree slot stays empty.",
            "No retailer link yet.",
        ),
        (
            "No healthy track. Do not invent a Walmart or Amazon hop.",
            "No retailer link yet.",
        ),
        (
            "L5 inventory still empty. Content-only.",
            EDITORIAL_ONLY,
        ),
        (
            "Always confirm on the retailer page before you buy—tax, shipping, and coupons can change the final total.",
            f"{AMAZON_DISCLAIMER}—tax, shipping, and coupons can change the final total.",
        ),
        (
            "those pages stay content-only until a real track exists.",
            f"those pages stay {EDITORIAL_ONLY}.",
        ),
        (
            "JMGO tracker, help centre with a preinstall downloader",
            "JMGO tracker, help center with a preinstall downloader",
        ),
        (
            "These decision-tree slots stay visible and empty. "
            "A missing button is better than a made-up link. Content-only follow-ups:",
            "These options stay listed even when we don't have a checkout link yet. "
            "A missing button is better than a made-up link. Related guides:",
        ),
        (
            "Chart prices are a  listing check (ZIP 10001)—not a live cart.",
            "Chart prices are a listing check (ZIP 10001)—not a live cart.",
        ),
        (
            "Prices and Check price come from  L2 plus a verified our retail partner fromsll track.",
            "Prices and Check price come from a checked retailer listing.",
        ),
        (
            "10 ASINs remain after accessory exclusions.",
            "10 products remain after we dropped accessories.",
        ),
        (
            "when L2 returned one",
            "when the listing included a star rating",
        ),
        (
            "A deep review lands after deploy.",
            "A deeper review will follow.",
        ),
        (
            "RoyalBaby EZ (12–20 inch Balance & Pedal, snapshot $239.99)",
            "RoyalBaby EZ (12–20 inch Balance & Pedal, $239.99)",
        ),
        (
            "<li><strong>Snapshot price:</strong> $75.99</li>",
            "<li><strong>Price:</strong> $75.99</li>",
        ),
        (
            "Holds a 4.7 rating with a price snapshot of $129.99, while qualifying for HSA.",
            f"Holds a 4.7 rating with a current price about $129.99 — {AMAZON_DISCLAIMER}, while qualifying for HSA.",
        ),
        (
            "listed at a snapshot price of $129.99 under ASIN B0F836S79D",
            f"listed at current price about $129.99 — {AMAZON_DISCLAIMER}",
        ),
        (
            "at a $139.99 price snapshot (ASIN: B0F4KQ3D34)",
            "at about $139.99",
        ),
        (
            "<strong>Snapshot value and HSA eligibility:</strong>",
            "<strong>Price and HSA eligibility:</strong>",
        ),
        (
            "The Dual Handbrake beginners bike (ASIN B0CPDZ7R5P) is a Freestyle-class pedal bike.",
            "The Dual Handbrake beginners bike is a Freestyle-class pedal bike.",
        ),
        (
            "We will not invent an ASIN to fill the slot.",
            "We will not invent a product to fill the slot.",
        ),
        (
            "None yet. We will scene-reorder the parent shortlist when healthy tracks land — not comparison order.",
            "None yet. We will scene-reorder the parent shortlist when verified retailer links land — not comparison order.",
        ),
        (
            "Density is honest at 0 — we do not invent ASINs, prices, images, or discounts.",
            "Density is honest at 0 — we do not invent product listings, prices, images, or discounts.",
        ),
    ]
    leaks = (
        "Snapshot $2997.99 · confirm on the retailer page",
        "Always confirm on the retailer page before you buy",
        "help centre with a preinstall downloader",
        "those pages stay content-only until a real track exists",
        "No healthy track in current PB∪YP feed. Decision-tree slot stays empty.",
        "L5 inventory still empty. Content-only.",
        "No healthy track. Do not invent a Walmart or Amazon hop.",
        "Prices and Check price come from  L2 plus a verified our retail partner fromsll track.",
        "10 ASINs remain after accessory exclusions.",
        "A deep review lands after deploy.",
        "snapshot $239.99",
        "Snapshot price: $75.99",
        "price snapshot of $129.99",
        "Snapshot pricing and standing",
        "Snapshot value and HSA",
        "(ASIN: B0F4KQ3D34)",
        "under ASIN B0F836S79D",
        "We will not invent an ASIN to fill the slot.",
        "when healthy tracks land",
        "we do not invent ASINs, prices",
    )
    for leak in leaks:
        if not VISITOR_LEAK_RE.search(leak):
            errors.append(f"leak regex missed {leak!r}")

    for src, want in cases:
        got = scrub_jargon(src)
        if want not in got:
            errors.append(f"scrub missed {src!r} → {got!r} (want {want!r})")
        if VISITOR_LEAK_RE.search(got):
            errors.append(f"scrub leftover leak in {got!r}")

    html = (
        '<meta name="description" content="Draft card from PartnerBoost L1 — Mac L2 required before publish."/>'
        "<li><strong>#1 — Bike:</strong> Draft card from PartnerBoost L1 — Mac L2 required before publish.</li>"
        "<p class='pc-tagline'>RoyalBaby EZ balance-to-pedal replacement after Mac CDP blocked…</p>"
        "<p>We only publish products that clear our card checklist: "
        "title, gallery, price snapshot, and a healthy affiliate CTA.</p>"
        '<a href="https://pboost.me/W5qh2g8d?uid=fromsll">Check price</a>'
        '<a href="https://yeahpromos.com/index/index/openurlproduct?track=abc">YP</a>'
        '<time datetime="2026-10-20T12:00:00Z">2026-10-20</time>'
    )
    out = rewrite_visible_jargon(html)
    if "PartnerBoost" in out or "Mac L2" in out or "card checklist" in out:
        errors.append("HTML rewrite left leak tokens")
    if "uid=fromsll" not in out:
        errors.append("rewrote affiliate track URL")
    if "yeahpromos.com" not in out or "our retail partner.com" in out:
        errors.append("rewrote YeahPromos affiliate hostname")
    if 'datetime="2026-10-20T12:00:00Z"' not in out:
        errors.append("rewrote time datetime")
    if PUBLISH_RULE not in out:
        errors.append("HTML rewrite missed publish rule")
    if "<p class='pc-tagline'>" not in out or "</p>" not in out:
        errors.append("Mac CDP rewrite ate surrounding tags")

    if VISITOR_LEAK_RE.search(PUBLISH_RULE):
        errors.append("leak regex flagged approved #35 price snapshot phrase")
    if VISITOR_LEAK_RE.search(AMAZON_DISCLAIMER):
        errors.append("leak regex flagged approved Amazon shopping disclaimer")
    if VISITOR_LEAK_RE.search(EDITORIAL_ONLY):
        errors.append("leak regex flagged approved editorial-only phrase")
    if VISITOR_LEAK_RE.search(RETAILER_CONFIRM):
        errors.append("leak regex flagged approved retailer-confirm phrase")

    ld_html = (
        '<script type="application/ld+json">'
        '{"@type":"Offer","price":"199.99","priceCurrency":"USD",'
        '"description":"price snapshot of $199.99 (ASIN: B0FD2VBCKN)"}'
        "</script>"
        "<p>Shortlist standing at a price snapshot of $199.99 (ASIN: B0FD2VBCKN).</p>"
        f"<p>{PUBLISH_RULE}</p>"
    )
    ld_out = rewrite_visible_jargon(ld_html)
    if '"@type":"Offer","price":"199.99","priceCurrency":"USD"' not in ld_out:
        errors.append("rewrote JSON-LD Offer price fields")
    if "price snapshot of $199.99 (ASIN: B0FD2VBCKN)" not in ld_out:
        errors.append("rewrote JSON-LD description")
    body = html_without_ld_json(ld_out)
    if VISITOR_LEAK_RE.search(body):
        errors.append(f"body still leaks after rewrite: {body!r}")
    if "current price about $199.99" not in body:
        errors.append("body missed price snapshot of $ rewrite")
    if "(ASIN:" in body or "B0FD2VBCKN" in body:
        errors.append("body still has visible ASIN prose")
    if PUBLISH_RULE not in ld_out:
        errors.append("rewrote approved #35 price snapshot phrase")

    if errors:
        print("visitor_copy_unit failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("visitor_copy_unit ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
