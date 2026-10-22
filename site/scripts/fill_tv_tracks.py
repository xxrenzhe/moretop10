#!/usr/bin/env python3
"""Map YeahPromos track_link rows onto site/data/shortlist-tv.json by ASIN.

Parent / refresh usage (no Live deploy):

    python3 site/scripts/fill_tv_tracks.py \\
        --tracks /path/to/tv-yp-tracks-google-YYYY-MM-DD.json

Hard lock: writes `affiliate_link` exactly as `track_link`. Never appends
uid / subid / site params. PB pboost.me hops (if any) go through
`ensure_affiliate_uid`; YP yeahpromos.com / Amazon maas pass through.

Does not invent ASINs. ASINs already in the shortlist that are missing from
the tracks file keep their previous link (or stay empty).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from affiliate_uid import prepare_affiliate_link  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SHORTLIST = ROOT / "site" / "data" / "shortlist-tv.json"


def _index_tracks(blob: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for bucket in ("google_tv", "fire_tv", "tracks", "items"):
        rows = blob.get(bucket) or []
        if isinstance(rows, dict):
            rows = rows.values()
        for row in rows:
            if not isinstance(row, dict):
                continue
            asin = (row.get("asin") or "").strip().upper()
            track = (row.get("track_link") or row.get("amazon_track_link") or "").strip()
            if asin and track:
                out[asin] = row
    return out


def fill(shortlist: dict, tracks: dict[str, dict]) -> tuple[int, int]:
    updated = 0
    skipped = 0
    for key in ("hero_google_tv", "honest_fire_tv"):
        for item in shortlist.get(key) or []:
            asin = (item.get("asin") or "").strip().upper()
            row = tracks.get(asin)
            if not row:
                skipped += 1
                continue
            raw = (row.get("track_link") or row.get("amazon_track_link") or "").strip()
            network = item.get("affiliate_network") or "yp"
            href = prepare_affiliate_link(raw, network)
            if href is None:
                skipped += 1
                continue
            item["affiliate_link"] = href
            item["affiliate_network"] = network
            if row.get("price") and not item.get("price_raw"):
                item["price_raw"] = row["price"]
            if row.get("in_stock"):
                item["in_stock"] = row["in_stock"]
            updated += 1
    return updated, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracks", required=True, help="YP track JSON (google_tv + fire_tv)")
    parser.add_argument("--shortlist", default=str(DEFAULT_SHORTLIST))
    args = parser.parse_args()

    shortlist_path = Path(args.shortlist)
    tracks_path = Path(args.tracks)
    shortlist = json.loads(shortlist_path.read_text(encoding="utf-8"))
    blob = json.loads(tracks_path.read_text(encoding="utf-8"))
    updated, skipped = fill(shortlist, _index_tracks(blob))
    shortlist_path.write_text(json.dumps(shortlist, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"filled {updated} tracks; {skipped} shortlist rows had no matching ASIN")


if __name__ == "__main__":
    main()
