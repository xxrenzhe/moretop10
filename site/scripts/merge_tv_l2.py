#!/usr/bin/env python3
"""Merge Mac CDP L2 price/stock/image into site/data/shortlist-tv.json by ASIN.

    python3 site/scripts/merge_tv_l2.py --l2 /path/to/tv-l2-merge.json

Does not invent ASINs. Does not rewrite `affiliate_link` (YP as-is).
OOS rows stay in the list with `oos: true` and no Check price at bake time.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SHORTLIST = ROOT / "site" / "data" / "shortlist-tv.json"


def parse_displayed_price(raw: str | None) -> str:
    if not raw:
        return ""
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)", str(raw))
    if not m:
        return ""
    return m.group(1).replace(",", "")


def merge_item(item: dict, l2: dict, meta: dict) -> None:
    displayed = l2.get("price_displayed") or ""
    numeric = parse_displayed_price(displayed)
    if numeric:
        item["price"] = numeric
    if displayed:
        item["price_displayed"] = displayed
        item["price_raw"] = displayed
    if l2.get("list_price"):
        item["list_price"] = l2["list_price"]
    oos = bool(l2.get("oos")) or (l2.get("availability") or "").lower().find("unavailable") >= 0
    item["oos"] = oos
    item["availability"] = l2.get("availability") or ("Currently unavailable" if oos else "In Stock")
    item["in_stock"] = "OOS" if oos else "IN_STOCK"
    if l2.get("image"):
        item["image"] = l2["image"]
    item["l2"] = {
        "fetched_at": meta.get("fetched_at"),
        "method": l2.get("method") or meta.get("method"),
        "zip": l2.get("checked_zip") or meta.get("zip"),
        "machine": meta.get("machine"),
        "ok": bool(l2.get("ok")),
    }
    # affiliate_link / affiliate_network left untouched.


def merge(shortlist: dict, blob: dict) -> tuple[int, int]:
    by_asin = {(p.get("asin") or "").upper(): p for p in (blob.get("products") or []) if p.get("asin")}
    meta = {
        "fetched_at": blob.get("fetched_at"),
        "method": blob.get("method"),
        "zip": blob.get("zip"),
        "machine": blob.get("machine"),
        "ok": blob.get("ok"),
        "oos": blob.get("oos") or [],
        "attempted": blob.get("attempted"),
        "blocked": blob.get("blocked"),
    }
    shortlist["l2"] = meta
    updated = 0
    missing = 0
    for key in ("hero_google_tv", "honest_fire_tv"):
        for item in shortlist.get(key) or []:
            row = by_asin.get((item.get("asin") or "").upper())
            if not row:
                missing += 1
                continue
            merge_item(item, row, meta)
            updated += 1
    return updated, missing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--l2", required=True, help="Mac CDP L2 merge JSON")
    parser.add_argument("--shortlist", default=str(DEFAULT_SHORTLIST))
    args = parser.parse_args()
    shortlist_path = Path(args.shortlist)
    blob = json.loads(Path(args.l2).read_text(encoding="utf-8"))
    shortlist = json.loads(shortlist_path.read_text(encoding="utf-8"))
    updated, missing = merge(shortlist, blob)
    notes = list(shortlist.get("notes") or [])
    stamp = (
        f"Mac CDP L2 {blob.get('fetched_at')} · ZIP {blob.get('zip')} · "
        f"ok {blob.get('ok')} / attempted {blob.get('attempted')} / "
        f"OOS {blob.get('oos')} · blocked {blob.get('blocked')}."
    )
    notes = [n for n in notes if not n.startswith("Mac CDP L2 ")]
    notes.append(stamp)
    shortlist["notes"] = notes
    shortlist_path.write_text(json.dumps(shortlist, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"merged L2 into {updated} rows; {missing} shortlist ASINs had no L2 row")


if __name__ == "__main__":
    main()
