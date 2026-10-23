#!/usr/bin/env python3
"""R8 soft queue: L2 restore_list_ok keeps list; clear_keep stays blank."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from price_honest import (  # noqa: E402
    CARD_RE,
    STRIKE_HINT_RE,
    format_display,
    l2_list_amount,
    l2_restore_list,
    load_shortlist,
    parse_money,
    pick_was_fields,
    r8_soft_queue_rows,
)

NOW_RE = re.compile(r'class="pc-price-value">(\$[0-9][0-9,]*(?:\.[0-9]{2})?)<')


def collect_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    data = site / "data"
    errors: list[str] = []
    rows = r8_soft_queue_rows(data)
    if not rows:
        errors.append("missing r8_soft_queue on shortlist JSON")
        return errors

    for row in rows:
        asin = (row.get("asin") or "").upper()
        slug = row.get("category") or ""
        src = row.get("src") or f"shortlist-{slug}.json"
        now = parse_money(row.get("now") or row.get("l2_now"))
        blob = load_shortlist(data / src)
        pick = next(
            (p for p in blob.get("picks") or [] if (p.get("asin") or "").upper() == asin),
            None,
        )
        if pick is None:
            errors.append(f"{src} missing queued ASIN {asin}")
            continue
        leftover = pick_was_fields(pick)
        pick_now = parse_money(pick.get("price") or pick.get("price_displayed"))
        if now is not None and pick_now is not None and abs(pick_now - now) > 0.009:
            errors.append(f"{src} {asin} now drifted {pick_now} != {now}")

        if l2_restore_list(row):
            want_list = l2_list_amount(row)
            got_list = parse_money(pick.get("list_price"))
            if want_list is None:
                errors.append(f"{src} {asin} restore_list_ok missing L2 list")
            elif got_list is None or abs(got_list - want_list) > 0.009:
                errors.append(f"{src} {asin} list {got_list} != L2 {want_list}")
            extra = {k: v for k, v in leftover.items() if k != "list_price"}
            if extra:
                errors.append(f"{src} {asin} restore invented {sorted(extra)}")
        else:
            if leftover:
                errors.append(f"{src} {asin} still has {sorted(leftover)}")

        cmp = site / slug / "comparison" / "index.html"
        if not cmp.exists():
            errors.append(f"missing {slug}/comparison/")
            continue
        html = cmp.read_text(encoding="utf-8")
        card = next((m.group(0) for m in CARD_RE.finditer(html) if m.group(1).upper() == asin), "")
        if not card:
            errors.append(f"{slug}/comparison missing card {asin}")
            continue
        price_m = NOW_RE.search(card)
        if not price_m:
            errors.append(f"{slug} {asin} card missing pc-price-value")
        elif now is not None and parse_money(price_m.group(1)) != now:
            errors.append(
                f"{slug} {asin} card now {price_m.group(1)} != shortlist {format_display(now)}"
            )

        if l2_restore_list(row):
            want_list = l2_list_amount(row)
            if want_list is not None and format_display(want_list) not in card:
                errors.append(f"{slug} {asin} card missing L2 list/strike {format_display(want_list)}")
            if want_list is not None and not re.search(
                r"<s[^>]*>\s*" + re.escape(format_display(want_list)), card
            ):
                errors.append(f"{slug} {asin} card missing restored <s> strike")
        else:
            if STRIKE_HINT_RE.search(card):
                errors.append(f"{slug} {asin} card still has was/strike/%")
            if re.search(r"%\s*OFF|was\s*\$", card, re.I):
                errors.append(f"{slug} {asin} card leaked was/% copy")

        review_slug = pick.get("review_slug")
        if review_slug:
            review = site / slug / "reviews" / review_slug / "index.html"
            if review.exists():
                body = review.read_text(encoding="utf-8")
                if not l2_restore_list(row) and STRIKE_HINT_RE.search(body) and re.search(
                    r"%\s*OFF|was-price", body, re.I
                ):
                    errors.append(f"{slug}/reviews/{review_slug} leaked was/%")
                if now is not None and format_display(now) not in body:
                    errors.append(f"{slug}/reviews/{review_slug} missing L2 now {format_display(now)}")
    return errors


def main() -> int:
    errors = collect_errors(SITE)
    if errors:
        print("r8_soft_list_price_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("r8_soft_list_price_assert ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
