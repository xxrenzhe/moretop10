#!/usr/bin/env python3
"""Bake P6c MT10 scenario best-of pages (6 type-07 children).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not recreate live parent hubs. Do not rebind CTA to YeahPromos.
Do not scaffold litter-boxes/best-litter-boxes-for-large-cats (SHORTFALL n=1).
Do not flip #58 P6a or #60 P6b (or day-add) scenes to published=true.

Hard rules:
  - Type-07 pages only. published=false / noindex until 部署上线.
  - Use products-*.json ASINs / roles / prices / tracks as given. No invented ASINs / was / %.
  - Density from products SoT (6/10/10/10/10/10). Honest shortfall counts OK; do not pad.
  - Soft parent densify: hub ASINs may appear on a scene. Sibling scene ASINs stay banned.
  - No accessories as hero picks. Lab independent.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).
  - Comparison / reviews stubs already exist on parent hubs — do not recreate or
    roll stamps earlier than 2026-10-24.

Usage:
    python3 site/scripts/bake_p6c_scenario.py
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
DATA = SITE / "data"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import bake_p4_scenario as p4  # noqa: E402
from affiliate_uid import classify_network  # noqa: E402
from bake_p4_scenario import (  # noqa: E402
    ACCESSORY_RE,
    ASIN_RE,
    TEMPLATE,
    TEMPLATE_LEFTOVER,
    TEMPLATE_LEFTOVER_NON_HUMIDIFIER,
    _asin_set,
    _esc,
    add_landing_cluster,
    bump_or_insert_sitemap,
    clone_chrome,
    healthy_track,
    replace_head,
    replace_main,
    scene_article,
    scene_faqs,
    token_env,
)
from seo_geo import LIVE, ROBOTS_NOINDEX, rewrite_visible_jargon, set_robots_meta  # noqa: E402

DATE = "2026-10-24"
p4.DATE = DATE
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P6c scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
OCCUPIED_PATH = DATA / "p6c-occupied-asins-2026-10-24.json"
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-p6c-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-p6c-fill-pack/mt10-p6c-fill-pack-2026-10-24.json"),
    Path("/home/ubuntu/.cursor/projects/workspace/uploads/mt10-p6c-fill-pack-2026-10-24_deca.json"),
    Path("/home/ubuntu/.cursor/projects/workspace/uploads/pack_7fc2.json"),
    DATA / "mt10-p6c-fill-pack-2026-10-24.json",
    DATA / "p6c-l1-fill-pack-2026-10-24.json",
)
PACK_INREPO = DATA / "p6c-l1-fill-pack-2026-10-24.json"
PARENT_HUBS = (
    "projectors",
    "humidifiers",
    "doormats",
    "noise-cancelling-headphones",
    "bluetooth-speakers",
    "office-chairs",
)
SKIPPED = (
    {
        "path": "best-litter-boxes-for-large-cats",
        "url": "/litter-boxes/best-litter-boxes-for-large-cats/",
        "reason": "SHORTFALL n=1 < density 4 — skip scaffold",
    },
)
OUT_NICHES = (
    "best-litter-boxes-for-large-cats",
    "best-hearing-aids-for-tinnitus",
    "best-mattresses-for-hanging",
    "best-red-light-therapy-masks",
    "best-robot-mops",
)
PRIOR_KEEP_UNPUBLISHED = (
    "products-best-robotic-pool-cleaners-for-inground-pools.json",
    "products-best-bike-racks-for-hitch.json",
    "products-best-espresso-machines-under-500.json",
    "products-best-hair-dryers-for-thick-hair.json",
    "products-best-security-cameras-for-indoor.json",
    "products-best-projectors-for-bedroom.json",
    "products-best-dehumidifiers-for-bathroom.json",
    "products-best-computer-speakers-for-gaming.json",
    "products-best-litter-boxes-for-multiple-cats.json",
    "products-best-light-therapy-for-face.json",
    "products-best-office-chairs-for-gaming.json",
    "products-best-dehumidifiers-for-crawl-space.json",
    "products-best-bluetooth-speakers-for-outdoor.json",
    "products-best-projectors-for-home-theater.json",
    "products-best-projectors-for-outdoor.json",
    "products-best-office-chairs-for-long-hours.json",
    "products-best-humidifiers-for-large-rooms.json",
)
MOUNT_TOY_RE = re.compile(
    r"\btripod only\b|\bwall mount only\b|\bceiling mount\b|\btoy projector\b|"
    r"galaxy projector|star projector",
    re.I,
)
OIL_TENT_RE = re.compile(r"essential oil|grow[\s-]?tent|diffuser only", re.I)
EARBUD_RE = re.compile(r"\bearbuds?\b|\bin-ear\b|true wireless", re.I)
WATERPROOF_RE = re.compile(r"\bipx?\s?\d|waterproof|shower", re.I)
SPEAKER_MOUNT_RE = re.compile(r"suction cup only|mount only", re.I)

SCENES: list[dict[str, Any]] = [
    {
        "n": 1,
        "slug": "projectors",
        "name": "Projectors",
        "path": "best-projectors-for-gaming",
        "label": "Best for gaming",
        "keyword": "best projectors for gaming",
        "title": "Best Projectors for Gaming",
        "h1": "Best Projectors for Gaming (2026)",
        "job": "gaming-capable smart or FHD projectors — not mounts, toys, or a bedroom/outdoor/home-theater paste",
        "confirm": (
            "Confirm input lag notes, native resolution, and smart-TV apps on the retailer "
            "page. We do not invent ANSI lumen scores."
        ),
        "skip": (
            "Skip this slice if you want a mount, a toy projector, or the bedroom, outdoor, "
            "or home-theater shortlists already on those pages."
        ),
        "lede": (
            "Gaming projection is a full smart or FHD projector job — not a mount or toy, "
            "and not a paste of the bedroom, outdoor, or home-theater shortlists."
        ),
        "ban_groups": ["projector_siblings"],
        "soft_hub_groups": ["projector_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-projectors-for-bedroom", "label": "Best for bedroom"},
            {"path": "best-projectors-for-outdoor", "label": "Best for outdoor"},
            {"path": "best-projectors-for-home-theater", "label": "Best for home theater"},
        ],
        "density_expected": 6,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-projectors.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-projectors.jpg",
    },
    {
        "n": 2,
        "slug": "humidifiers",
        "name": "Humidifiers",
        "path": "best-humidifiers-for-plants",
        "label": "Best for plants",
        "keyword": "best humidifiers for plants",
        "title": "Best Humidifiers for Plants",
        "h1": "Best Humidifiers for Plants (2026)",
        "job": "cool-mist humidifiers that can serve plants — not essential-oil accessories or grow-tent bundles",
        "confirm": (
            "Confirm tank size, cool-mist notes, and whether any plant or grow kit ships "
            "in the box on the retailer page. We do not invent humidity scores."
        ),
        "skip": (
            "Skip this slice if you want an essential-oil accessory, a grow-tent bundle, or "
            "the baby, bedroom, or large-room shortlists already on those pages."
        ),
        "lede": (
            "Plant humidity is a cool-mist humidifier job — not an essential-oil add-on, "
            "and not a paste of the baby, bedroom, or large-room shortlists."
        ),
        "ban_groups": ["humidifier_siblings"],
        "soft_hub_groups": ["humidifier_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-humidifiers-for-babies", "label": "Best for babies"},
            {"path": "best-humidifiers-for-bedrooms", "label": "Best for bedrooms"},
            {"path": "best-humidifiers-for-large-rooms", "label": "Best for large rooms"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-humidifiers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-humidifiers.jpg",
    },
    {
        "n": 3,
        "slug": "doormats",
        "name": "Doormats",
        "path": "best-doormats-for-outdoors",
        "label": "Best for outdoors",
        "keyword": "best doormats for outdoors",
        "title": "Best Doormats for Outdoors",
        "h1": "Best Doormats for Outdoors (2026)",
        "job": "outdoor or entry dirt-trapper doormats — not indoor-only runners",
        "confirm": (
            "Confirm size, washability, and outdoor or entry use on the retailer page. "
            "We do not invent absorbency scores."
        ),
        "skip": (
            "Skip this slice if you want an indoor-only runner or a kitchen rug. Those "
            "jobs are not this outdoor entry page."
        ),
        "lede": (
            "Outdoor entry cleanup is a dirt-trapper doormat job — not an indoor runner "
            "and not a kitchen rug."
        ),
        "ban_groups": ["doormat_siblings"],
        "soft_hub_groups": ["doormat_hub"],
        "cross_ban_scenes": [],
        "siblings": [],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-doormats.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-doormats.jpg",
    },
    {
        "n": 4,
        "slug": "noise-cancelling-headphones",
        "name": "Noise-Cancelling Headphones",
        "path": "best-noise-cancelling-headphones-for-work",
        "label": "Best for work",
        "keyword": "best noise cancelling headphones for work",
        "title": "Best Noise Cancelling Headphones for Work",
        "h1": "Best Noise Cancelling Headphones for Work (2026)",
        "job": "over-ear active noise-cancelling headphones for desk or office work — not earbuds",
        "confirm": (
            "Confirm over-ear fit, ANC notes, and call-mic features on the retailer page. "
            "We do not invent decibel-reduction scores."
        ),
        "skip": (
            "Skip this slice if you want earbuds, in-ear buds, or a travel-first shortlist. "
            "Those jobs are not this work page."
        ),
        "lede": (
            "Desk and office quiet is an over-ear ANC headphone job — not earbuds, and "
            "not a paste of a travel shortlist."
        ),
        "ban_groups": ["nc_siblings"],
        "soft_hub_groups": ["nc_hub"],
        "cross_ban_scenes": [],
        "siblings": [],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-headphones.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-headphones.jpg",
    },
    {
        "n": 5,
        "slug": "bluetooth-speakers",
        "name": "Bluetooth Speakers",
        "path": "best-bluetooth-speakers-for-shower",
        "label": "Best for shower",
        "keyword": "best bluetooth speakers for shower",
        "title": "Best Bluetooth Speakers for Shower",
        "h1": "Best Bluetooth Speakers for Shower (2026)",
        "job": "IP-rated waterproof shower Bluetooth speakers — not mounts or outdoor-first portables",
        "confirm": (
            "Confirm IP or waterproof rating and how it hangs or sits in a shower on the "
            "retailer page. We do not invent watt ratings."
        ),
        "skip": (
            "Skip this slice if you want a suction-cup mount by itself or the outdoor "
            "Bluetooth shortlist already on Best for outdoor."
        ),
        "lede": (
            "Shower audio is an IP-rated waterproof speaker job — not a mount, and not a "
            "paste of the outdoor Bluetooth shortlist."
        ),
        "ban_groups": ["bt_siblings"],
        "soft_hub_groups": ["bt_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-bluetooth-speakers-for-outdoor", "label": "Best for outdoor"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-bluetooth-speakers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-bluetooth-speakers.jpg",
    },
    {
        "n": 6,
        "slug": "office-chairs",
        "name": "Office Chairs",
        "path": "best-office-chairs-under-200",
        "label": "Best under $200",
        "keyword": "best office chairs under 200",
        "title": "Best Office Chairs Under $200",
        "h1": "Best Office Chairs Under $200 (2026)",
        "job": "office or desk chairs with an honest now price at or under $200",
        "confirm": (
            "Confirm the live cart is still at or under $200, plus lumbar support and "
            "weight rating on the retailer page. We do not invent discounts."
        ),
        "skip": (
            "Skip this slice if you want a gaming, back-pain, or long-hours chair already "
            "on those pages, or any chair whose honest now price is over $200."
        ),
        "lede": (
            "A sub-$200 desk chair is a full office chair with an honest now price at or "
            "under $200 — not a mat, and not a paste of the gaming, back-pain, or "
            "long-hours shortlists."
        ),
        "ban_groups": ["chair_siblings"],
        "soft_hub_groups": ["chair_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-office-chairs-for-back-pain", "label": "Best for back pain"},
            {"path": "best-office-chairs-for-long-hours", "label": "Best for long hours"},
            {"path": "best-office-chairs-for-gaming", "label": "Best for gaming"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-office-chairs.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-office-chairs.jpg",
    },
]


def load_occupied() -> dict[str, set[str]]:
    blob = json.loads(OCCUPIED_PATH.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = {}
    for key, values in (blob.get("scene_ban_keys") or {}).items():
        out[key] = _asin_set(values)
    for key, values in (blob.get("by_source") or {}).items():
        if key in out or not isinstance(values, list):
            continue
        out[key] = _asin_set(values)
    out["global"] = _asin_set(blob.get("flat"))
    if not out["global"]:
        extra: set[str] = set()
        for key, values in out.items():
            if key != "global":
                extra |= values
        out["global"] = extra
    return out


def pack_blob(pack: dict[str, Any] | None, scene: dict[str, Any]) -> dict[str, Any]:
    if not pack:
        return {}
    scenes = pack.get("scenes") or {}
    return (
        scenes.get(scene["path"])
        or scenes.get(f"/{scene['slug']}/{scene['path']}/")
        or scenes.get(scene.get("scene_slug") or "")
        or {}
    )


def sibling_asins_from_pack(pack: dict[str, Any] | None) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for scene in SCENES:
        asins: set[str] = set()
        for row in pack_blob(pack, scene).get("products") or pack_blob(pack, scene).get("picks") or []:
            asin = str(row.get("asin") or "").strip().upper()
            if ASIN_RE.fullmatch(asin):
                asins.add(asin)
        out[scene["path"]] = asins
    return out


def banned_for(
    scene: dict[str, Any],
    occupied: dict[str, set[str]],
    sibling_asins: dict[str, set[str]] | None = None,
) -> set[str]:
    banned = set(occupied.get("global") or ())
    for key in scene.get("soft_hub_groups") or []:
        banned -= occupied.get(key) or set()
    for key in scene.get("ban_groups") or []:
        banned |= occupied.get(key) or set()
    for sib in scene.get("cross_ban_scenes") or []:
        banned |= (sibling_asins or {}).get(sib) or set()
    return banned


def find_fill_pack() -> Path | None:
    for path in PACK_CANDIDATES:
        if path.exists():
            return path
    return None


def parse_price(row: dict[str, Any]) -> float | None:
    raw = row.get("price")
    if raw is not None and raw != "":
        try:
            return float(raw)
        except (TypeError, ValueError):
            pass
    text = str(row.get("price_str") or row.get("price_displayed") or "").replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if match:
        return float(match.group(1))
    return None


def pick_from_pack(row: dict[str, Any], banned: set[str], scene: dict[str, Any]) -> dict[str, Any] | None:
    asin = str(row.get("asin") or "").strip().upper()
    title = str(row.get("title") or "").strip()
    track = healthy_track(row.get("track_url") or row.get("affiliate_link"))
    if not asin or not title or not track:
        return None
    if not ASIN_RE.fullmatch(asin):
        return None
    if asin.upper().startswith("B0X") and set(asin[2:]) <= set("X"):
        return None
    if asin in banned:
        return None
    if ACCESSORY_RE.search(title):
        return None
    path = scene["path"]
    if path == "best-projectors-for-gaming" and MOUNT_TOY_RE.search(title):
        return None
    if path == "best-humidifiers-for-plants" and OIL_TENT_RE.search(title):
        return None
    if path == "best-noise-cancelling-headphones-for-work" and EARBUD_RE.search(title):
        return None
    if path == "best-bluetooth-speakers-for-shower":
        if SPEAKER_MOUNT_RE.search(title) or not WATERPROOF_RE.search(title):
            return None
    price = row.get("price")
    price_str = row.get("price_str") or row.get("price_displayed")
    if price is not None and not price_str:
        price_str = f"${float(price):.2f}" if isinstance(price, (int, float)) else f"${price}"
    parsed = parse_price(row)
    if path == "best-office-chairs-under-200":
        if parsed is None or parsed > 200:
            return None
    network = classify_network(row.get("track_url") or row.get("affiliate_link") or "")
    if network != "pb":
        return None
    return {
        "asin": asin,
        "title": title,
        "title_source": "l1_pack",
        "brand": str(row.get("brand") or "").strip() or None,
        "role": str(row.get("role") or "").strip() or None,
        "affiliate_network": "pb",
        "affiliate_link": track,
        "track_status": "ok",
        "price": f"{price}" if price is not None else None,
        "price_displayed": price_str,
        "image": None,
        "feature_bullets": [],
        "availability": row.get("availability"),
    }


def products_path(scene: dict[str, Any]) -> Path:
    return DATA / f"products-{scene['path']}.json"


def load_products_sot(scene: dict[str, Any]) -> list[dict[str, Any]]:
    dest = products_path(scene)
    if not dest.exists():
        return []
    blob = json.loads(dest.read_text(encoding="utf-8"))
    if blob.get("published") is True:
        raise SystemExit(f"{dest.name} must stay published=false")
    return list(blob.get("products") or [])


def scene_picks_from_products(
    scene: dict[str, Any], banned: set[str]
) -> list[dict[str, Any]]:
    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in load_products_sot(scene):
        pick = pick_from_pack(row, banned, scene)
        if not pick or pick["asin"] in seen:
            continue
        seen.add(pick["asin"])
        picks.append(pick)
    return picks


def write_products_shell(scene: dict[str, Any], picks: list[dict[str, Any]]) -> None:
    dest = products_path(scene)
    dest.write_text(
        json.dumps(
            {
                "path": f"/{scene['slug']}/{scene['path']}/",
                "published": False,
                "fill_status": "filled" if picks else "need_fill",
                "waiting_for_部署上线": True,
                "stub": bool(scene.get("stub")),
                "products": [
                    {
                        "asin": p["asin"],
                        "title": p["title"],
                        "role": p.get("role"),
                        "brand": p.get("brand"),
                        "track_url": p.get("affiliate_link"),
                        "price": p.get("price"),
                        "price_str": p.get("price_displayed"),
                    }
                    for p in picks
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _pick_public(pick: dict[str, Any]) -> dict[str, Any]:
    return {
        "asin": pick["asin"],
        "title": pick["title"],
        "role": pick.get("role"),
        "brand": pick.get("brand"),
        "affiliate_link": pick.get("affiliate_link"),
        "track_status": pick.get("track_status"),
        "price": pick.get("price_displayed"),
        "image": None,
    }


def hub_product_count(slug: str) -> int:
    html = (SITE / slug / "index.html").read_text(encoding="utf-8")
    return len(set(ASIN_RE.findall(html.upper())))


def build_inventory(
    by_path: dict[str, list[dict[str, Any]]],
    pack_path: Path | None,
    occupied: dict[str, set[str]],
) -> dict[str, Any]:
    tokens = token_env()
    pages = []
    for scene in SCENES:
        picks = by_path[scene["path"]]
        n = len(picks)
        pages.append(
            {
                "n": scene["n"],
                "path": f"/{scene['slug']}/{scene['path']}/",
                "type": "07-best-of",
                "parent": f"/{scene['slug']}/",
                "published": False,
                "robots": ROBOTS_NOINDEX,
                "density": n,
                "density_target": 10,
                "density_expected": scene["density_expected"],
                "stub": bool(scene.get("stub")),
                "fill_status": "filled" if n else "need_fill",
                "cta_status": "pb_fromsll" if n else "empty",
                "cta_rule": "PB fromsll only when a verified track exists; never invent hops; do not rebind to YP",
                "reviews": "none — Top pick + Upgrade articles do not exist for this scene",
                "ban_groups": scene["ban_groups"],
                "soft_hub_groups": scene.get("soft_hub_groups") or [],
                "cross_ban_scenes": scene["cross_ban_scenes"],
                "picks": [_pick_public(p) for p in picks],
            }
        )
    filled = sum(1 for row in pages if row["fill_status"] == "filled")
    hub_counts = {hub: hub_product_count(hub) for hub in PARENT_HUBS}
    hub_note = " ".join(f"{hub}={hub_counts[hub]}" for hub in PARENT_HUBS)
    return {
        "date": DATE,
        "batch": "P6c",
        "lock": "lock-p6c-rec",
        "tip_reference": "007d73ffe4e27a012c952f92499c9073e6fcda56",
        "waiting_for_部署上线": True,
        "published": False,
        "live": False,
        "merged": False,
        "independent_of_shortlist_lab": True,
        "do_not_touch": [
            "Lab",
            "RR",
            "OL",
            "#54 home nav",
            "#55 stamp",
            "#58 P6a published flip",
            "#60 P6b published flip",
            "day-add published flip",
            "parent hub cards",
        ],
        "parent_hubs": "exist_not_recreated",
        "soft_parent_densify": (
            "hub ASINs may appear on scene; sibling bans still hold; "
            f"hub ASINs {hub_note}"
        ),
        "skipped": list(SKIPPED),
        "out_of_scope": list(OUT_NICHES),
        "brand_notes": {
            "best-doormats-for-outdoors": (
                "JSEI brand_gate risk reported; multi-brand with BEQHAUSE; density 10 OK"
            ),
            "best-office-chairs-under-200": "honest now price <=200 on every packed card",
            "best-projectors-for-gaming": "aurzen + happrun; density 6 >= 4",
        },
        "fill_pack": str(pack_path) if pack_path else None,
        "fill_status": "partial" if 0 < filled < len(pages) else ("filled" if filled else "need_fill"),
        "need_fill": [row["path"] for row in pages if row["fill_status"] == "need_fill"],
        "counts": {scene["path"]: len(by_path[scene["path"]]) for scene in SCENES},
        "sources": {
            "1_pb": {
                "live_query": "skipped_no_token" if not tokens["available"] else "ran",
                "note": tokens["note"],
            },
            "2_yp": {
                "live_query": "skipped_yp_timeout_or_500",
                "note": "YP unused. Pack is PB-only. Live CTA stays PB ?uid=fromsll.",
            },
            "l1_fill_pack": pack_path.name if pack_path else None,
            "products_sot": [f"products-{scene['path']}.json" for scene in SCENES],
        },
        "occupied_groups": {
            k: sorted(v)
            for k, v in occupied.items()
            if k
            in {
                "projector_siblings",
                "projector_hub",
                "humidifier_siblings",
                "humidifier_hub",
                "doormat_siblings",
                "doormat_hub",
                "nc_siblings",
                "nc_hub",
                "bt_siblings",
                "bt_hub",
                "chair_siblings",
                "chair_hub",
            }
        },
        "occupied_global_n": len(occupied.get("global") or ()),
        "pages": pages,
        "notes": [
            "No invented ASINs, prices, was/%, gallery, or Check price hops.",
            "Parent hubs already exist. Not recreated. Soft densify = hub ASINs allowed; sibling bans hold.",
            "published=false / noindex until a later 部署上线 order.",
            "Independent of Shortlist Lab.",
            "Litter large-cats skipped (SHORTFALL n=1).",
            "Did not flip #58 P6a or #60 P6b published=true.",
            "Did not flip day-add published=true.",
            "OUT: tinnitus · mattress hang · red-light masks · robot-mop · TV blocked.",
            "JSEI doormat brand_gate risk reported, not hard-fail.",
            "Comparison / reviews stubs already exist. Stamps not rolled back.",
        ],
    }


def leftover_terms(scene: dict[str, Any]) -> tuple[str, ...]:
    leftovers = list(TEMPLATE_LEFTOVER)
    if scene["slug"] != "humidifiers":
        leftovers.extend(TEMPLATE_LEFTOVER_NON_HUMIDIFIER)
    leftovers.extend(
        (
            "inventory_blocked",
            "best-litter-boxes-for-large-cats",
            "best-hearing-aids-for-tinnitus",
            "best-mattresses-for-hanging",
            "best-red-light-therapy-masks",
            "best-robot-mops",
            "best-pillows-for-snoring",
            "best-ceramic-space-heaters-for-bedroom",
            "best-pillows-for-back-sleepers",
            "best-mattresses-for-back-pain",
        )
    )
    return tuple(leftovers)


def assert_clean_page(
    html: str, scene: dict[str, Any], banned: set[str], picks: list[dict[str, Any]]
) -> None:
    errors: list[str] = []
    n = len(picks)
    if DRAFT_COMMENT not in html:
        errors.append("missing waiting_for_部署上线 draft comment")
    if f'name="robots" content="{ROBOTS_NOINDEX}"' not in html:
        errors.append("robots is not noindex,follow")
    for leak in leftover_terms(scene):
        if leak in html:
            errors.append(f"template leftover {leak!r}")
    visits = html.count('class="bestof-visit-card"')
    if visits != n:
        errors.append(f"visit cards={visits} (need {n})")
    inline_need = min(3, n)
    if html.count('class="inline-pick-card"') != inline_need:
        errors.append(f"inline picks != {inline_need}")
    if n == 0:
        if "btn-cta-yellow" in html:
            errors.append("invented Check price CTA")
        if "pboost.me" in html or "yeahpromos.com" in html:
            errors.append("invented affiliate hop")
        if re.search(r"\$\d", html):
            errors.append("invented price")
        if "Density is honest at 0" not in html:
            errors.append("missing honest density copy")
    else:
        if html.count("pboost.me") < n:
            errors.append("missing PB tracks on visit cards")
        if "uid=fromsll" not in html:
            errors.append("PB tracks missing uid=fromsll")
        if "yeahpromos.com" in html:
            errors.append("YP rebind is not allowed")
        if f"Density is honest at {n}" not in html:
            errors.append("missing honest density copy")
        for pick in picks:
            if pick["asin"] not in html:
                errors.append(f"missing packed ASIN {pick['asin']}")
            if pick["affiliate_link"] not in html:
                errors.append(f"missing track for {pick['asin']}")
    if "amazon.com/dp/" in html or "m.media-amazon.com" in html:
        errors.append("invented Amazon gallery or hop")
    if "10%" in html or "12%" in html:
        errors.append("invented or leftover was/%")
    if "was $" in html.lower() or "list_price" in html:
        errors.append("invented or leftover was/list_price")
    for asin in banned:
        if asin in html:
            errors.append(f"banned ASIN leaked {asin}")
    visible_article = ""
    start = html.find('<article class="landing-article">')
    end = html.find("</article>", start) if start >= 0 else -1
    if start >= 0 and end >= 0:
        visible_article = html[start:end]
    if "kids-bikes" in visible_article:
        errors.append("kids-bikes chrome leaked into visitor article")
    if errors:
        raise SystemExit(f"{scene['path']} bake assert failed: " + "; ".join(errors))


def write_scene(
    scene: dict[str, Any],
    banned: set[str],
    picks: list[dict[str, Any]],
) -> None:
    faqs = scene_faqs(scene, picks)
    out_rel = f"{scene['slug']}/{scene['path']}/index.html"
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{LIVE}/{scene['slug']}/{scene['path']}/"
    title = f"{scene['title']} | MoreTop10"
    n = len(picks)
    if n:
        desc = (
            f"{scene['lede']} This best-of lists {n} verified products that fit this job."
        )
        page_desc = (
            f"Editorial slice of {scene['name'].lower()} for {scene['keyword']} — "
            f"honest density {n} from verified retailer links."
        )
    else:
        desc = (
            f"{scene['lede']} This best-of stays empty until a verified retailer "
            "link exists — we do not invent a padded Top 10."
        )
        page_desc = (
            f"Editorial slice of {scene['name'].lower()} for {scene['keyword']} — "
            "honest density 0 until a verified retailer link exists."
        )
    html = clone_chrome(out_rel, scene["slug"])
    html = replace_head(
        html,
        title=title,
        description=desc,
        url=url,
        og_image=scene["og_image"],
        faqs=faqs,
        page_desc=page_desc,
        picks=picks,
        scene=scene,
    )
    html = replace_main(
        html,
        h1=scene["h1"],
        article=scene_article(scene, faqs, picks),
        scene=scene,
    )
    html = rewrite_visible_jargon(html)
    html = set_robots_meta(html, ROBOTS_NOINDEX)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    assert_clean_page(html, scene, banned, picks)
    dest.write_text(html, encoding="utf-8")


def patch_html_sitemap() -> None:
    path = SITE / "sitemap" / "index.html"
    html = path.read_text(encoding="utf-8")
    for scene in SCENES:
        href = f'../{scene["slug"]}/{scene["path"]}/'
        if href not in html:
            marker = f'<a href="../{scene["slug"]}/comparison/">Compare</a>'
            if marker not in html:
                raise SystemExit(f"sitemap/index.html missing {scene['slug']} row")
            html = html.replace(
                marker,
                f'{marker} · <a href="{href}">{_esc(scene["label"])}</a>',
                1,
            )
        li_re = re.compile(
            rf'(<li><a href="../{re.escape(scene["slug"])}/">.*?</li>)'
        )
        match = li_re.search(html)
        if match and href not in match.group(1):
            html = (
                html[: match.end() - 5]
                + f' · <a href="{href}">{_esc(scene["label"])}</a></li>'
                + html[match.end() :]
            )
    path.write_text(html, encoding="utf-8")


def write_inventory(inv: dict[str, Any]) -> None:
    dest = DATA / "p6c-scenario-inventory-2026-10-24.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = []
    for row in inv["pages"]:
        rows.append(
            f"| `{row['path']}` | **{row['density']}** | `{row['fill_status']}` | "
            f"{row['cta_status']} | none |"
        )
    need = inv.get("need_fill") or []
    md = DATA / "p6c-scenario-inventory-2026-10-24.md"
    md.write_text(
        "\n".join(
            [
                "# P6c scenario best-of inventory (2026-10-24)",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / noindex",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Parent hubs:** already exist — not recreated.",
                "**Tip:** `007d73ffe4e27a012c952f92499c9073e6fcda56` (#60 Live).",
                "",
                "## Fill status",
                "",
                f"- Global fill status: `{inv['fill_status']}`",
                f"- Fill pack: `{inv.get('fill_pack') or 'missing — need_fill shells'}`",
                f"- Occupied collision set: `{inv.get('occupied_global_n')} ASINs`",
                f"- Affiliate tokens on VM: `{inv['sources']['1_pb']['live_query']}` / `{inv['sources']['2_yp']['live_query']}`",
                f"- Hubs that need_fill: {len(need)}",
                f"- Soft parent densify: `{inv.get('soft_parent_densify')}`",
                "",
                "## Paths",
                "",
                "| Path | Density | Fill | CTA | Reviews |",
                "| --- | --- | --- | --- | --- |",
                *rows,
                "",
                "## Skipped",
                "",
                "- `/litter-boxes/best-litter-boxes-for-large-cats/` — SHORTFALL n=1 < density 4. Not scaffolded.",
                "",
                "## Hard rules kept",
                "",
                "- No invented ASINs / prices / was / % / gallery / CTAs.",
                "- No accessories as primary picks.",
                "- Sibling ASIN bans hold. Soft parent densify preferred (hub ASINs may appear).",
                "- Reviews skipped. Comparison / reviews stubs already exist — stamps not rolled back.",
                "- Independent of Shortlist Lab.",
                "- Did not flip #58 P6a or #60 P6b published=true.",
                "- Did not flip day-add published=true.",
                "- JSEI doormat brand_gate risk reported, not hard-fail.",
                "- Office chairs use honest now price ≤$200.",
                "- OUT: tinnitus · mattress hang · red-light masks · robot-mop · TV blocked.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def refuse_skipped_pages() -> None:
    blocked = (
        SITE / "litter-boxes" / "best-litter-boxes-for-large-cats" / "index.html",
        SITE / "hearing-aids" / "best-hearing-aids-for-tinnitus" / "index.html",
        SITE / "mattresses" / "best-mattresses-for-hanging" / "index.html",
        SITE / "light-therapy" / "best-red-light-therapy-masks" / "index.html",
        SITE / "robot-vacuums" / "best-robot-mops" / "index.html",
        DATA / "products-best-litter-boxes-for-large-cats.json",
    )
    for path in blocked:
        if path.exists():
            raise SystemExit(f"must not scaffold {path}")


def assert_prior_stays_unpublished() -> None:
    for name in PRIOR_KEEP_UNPUBLISHED:
        path = DATA / name
        if not path.exists():
            raise SystemExit(f"expected existing unpublished shell {name}")
        blob = json.loads(path.read_text(encoding="utf-8"))
        if blob.get("published") is True:
            raise SystemExit(f"must not flip {name} to published=true")


def main() -> int:
    if not TEMPLATE.exists():
        raise SystemExit(f"missing type-07 template {TEMPLATE}")
    for hub in PARENT_HUBS:
        if not (SITE / hub / "index.html").exists():
            raise SystemExit(f"expected existing /{hub}/ hub — do not invent a new hub here")
        if not (SITE / hub / "comparison" / "index.html").exists():
            raise SystemExit(f"expected existing /{hub}/comparison/ stub — do not invent one here")
        if not (SITE / hub / "reviews" / "index.html").exists():
            raise SystemExit(f"expected existing /{hub}/reviews/ stub — do not invent one here")
    occupied = load_occupied()
    pack_path = find_fill_pack()
    pack = None
    if pack_path:
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        if pack_path.resolve() != PACK_INREPO.resolve():
            PACK_INREPO.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pack_path, PACK_INREPO)
            pack_path = PACK_INREPO
    siblings = sibling_asins_from_pack(pack)
    by_path: dict[str, list[dict[str, Any]]] = {}
    for scene in SCENES:
        banned = banned_for(scene, occupied, siblings)
        sot = load_products_sot(scene)
        if not sot:
            raise SystemExit(f"{scene['path']} missing products-*.json source of truth")
        picks = scene_picks_from_products(scene, banned)
        expected = int(scene["density_expected"])
        if len(picks) != expected:
            raise SystemExit(
                f"{scene['path']} expected density {expected} from products SoT, got {len(picks)}"
            )
        sot_asins = [str(row.get("asin") or "").strip().upper() for row in sot]
        pick_asins = [p["asin"] for p in picks]
        if pick_asins != sot_asins:
            raise SystemExit(
                f"{scene['path']} bake reordered or dropped products SoT ASINs: "
                f"{pick_asins} != {sot_asins}"
            )
        by_path[scene["path"]] = picks
        write_products_shell(scene, picks)
        write_scene(scene, banned, picks)
        add_landing_cluster(scene)
    refuse_skipped_pages()
    assert_prior_stays_unpublished()
    inv = build_inventory(by_path, pack_path, occupied)
    write_inventory(inv)
    bump_or_insert_sitemap([f"{s['slug']}/{s['path']}/" for s in SCENES])
    patch_html_sitemap()
    counts = "/".join(str(len(by_path[s["path"]])) for s in SCENES)
    print(
        "bake_p6c_scenario ok "
        f"(fill={inv['fill_status']} counts={counts} litter=skipped p6a+p6b=unpublished)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
