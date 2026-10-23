#!/usr/bin/env python3
"""R8 soft queue: no unverified list_price / was / % on shortlist or baked cards."""

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
        now = parse_money(row.get("now"))
        blob = load_shortlist(data / src)
        pick = next(
            (p for p in blob.get("picks") or [] if (p.get("asin") or "").upper() == asin),
            None,
        )
        if pick is None:
            errors.append(f"{src} missing queued ASIN {asin}")
            continue
        leftover = pick_was_fields(pick)
        if leftover:
            errors.append(f"{src} {asin} still has {sorted(leftover)}")
        pick_now = parse_money(pick.get("price") or pick.get("price_displayed"))
        if now is not None and pick_now is not None and abs(pick_now - now) > 0.009:
            errors.append(f"{src} {asin} now drifted {pick_now} != {now}")

        cmp = site / slug / "comparison" / "index.html"
        if not cmp.exists():
            errors.append(f"missing {slug}/comparison/")
            continue
        html = cmp.read_text(encoding="utf-8")
        card = next((m.group(0) for m in CARD_RE.finditer(html) if m.group(1).upper() == asin), "")
        if not card:
            errors.append(f"{slug}/comparison missing card {asin}")
            continue
        if STRIKE_HINT_RE.search(card):
            errors.append(f"{slug} {asin} card still has was/strike/%")
        price_m = NOW_RE.search(card)
        if not price_m:
            errors.append(f"{slug} {asin} card missing pc-price-value")
        elif now is not None and parse_money(price_m.group(1)) != now:
            errors.append(
                f"{slug} {asin} card now {price_m.group(1)} != shortlist {format_display(now)}"
            )
        if re.search(r"%\s*OFF|was\s*\$", card, re.I):
            errors.append(f"{slug} {asin} card leaked was/% copy")

        review_slug = pick.get("review_slug")
        if review_slug:
            review = site / slug / "reviews" / review_slug / "index.html"
            if review.exists():
                body = review.read_text(encoding="utf-8")
                if STRIKE_HINT_RE.search(body) and re.search(r"%\s*OFF|was-price", body, re.I):
                    errors.append(f"{slug}/reviews/{review_slug} leaked was/%")
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
