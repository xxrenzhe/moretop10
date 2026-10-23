#!/usr/bin/env python3
"""Baked site/ must not ship visitor jargon or UK/Utilize leaks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import VISITOR_LEAK_RE  # noqa: E402

SKIP = {".cache", "fixtures", "data", "assets"}


def main() -> int:
    errors: list[str] = []
    scanned = 0
    for path in sorted(SITE.rglob("*")):
        if not path.is_file():
            continue
        if set(path.relative_to(SITE).parts) & SKIP:
            continue
        if path.suffix not in {".html", ".txt"}:
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8")
        hit = VISITOR_LEAK_RE.search(text)
        if hit:
            errors.append(f"{path.relative_to(SITE)} still has {hit.group(0)!r}")

    if errors:
        print("visitor_copy_assert failed:")
        for err in errors[:40]:
            print(f"- {err}")
        if len(errors) > 40:
            print(f"- … {len(errors) - 40} more")
        return 1
    print(f"visitor_copy_assert ok ({scanned} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
