#!/usr/bin/env python3
"""Unit tests for R8 soft list_price gate (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from price_honest import (  # noqa: E402
    apply_l2_list_strike_to_card,
    apply_now_to_card,
    list_price_for_pick,
    r8_soft,
    scrub_pick_was,
)


def main() -> int:
    errors: list[str] = []

    if not r8_soft(72.99, 149.99):
        errors.append("B0FH1RFP91 72.99/149.99 should be R8 soft")
    if not r8_soft(39.95, 99.99):
        errors.append("catalog inverted 39.95/99.99 should be R8 soft")
    if r8_soft(99.99, None):
        errors.append("L2 now $99.99 with no list must not trip R8")
    if r8_soft(899.99, 1599.99):
        errors.append("honest 44% / 1.78x must not trip R8")
    if r8_soft(72.99, None):
        errors.append("missing was must not trip R8")

    queued = {"B0FH1RFP91"}
    if list_price_for_pick("B0FH1RFP91", 72.99, 149.99, queued=queued, l2_restore=set()) is not None:
        errors.append("queued ASIN without L2 restore must drop list_price")
    if list_price_for_pick("B0FH1RFP91", 72.99, 149.99, queued=queued, l2_restore={"B0FH1RFP91"}) != 149.99:
        errors.append("L2 restore_list_ok must keep Amazon list even when R8-soft")
    if list_price_for_pick("B0OTHER", 72.99, 149.99, queued=queued, l2_restore=set()) is not None:
        errors.append("R8 soft affiliate list must drop even off-queue")
    if list_price_for_pick("B0OTHER", 899.99, 1599.99, queued=queued, l2_restore=set()) != 1599.99:
        errors.append("honest list_price must pass")

    pick = scrub_pick_was(
        {"asin": "B0GVDBKMVN", "price": "99.99", "list_price": 99.99, "discount": "60%"}
    )
    if pick.get("price") != "99.99":
        errors.append("scrub must keep now")
    if pick.get("list_price") is not None or pick.get("discount") is not None:
        errors.append("scrub must blank list/discount")

    card = (
        '<article class="product-card" data-asin="B0FH1RFP91" data-position="10">'
        '<div class="pc-price-decision"><span class="pc-price-value">$72.99</span></div>'
        "</article>"
        '<article class="product-card" data-asin="B0OTHER" data-position="1">'
        '<div class="pc-price-decision"><span class="pc-price-value">$72.99</span></div>'
        "</article>"
    )
    out = apply_l2_list_strike_to_card(card, "B0FH1RFP91", 72.99, 149.99)
    if "$72.99" not in out or "<s class=\"pc-was\">$149.99</s>" not in out:
        errors.append("L2 restore must add list strike on the queued card")
    if out.count("$149.99") != 1:
        errors.append("L2 strike must be ASIN-scoped")

    tower = (
        '<article class="product-card" data-asin="B0GVDBKMVN" data-position="5">'
        '<div class="pc-price-decision"><span class="pc-price-value">$39.95</span></div>'
        "</article>"
        '<article class="product-card" data-asin="B0OTHERFAN" data-position="9">'
        '<div class="pc-price-decision"><span class="pc-price-value">$39.95</span></div>'
        "</article>"
    )
    swapped = apply_now_to_card(tower, "B0GVDBKMVN", 39.95, 99.99)
    if swapped.count("$99.99") != 1 or swapped.count("$39.95") != 1:
        errors.append("clear_keep now swap must be ASIN-scoped")

    if errors:
        print("r8_soft_list_price_unit failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("r8_soft_list_price_unit ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
