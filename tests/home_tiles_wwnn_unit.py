#!/usr/bin/env python3
"""Unit tests for home-tile WWNN packing (no network)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from chrome import (  # noqa: E402
    HOME_TILE_GRID_RE,
    TV_HOME_TILE,
    arrange_tiles_wwnn,
    ensure_tv_home_tile,
    expected_wwnn_codes,
    home_tile_width_codes,
    reorder_home_tiles,
    split_home_tiles,
    tile_is_tv,
)
from site_config import CATS_BY_SLUG, HOME_VISIBLE_TILES  # noqa: E402


def _tile(kind: str, title: str, href: str = "", extra: str = "") -> str:
    width = "home-tile--wide" if kind == "W" else "home-tile--compact home-tile--narrow"
    tag = "div" if kind == "W" else "a"
    href_attr = f' href="{href}"' if href else ""
    return (
        f'<{tag} class="home-tile {width}" data-home-tile{extra}{href_attr}>'
        f'<strong class="home-tile-title">{title}</strong></{tag}>'
    )


def _grid(*tiles: str) -> str:
    return (
        '<div class="home-tile-grid" data-home-tile-grid>'
        + "".join(tiles)
        + '</div>\n      <button type="button" class="home-show-more"></button>'
    )


def main() -> int:
    errors: list[str] = []
    cats = CATS_BY_SLUG

    broken = [
        _tile("W", "Kids Bikes", "kids-bikes/comparison/"),
        TV_HOME_TILE,
        _tile("W", "Robot Vacuums", "robot-vacuums/"),
        _tile("W", "Espresso Machines", "espresso-machines/"),
        _tile("N", "Wet Dry Vacuums", "wet-dry-vacuums/"),
        _tile("N", "Cordless Vacuums", "cordless-vacuums/"),
        _tile("W", "Air Fryers", "air-fryers/"),
        _tile("W", "Air Purifiers", "air-purifiers/"),
        _tile("N", "Security Cameras", "security-cameras/"),
    ]
    if "".join(home_tile_width_codes(broken, 8)) != "WNWWNNWW":
        errors.append("fixture should start as live-broken WNWWNNWW")

    packed = arrange_tiles_wwnn(broken, cats)
    got = "".join(home_tile_width_codes(packed, 8))
    want = "".join(expected_wwnn_codes(8))
    if got != want:
        errors.append(f"arrange_tiles_wwnn expected {want} got {got}")
    if not tile_is_tv(packed[2]):
        errors.append("TV tile should occupy first-row narrow slot 2")
    if "Kids Bikes" not in packed[0]:
        errors.append("kids-bikes should stay first wide")

    page = _grid(*broken)
    out = ensure_tv_home_tile(page, cats, HOME_VISIBLE_TILES)
    match = HOME_TILE_GRID_RE.search(out)
    tiles = split_home_tiles(match.group(2) if match else "")
    if "".join(home_tile_width_codes(tiles, 8)) != want:
        errors.append(
            "ensure_tv_home_tile did not restore WWNN: "
            + "".join(home_tile_width_codes(tiles, 8))
        )
    if any("is-more" in t[:160] for t in tiles[:HOME_VISIBLE_TILES]):
        errors.append("visible tiles should not have is-more after ensure_tv")

    # Insert-at-1 must not win: reorder + ensure on a clean WWNN source
    # that then gets a naive mid-grid TV pin.
    source = [
        _tile("W", "Kids Bikes", "kids-bikes/comparison/"),
        _tile("W", "Robot Vacuums", "robot-vacuums/"),
        _tile("N", "Wet Dry Vacuums", "wet-dry-vacuums/"),
        _tile("N", "Cordless Vacuums", "cordless-vacuums/"),
        _tile("W", "Air Fryers", "air-fryers/"),
        _tile("W", "Air Purifiers", "air-purifiers/"),
        _tile("N", "Security Cameras", "security-cameras/"),
        _tile("N", "Video Doorbells", "video-doorbells/"),
        _tile("W", "Standing Desks", "standing-desks/"),
    ]
    page = _grid(*source)
    page = reorder_home_tiles(page, cats, HOME_VISIBLE_TILES)
    page = ensure_tv_home_tile(page, cats, HOME_VISIBLE_TILES)
    match = HOME_TILE_GRID_RE.search(page)
    tiles = split_home_tiles(match.group(2) if match else "")
    n_check = min(len(tiles), max(8, (len(tiles) // 4) * 4))
    got = "".join(home_tile_width_codes(tiles, n_check))
    want_n = "".join(expected_wwnn_codes(n_check))
    if got != want_n:
        errors.append(f"reorder+ensure expected {want_n} got {got}")
    if not any(tile_is_tv(t) for t in tiles[:4]):
        errors.append("TV tile missing from first row after reorder+ensure")
    if "is-more" not in tiles[-1][:160]:
        errors.append("overflow tile should receive is-more")

    if errors:
        print("home_tiles_wwnn_unit FAILED")
        for e in errors:
            print(" -", e)
        return 1
    print("home_tiles_wwnn_unit OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
