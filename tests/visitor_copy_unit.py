#!/usr/bin/env python3
"""Visitor-copy jargon / US-English rewrites (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import (  # noqa: E402
    PUBLISH_RULE,
    RETAILER_CONFIRM,
    UNPUBLISHED_UNTIL_TEN,
    VISITOR_LEAK_RE,
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
    ]
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

    if errors:
        print("visitor_copy_unit failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("visitor_copy_unit ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
