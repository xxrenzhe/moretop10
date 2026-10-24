#!/usr/bin/env python3
"""Unit tests for comparison last-checked anti-rollback (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from stamp_guard import (  # noqa: E402
    apply_card_checked_floors,
    apply_known_stamp_floors,
    apply_page_stamp_floor,
    apply_visitor_stamp_floor,
    bake_stamp_date,
    catalog_page_floor,
    clamp_comparison_stamps,
    extract_card_checked,
    extract_page_stamps,
    later_iso_date,
    stamp_rollback_errors,
)


def _card(asin: str, checked: str, price: str = "$10.00") -> str:
    return (
        f'<article class="product-card" data-asin="{asin}" data-position="1">'
        f'<div class="pc-price-decision"><span class="pc-price-value">{price}</span>'
        f'<span class="pc-price-checked">Checked {checked}</span></div>'
        "</article>"
    )


def _page(as_of: str, last_updated: str, cards: str) -> str:
    return (
        f'<span class="badge">Last Updated: {last_updated}</span>'
        f"<p>As of {as_of}, we rank 10 complete robot vacuums.</p>"
        f'<script type="application/ld+json">{{"dateModified":"{last_updated}"}}</script>'
        f'<div class="product-stack">{cards}</div>'
        f'<aside class="geo-cite-strip">(last checked {last_updated})</aside>'
    )


def main() -> int:
    errors: list[str] = []

    if later_iso_date("2026-10-20", "2026-10-23") != "2026-10-23":
        errors.append("later_iso_date must keep the later day")
    if later_iso_date("2026-10-23", "2026-10-18") != "2026-10-23":
        errors.append("later_iso_date must not roll back")
    if later_iso_date(None, "2026-10-23") != "2026-10-23":
        errors.append("later_iso_date must ignore None")

    current = _page(
        "2026-10-20",
        "2026-10-20",
        _card("B0GGRTD2ZY", "2026-10-18", "$699.99")
        + _card("B0CQ7JCN6Z", "2026-10-18", "$349.99"),
    )
    sot = _page(
        "2026-10-23",
        "2026-10-23",
        _card("B0GGRTD2ZY", "2026-10-23", "$1.00")
        + _card("B0CQ7JCN6Z", "2026-10-23", "$1.00"),
    )

    page = extract_page_stamps(current)
    if page.get("as_of") != "2026-10-20":
        errors.append("extract_page_stamps as_of")
    if page.get("last_updated") != "2026-10-20":
        errors.append("extract_page_stamps last_updated")
    cards = extract_card_checked(current)
    if cards.get("B0GGRTD2ZY") != "2026-10-18":
        errors.append("extract_card_checked B0GGRTD2ZY")

    rollback = stamp_rollback_errors(sot, current, page_id="robot-vacuums/comparison/")
    if not rollback:
        errors.append("stamp_rollback_errors must flag writing 10-20 over 10-23")
    if not any("B0GGRTD2ZY" in err for err in rollback):
        errors.append("stamp_rollback_errors must name the rolled-back ASIN")

    same = stamp_rollback_errors(sot, sot, page_id="robot-vacuums/comparison/")
    if same:
        errors.append(f"equal stamps must not error: {same}")

    clamped, notes = clamp_comparison_stamps(sot, current)
    if extract_page_stamps(clamped).get("as_of") != "2026-10-23":
        errors.append("clamp must raise page As of to existing 10-23")
    if extract_page_stamps(clamped).get("last_updated") != "2026-10-23":
        errors.append("clamp must raise Last Updated to existing 10-23")
    clamped_cards = extract_card_checked(clamped)
    if clamped_cards.get("B0GGRTD2ZY") != "2026-10-23":
        errors.append("clamp must raise card Checked to existing 10-23")
    if "$699.99" not in clamped or "$1.00" in clamped:
        errors.append("clamp must not invent or rewrite prices")
    if not notes:
        errors.append("clamp should report what it raised")

    advanced = _page(
        "2026-10-24",
        "2026-10-24",
        _card("B0GGRTD2ZY", "2026-10-24", "$699.99"),
    )
    kept, _ = clamp_comparison_stamps(sot, advanced)
    if extract_page_stamps(kept).get("as_of") != "2026-10-24":
        errors.append("clamp must allow a later day-update")
    if extract_card_checked(kept).get("B0GGRTD2ZY") != "2026-10-24":
        errors.append("clamp must allow a later card Checked")

    floored = apply_page_stamp_floor(current, "2026-10-23")
    floored = apply_card_checked_floors(floored, {"B0GGRTD2ZY": "2026-10-23"})
    if extract_page_stamps(floored).get("as_of") != "2026-10-23":
        errors.append("apply_page_stamp_floor should raise As of")
    if extract_card_checked(floored).get("B0GGRTD2ZY") != "2026-10-23":
        errors.append("apply_card_checked_floors should raise that ASIN")
    if extract_card_checked(floored).get("B0CQ7JCN6Z") != "2026-10-18":
        errors.append("apply_card_checked_floors must not invent a floor for other ASINs")

    fry = _page(
        "2026-10-20",
        "2026-10-20",
        _card("B0FJYK886N", "2026-10-20", "$99.99"),
    )
    floored_fry, floor_notes = apply_known_stamp_floors(
        fry,
        "air-fryers",
        {
            "air-fryers": {
                "page_floor": "2026-10-23",
                "checked": {"B0FJYK886N": "2026-10-23"},
            }
        },
    )
    if extract_page_stamps(floored_fry).get("as_of") != "2026-10-23":
        errors.append("apply_known_stamp_floors must raise a non-robot page As of")
    if extract_card_checked(floored_fry).get("B0FJYK886N") != "2026-10-23":
        errors.append("apply_known_stamp_floors must raise a non-robot card Checked")
    if "$99.99" not in floored_fry:
        errors.append("apply_known_stamp_floors must not rewrite prices")
    if not floor_notes:
        errors.append("apply_known_stamp_floors should report raises")

    skipped, skip_notes = apply_known_stamp_floors(fry, "unknown-hub", {"air-fryers": {}})
    if skipped != fry or skip_notes:
        errors.append("apply_known_stamp_floors must no-op unknown slugs")

    floor = catalog_page_floor()
    if floor != "2026-10-24":
        errors.append(f"catalog_page_floor expected 2026-10-24 got {floor}")
    if bake_stamp_date("2026-10-20") != floor:
        errors.append("bake_stamp_date must raise a hardcoded default to catalog floor")
    if bake_stamp_date("2026-10-25") != "2026-10-25":
        errors.append("bake_stamp_date must keep a later day-update")

    mixed = (
        '<p>Prices are publish-time snapshots (Last Updated 2026-10-20)—always check.</p>'
        '<p>The $89.95 figure is a publish-time snapshot (price checked 2026-10-18).</p>'
        f'<span class="pc-price-checked">Checked 2026-10-18</span>'
        f'<span class="ed-pick-date">2026-10-20</span>'
        "<lastmod>2026-10-22</lastmod>"
        "<lastmod>2026-10-22T23:25:47+00:00</lastmod>"
        "<p>Prices as of 2026-10-22.</p>"
        f'<aside>(last checked 2026-10-23)</aside>'
        f'<span class="badge">Last Updated: 2026-10-24</span>'
    )
    raised = apply_visitor_stamp_floor(mixed, floor)
    if "Last Updated 2026-10-20" in raised or "Checked 2026-10-18" in raised:
        errors.append("apply_visitor_stamp_floor must raise FAQ/card dates")
    if "price checked 2026-10-18" in raised:
        errors.append("apply_visitor_stamp_floor must raise price-checked FAQ dates")
    if "<lastmod>2026-10-22</lastmod>" in raised:
        errors.append("apply_visitor_stamp_floor must raise sitemap lastmod")
    if "<lastmod>2026-10-22T23:25:47+00:00</lastmod>" in raised:
        errors.append("apply_visitor_stamp_floor must raise lastmod datetimes")
    if "Prices as of 2026-10-22" in raised:
        errors.append("apply_visitor_stamp_floor must raise lowercase as-of prices")
    if f"Last Updated: {floor}" not in raised:
        errors.append("apply_visitor_stamp_floor must keep dates already on the floor")
    if apply_visitor_stamp_floor(raised, "2026-10-20") != raised:
        errors.append("apply_visitor_stamp_floor must never roll a date backward")

    if errors:
        print("stamp_guard_unit failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("stamp_guard_unit ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
