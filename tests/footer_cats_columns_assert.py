#!/usr/bin/env python3
"""Footer Categories list is 3 CSS columns on desktop (no network, no deploy)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = SITE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chrome import NAV_CSS  # noqa: E402

DESKTOP_3COL = re.compile(
    r"@media\s*\(\s*min-width:\s*720px\s*\)\s*\{.*?"
    r"\.footer-col-cats(?:\s*,\s*\.footer-col-categories)?\s+ul.*?columns\s*:\s*3",
    re.S,
)
NAV_BLOCK = re.compile(r'<style id="landing-hub-nav">.*?</style>', re.S)


def _ok(css: str) -> bool:
    return bool(DESKTOP_3COL.search(css))


def main() -> int:
    errors: list[str] = []
    if not _ok(NAV_CSS):
        errors.append("chrome.py NAV_CSS missing desktop columns:3 for Categories")

    site_css = (SITE / "assets/css/site.css").read_text(encoding="utf-8")
    if not _ok(site_css):
        errors.append("site.css missing desktop columns:3 for Categories")

    home = (SITE / "index.html").read_text(encoding="utf-8")
    if 'id="landing-hub-nav"' in home and not _ok(home):
        errors.append("homepage inlines landing-hub-nav without desktop columns:3")
    if "footer-col-cats" not in home and "footer-col-categories" not in home:
        errors.append("homepage missing Categories footer column")

    hub = SITE / "robot-vacuums" / "index.html"
    if not hub.is_file():
        errors.append("missing hub site/robot-vacuums/index.html")
    else:
        text = hub.read_text(encoding="utf-8")
        block = NAV_BLOCK.search(text)
        if not block:
            errors.append("robot-vacuums missing landing-hub-nav")
        elif not _ok(block.group(0)):
            errors.append("robot-vacuums landing-hub-nav missing desktop columns:3")

    stale: list[str] = []
    for path in SITE.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        if 'id="landing-hub-nav"' not in text:
            continue
        block = NAV_BLOCK.search(text)
        if not block or not _ok(block.group(0)):
            stale.append(str(path.relative_to(ROOT)))
    if stale:
        preview = ", ".join(stale[:8])
        extra = f" (+{len(stale) - 8} more)" if len(stale) > 8 else ""
        errors.append(f"{len(stale)} pages still lack desktop 3-col cats: {preview}{extra}")

    if errors:
        print("footer_cats_columns_assert FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print("footer_cats_columns_assert OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
