#!/usr/bin/env python3
"""All comparison-page stamps must not sit earlier than the daily SoT floor.

Covers the 21 hubs restored from mt10-stamp-sot-all-cmp-2026-10-24.
Also fail-closed if a proposed bake would write page/card dates earlier
than the committed HTML for the same ASINs.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = SITE / "scripts"
sys.path.insert(0, str(SCRIPTS))

from stamp_guard import (  # noqa: E402
    extract_card_checked,
    extract_page_stamps,
    load_comparison_floors,
    page_stamp_floor_errors,
    stamp_rollback_errors,
)

FLEET_PATH = SITE / "data" / "comparison-stamp-floors.json"
EXPECTED_COUNT = 21


def _rollback_probe(html: str, page_id: str) -> list[str]:
    page = extract_page_stamps(html)
    cards = extract_card_checked(html)
    older = (
        html.replace(page.get("as_of") or "2026-10-23", "2026-10-19")
        .replace(page.get("last_updated") or "2026-10-23", "2026-10-19")
    )
    for date in cards.values():
        older = older.replace(
            f'<span class="pc-price-checked">Checked {date}</span>',
            '<span class="pc-price-checked">Checked 2026-10-17</span>',
            1,
        )
    rollback = stamp_rollback_errors(html, older, page_id=page_id)
    if not rollback:
        return [f"{page_id}: anti-rollback helper did not reject an older bake"]
    return []


def collect_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    data_dir = site / "data"
    floors = load_comparison_floors(data_dir)
    errors: list[str] = []
    if not floors:
        return [f"missing comparison stamp floors under {data_dir}"]
    if len(floors) < EXPECTED_COUNT:
        errors.append(
            f"expected {EXPECTED_COUNT} comparison stamp floors, found {len(floors)}"
        )

    for slug, spec in sorted(floors.items()):
        page_id = spec.get("page") or f"{slug}/comparison/"
        cmp_path = site / slug / "comparison" / "index.html"
        if not cmp_path.is_file():
            errors.append(f"missing {page_id}index.html")
            continue
        html = cmp_path.read_text(encoding="utf-8")
        errors.extend(
            page_stamp_floor_errors(
                html,
                page_floor=spec.get("page_floor") or "",
                checked_floors=spec.get("checked") or {},
                page_id=page_id,
            )
        )
        errors.extend(_rollback_probe(html, page_id))
    return errors


def main() -> int:
    if not FLEET_PATH.is_file():
        print("comparison_stamp_assert failed:")
        print(f"- missing {FLEET_PATH}")
        return 1
    errors = collect_errors(SITE)
    if errors:
        print("comparison_stamp_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print(f"comparison_stamp_assert ok ({EXPECTED_COUNT} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
