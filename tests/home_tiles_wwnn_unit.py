#!/usr/bin/env python3
"""Unit tests for home-tile WWNN packing (no network)."""

from __future__ import annotations

import re
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
    tile_width_code,
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


_COL_FIX_RE = re.compile(
    r"home-tile--col-[34]|grid-column\s*:\s*[34]|data-home-col=\"[34]\""
)


def _unfixed_narrow_on_wide_track(tiles: list[str]) -> list[int]:
    """Narrow tiles whose auto slot is a W track (index%4 in {0,1}) need a col fix."""
    bad: list[int] = []
    for i, tile in enumerate(tiles):
        if tile_width_code(tile) != "N":
            continue
        if i % 4 in (0, 1) and not _COL_FIX_RE.search(tile[:320]):
            bad.append(i)
    return bad


def _wwnn_rows(rows: int, start: int = 0) -> list[str]:
    tiles: list[str] = []
    for i in range(start, start + rows):
        tiles.extend(
            [
                _tile("W", f"Wide {i}a", f"wide-{i}a/"),
                _tile("W", f"Wide {i}b", f"wide-{i}b/"),
                _tile("N", f"Narrow {i}a", f"narrow-{i}a/"),
                _tile("N", f"Narrow {i}b", f"narrow-{i}b/"),
            ]
        )
    return tiles


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

    # Leftover WN after complete WWNN rows (live 22=4k+2; N at %4==1).
    # Auto-placement would put that N on a 2.15fr W column → giant square.
    leftover_src = _wwnn_rows(5) + [
        _tile("W", "Hair Dryers", "hair-dryers/"),
        _tile("N", "Dash Cams", "dash-cams/"),
    ]
    leftover_packed = arrange_tiles_wwnn(leftover_src, cats)
    leftover_codes = "".join(home_tile_width_codes(leftover_packed))
    if leftover_codes != "WWNN" * 5 + "WN":
        errors.append(f"leftover WN pack expected WWNN×5+WN got {leftover_codes}")
    if "Dash Cams" not in leftover_packed[-1]:
        errors.append("leftover narrow should remain last (Dash Cams)")
    if "Hair Dryers" not in leftover_packed[-2]:
        errors.append("leftover wide should remain Hair Dryers")
    unfixed = _unfixed_narrow_on_wide_track(leftover_packed)
    if unfixed:
        errors.append(
            "leftover WN: narrow must not sit on track index%4 in {0,1} "
            f"without an explicit column fix (unfixed indexes {unfixed})"
        )
    leftover_n = leftover_packed[-1]
    if leftover_codes.endswith("WN") and not _COL_FIX_RE.search(leftover_n[:320]):
        errors.append("leftover WN narrow (%4==1) missing explicit N-track column")
    if "home-tile--col-3" not in leftover_n[:320] and 'grid-column:3' not in leftover_n[:320].replace(" ", ""):
        errors.append("leftover narrow should pin to column 3 (first N track)")

    leftover_page = reorder_home_tiles(_grid(*leftover_src), cats, HOME_VISIBLE_TILES)
    leftover_match = HOME_TILE_GRID_RE.search(leftover_page)
    leftover_tiles = split_home_tiles(leftover_match.group(2) if leftover_match else "")
    if _unfixed_narrow_on_wide_track(leftover_tiles):
        errors.append("reorder_home_tiles leftover WN left a narrow on a W track")
    if leftover_tiles[:8] and "".join(home_tile_width_codes(leftover_tiles, 8)) != "WWNNWWNN":
        errors.append(
            "first-8 after leftover pack should stay WWNN: "
            + "".join(home_tile_width_codes(leftover_tiles, 8))
        )

    # Future leftover single N: count == 4k+1, leftover index%4==0 (W track).
    solo_src = _wwnn_rows(5) + [_tile("N", "Solo Narrow", "solo-narrow/")]
    solo_packed = arrange_tiles_wwnn(solo_src, cats)
    if len(solo_packed) != 21 or len(solo_packed) % 4 != 1:
        errors.append(f"4k+1 leftover fixture should be 21 tiles, got {len(solo_packed)}")
    if tile_width_code(solo_packed[-1]) != "N" or "Solo Narrow" not in solo_packed[-1]:
        errors.append("4k+1 leftover should keep the extra narrow last")
    if (len(solo_packed) - 1) % 4 != 0:
        errors.append("4k+1 leftover index should be %4==0")
    if _unfixed_narrow_on_wide_track(solo_packed):
        errors.append(
            "leftover single N at 4k+1 must stay narrow "
            f"(unfixed {_unfixed_narrow_on_wide_track(solo_packed)})"
        )
    if "home-tile--col-3" not in solo_packed[-1][:320]:
        errors.append("leftover single N (4k+1) should pin to column 3")

    # Leftover NN after 4k: first N → col 3, second → col 4.
    nn_src = _wwnn_rows(5) + [
        _tile("N", "Narrow Extra A", "narrow-extra-a/"),
        _tile("N", "Narrow Extra B", "narrow-extra-b/"),
    ]
    nn_packed = arrange_tiles_wwnn(nn_src, cats)
    if _unfixed_narrow_on_wide_track(nn_packed):
        errors.append("leftover NN left a narrow on a W track")
    if "home-tile--col-3" not in nn_packed[-2][:320]:
        errors.append("leftover NN first N should pin to column 3")
    if "home-tile--col-4" not in nn_packed[-1][:320]:
        errors.append("leftover NN second N should pin to column 4")

    if errors:
        print("home_tiles_wwnn_unit FAILED")
        for e in errors:
            print(" -", e)
        return 1
    print("home_tiles_wwnn_unit OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
