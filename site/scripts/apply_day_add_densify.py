#!/usr/bin/env python3
"""Apply filter densify L2 + fromsll tracks to PR #33 drafts.

Replaces water-filters / pitcher-water-filters with 10 main-product ASINs.
Optionally swaps one glass blocked slot for B0H9YH5DF9.
No wrangler / no Live / no invented tracks. kvm-switches is dropped (PR #33).

Usage:
    python3 site/scripts/apply_day_add_densify.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from affiliate_uid import ensure_affiliate_uid, is_allowed_track_host, is_empty_track
from apply_day_add_l2 import (
    DATE,
    parse_price,
    rebake_chrome_and_hubs,
    shortlist_payload,
    write_pages,
)
from scaffold_day_add import DATA, SITE

DENSIFY_DIR = Path("/tmp/mt10-densify")
DENSIFY_JSON = DENSIFY_DIR / "mt10-day-add-filter-densify-2026-10-23.json"
PACK_DIRS = [
    DENSIFY_DIR / "mt10-day-add-densify-l2-2026-10-23",
    Path("/tmp/mt10-l2-handoff/mt10-day-add-l2-2026-10-23"),
]
PROBE = DATA / "mt10-day-add-track-probe-2026-10-23.json"
BLOCKED_KEEP = frozenset({"B0HMBF83JS", "B0HLCQQ21L", "B0HJNLKK9R"})
GLASS_REPLACE = "B0HKK8PJJR"
GLASS_ALT = "B0H9YH5DF9"
BAD_TITLE = re.compile(r"<\s*a\b|href=|</|img src", re.I)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_pack(asin: str) -> dict | None:
    for folder in PACK_DIRS:
        path = folder / f"shortlistlab-detail-{asin}.json"
        if path.exists():
            blob = load_json(path)
            if blob.get("blocked"):
                return None
            return blob
    return None


def probe_tracks() -> dict[str, str]:
    out: dict[str, str] = {}
    if not PROBE.exists():
        return out
    for row in load_json(PROBE).get("per_asin") or []:
        url = (row.get("track") or "").strip()
        if row.get("asin") and url:
            out[row["asin"]] = url
    return out


def sanitize_title(raw: str | None, fallback: str) -> str:
    text = (raw or "").strip()
    if not text or BAD_TITLE.search(text) or len(text) < 8:
        return fallback
    return text


def verified_track(*candidates: str | None) -> str | None:
    for url in candidates:
        if is_empty_track(url) or not url:
            continue
        raw = url.strip()
        if not is_allowed_track_host(raw):
            continue
        if "pboost.me" in raw:
            out = ensure_affiliate_uid(raw, "pb")
            if "uid=fromsll" in out:
                return out
            continue
        # PB-attributed Amazon maas (densify SoT) — pass through if uid=fromsll already.
        if "amazon.com" in raw and "maas=" in raw and "uid=fromsll" in raw:
            return raw
    return None


def merge_row(asin: str, proposed: dict, probe: dict[str, str], *, blocked: bool = False) -> dict:
    pack = None if blocked else load_pack(asin)
    fallback_title = proposed.get("title") or asin
    title = sanitize_title((pack or {}).get("title"), fallback_title)
    title = sanitize_title(title, fallback_title)
    track = verified_track(probe.get(asin), proposed.get("pb_track"), proposed.get("held_track"))
    brand = (pack or {}).get("brand") or proposed.get("brand")
    if isinstance(brand, str):
        brand = brand.strip() or None
    price, price_raw = parse_price((pack or {}).get("price_displayed") or proposed.get("price"))
    images = (pack or {}).get("image_urls") or []
    image = images[0] if images else None
    l2_ok = bool(pack) and not blocked
    cta_ok = l2_ok and bool(track)
    pick = {
        "asin": asin,
        "title": title,
        "title_source": "l2_pack" if pack and not BAD_TITLE.search((pack or {}).get("title") or "") else "densify_sot",
        "brand": brand,
        "affiliate_network": "pb",
        "affiliate_link": track if cta_ok else None,
        "track_status": "ok" if cta_ok else "track_pending",
        "l2_status": "ok" if l2_ok else ("l2_blocked" if blocked else "l2_pending"),
        "price": price,
        "price_raw": price_raw,
        "price_displayed": (pack or {}).get("price_displayed") or proposed.get("price"),
        "list_price": (pack or {}).get("list_price"),
        "image": image,
        "availability": (pack or {}).get("availability") if l2_ok else None,
        "in_stock": (pack or {}).get("in_stock_verified") if l2_ok else None,
        "rating": (pack or {}).get("rating") if l2_ok else None,
        "review_count": (pack or {}).get("review_count") if l2_ok else None,
        "feature_bullets": ((pack or {}).get("feature_bullets") or [])[:3] if l2_ok else [],
        "l2": {
            "ok": True,
            "method": (pack or {}).get("method_used") or "mac_chrome_cdp",
            "zip": (pack or {}).get("checked_zip") or "10001",
            "fetched_at": (pack or {}).get("verified_at") or (pack or {}).get("scraped_at"),
        }
        if l2_ok
        else {"ok": False, "method": "mac_chrome_cdp", "status": "blocked" if blocked else "pending"},
    }
    if not cta_ok and track:
        pick["held_track"] = track
        pick["held_track_note"] = "PB fromsll track exists; CTA withheld until L2 ok"
    return pick


def write_shortlist(old: dict, picks: list[dict], extra_notes: list[str]) -> dict:
    payload = shortlist_payload(old, picks)
    payload["notes"] = [
        f"Day-add densify L2 {DATE}. waiting_for_部署上线=yes. No Live.",
        "Main products only — no fridge/Brita cartridges, mounts, or arms.",
        "CTA = verified fromsll (pboost.me or PB Amazon maas). No invented hops.",
        "Lifestyle cover remains a gradient placeholder.",
        *extra_notes,
    ]
    n_ok = len(payload["l2_ok_asins"])
    n = payload["density"]
    payload["density_shortfall"] = n < 10
    payload["inventory"] = (
        "l2_ok" if n == 10 and not payload["l2_pending_asins"] else ("l2_partial" if n == 10 else "density_shortfall")
    )
    payload["publishable"] = n == 10 and n_ok >= 8
    payload["baked"] = True
    dest = DATA / f"shortlist-{old['slug']}.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_pages(old["slug"], payload["name"], picks)
    return payload


def main() -> None:
    densify = load_json(DENSIFY_JSON)
    probe = probe_tracks()
    for src in (
        DENSIFY_JSON,
        DENSIFY_DIR / "mt10-day-add-densify-l2-summary-2026-10-23.json",
        DENSIFY_DIR / "mt10-day-add-filter-densify-2026-10-23.md",
    ):
        (DATA / src.name).write_bytes(src.read_bytes())

    # water-filters — full replace, drop B01CC87G86
    water_old = load_json(DATA / "shortlist-water-filters.json")
    water_rows = densify["by_slug"]["water-filters"]["proposed"]
    water_picks = [merge_row(r["asin"], r, probe) for r in water_rows]
    water = write_shortlist(
        water_old,
        water_picks,
        ["Rebuilt from densify main systems. Dropped B01CC87G86 fridge cartridge."],
    )

    # pitcher — full replace (10 main pitchers)
    pitcher_old = load_json(DATA / "shortlist-pitcher-water-filters.json")
    pitcher_rows = densify["by_slug"]["pitcher-water-filters"]["proposed"]
    pitcher_picks = [merge_row(r["asin"], r, probe) for r in pitcher_rows]
    pitcher = write_shortlist(
        pitcher_old,
        pitcher_picks,
        ["Densified to 10 pitcher/dispenser systems. Replacement cartridges stay out."],
    )

    # glass — prefer B0H9YH5DF9 over blocked B0HDKZKXS9 / B0HKK8PJJR
    glass_old = load_json(DATA / "shortlist-glass-display-cabinets.json")
    glass_picks = []
    for row in glass_old["picks"]:
        asin = row["asin"]
        if asin == GLASS_REPLACE:
            alt = next(
                r
                for r in densify["by_slug"]["glass-display-cabinets_optional"]["proposed_alts"]
                if r["asin"] == GLASS_ALT
            )
            glass_picks.append(merge_row(GLASS_ALT, alt, probe))
            continue
        glass_picks.append(
            merge_row(
                asin,
                {
                    "title": row.get("title"),
                    "brand": row.get("brand"),
                    "pb_track": row.get("affiliate_link") or row.get("held_track"),
                    "price": row.get("price_displayed"),
                },
                probe,
                blocked=asin in BLOCKED_KEEP,
            )
        )
    glass = write_shortlist(
        glass_old,
        glass_picks,
        [f"Replaced {GLASS_REPLACE} with {GLASS_ALT}. Skipped blocked alt B0HDKZKXS9."],
    )

    cover = load_json(DATA / "day-add-cover-map-2026-10-23.json")
    cover["notes"] = [
        "Cover slots only. Gradient placeholders, not product photos.",
        "waiting_for_部署上线=yes. No Live.",
        "water-filters and pitcher-water-filters densified to 10 main products.",
    ]
    (DATA / "day-add-cover-map-2026-10-23.json").write_text(
        json.dumps(cover, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    rebake_chrome_and_hubs()
    for payload in (water, pitcher, glass):
        print(
            f"{payload['slug']}: density={payload['density']} shortfall={payload['density_shortfall']} "
            f"inv={payload['inventory']} publishable={payload['publishable']} "
            f"cta={len(payload['l2_ok_asins'])} pending={payload['l2_pending_asins']}"
        )
    print("apply_day_add_densify done")


if __name__ == "__main__":
    main()
