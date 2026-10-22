#!/usr/bin/env python3
"""Footer Categories: 3 CSS columns + widened 4-track grid on desktop.

Bake-time only (no network, no deploy). Desktop = min-width 720px.

Tracks are Brand | Categories | Company | Legal. Categories must be the
widest track so the 3-column cats list is not squeezed into 1fr.
"""

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

# Brand | wide Categories | Company | Legal — same recipe in site.css + NAV_CSS.
WIDENED_4TRACK = "1.4fr 2.2fr 0.85fr 0.85fr"
STALE_5TRACK = "1.4fr 1fr 1.1fr 0.9fr 0.8fr"

DESKTOP_3COL = re.compile(
    r"@media\s*\(\s*min-width:\s*720px\s*\)\s*\{.*?"
    r"\.footer-col-cats(?:\s*,\s*\.footer-col-categories)?\s+ul.*?columns\s*:\s*3",
    re.S,
)
DESKTOP_GRID = re.compile(
    r"@media\s*\(\s*min-width:\s*720px\s*\)\s*\{.*?"
    r"\.footer-grid\s*\{\s*grid-template-columns\s*:\s*([^;}]+)",
    re.S,
)
NAV_BLOCK = re.compile(r'<style id="landing-hub-nav">.*?</style>', re.S)
FR_TRACK = re.compile(r"([\d.]+)fr")


def _has_3col(css: str) -> bool:
    return bool(DESKTOP_3COL.search(css))


def _desktop_tracks(css: str) -> list[float] | None:
    m = DESKTOP_GRID.search(css)
    if not m:
        return None
    raw = m.group(1).strip()
    tracks = [float(x) for x in FR_TRACK.findall(raw)]
    return tracks or None


def _has_widened_4track(css: str) -> bool:
    if STALE_5TRACK in css:
        return False
    if WIDENED_4TRACK in css:
        return True
    tracks = _desktop_tracks(css)
    if not tracks or len(tracks) != 4:
        return False
    brand, cats, company, legal = tracks
    return cats > brand and cats > company and cats > legal


def sample_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    errors: list[str] = []

    if not _has_3col(NAV_CSS):
        errors.append("chrome.py NAV_CSS missing desktop columns:3 for Categories")
    if not _has_widened_4track(NAV_CSS):
        errors.append(
            "chrome.py NAV_CSS missing desktop 4-track widened-cats "
            f"({WIDENED_4TRACK}); stale 5-track is not allowed"
        )
    if STALE_5TRACK in NAV_CSS:
        errors.append("chrome.py NAV_CSS still has mismatched 5-track footer-grid")

    site_css = (site / "assets/css/site.css").read_text(encoding="utf-8")
    if not _has_3col(site_css):
        errors.append("site.css missing desktop columns:3 for Categories")
    if not _has_widened_4track(site_css):
        errors.append(
            f"site.css missing desktop 4-track widened-cats ({WIDENED_4TRACK})"
        )

    home = (site / "index.html").read_text(encoding="utf-8")
    if 'id="landing-hub-nav"' in home:
        if not _has_3col(home):
            errors.append("homepage inlines landing-hub-nav without desktop columns:3")
        if not _has_widened_4track(home):
            errors.append("homepage inlines landing-hub-nav without widened 4-track")
    if "footer-col-cats" not in home and "footer-col-categories" not in home:
        errors.append("homepage missing Categories footer column")

    hub = site / "robot-vacuums" / "index.html"
    if not hub.is_file():
        errors.append("missing hub site/robot-vacuums/index.html")
    else:
        text = hub.read_text(encoding="utf-8")
        block = NAV_BLOCK.search(text)
        if not block:
            errors.append("robot-vacuums missing landing-hub-nav")
        else:
            if not _has_3col(block.group(0)):
                errors.append("robot-vacuums landing-hub-nav missing desktop columns:3")
            if not _has_widened_4track(block.group(0)):
                errors.append(
                    "robot-vacuums landing-hub-nav missing desktop 4-track widened-cats"
                )

    stale_3col: list[str] = []
    stale_grid: list[str] = []
    for path in site.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        if 'id="landing-hub-nav"' not in text:
            continue
        block = NAV_BLOCK.search(text)
        try:
            rel = str(path.relative_to(ROOT))
        except ValueError:
            rel = str(path)
        if not block or not _has_3col(block.group(0)):
            stale_3col.append(rel)
        if not block or not _has_widened_4track(block.group(0)):
            stale_grid.append(rel)
    if stale_3col:
        preview = ", ".join(stale_3col[:8])
        extra = f" (+{len(stale_3col) - 8} more)" if len(stale_3col) > 8 else ""
        errors.append(
            f"{len(stale_3col)} pages still lack desktop 3-col cats: {preview}{extra}"
        )
    if stale_grid:
        preview = ", ".join(stale_grid[:8])
        extra = f" (+{len(stale_grid) - 8} more)" if len(stale_grid) > 8 else ""
        errors.append(
            f"{len(stale_grid)} pages still lack desktop 4-track widened-cats: "
            f"{preview}{extra}"
        )

    return errors


def main() -> int:
    errors = sample_errors()
    if errors:
        print("footer_cats_columns_assert FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print("footer_cats_columns_assert OK")
    print(f"  desktop grid: {WIDENED_4TRACK} (Brand | wide Categories | Company | Legal)")
    print("  Categories ul: columns:1 mobile / columns:3 ≥720px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
