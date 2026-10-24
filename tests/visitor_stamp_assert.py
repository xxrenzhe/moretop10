#!/usr/bin/env python3
"""Visitor calendar stamps in baked site/ must be ≥ catalog page_floor."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from stamp_guard import (  # noqa: E402
    VISITOR_STAMP_FIND_RE,
    catalog_page_floor,
)

SKIP = {".cache", "fixtures", "data", "assets"}


def collect_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    floor = catalog_page_floor(site / "data")
    errors: list[str] = []
    for path in sorted(site.rglob("*")):
        if not path.is_file():
            continue
        if set(path.relative_to(site).parts) & SKIP:
            continue
        if path.suffix not in {".html", ".txt", ".xml"}:
            continue
        text = path.read_text(encoding="utf-8")
        for match in VISITOR_STAMP_FIND_RE.finditer(text):
            date = match.group(1)
            if date < floor:
                rel = path.relative_to(site)
                errors.append(f"{rel} visitor stamp {date} is earlier than {floor}")
                break
    return errors


def main() -> int:
    floor = catalog_page_floor(SITE / "data")
    errors = collect_errors(SITE)
    if errors:
        print("visitor_stamp_assert failed:")
        for err in errors[:40]:
            print(f"- {err}")
        if len(errors) > 40:
            print(f"- … {len(errors) - 40} more")
        return 1
    print(f"visitor_stamp_assert ok (floor {floor})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
