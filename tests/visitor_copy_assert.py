#!/usr/bin/env python3
"""Baked site/ must not ship visitor jargon, UK/Utilize, TV ops-copy, or day-add leaks."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from seo_geo import VISITOR_LEAK_RE, html_without_ld_json  # noqa: E402

SKIP = {".cache", "fixtures", "data", "assets"}


def collect_errors(site: Path | None = None) -> list[str]:
    """Sitewide visitor-body leak scan. JSON-LD scripts are stripped first."""
    site = site or SITE
    errors: list[str] = []
    for path in sorted(site.rglob("*")):
        if not path.is_file():
            continue
        if set(path.relative_to(site).parts) & SKIP:
            continue
        if path.suffix not in {".html", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".html":
            text = html_without_ld_json(text)
        hit = VISITOR_LEAK_RE.search(text)
        if hit:
            errors.append(f"{path.relative_to(site)} still has {hit.group(0)!r}")
    return errors


def main() -> int:
    errors = collect_errors(SITE)
    scanned = sum(
        1
        for path in SITE.rglob("*")
        if path.is_file()
        and path.suffix in {".html", ".txt"}
        and not (set(path.relative_to(SITE).parts) & SKIP)
    )
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
