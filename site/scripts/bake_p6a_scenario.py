#!/usr/bin/env python3
"""Bake P6a MT10 scenario best-of pages (7 type-07 children).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not recreate live parent hubs. Do not rebind CTA to YeahPromos.
Do not scaffold pillows/best-pillows-for-back-sleepers (SHORTFALL n=2).
Do not reopen mattresses/best-mattresses-for-back-pain.

Hard rules:
  - Type-07 pages only. published=false / noindex until 部署上线.
  - Use L1 pack ASINs / roles / prices / tracks as given. No invented ASINs / was / %.
  - Density from pack (10/9/9/10/10/6/7). Honest shortfall counts OK; do not pad.
  - Soft parent densify: hub ASINs may appear on a scene. Sibling scene ASINs stay banned.
  - No accessories as hero picks. Lab independent.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).
  - Comparison / reviews stubs already exist on parent hubs — do not recreate or
    roll stamps earlier than 2026-10-24.

Usage:
    python3 site/scripts/bake_p6a_scenario.py
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
    DOORBELL_RE,
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
    "<!-- waiting_for_部署上线: yes. P6a scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
OCCUPIED_PATH = DATA / "p6a-occupied-asins-2026-10-24.json"
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-p6a-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-p6a-fill-pack-2026-10-24/p6a-l1-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-p6a-fill-pack-2026-10-24.json"),
    Path("/home/ubuntu/.cursor/projects/workspace/uploads/mt10-p6a-fill-pack-2026-10-24_6ed4.json"),
    DATA / "mt10-p6a-fill-pack-2026-10-24.json",
    DATA / "p6a-l1-fill-pack-2026-10-24.json",
)
PACK_INREPO = DATA / "p6a-l1-fill-pack-2026-10-24.json"
PARENT_HUBS = (
    "robotic-pool-cleaners",
    "bike-racks",
    "espresso-machines",
    "hair-dryers",
    "security-cameras",
    "projectors",
    "dehumidifiers",
)
SKIPPED = (
    {
        "path": "best-pillows-for-back-sleepers",
        "url": "/pillows/best-pillows-for-back-sleepers/",
        "reason": "SHORTFALL n=2 < density 4 — skip scaffold",
    },
    {
        "path": "best-mattresses-for-back-pain",
        "url": "/mattresses/best-mattresses-for-back-pain/",
        "reason": "do not reopen",
    },
)
OUT_NICHES = ("best-pillows-for-back-sleepers",)
OUTDOOR_TITLE_RE = re.compile(r"\boutdoor\b", re.I)
GALAXY_RE = re.compile(r"galaxy projector|star projector|inflatable screen", re.I)
HITCH_RE = re.compile(r"hitch|receiver", re.I)

SCENES: list[dict[str, Any]] = [
    {
        "n": 1,
        "slug": "robotic-pool-cleaners",
        "name": "Robotic Pool Cleaners",
        "path": "best-robotic-pool-cleaners-for-inground-pools",
        "label": "Best for inground pools",
        "keyword": "best robotic pool cleaner for inground pools",
        "title": "Best Robotic Pool Cleaners for Inground Pools",
        "h1": "Best Robotic Pool Cleaners for Inground Pools (2026)",
        "job": "cordless robotic pool cleaners that can clean inground or dual-use pools",
        "confirm": (
            "Confirm pool type (inground vs above-ground-only), wall and waterline coverage, "
            "and runtime on the retailer page. We do not invent GPH ratings."
        ),
        "skip": (
            "Skip this slice if you want an above-ground-only cleaner, a hose-powered vacuum, "
            "or a spare filter basket. Those jobs are not this page."
        ),
        "lede": (
            "Inground robotic cleaning is a full cordless cleaner job — not a hose vacuum "
            "and not an above-ground-only unit."
        ),
        "ban_groups": [],
        "soft_hub_groups": ["pool_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-robotic-pool-cleaners", "label": "Best robotic pool cleaners"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-robotic-pool-cleaners.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-robotic-pool-cleaners.jpg",
    },
    {
        "n": 2,
        "slug": "bike-racks",
        "name": "Bike Racks",
        "path": "best-bike-racks-for-hitch",
        "label": "Best for hitch",
        "keyword": "best bike racks for hitch",
        "title": "Best Bike Racks for Hitch",
        "h1": "Best Bike Racks for Hitch (2026)",
        "job": "hitch-mount bike racks for cars, SUVs, and trucks",
        "confirm": (
            "Confirm hitch class, receiver size (usually 2\"), bike count, and weight "
            "capacity on the retailer page. We do not invent pound ratings."
        ),
        "skip": (
            "Skip this slice if you want a trunk-mount, roof, or spare-tire rack, or a "
            "hitch lock by itself."
        ),
        "lede": (
            "Hitch-mount bike hauling is a full rack job — not a lock-only accessory "
            "and not a trunk-strap rack."
        ),
        "ban_groups": [],
        "soft_hub_groups": ["bike_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-bike-racks", "label": "Best bike racks"},
        ],
        "density_expected": 9,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-bike-racks.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-bike-racks.jpg",
    },
    {
        "n": 3,
        "slug": "espresso-machines",
        "name": "Espresso Machines",
        "path": "best-espresso-machines-under-500",
        "label": "Best under $500",
        "keyword": "best espresso machines under 500",
        "title": "Best Espresso Machines Under $500",
        "h1": "Best Espresso Machines Under $500 (2026)",
        "job": "countertop espresso machines with a real retailer price at or under $500",
        "confirm": (
            "Confirm the live cart is still $500 or under, plus portafilter size and "
            "whether a grinder ships in the box."
        ),
        "skip": (
            "Skip this slice if you want a café prosumer deck or a machine already on "
            "Best espresso machines for home or Best espresso machines for beginners. "
            "Spare portafilters stay off this list."
        ),
        "lede": (
            "Sub-$500 home espresso is a complete countertop machine job — not a spare "
            "portafilter and not a paste of the home or beginner shortlists."
        ),
        "ban_groups": ["espresso_siblings"],
        "soft_hub_groups": ["espresso_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-espresso-machines-for-home", "label": "Best for home"},
            {"path": "best-espresso-machines-for-beginners", "label": "Best for beginners"},
        ],
        "density_expected": 9,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/espresso.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/espresso.jpg",
    },
    {
        "n": 4,
        "slug": "hair-dryers",
        "name": "Hair Dryers",
        "path": "best-hair-dryers-for-thick-hair",
        "label": "Best for thick hair",
        "keyword": "best hair dryers for thick hair",
        "title": "Best Hair Dryers for Thick Hair",
        "h1": "Best Hair Dryers for Thick Hair (2026)",
        "job": "full high-speed dryers that can move thick or dense hair",
        "confirm": (
            "Confirm heat settings, wattage or high-speed notes, and whether a diffuser "
            "or concentrator ships in the box. We do not invent heat-damage scores."
        ),
        "skip": (
            "Skip this slice if you want a curly-hair, fine-hair, or travel dryer already "
            "on those pages, or a spare diffuser only."
        ),
        "lede": (
            "Thick-hair drying is a full dryer job — not a standalone diffuser and not a "
            "paste of the curly, fine, or travel shortlists."
        ),
        "ban_groups": ["hair_siblings"],
        "soft_hub_groups": ["hair_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-hair-dryers-for-curly-hair", "label": "Best for curly hair"},
            {"path": "best-hair-dryers-for-fine-hair", "label": "Best for fine hair"},
            {"path": "best-hair-dryers-for-travel", "label": "Best for travel"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
    },
    {
        "n": 5,
        "slug": "security-cameras",
        "name": "Security Cameras",
        "path": "best-security-cameras-for-indoor",
        "label": "Best for indoor",
        "keyword": "best security cameras for indoor",
        "title": "Best Security Cameras for Indoor",
        "h1": "Best Security Cameras for Indoor (2026)",
        "job": "indoor-only security or baby and pet cameras, not outdoor cams or doorbells",
        "confirm": (
            "Confirm indoor use, resolution, and whether a subscription is required on "
            "the retailer page."
        ),
        "skip": (
            "Skip this slice if you want an outdoor camera or a video doorbell. Any "
            "outdoor listing stays off this page."
        ),
        "lede": (
            "Indoor monitoring is an indoor-only camera job — not a doorbell, not a "
            "weather-rated outdoor cam, and not a mount-only accessory."
        ),
        "ban_groups": ["security_siblings"],
        "soft_hub_groups": ["security_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-security-cameras-for-outdoor", "label": "Best for outdoor"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-security-cameras.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-security-cameras.jpg",
    },
    {
        "n": 6,
        "slug": "projectors",
        "name": "Projectors",
        "path": "best-projectors-for-bedroom",
        "label": "Best for bedroom",
        "keyword": "best projectors for bedroom",
        "title": "Best Projectors for Bedroom",
        "h1": "Best Projectors for Bedroom (2026)",
        "job": "compact bedroom projectors, not galaxy night lights or inflatable screens",
        "confirm": (
            "Confirm throw distance, brightness notes, and speaker or smart-TV features "
            "on the retailer page. We do not invent lumens."
        ),
        "skip": (
            "Skip this slice if you want an outdoor or home-theater projector already on "
            "those pages, or a galaxy or star night-light projector."
        ),
        "lede": (
            "Bedroom projection is a compact projector job — not a galaxy night light, "
            "not a screen-only accessory, and not a paste of the outdoor or theater shortlists."
        ),
        "ban_groups": ["projector_siblings"],
        "soft_hub_groups": ["projector_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-projectors-for-outdoor", "label": "Best for outdoor"},
            {"path": "best-projectors-for-home-theater", "label": "Best for home theater"},
        ],
        "density_expected": 6,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-projectors.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-projectors.jpg",
    },
    {
        "n": 7,
        "slug": "dehumidifiers",
        "name": "Dehumidifiers",
        "path": "best-dehumidifiers-for-bathroom",
        "label": "Best for bathroom",
        "keyword": "best dehumidifiers for bathroom",
        "title": "Best Dehumidifiers for Bathroom",
        "h1": "Best Dehumidifiers for Bathroom (2026)",
        "job": "compact dehumidifiers suited to a bathroom (prefer 35 pint or under)",
        "confirm": (
            "Confirm pint rating, tank or drain hose, and noise notes on the retailer page. "
            "We do not invent pint ratings."
        ),
        "skip": (
            "Skip this slice if you want a 50+ pint basement-primary or crawl-space unit "
            "already on Best dehumidifiers for basements."
        ),
        "lede": (
            "Bathroom moisture control is a compact dehumidifier job — not a commercial "
            "50-pint tank and not a paste of the basement shortlist."
        ),
        "ban_groups": ["dehumid_siblings"],
        "soft_hub_groups": ["dehumid_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-dehumidifiers-for-basements", "label": "Best for basements"},
        ],
        "density_expected": 7,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-dehumidifiers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-dehumidifiers.jpg",
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


def _price_number(row: dict[str, Any]) -> float | None:
    raw = row.get("price")
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(row.get("price_str") or row.get("price_displayed") or raw or "").strip()
    match = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    if not match:
        return None
    return float(match.group(1))


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
    if path == "best-security-cameras-for-indoor":
        if DOORBELL_RE.search(title) or OUTDOOR_TITLE_RE.search(title):
            return None
    if path == "best-projectors-for-bedroom" and GALAXY_RE.search(title):
        return None
    if path == "best-bike-racks-for-hitch" and not HITCH_RE.search(title):
        return None
    if path == "best-espresso-machines-under-500":
        price_n = _price_number(row)
        if price_n is not None and price_n > 500:
            return None
    network = classify_network(row.get("track_url") or row.get("affiliate_link") or "")
    if network != "pb":
        return None
    price = row.get("price")
    price_str = row.get("price_str") or row.get("price_displayed")
    if price is not None and not price_str:
        price_str = f"${price}"
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


def scene_picks_from_pack(
    pack: dict[str, Any] | None, scene: dict[str, Any], banned: set[str]
) -> list[dict[str, Any]]:
    if not pack:
        return []
    blob = pack_blob(pack, scene)
    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in blob.get("products") or blob.get("picks") or []:
        pick = pick_from_pack(row, banned, scene)
        if not pick or pick["asin"] in seen:
            continue
        seen.add(pick["asin"])
        picks.append(pick)
    return picks


def products_path(scene: dict[str, Any]) -> Path:
    return DATA / f"products-{scene['path']}.json"


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
        "batch": "P6a",
        "lock": "lock-p6a-rec",
        "tip_reference": "c58e0df1",
        "waiting_for_部署上线": True,
        "published": False,
        "live": False,
        "merged": False,
        "independent_of_shortlist_lab": True,
        "do_not_touch": ["Lab", "RR", "OL", "#54 home nav", "#55 stamp", "parent hub cards"],
        "parent_hubs": "exist_not_recreated",
        "soft_parent_densify": (
            "hub ASINs may appear on scene; sibling bans still hold; "
            f"hub ASINs {hub_note}; L1 pack soft_parent_count=0"
        ),
        "skipped": list(SKIPPED),
        "out_of_scope": list(OUT_NICHES),
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
        },
        "occupied_groups": {
            k: sorted(v)
            for k, v in occupied.items()
            if k in {
                "pillow_siblings",
                "pool_hub",
                "bike_hub",
                "espresso_siblings",
                "espresso_hub",
                "hair_siblings",
                "hair_hub",
                "security_siblings",
                "security_hub",
                "projector_siblings",
                "projector_hub",
                "dehumid_siblings",
                "dehumid_hub",
            }
        },
        "occupied_global_n": len(occupied.get("global") or ()),
        "pages": pages,
        "notes": [
            "No invented ASINs, prices, was/%, gallery, or Check price hops.",
            "Parent hubs already exist. Not recreated. Soft densify = hub ASINs allowed; sibling bans hold.",
            "published=false / noindex until a later 部署上线 order.",
            "Independent of Shortlist Lab.",
            "Pillows back-sleepers skipped (SHORTFALL n=2).",
            "Mattresses back-pain not reopened.",
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
            "best-pillows-for-back-sleepers",
            "best-mattresses-for-back-pain",
            "best-mattresses-for-heavy-people",
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
    dest = DATA / "p6a-scenario-inventory-2026-10-24.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = []
    for row in inv["pages"]:
        rows.append(
            f"| `{row['path']}` | **{row['density']}** | `{row['fill_status']}` | "
            f"{row['cta_status']} | none |"
        )
    need = inv.get("need_fill") or []
    md = DATA / "p6a-scenario-inventory-2026-10-24.md"
    md.write_text(
        "\n".join(
            [
                "# P6a scenario best-of inventory (2026-10-24)",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / noindex",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Parent hubs:** already exist — not recreated.",
                "**Tip:** `c58e0df1` (#54+#55+#57).",
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
                "- `/pillows/best-pillows-for-back-sleepers/` — SHORTFALL n=2 < density 4. Not scaffolded.",
                "- `/mattresses/best-mattresses-for-back-pain/` — do not reopen.",
                "",
                "## Hard rules kept",
                "",
                "- No invented ASINs / prices / was / % / gallery / CTAs.",
                "- No accessories as primary picks.",
                "- Sibling ASIN bans hold. Soft parent densify preferred (hub ASINs may appear).",
                "- Reviews skipped. Comparison / reviews stubs already exist — stamps not rolled back.",
                "- Independent of Shortlist Lab.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def refuse_skipped_pages() -> None:
    mattress = SITE / "mattresses" / "best-mattresses-for-back-pain" / "index.html"
    if mattress.exists():
        raise SystemExit("must not scaffold /mattresses/best-mattresses-for-back-pain/")
    pillow = SITE / "pillows" / "best-pillows-for-back-sleepers" / "index.html"
    if pillow.exists():
        raise SystemExit("must not scaffold /pillows/best-pillows-for-back-sleepers/")


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
        picks = scene_picks_from_pack(pack, scene, banned)
        expected = int(scene["density_expected"])
        if pack and len(picks) != expected:
            raise SystemExit(
                f"{scene['path']} expected density {expected} from L1 pack, got {len(picks)}"
            )
        by_path[scene["path"]] = picks
        write_products_shell(scene, picks)
        write_scene(scene, banned, picks)
        add_landing_cluster(scene)
    refuse_skipped_pages()
    inv = build_inventory(by_path, pack_path, occupied)
    write_inventory(inv)
    bump_or_insert_sitemap([f"{s['slug']}/{s['path']}/" for s in SCENES])
    patch_html_sitemap()
    counts = "/".join(str(len(by_path[s["path"]])) for s in SCENES)
    print(
        "bake_p6a_scenario ok "
        f"(fill={inv['fill_status']} counts={counts} pillows=skipped mattress=not_reopened)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
