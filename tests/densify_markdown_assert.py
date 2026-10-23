#!/usr/bin/env python3
"""Baked site/**/*.html must not ship raw densify Markdown to visitors."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from densify_html import scan_site  # noqa: E402


def main() -> int:
    scanned, leaked, errors = scan_site(ROOT / "site")
    if errors:
        print("densify_markdown_assert failed:")
        for err in errors[:40]:
            print(f"- {err}")
        if len(errors) > 40:
            print(f"- … {len(errors) - 40} more")
        print(f"scanned={scanned} leaked={leaked}")
        return 1
    print(f"densify_markdown_assert ok ({scanned} pages, {leaked} leaks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
