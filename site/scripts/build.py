#!/usr/bin/env python3
"""MoreTop10 site bake — chrome / internal-link SoT.

This repo clone does not ship the full inventory generator. `build.py` is the
source of truth for category *landing* internal links:

  1. Non-home header mega + mobile: Overview → /{slug}/ plus Compare / Reviews
  2. Footer Categories column: every ALL_CATS (MVP + NON_MVP) landing
  3. Home grid: pin tier=extended / newly published cats, is-more when i >= 8
  4. comparison/ + reviews/ hubs: Related jump back to the landing

Product cards, ASINs, and affiliate URLs are copied from Live snapshots — never
invented here. Do not wrangler-deploy from this script.

Usage:
    python3 site/scripts/build.py
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
CACHE = SITE / ".cache"
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chrome import (  # noqa: E402
    ensure_hub_reciprocity,
    inject_nav_css,
    rel_prefix,
    reorder_home_tiles,
    rewrite_footer,
    rewrite_non_home_nav,
)
from site_config import (  # noqa: E402
    ALL_CATS,
    CATS_BY_SLUG,
    HOME_VISIBLE_TILES,
    load_site_config,
)

LIVE = "https://moretop10.com"
UA = "MoreTop10Bake/1.0 (+internal-links)"

# Pages we rewrite for the landing-hub contract. Bodies (products) stay Live.
PAGES = [
    {"live": f"{LIVE}/", "out": "index.html", "kind": "home"},
    {"live": f"{LIVE}/about-us/", "out": "about-us/index.html", "kind": "page"},
    {"live": f"{LIVE}/kids-bikes/", "out": "kids-bikes/index.html", "kind": "landing"},
    {
        "live": f"{LIVE}/kids-bikes/comparison/",
        "out": "kids-bikes/comparison/index.html",
        "kind": "comparison",
    },
    {
        "live": f"{LIVE}/kids-bikes/reviews/",
        "out": "kids-bikes/reviews/index.html",
        "kind": "reviews",
    },
]


def fetch(url: str, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 500:
        return dest.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    dest.write_text(text, encoding="utf-8")
    return text


def bake_page(spec: dict, cfg: dict) -> Path:
    cats = cfg["ALL_CATS"]
    out_rel = spec["out"]
    prefix = rel_prefix(out_rel)
    cache_name = out_rel.replace("/", "__")
    html = fetch(spec["live"], CACHE / cache_name)

    if spec["kind"] != "home":
        html = inject_nav_css(html)
    html = rewrite_non_home_nav(html, cats, prefix)
    html = rewrite_footer(html, cats, prefix)

    if spec["kind"] == "home":
        html = reorder_home_tiles(html, cfg["CATS_BY_SLUG"], cfg["home_visible_tiles"])

    if spec["kind"] in {"comparison", "reviews"}:
        html = ensure_hub_reciprocity(html, spec["kind"])

    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    return dest


def _first_home_tiles(html: str, n: int = 8) -> list[str]:
    from chrome import split_home_tiles, tile_slug

    m = __import__("re").search(
        r'<div class="home-tile-grid"[^>]*>(.*?)</div>\s*<button type="button" class="home-show-more"',
        html,
        __import__("re").S,
    )
    if not m:
        return []
    tiles = split_home_tiles(m.group(1))
    slugs = set(CATS_BY_SLUG)
    out = []
    for tile in tiles[:n]:
        slug = tile_slug(tile, slugs) or "?"
        more = " is-more" if "is-more" in tile[:160] else ""
        out.append(f"{slug}{more}")
    return out


def verify() -> None:
    home = (SITE / "index.html").read_text(encoding="utf-8")
    about = (SITE / "about-us" / "index.html").read_text(encoding="utf-8")
    cmp = (SITE / "kids-bikes" / "comparison" / "index.html").read_text(encoding="utf-8")
    rev = (SITE / "kids-bikes" / "reviews" / "index.html").read_text(encoding="utf-8")
    errors: list[str] = []
    if rel_prefix("index.html") != "":
        errors.append("rel_prefix home")
    if rel_prefix("about-us/index.html") != "../":
        errors.append("rel_prefix about")
    if rel_prefix("kids-bikes/comparison/index.html") != "../../":
        errors.append("rel_prefix comparison")

    # 1) Home: kids-bikes tile visible (no is-more) / first 8
    import re

    from chrome import split_home_tiles, tile_slug

    gm = re.search(
        r'<div class="home-tile-grid"[^>]*>(.*?)</div>\s*<button type="button" class="home-show-more"',
        home,
        re.S,
    )
    if not gm:
        errors.append("home tile grid missing")
    else:
        tiles = split_home_tiles(gm.group(1))
        slugs = set(CATS_BY_SLUG)
        kids = [(i, t) for i, t in enumerate(tiles) if tile_slug(t, slugs) == "kids-bikes"]
        if not kids:
            errors.append("kids-bikes tile missing on home")
        else:
            i, t = kids[0]
            if i >= HOME_VISIBLE_TILES:
                errors.append(f"kids-bikes tile at slot {i} (need < {HOME_VISIBLE_TILES})")
            if "is-more" in t[:200]:
                errors.append("kids-bikes tile still has is-more")

    if "nav-home-simple" not in home:
        errors.append("home header should stay nav-home-simple")
    if 'class="mega"' in home and "site-header-home" in home:
        # mega must not be added to the home top bar
        if "mega-overview" in home.split("<main", 1)[0]:
            errors.append("home header must not grow a category mega")

    # 2) Non-home mega contains kids-bikes landing (not only comparison/reviews)
    head = about.split("<main", 1)[0]
    if "kids-bikes/" not in head or "kids-bikes/comparison/" not in head:
        errors.append("about mega missing kids-bikes landing and/or comparison")
    # a landing href that is not comparison/reviews
    if not re.search(r'href="\.\./kids-bikes/"', head):
        errors.append("about mega missing ../kids-bikes/ landing href")
    if not re.search(r'href="\.\./\.\./kids-bikes/"', cmp.split("<main", 1)[0]):
        errors.append("comparison mega missing ../../kids-bikes/ landing href")

    # 3) Footer lists kids-bikes landing
    if not re.search(r'href="(?:\.\./)*kids-bikes/"', home) and 'href="kids-bikes/"' not in home:
        errors.append("home footer missing kids-bikes landing")
    if "kids-bikes/" not in about.split("<footer", 1)[-1]:
        errors.append("about footer missing kids-bikes")

    # 4) Hub reciprocity
    if not re.search(r'href="(?:\.\./|../kids-bikes/)"', cmp) and 'href="../"' not in cmp:
        if "kids-bikes/" not in cmp:
            errors.append("comparison missing landing href")
    if "Category overview" not in cmp and "Full guide" not in cmp:
        errors.append("comparison missing Category overview / Full guide copy")
    if 'href="../"' not in rev and "kids-bikes/" not in rev:
        errors.append("reviews hub missing landing href")
    if "Category overview" not in rev and "Full guide" not in rev:
        errors.append("reviews hub missing Category overview / Full guide copy")

    if errors:
        raise SystemExit("verify failed:\n- " + "\n- ".join(errors))

    print("verify ok")
    print("  home first 8 tiles:", ", ".join(_first_home_tiles(home)))
    print("  ALL_CATS:", ", ".join(c["slug"] for c in ALL_CATS))


def main() -> None:
    cfg = load_site_config()
    print(f"bake {len(cfg['ALL_CATS'])} cats (MVP={len(cfg['MVP_CATS'])} NON_MVP={len(cfg['NON_MVP_CATS'])})")
    for spec in PAGES:
        dest = bake_page(spec, cfg)
        print(f"  wrote {dest.relative_to(ROOT)}")
    verify()


if __name__ == "__main__":
    main()
