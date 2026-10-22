#!/usr/bin/env python3
"""Homepage asset + link assertions (no network, no deploy)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
HOME = SITE / "index.html"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from chrome import (  # noqa: E402
    expected_wwnn_codes,
    home_tile_width_codes,
    split_home_tiles,
    tile_is_tv,
)
from site_config import HOME_VISIBLE_TILES  # noqa: E402

REQUIRED_FILES = [
    "assets/css/pages-home.css",
    "assets/js/site.js",
    "assets/img/symbol-color.svg",
    "assets/img/brands/retail/amazon.svg",
    "assets/img/brands/retail/best-buy.svg",
    "assets/img/brands/retail/walmart.svg",
    "assets/img/brands/retail/target.svg",
    "assets/img/brands/retail/home-depot.svg",
    "assets/img/brands/retail/costco.svg",
    "assets/img/brands/retail/wayfair.svg",
    "assets/img/brands/retail/trustpilot.svg",
    "assets/img/lifestyle/devices-mockup.jpg",
    "assets/img/lifestyle/picks/couple.jpg",
    "assets/img/lifestyle/picks/seniors.jpg",
    "assets/img/lifestyle/picks/office.jpg",
    "assets/img/lifestyle/picks/hosting-style-robot.jpg",
    "assets/img/lifestyle/robot-under-sofa.jpg",
    "assets/img/lifestyle/experts/alex.jpg",
    "favicon.ico",
    "favicon.svg",
    "site.webmanifest",
    "icon-512.png",
    "privacy-policy/index.html",
    "terms-of-use/index.html",
    "cookie/index.html",
    "contact/index.html",
    "partner-with-us/index.html",
    "blog/index.html",
    "sitemap/index.html",
]

PICKS = {
    "Best robot vacuums for busy households": "robot-vacuums/comparison/",
    "Quiet floor care for everyday homes": "wet-dry-vacuums/comparison/",
    "Desk setup upgrades that actually help": "standing-desks/comparison/",
    "Self-empty docks worth the premium": "robot-vacuums/",
    "Top cordless vacuums for stairs and cars": "cordless-vacuums/comparison/",
}


def main() -> int:
    errors: list[str] = []
    html = HOME.read_text()

    for rel in REQUIRED_FILES:
        path = SITE / rel
        if not path.is_file() or path.stat().st_size < 20:
            errors.append(f"missing or empty {rel}")

    local_refs = sorted(
        set(
            re.findall(
                r'(?:src|href)="((?:assets/|favicon|apple-touch-icon|icon-512|site\.webmanifest)[^"]+)"',
                html,
            )
        )
    )
    for ref in local_refs:
        path = SITE / ref.split("#")[0]
        if not path.is_file():
            errors.append(f"homepage references missing file {ref}")

    if 'href="/"' not in html:
        errors.append("logo/home should point at / not index.html")
    if 'href="index.html"' in html:
        errors.append("homepage still has index.html href")

    if "<circle cx=\"24\" cy=\"24\" r=\"10\"/>" in html and "Kids Bikes" in html:
        # empty circle icon must not remain on the Kids Bikes tile
        tile = html.split("Kids Bikes", 1)[0][-800:]
        if "<circle cx=\"24\" cy=\"24\" r=\"10\"/>" in tile:
            errors.append("Kids Bikes tile still uses the empty-circle icon")

    hrefs = set()
    for title, want in PICKS.items():
        m = re.search(
            rf'<a class="pick-card[^"]*" href="([^"]+)"><img[^>]*>'
            rf'<span class="pick-overlay"><span class="pick-title">{re.escape(title)}',
            html,
        )
        if not m:
            errors.append(f"missing Editor's Pick card for {title!r}")
            continue
        hrefs.add(m.group(1))
        if m.group(1) != want:
            errors.append(f"pick {title!r} href {m.group(1)!r} != {want!r}")
        dest = SITE / m.group(1).strip("/") / "index.html"
        if not dest.is_file():
            errors.append(f"pick {title!r} points at missing {m.group(1)}")
    if len(hrefs) < 5:
        errors.append(f"Editor's Picks are not five distinct hrefs: {sorted(hrefs)}")

    css = (SITE / "assets/css/pages-home.css").read_text()
    if ".pc-main" in css:
        errors.append("pages-home.css must not touch .pc-main")
    if ".home-tile-grid" not in css or ".explore-footer" not in css:
        errors.append("pages-home.css missing home-tile-grid / explore-footer layout")
    if "2.15fr 2.15fr 1fr 1fr" not in css:
        errors.append("pages-home.css missing WWNN grid-template-columns contract")

    gm = re.search(
        r'<div class="home-tile-grid"[^>]*>(.*?)</div>\s*<button type="button" class="home-show-more"',
        html,
        re.S,
    )
    if not gm:
        errors.append("home tile grid missing")
    else:
        tiles = split_home_tiles(gm.group(1))
        n_check = min(max(8, (len(tiles) // 4) * 4), len(tiles))
        got = home_tile_width_codes(tiles, n_check)
        want = expected_wwnn_codes(n_check)
        if got != want:
            errors.append(f"home tiles WWNN expected {''.join(want)} got {''.join(got)}")
        tv_idxs = [i for i, t in enumerate(tiles) if tile_is_tv(t)]
        if not tv_idxs:
            errors.append("home missing editorial /tv/ tile in grid")
        elif tv_idxs[0] not in (2, 3):
            errors.append(
                f"tv tile at slot {tv_idxs[0]} (need row-1 narrow slot 2 or 3)"
            )
        if any("is-more" in t[:200] for t in tiles[:HOME_VISIBLE_TILES]):
            errors.append("first visible home tiles still have is-more")

    js = (SITE / "assets/js/site.js").read_text()
    if "data-home-show-more" not in js or "is-expanded" not in js:
        errors.append("site.js must toggle Show more / is-expanded")

    if errors:
        print("homepage_assets_assert FAILED")
        for e in errors:
            print(" -", e)
        return 1
    print(f"homepage_assets_assert OK files={len(REQUIRED_FILES)} picks={len(PICKS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
