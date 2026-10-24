#!/usr/bin/env python3
"""Robot-vacuums comparison stamps must not sit earlier than the daily SoT.

Also fail-closed if a proposed bake would write page/card dates earlier
than the committed HTML for the same ASINs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = SITE / "scripts"
sys.path.insert(0, str(SCRIPTS))

from stamp_guard import (  # noqa: E402
    extract_card_checked,
    extract_page_stamps,
    page_stamp_floor_errors,
    stamp_rollback_errors,
)

FLOOR_PATH = SITE / "data" / "robot-vacuums-comparison-stamp-floor.json"
PAGE_ID = "robot-vacuums/comparison/"


def collect_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    cmp_path = site / "robot-vacuums" / "comparison" / "index.html"
    floor_path = site / "data" / "robot-vacuums-comparison-stamp-floor.json"
    errors: list[str] = []
    if not cmp_path.is_file():
        return [f"missing {PAGE_ID}index.html"]
    if not floor_path.is_file():
        return [f"missing stamp floor JSON {floor_path.name}"]

    floor = json.loads(floor_path.read_text(encoding="utf-8"))
    html = cmp_path.read_text(encoding="utf-8")
    errors.extend(
        page_stamp_floor_errors(
            html,
            page_floor=floor["page_floor"],
            checked_floors=floor["checked"],
            page_id=PAGE_ID,
        )
    )

    page = extract_page_stamps(html)
    cards = extract_card_checked(html)
    # A synthetic older bake of the same cards must be rejected.
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
    rollback = stamp_rollback_errors(html, older, page_id=PAGE_ID)
    if not rollback:
        errors.append(f"{PAGE_ID}: anti-rollback helper did not reject an older bake")
    return errors


def main() -> int:
    if not FLOOR_PATH.is_file():
        print("robot_stamp_assert failed:")
        print(f"- missing {FLOOR_PATH}")
        return 1
    errors = collect_errors(SITE)
    if errors:
        print("robot_stamp_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("robot_stamp_assert ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
