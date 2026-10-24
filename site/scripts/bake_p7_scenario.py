#!/usr/bin/env python3
"""Bake P7 MT10 scenario best-of pages (7 type-07 children).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not recreate live parent hubs. Do not rebind CTA to YeahPromos.
Do not open tinnitus / seniors / mattress hang / robot-mop / TV / litter kittens.
Do not flip #58 P6a, #60 P6b, #61 P6c, #64 P6d, or day-add scenes.

Hard rules:
  - Type-07 pages only. published=false / noindex until 部署上线.
  - Use products-*.json ASINs / roles / prices / tracks as given. No invented ASINs / was / %.
  - Density from products SoT (10/10/10/10/10/10/10). Honest shortfall counts OK; do not pad.
  - Soft parent densify: hub ASINs may appear on a scene. Sibling scene ASINs stay banned.
  - No accessories as hero picks. Lab independent.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).
  - Comparison / reviews stubs already exist on parent hubs — do not recreate or
    roll stamps earlier than 2026-10-24.

Usage:
    python3 site/scripts/bake_p7_scenario.py
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
from seo_geo import (  # noqa: E402
    LIVE,
    ROBOTS_NOINDEX,
    rewrite_visible_jargon,
    scrub_association_copy,
    set_robots_meta,
)

DATE = "2026-10-24"
p4.DATE = DATE
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P7 scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
OCCUPIED_PATH = DATA / "p7-occupied-asins-2026-10-24.json"
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-p7-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-p7-fill/mt10-p7-fill-pack-2026-10-24/p7-l1-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-p7-fill/mt10-p7-fill-pack-2026-10-24/pack.json"),
    Path("/tmp/mt10-p7-fill/mt10-p7-fill-pack-2026-10-24.json"),
    Path("/home/ubuntu/.cursor/projects/workspace/uploads/mt10-p7-fill-pack-2026-10-24.json"),
    DATA / "mt10-p7-fill-pack-2026-10-24.json",
    DATA / "p7-l1-fill-pack-2026-10-24.json",
)
PACK_INREPO = DATA / "p7-l1-fill-pack-2026-10-24.json"
PRODUCTS_PACK_DIRS = (
    Path("/tmp/mt10-p7-fill/mt10-p7-fill-pack-2026-10-24"),
    Path("/workspace/shared/mt10-p7-fill-pack-2026-10-24"),
    DATA,
)
PARENT_HUBS = (
    "hair-dryers",
    "dehumidifiers",
    "kitchen-rugs",
    "noise-cancelling-headphones",
    "docking-stations",
    "office-chairs",
    "dash-cams",
)
SKIPPED: tuple[dict[str, str], ...] = ()
OUT_NICHES = (
    "best-hearing-aids-for-tinnitus",
    "best-hearing-aids-for-seniors",
    "best-mattresses-for-hanging",
    "best-robot-mops",
    "best-litter-boxes-for-kittens",
    "best-litter-boxes-for-large-cats",
)
P7_SLUGS = (
    "best-hair-dryers-for-men",
    "best-dehumidifiers-for-rv",
    "best-washable-kitchen-rugs",
    "best-noise-cancelling-headphones-for-flying",
    "best-docking-stations-for-dual-monitors",
    "best-office-chairs-for-heavy-people",
    "best-dash-cams-for-motorcycle",
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
    "products-best-projectors-for-gaming.json",
    "products-best-humidifiers-for-plants.json",
    "products-best-doormats-for-outdoors.json",
    "products-best-noise-cancelling-headphones-for-work.json",
    "products-best-bluetooth-speakers-for-shower.json",
    "products-best-office-chairs-under-200.json",
    "products-best-hair-dryers-for-frizzy-hair.json",
    "products-best-office-chairs-for-tall-people.json",
    "products-best-barstools-for-kitchen-island.json",
    "products-best-bike-racks-for-suv.json",
    "products-best-bookcases-for-small-spaces.json",
    "products-best-docking-stations-for-macbook.json",
    "products-best-massage-guns-for-athletes.json",
)
DAY_ADD_STAY_UNPUBLISHED = {
    "products-best-bluetooth-speakers-for-outdoor.json",
    "products-best-projectors-for-home-theater.json",
    "products-best-projectors-for-outdoor.json",
    "products-best-office-chairs-for-long-hours.json",
    "products-best-humidifiers-for-large-rooms.json",
}
HAIR_BRUSH_RE = re.compile(
    r"hair dryer brush|hot air brush|hot-brush|blowout brush|hot brush",
    re.I,
)
HANDHELD_DOCK_RE = re.compile(r"steam deck|nintendo switch", re.I)
KIDS_HEADPHONE_RE = re.compile(
    r"kids headphones|headphones for kids|children'?s headphones|toddler headphones",
    re.I,
)
SIBLING_PAGE_MAP = {
    "hair_siblings": (
        "hair-dryers/best-hair-dryers-for-curly-hair",
        "hair-dryers/best-hair-dryers-for-fine-hair",
        "hair-dryers/best-hair-dryers-for-frizzy-hair",
        "hair-dryers/best-hair-dryers-for-thick-hair",
        "hair-dryers/best-hair-dryers-for-travel",
    ),
    "dehum_siblings": (
        "dehumidifiers/best-dehumidifiers-for-basements",
        "dehumidifiers/best-dehumidifiers-for-bathroom",
        "dehumidifiers/best-dehumidifiers-for-crawl-space",
    ),
    "rug_siblings": ("kitchen-rugs/best-kitchen-rugs",),
    "nch_siblings": (
        "noise-cancelling-headphones/best-noise-cancelling-headphones-for-work",
    ),
    "dock_siblings": (
        "docking-stations/best-docking-stations",
        "docking-stations/best-docking-stations-for-macbook",
    ),
    "chair_siblings": (
        "office-chairs/best-office-chairs-for-back-pain",
        "office-chairs/best-office-chairs-for-gaming",
        "office-chairs/best-office-chairs-for-long-hours",
        "office-chairs/best-office-chairs-for-tall-people",
        "office-chairs/best-office-chairs-under-200",
    ),
    "dash_siblings": (),
}
HUB_PAGE_MAP = {
    "hair_hub": "hair-dryers",
    "dehum_hub": "dehumidifiers",
    "rug_hub": "kitchen-rugs",
    "nch_hub": "noise-cancelling-headphones",
    "dock_hub": "docking-stations",
    "chair_hub": "office-chairs",
    "dash_hub": "dash-cams",
}

SCENES: list[dict[str, Any]] = [
    {
        "n": 1,
        "slug": "hair-dryers",
        "name": "Hair Dryers",
        "path": "best-hair-dryers-for-men",
        "label": "Best for men",
        "keyword": "best hair dryers for men",
        "title": "Best Hair Dryers for Men",
        "h1": "Best Hair Dryers for Men (2026)",
        "job": "high-speed ionic blow dryers for shorter or men's grooming — not a hot brush or dryer-brush",
        "confirm": (
            "Confirm attachments, heat settings, and voltage on the listing. "
            "We do not invent grooming scores."
        ),
        "skip": (
            "Skip this slice if you want a hot brush, a dryer-brush, or the curly, fine, "
            "travel, thick, or frizzy shortlists already on those pages."
        ),
        "lede": (
            "A men's grooming setup is a high-speed ionic blow-dryer job — not a hot brush, "
            "and not a paste of the curly, fine, travel, thick, or frizzy shortlists."
        ),
        "ban_groups": ["hair_siblings"],
        "soft_hub_groups": ["hair_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-hair-dryers-for-curly-hair", "label": "Best for curly hair"},
            {"path": "best-hair-dryers-for-fine-hair", "label": "Best for fine hair"},
            {"path": "best-hair-dryers-for-travel", "label": "Best for travel"},
            {"path": "best-hair-dryers-for-thick-hair", "label": "Best for thick hair"},
            {"path": "best-hair-dryers-for-frizzy-hair", "label": "Best for frizzy hair"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
    },
    {
        "n": 2,
        "slug": "dehumidifiers",
        "name": "Dehumidifiers",
        "path": "best-dehumidifiers-for-rv",
        "label": "Best for RV",
        "keyword": "best dehumidifiers for RV",
        "title": "Best Dehumidifiers for RV",
        "h1": "Best Dehumidifiers for RV (2026)",
        "job": "compact dehumidifiers or moisture absorbers for an RV or camper — not a humidifier",
        "confirm": (
            "Confirm tank size, drain options, and whether it is a refillable absorber "
            "or a powered unit on the listing. We do not invent RV square-footage scores."
        ),
        "skip": (
            "Skip this slice if you want a humidifier or the basement, bathroom, or "
            "crawl-space shortlists already on those pages."
        ),
        "lede": (
            "RV moisture control is a compact dehumidifier or absorber job — not a "
            "humidifier, and not a paste of the basement, bathroom, or crawl-space shortlists."
        ),
        "ban_groups": ["dehum_siblings"],
        "soft_hub_groups": ["dehum_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-dehumidifiers-for-basements", "label": "Best for basements"},
            {"path": "best-dehumidifiers-for-bathroom", "label": "Best for bathroom"},
            {"path": "best-dehumidifiers-for-crawl-space", "label": "Best for crawl space"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-dehumidifiers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-dehumidifiers.jpg",
    },
    {
        "n": 3,
        "slug": "kitchen-rugs",
        "name": "Kitchen Rugs",
        "path": "best-washable-kitchen-rugs",
        "label": "Best washable kitchen rugs",
        "keyword": "best washable kitchen rugs",
        "title": "Best Washable Kitchen Rugs",
        "h1": "Best Washable Kitchen Rugs (2026)",
        "job": "machine-washable kitchen mats and runners — not a doormat",
        "confirm": (
            "Confirm size, wash instructions, and non-slip backing on the listing. "
            "We do not invent absorbency scores."
        ),
        "skip": (
            "Skip this slice if you want a doormat or the main kitchen-rug shortlist "
            "already on Best kitchen rugs."
        ),
        "lede": (
            "A kitchen floor is a washable mat or runner job — not a doormat, and not "
            "a paste of the main kitchen-rug shortlist."
        ),
        "ban_groups": ["rug_siblings"],
        "soft_hub_groups": ["rug_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-kitchen-rugs", "label": "Best kitchen rugs"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-kitchen-rugs.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-kitchen-rugs.jpg",
    },
    {
        "n": 4,
        "slug": "noise-cancelling-headphones",
        "name": "Noise-Cancelling Headphones",
        "path": "best-noise-cancelling-headphones-for-flying",
        "label": "Best for flying",
        "keyword": "best noise cancelling headphones for flying",
        "title": "Best Noise Cancelling Headphones for Flying",
        "h1": "Best Noise Cancelling Headphones for Flying (2026)",
        "job": "over-ear ANC headphones you can wear on a flight — not kids headphones",
        "confirm": (
            "Confirm ANC, a wired backup option, and battery hours on the listing. "
            "We do not invent cabin-noise scores."
        ),
        "skip": (
            "Skip this slice if you want kids headphones or the work shortlist already "
            "on Best for work."
        ),
        "lede": (
            "A flight is an over-ear ANC headphone job — not a kids set, and not a "
            "paste of the work shortlist."
        ),
        "ban_groups": ["nch_siblings"],
        "soft_hub_groups": ["nch_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {
                "path": "best-noise-cancelling-headphones-for-work",
                "label": "Best for work",
            },
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-headphones.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-headphones.jpg",
    },
    {
        "n": 5,
        "slug": "docking-stations",
        "name": "Docking Stations",
        "path": "best-docking-stations-for-dual-monitors",
        "label": "Best for dual monitors",
        "keyword": "best docking stations for dual monitors",
        "title": "Best Docking Stations for Dual Monitors",
        "h1": "Best Docking Stations for Dual Monitors (2026)",
        "job": "USB-C docks that can drive two displays — not a cable or handheld-console dock",
        "confirm": (
            "Confirm video outputs, DisplayPort or HDMI count, and host OS notes on the "
            "listing. We do not invent wattage scores."
        ),
        "skip": (
            "Skip this slice if you want a charging cable, a Steam Deck or Switch dock, "
            "or the MacBook or main docking-station shortlists already on those pages."
        ),
        "lede": (
            "Dual monitors are a multi-port USB-C dock job — not a cable or "
            "handheld-console dock, and not a paste of the MacBook or main "
            "docking-station shortlists."
        ),
        "ban_groups": ["dock_siblings"],
        "soft_hub_groups": ["dock_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-docking-stations", "label": "Best docking stations"},
            {"path": "best-docking-stations-for-macbook", "label": "Best for MacBook"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-docking-stations.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-docking-stations.jpg",
    },
    {
        "n": 6,
        "slug": "office-chairs",
        "name": "Office Chairs",
        "path": "best-office-chairs-for-heavy-people",
        "label": "Best for heavy people",
        "keyword": "best office chairs for heavy people",
        "title": "Best Office Chairs for Heavy People",
        "h1": "Best Office Chairs for Heavy People (2026)",
        "job": "big-and-tall office chairs with a published weight rating — not a mat",
        "confirm": (
            "Confirm weight rating, seat width, and recline notes on the listing. "
            "We do not invent capacity scores beyond the listing."
        ),
        "skip": (
            "Skip this slice if you want a chair mat or the gaming, back-pain, "
            "long-hours, under-$200, or tall-people shortlists already on those pages."
        ),
        "lede": (
            "A heavier sitter is a big-and-tall office chair job — not a mat, and not "
            "a paste of the gaming, back-pain, long-hours, under-$200, or tall-people "
            "shortlists."
        ),
        "ban_groups": ["chair_siblings"],
        "soft_hub_groups": ["chair_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-office-chairs-for-back-pain", "label": "Best for back pain"},
            {"path": "best-office-chairs-for-long-hours", "label": "Best for long hours"},
            {"path": "best-office-chairs-for-gaming", "label": "Best for gaming"},
            {"path": "best-office-chairs-under-200", "label": "Best under $200"},
            {"path": "best-office-chairs-for-tall-people", "label": "Best for tall people"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-office-chairs.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-office-chairs.jpg",
    },
    {
        "n": 7,
        "slug": "dash-cams",
        "name": "Dash Cams",
        "path": "best-dash-cams-for-motorcycle",
        "label": "Best for motorcycle",
        "keyword": "best dash cams for motorcycle",
        "title": "Best Dash Cams for Motorcycle",
        "h1": "Best Dash Cams for Motorcycle (2026)",
        "job": "motorcycle-ready or dual-channel dash cams — not a mount-only accessory",
        "confirm": (
            "Confirm mounting hardware, weather notes, and whether a rear cam ships in "
            "the box on the listing. We do not invent crash scores."
        ),
        "skip": (
            "Skip this slice if you want a mount-only accessory rather than a camera "
            "that can record the ride."
        ),
        "lede": (
            "Motorcycle recording is a dual-channel dash-cam job — not a mount-only "
            "accessory. The top card is a motorcycle kit; the rest are dual-channel cams "
            "you still need to confirm for bike fit."
        ),
        "ban_groups": ["dash_siblings"],
        "soft_hub_groups": ["dash_hub"],
        "cross_ban_scenes": [],
        "siblings": [],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-dash-cams.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-dash-cams.jpg",
    },
]


def _asins_from_json(path: Path) -> set[str]:
    if not path.exists():
        return set()
    blob = json.loads(path.read_text(encoding="utf-8"))
    out: set[str] = set()
    for row in blob.get("products") or []:
        asin = str(row.get("asin") or "").strip().upper()
        if ASIN_RE.fullmatch(asin):
            out.add(asin)
    return out


def _asins_from_html(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(ASIN_RE.findall(path.read_text(encoding="utf-8").upper()))


def harvest_occupied() -> dict[str, Any]:
    p6d_path = DATA / "p6d-occupied-asins-2026-10-24.json"
    flat: set[str] = set()
    if p6d_path.exists():
        prior = json.loads(p6d_path.read_text(encoding="utf-8"))
        flat |= _asin_set(prior.get("flat"))
    for path in DATA.glob("products-best-*.json"):
        slug = path.stem.replace("products-", "")
        if slug in P7_SLUGS:
            continue
        flat |= _asins_from_json(path)
    scene_ban: dict[str, list[str]] = {}
    by_source: dict[str, list[str]] = {}
    for key, rels in SIBLING_PAGE_MAP.items():
        group: set[str] = set()
        for rel in rels:
            slug = rel.split("/", 1)[1]
            group |= _asins_from_json(DATA / f"products-{slug}.json")
            group |= _asins_from_html(SITE / rel / "index.html")
        scene_ban[key] = sorted(group)
        by_source[key] = scene_ban[key]
        flat |= group
    for key, hub in HUB_PAGE_MAP.items():
        group = _asins_from_html(SITE / hub / "index.html")
        scene_ban[key] = sorted(group)
        by_source[key] = scene_ban[key]
    for html in SITE.glob("*/best-*/index.html"):
        rel = str(html.relative_to(SITE))
        if any(slug in rel for slug in P7_SLUGS):
            continue
        flat |= _asins_from_html(html)
    blob = {
        "tip": "616fee79",
        "generated_at": "2026-10-24T12:20:00+00:00",
        "source": (
            "tip 616fee79 (#65 Live) + P6d occupied flat + sibling scene shortlists "
            "+ hub files; soft hubs recorded separately"
        ),
        "by_source": by_source,
        "scene_ban_keys": scene_ban,
        "flat": sorted(flat),
        "counts": {key: len(values) for key, values in scene_ban.items()},
        "flat_n": len(flat),
    }
    OCCUPIED_PATH.write_text(
        json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return blob


def load_occupied() -> dict[str, set[str]]:
    if not OCCUPIED_PATH.exists():
        harvest_occupied()
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
    if path == "best-hair-dryers-for-men" and HAIR_BRUSH_RE.search(title):
        return None
    if path == "best-docking-stations-for-dual-monitors" and HANDHELD_DOCK_RE.search(title):
        return None
    if path == "best-noise-cancelling-headphones-for-flying" and KIDS_HEADPHONE_RE.search(title):
        return None
    price = row.get("price")
    price_str = row.get("price_str") or row.get("price_displayed")
    if price is not None and not price_str:
        price_str = f"${float(price):.2f}" if isinstance(price, (int, float)) else f"${price}"
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


def ensure_products_as_is(scene: dict[str, Any]) -> Path:
    dest = products_path(scene)
    if dest.exists():
        return dest
    for folder in PRODUCTS_PACK_DIRS:
        src = folder / dest.name
        if src.exists() and src.resolve() != dest.resolve():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            return dest
    raise SystemExit(f"{scene['path']} missing products-*.json source of truth")


def load_products_sot(scene: dict[str, Any]) -> list[dict[str, Any]]:
    dest = ensure_products_as_is(scene)
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
        "batch": "P7",
        "lock": "lock-p7-1-7",
        "tip_reference": "616fee79",
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
            "#61 P6c published flip",
            "#64/#65 P6d published flip",
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
            "best-hair-dryers-for-men": (
                "Dreame / Laifen / slopehill / Wavytalk. Laifen titles may ride Wavytalk PB brand_id."
            ),
            "best-dehumidifiers-for-rv": (
                "Medcursor / CLEVAST absorbers + Waykar powered units; closet absorbers kept as RV densify."
            ),
            "best-washable-kitchen-rugs": "Cosy Homeer / BEQHAUSE / JSEI washable mats and runners.",
            "best-noise-cancelling-headphones-for-flying": (
                "OneOdio / Baseus / Soundcore-via-Nebula / EarFun / Edifier. Kids NC banned."
            ),
            "best-docking-stations-for-dual-monitors": (
                "WAVLINK / Baseus / Anker dual-display docks; handheld-console docks banned."
            ),
            "best-office-chairs-for-heavy-people": (
                "Dowinx / SEDETA / amseatec / HOMRELEXA big-and-tall. Sibling tall/gaming/back/long/under-200 banned."
            ),
            "best-dash-cams-for-motorcycle": (
                "Vantrue F1 motorcycle kit on top; 70mai / BOTSLAB / VIOFO / REDTIGER dual-channel densify."
            ),
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
                "hair_siblings",
                "hair_hub",
                "dehum_siblings",
                "dehum_hub",
                "rug_siblings",
                "rug_hub",
                "nch_siblings",
                "nch_hub",
                "dock_siblings",
                "dock_hub",
                "chair_siblings",
                "chair_hub",
                "dash_siblings",
                "dash_hub",
            }
        },
        "occupied_global_n": len(occupied.get("global") or ()),
        "pages": pages,
        "notes": [
            "No invented ASINs, prices, was/%, gallery, or Check price hops.",
            "Parent hubs already exist. Not recreated. Soft densify = hub ASINs allowed; sibling bans hold.",
            "published=false / noindex until a later 部署上线 order. Draft PR only — not Live deployed.",
            "Independent of Shortlist Lab.",
            "Did not flip P6a–d or day-add published flags.",
            "OUT: tinnitus · seniors · mattress hang · robot-mop · TV · litter kittens.",
            "YP site 11767 returned 0 usable rows — honest PB-only. Live CTA stays PB ?uid=fromsll.",
            "Comparison / reviews stubs already exist. Stamps not rolled back.",
            "Products JSON applied as-is from the L1 fill pack.",
        ],
    }


def leftover_terms(scene: dict[str, Any]) -> tuple[str, ...]:
    leftovers = list(TEMPLATE_LEFTOVER)
    if scene["slug"] != "humidifiers":
        leftovers.extend(TEMPLATE_LEFTOVER_NON_HUMIDIFIER)
    leftovers.extend(
        (
            "inventory_blocked",
            "best-hearing-aids-for-tinnitus",
            "best-hearing-aids-for-seniors",
            "best-mattresses-for-hanging",
            "best-robot-mops",
            "best-litter-boxes-for-kittens",
            "best-litter-boxes-for-large-cats",
            "best-red-light-therapy-masks",
            "best-pillows-for-snoring",
            "best-ceramic-space-heaters-for-bedroom",
            "Top10.com",
            "Natural Intelligence",
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
    html = scrub_association_copy(html)
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
    dest = DATA / "p7-scenario-inventory-2026-10-24.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = []
    for row in inv["pages"]:
        rows.append(
            f"| `{row['path']}` | **{row['density']}** | `{row['fill_status']}` | "
            f"{row['cta_status']} | none |"
        )
    need = inv.get("need_fill") or []
    md = DATA / "p7-scenario-inventory-2026-10-24.md"
    md.write_text(
        "\n".join(
            [
                "# P7 scenario best-of inventory (2026-10-24)",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / noindex",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Parent hubs:** already exist — not recreated.",
                "**Tip:** `616fee79` (#65 Live).",
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
                "- None. All seven lock-p7-1-7 scenes passed density ≥4.",
                "",
                "## Hard rules kept",
                "",
                "- No invented ASINs / prices / was / % / gallery / CTAs.",
                "- No accessories as primary picks.",
                "- Sibling ASIN bans hold. Soft parent densify preferred (hub ASINs may appear).",
                "- Reviews skipped. Comparison / reviews stubs already exist — stamps not rolled back.",
                "- Independent of Shortlist Lab.",
                "- Did not flip P6a–d or day-add published=true.",
                "- Products JSON applied as-is from the L1 fill pack.",
                "- YP site 11767 returned 0 usable rows — honest PB-only. Live CTA stays PB ?uid=fromsll.",
                "- OUT: tinnitus · seniors · mattress hang · robot-mop · TV · litter kittens.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def refuse_skipped_pages() -> None:
    blocked = (
        SITE / "hearing-aids" / "best-hearing-aids-for-tinnitus" / "index.html",
        SITE / "hearing-aids" / "best-hearing-aids-for-seniors" / "index.html",
        SITE / "mattresses" / "best-mattresses-for-hanging" / "index.html",
        SITE / "robot-vacuums" / "best-robot-mops" / "index.html",
        SITE / "litter-boxes" / "best-litter-boxes-for-kittens" / "index.html",
        SITE / "litter-boxes" / "best-litter-boxes-for-large-cats" / "index.html",
        DATA / "products-best-hearing-aids-for-tinnitus.json",
        DATA / "products-best-hearing-aids-for-seniors.json",
        DATA / "products-best-mattresses-for-hanging.json",
        DATA / "products-best-robot-mops.json",
        DATA / "products-best-litter-boxes-for-kittens.json",
    )
    for path in blocked:
        if path.exists():
            raise SystemExit(f"must not scaffold {path}")


P6_OK_PUBLISH = {
    name.removeprefix("products-").removesuffix(".json")
    for name in PRIOR_KEEP_UNPUBLISHED
    if name not in DAY_ADD_STAY_UNPUBLISHED
}


def assert_prior_stays_unpublished() -> None:
    for name in PRIOR_KEEP_UNPUBLISHED:
        path = DATA / name
        if not path.exists():
            raise SystemExit(f"expected existing shell {name}")
        blob = json.loads(path.read_text(encoding="utf-8"))
        slug = name.removeprefix("products-").removesuffix(".json")
        if slug in P6_OK_PUBLISH:
            if blob.get("published") is not True:
                raise SystemExit(f"{name} must stay published=true after P6 flip")
        elif blob.get("published") is True:
            raise SystemExit(f"must not flip {name} to published=true")
    for name in P7_SLUGS:
        path = DATA / f"products-{name}.json"
        blob = json.loads(path.read_text(encoding="utf-8"))
        if blob.get("published") is not False:
            raise SystemExit(f"{path.name} must stay published=false")


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
    harvest_occupied()
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
        write_scene(scene, banned, picks)
        add_landing_cluster(scene)
    refuse_skipped_pages()
    assert_prior_stays_unpublished()
    inv = build_inventory(by_path, pack_path, occupied)
    write_inventory(inv)
    bump_or_insert_sitemap([f"{s['slug']}/{s['path']}/" for s in SCENES])
    patch_html_sitemap()
    notes = ROOT / "notes" / "p7-scenario-draft-2026-10-24.md"
    if not notes.exists():
        notes.write_text(
            "# P7 scenario batch draft — 2026-10-24\n\n"
            "**waiting_for_部署上线:** yes\n",
            encoding="utf-8",
        )
    counts = "/".join(str(len(by_path[s["path"]])) for s in SCENES)
    print(
        "bake_p7_scenario ok "
        f"(fill={inv['fill_status']} counts={counts} published=false p6+day-add untouched)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
