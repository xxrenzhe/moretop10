#!/usr/bin/env python3
"""Bake P4 MT10 scenario best-of pages (8 hubs).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not edit open #48 (computer-speakers / tower-fans) or #49 (P1a reviews).
Do not recreate live parent hubs. /pillows/ already exists from P2.

Hard rules:
  - Type-07 pages only. published=false / noindex until 部署上线.
  - Honest empty shells when the L1 fill pack is missing. No invented ASINs / was / %.
  - No accessories as primary picks.
  - Collision bans: #2 litter main, #3 doorbells, #4 robot pet-hair,
    #6 baby humidifiers, #8 neck-pain pillows.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).

Usage:
    python3 site/scripts/bake_p4_scenario.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
DATA = SITE / "data"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from affiliate_uid import (  # noqa: E402
    classify_network,
    ensure_affiliate_uid,
    is_allowed_track_host,
    is_empty_track,
)
from chrome import (  # noqa: E402
    inject_nav_css,
    rel_prefix,
    rewrite_compare_cta,
    rewrite_disclosure,
    rewrite_footer,
    rewrite_non_home_nav,
)
from seo_geo import LIVE, ROBOTS_NOINDEX, dumps_ld, rewrite_visible_jargon, set_robots_meta  # noqa: E402
from site_config import load_site_config  # noqa: E402

TEMPLATE = SITE / "humidifiers" / "best-humidifiers-for-bedrooms" / "index.html"
from stamp_guard import bake_stamp_date  # noqa: E402

DATE = bake_stamp_date("2026-10-23")
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P4 scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
OCCUPIED_PATH = DATA / "p4-occupied-asins-2026-10-23.json"
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-p4-fill-pack-2026-10-23.json"),
    DATA / "mt10-p4-fill-pack-2026-10-23.json",
    DATA / "p4-l1-fill-pack-2026-10-23.json",
)
PACK_INREPO = DATA / "p4-l1-fill-pack-2026-10-23.json"
TEMPLATE_LEFTOVER = (
    "What bedroom shoppers should optimize",
    'href="../../humidifiers/how-to-choose-a-humidifier/"',
    'href="../../humidifiers/premium-humidifier-alternatives/"',
    'href="../../humidifiers/levoit-bedroom-vs-homvana-cool-mist/"',
    "Best Humidifiers for Bedrooms (2026)",
)
TEMPLATE_LEFTOVER_NON_HUMIDIFIER = (
    "Our top humidifiers for this scene",
    "best-humidifiers-for-bedrooms",
    "Best Humidifiers for Bedrooms",
)
ASIN_RE = re.compile(r"\bB0[A-Z0-9]{8}\b")
ACCESSORY_RE = re.compile(
    r"replacement|cartridge|filter pack|brush head|roller only|mop pad|"
    r"diffuser only|concentrator only|attachment only|pillowcase|protector|"
    r"sham\b|litter beads|trash bag|liner only|solar panel only|wall mount only|"
    r"screen only|tripod only|portafilter only|tamper only|capsule only",
    re.I,
)
DOORBELL_RE = re.compile(r"doorbell|video door", re.I)
ROBOT_RE = re.compile(r"robot vacuum|robovac|self[\s-]?empty dock", re.I)

SCENES: list[dict[str, Any]] = [
    {
        "n": 1,
        "slug": "espresso-machines",
        "name": "Espresso Machines",
        "path": "best-espresso-machines-for-home",
        "label": "Best for home",
        "keyword": "best espresso machines for home",
        "title": "Best Espresso Machines for Home",
        "h1": "Best Espresso Machines for Home (2026)",
        "job": "home espresso machines you can run on a kitchen counter",
        "confirm": (
            "Confirm boiler type, portafilter size, and whether a grinder ships in the box "
            "on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a café-only prosumer deck or a spare portafilter. "
            "Those jobs live on the main espresso-machines comparison."
        ),
        "lede": (
            "Home espresso is a countertop machine job — a full brewer you can run without "
            "a shop install — not a spare portafilter or capsule-only accessory."
        ),
        "ban_groups": [],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/espresso.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/espresso.jpg",
    },
    {
        "n": 2,
        "slug": "litter-boxes",
        "name": "Self-Cleaning Litter Boxes",
        "path": "best-automatic-litter-boxes",
        "label": "Best automatic",
        "keyword": "best automatic litter boxes",
        "title": "Best Automatic Litter Boxes",
        "h1": "Best Automatic Litter Boxes (2026)",
        "job": "automatic self-cleaning litter boxes that are not already on the main chart",
        "confirm": (
            "Confirm cat count, waste-drawer size, and what liners or bags ship in the box "
            "on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want the live litter-boxes shortlist or a bag of litter. "
            "Those jobs live on the main comparison."
        ),
        "lede": (
            "Automatic litter boxes are a machine slice — a self-cleaning box, not litter, "
            "liners, or a paste of the main chart."
        ),
        "ban_groups": ["litter_main"],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-litter-boxes.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-litter-boxes.jpg",
    },
    {
        "n": 3,
        "slug": "security-cameras",
        "name": "Security Cameras",
        "path": "best-security-cameras-for-outdoor",
        "label": "Best for outdoor",
        "keyword": "best security cameras for outdoor",
        "title": "Best Security Cameras for Outdoor",
        "h1": "Best Security Cameras for Outdoor (2026)",
        "job": "outdoor security cameras, not video doorbells",
        "confirm": (
            "Confirm weather rating, power source, and field of view on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a video doorbell or an indoor-only cam. "
            "Doorbells live on their own comparison."
        ),
        "lede": (
            "Outdoor security cameras are a weather-rated camera job — not a video doorbell "
            "and not a mount-only accessory."
        ),
        "ban_groups": ["video_doorbells"],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-security-cameras.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-security-cameras.jpg",
    },
    {
        "n": 4,
        "slug": "cordless-vacuums",
        "name": "Cordless Vacuums",
        "path": "best-cordless-vacuums-for-pet-hair",
        "label": "Best for pet hair",
        "keyword": "best cordless vacuums for pet hair",
        "title": "Best Cordless Vacuums for Pet Hair",
        "h1": "Best Cordless Vacuums for Pet Hair (2026)",
        "job": "handheld cordless vacuums for pet hair, not robot vacs",
        "confirm": (
            "Confirm runtime, bin size, and whether a pet-hair tool ships in the box "
            "on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a robot vacuum for pet hair. That job lives on "
            "the robot-vacuums pet-homes niche."
        ),
        "lede": (
            "Cordless pet-hair cleanup is a stick or handheld job — not a robot vacuum "
            "and not a spare brush roll."
        ),
        "ban_groups": ["robot_pet_hair"],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-cordless-vacuums.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-cordless-vacuums.jpg",
    },
    {
        "n": 5,
        "slug": "hair-dryers",
        "name": "Hair Dryers",
        "path": "best-hair-dryers-for-curly-hair",
        "label": "Best for curly hair",
        "keyword": "best hair dryers for curly hair",
        "title": "Best Hair Dryers for Curly Hair",
        "h1": "Best Hair Dryers for Curly Hair (2026)",
        "job": "full hair dryers that are curly-hair or diffuser friendly",
        "confirm": (
            "Confirm heat settings and whether a diffuser ships in the box on the retailer page."
        ),
        "skip": (
            "Skip this slice if you only need a spare diffuser or concentrator. "
            "Accessories are not a primary pick here."
        ),
        "lede": (
            "Curly-hair drying is a full dryer job — a unit that ships a diffuser or says "
            "curly-friendly — not a standalone diffuser accessory."
        ),
        "ban_groups": [],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
    },
    {
        "n": 6,
        "slug": "humidifiers",
        "name": "Humidifiers",
        "path": "best-humidifiers-for-large-rooms",
        "label": "Best for large rooms",
        "keyword": "best humidifiers for large rooms",
        "title": "Best Humidifiers for Large Rooms",
        "h1": "Best Humidifiers for Large Rooms (2026)",
        "job": "large-room humidifiers by tank and coverage, not nursery units",
        "confirm": (
            "Confirm coverage in square feet, tank size, and mist type on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a nursery or baby humidifier. That job lives on "
            "Best humidifiers for babies."
        ),
        "lede": (
            "Large-room humidifiers are a coverage and tank-size job — not a nursery unit "
            "and not a filter cartridge."
        ),
        "ban_groups": ["humidifiers_babies"],
        "siblings": [
            {"path": "best-humidifiers-for-babies", "label": "Best for babies"},
            {"path": "best-humidifiers-for-bedrooms", "label": "Best for bedrooms"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-humidifiers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-humidifiers.jpg",
    },
    {
        "n": 7,
        "slug": "projectors",
        "name": "Projectors",
        "path": "best-projectors-for-outdoor",
        "label": "Best for outdoor",
        "keyword": "best projectors for outdoor",
        "title": "Best Projectors for Outdoor",
        "h1": "Best Projectors for Outdoor (2026)",
        "job": "outdoor projectors you can confirm brightness and weather notes for",
        "confirm": (
            "Confirm brightness, weather notes, and power source on the retailer page. "
            "We do not invent lumens or IP ratings."
        ),
        "skip": (
            "Skip this slice if you want a bedroom-only projector or a spare screen. "
            "Those jobs live on the main projectors comparison."
        ),
        "lede": (
            "Outdoor projection is a portable or weather-ready projector job — not a "
            "screen-only accessory and not invented brightness copy."
        ),
        "ban_groups": [],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-projectors.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-projectors.jpg",
    },
    {
        "n": 8,
        "slug": "pillows",
        "name": "Pillows",
        "path": "best-pillows-for-side-sleepers",
        "label": "Best for side sleepers",
        "keyword": "best pillows for side sleepers",
        "title": "Best Pillows for Side Sleepers",
        "h1": "Best Pillows for Side Sleepers (2026)",
        "job": "side-sleeper pillows that are not already on the neck-pain slice",
        "confirm": (
            "Confirm loft, fill, and whether the listing names side sleepers on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a neck-pain pillow. That job lives on "
            "Best pillows for neck pain."
        ),
        "lede": (
            "Side-sleeper pillows are a loft and fill job — not a pillowcase and not a "
            "paste of the neck-pain shortlist."
        ),
        "ban_groups": ["pillows_neck_pain"],
        "siblings": [
            {"path": "best-pillows-for-neck-pain", "label": "Best for neck pain"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-pillows.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-pillows.jpg",
    },
]


def _esc(text: str) -> str:
    return escape(text or "", quote=True)


OCCUPIED_SOURCE_MAP = {
    "litter_main": ("hub:litter-boxes",),
    "video_doorbells": ("hub:video-doorbells",),
    "robot_pet_hair": (
        "hub:robot-vacuums",
        "inv:/robot-vacuums/pet-homes/",
        "scene:pet-homes",
    ),
    "humidifiers_babies": (
        "hub:humidifiers",
        "inv:/humidifiers/best-humidifiers-for-babies/",
        "scene:humidifiers-babies",
    ),
    "pillows_neck_pain": (
        "hub:pillows",
        "inv:/pillows/best-pillows-for-neck-pain/",
        "shortlist-pillows",
    ),
}


def _asin_set(values: Any) -> set[str]:
    return {str(a).strip().upper() for a in values or [] if str(a).strip()}


def load_occupied() -> dict[str, set[str]]:
    blob = json.loads(OCCUPIED_PATH.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = {}
    if blob.get("groups"):
        for key, group in blob["groups"].items():
            out[key] = _asin_set(group.get("asins"))
    by_source = blob.get("by_source") or {}
    if by_source:
        for key, sources in OCCUPIED_SOURCE_MAP.items():
            merged: set[str] = set()
            for src in sources:
                merged |= _asin_set(by_source.get(src))
            out[key] = merged
    out["global"] = _asin_set(blob.get("flat"))
    if not out["global"]:
        extra: set[str] = set()
        for key, values in out.items():
            if key != "global":
                extra |= values
        out["global"] = extra
    return out


def banned_for(scene: dict[str, Any], occupied: dict[str, set[str]]) -> set[str]:
    banned = set(occupied.get("global") or ())
    for key in scene.get("ban_groups") or []:
        banned |= occupied.get(key) or set()
    return banned


def token_env() -> dict[str, Any]:
    names = [
        "PARTNERBOOST_API_KEY",
        "PARTNERBOOST_TOKEN",
        "PB_API_KEY",
        "PB_TOKEN",
        "YEAHPROMOS_API_KEY",
        "YEAHPROMOS_TOKEN",
        "YP_API_KEY",
        "YP_TOKEN",
        "AFFILIATE_API_KEY",
    ]
    present = [n for n in names if (os.environ.get(n) or "").strip()]
    return {
        "present": present,
        "available": bool(present),
        "note": (
            "No affiliate API tokens in this VM environment. "
            "Do not invent Check price hops."
        ),
    }


def find_fill_pack() -> Path | None:
    for path in PACK_CANDIDATES:
        if path.exists():
            return path
    return None


def healthy_track(url: str | None) -> str | None:
    if is_empty_track(url):
        return None
    raw = (url or "").strip()
    if not is_allowed_track_host(raw):
        return None
    if classify_network(raw) != "pb":
        return None
    out = ensure_affiliate_uid(raw, "pb")
    return out if "uid=fromsll" in out else None


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
    if scene["path"] == "best-security-cameras-for-outdoor" and DOORBELL_RE.search(title):
        return None
    if scene["path"] == "best-cordless-vacuums-for-pet-hair" and ROBOT_RE.search(title):
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
    scenes = pack.get("scenes") or {}
    blob = scenes.get(scene["path"]) or scenes.get(f"/{scene['slug']}/{scene['path']}/") or {}
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
                "density_target": "6-10 scene-fit if inventory allows",
                "fill_status": "filled" if n else "need_fill",
                "cta_status": "pb_fromsll" if n else "empty",
                "cta_rule": "PB fromsll only when a verified track exists; never invent hops",
                "reviews": "none — Top pick + Upgrade articles do not exist for this scene",
                "ban_groups": scene["ban_groups"],
                "picks": [_pick_public(p) for p in picks],
            }
        )
    filled = sum(1 for row in pages if row["fill_status"] == "filled")
    return {
        "date": DATE,
        "waiting_for_部署上线": True,
        "published": False,
        "live": False,
        "merged": False,
        "independent_of_shortlist_lab": True,
        "do_not_touch": ["#48", "#49", "Lab", "RR", "OL"],
        "pillows_hub": "exists_p2_not_recreated",
        "fill_pack": str(pack_path) if pack_path else None,
        "fill_status": "partial" if 0 < filled < len(pages) else ("filled" if filled else "need_fill"),
        "need_fill": [row["path"] for row in pages if row["fill_status"] == "need_fill"],
        "sources": {
            "1_pb": {
                "live_query": "skipped_no_token" if not tokens["available"] else "ran",
                "note": tokens["note"],
            },
            "2_yp": {
                "live_query": "skipped_no_token" if not tokens["available"] else "ran",
                "note": tokens["note"],
            },
            "l1_fill_pack": pack_path.name if pack_path else None,
        },
        "occupied_groups": {k: sorted(v) for k, v in occupied.items()},
        "pages": pages,
        "notes": [
            "Affiliate tokens were not available in this VM. Empty shells stay empty.",
            "No invented ASINs, prices, was/%, gallery, or Check price hops.",
            "Parent hubs already exist — including /pillows/ from P2. Not recreated.",
            "published=false / noindex until a later 部署上线 order.",
        ],
    }


def faq_html(pairs: list[tuple[str, str]]) -> str:
    bits = ['<div class="faq prose-block"><h2>FAQ</h2>']
    for i, (q, a) in enumerate(pairs):
        open_attr = " open" if i == 0 else ""
        bits.append(
            f"<details{open_attr}><summary>{_esc(q)}</summary><p>{_esc(a)}</p></details>"
        )
    bits.append("</div>")
    return "".join(bits)


def faq_ld(pairs: list[tuple[str, str]]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in pairs
        ],
    }


def desc_trunc(text: str, n: int = 155) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    cut = text[: n - 1].rsplit(" ", 1)[0]
    return cut + "…"


def scene_faqs(scene: dict[str, Any], picks: list[dict[str, Any]]) -> list[tuple[str, str]]:
    n = len(picks)
    relate = (
        f"The main chart covers the live {scene['name'].lower()} shortlist. "
        f"This URL lists {n} scene-fit picks that are not a paste of that order."
        if n
        else (
            f"The main chart covers the live {scene['name'].lower()} shortlist. "
            "This URL only lists scene-fit picks when a verified retailer link exists. "
            "An empty slot beats a guessed card."
        )
    )
    pairs = [
        (
            f"What does “{scene['keyword']}” mean on this page?",
            f"It is an editorial slice for {scene['job']} — not a paid badge, "
            f"and not a second copy of the main {scene['name'].lower()} chart.",
        ),
        (
            "Who should skip this slice?",
            scene["skip"],
        ),
    ]
    if n == 0:
        pairs.append(
            (
                "Why is this shortlist empty?",
                "No verified retailer link exists yet for a scene-fit product that can live "
                "on this page. An empty slot beats a guessed card.",
            )
        )
    else:
        pairs.append(
            (
                f"How does this page relate to the main {scene['name'].lower()} comparison?",
                relate,
            )
        )
    pairs.append(("What should I confirm before I buy?", scene["confirm"]))
    return pairs


def _short_title(title: str, n: int = 52) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    return title if len(title) <= n else title[: n - 1].rsplit(" ", 1)[0] + "…"


def visit_cards_html(picks: list[dict[str, Any]], confirm: str) -> str:
    if not picks:
        return ""
    bits = ['<div class="bestof-visit-stack">']
    for i, pick in enumerate(picks, start=1):
        href = pick.get("affiliate_link") or ""
        role = pick.get("role") or "Shortlist"
        price = pick.get("price_displayed") or ""
        pitch = f"{role}."
        if price:
            pitch += f" {price}."
        pitch += f" {confirm}"
        cta = ""
        if href and pick.get("track_status") == "ok":
            cta = (
                f'<a class="btn btn-cta-yellow" href="{_esc(href)}" '
                'rel="sponsored noopener noreferrer" target="_blank">'
                "<span>Check price</span></a>"
            )
        bits.append(
            f'<section class="bestof-visit-card" id="bestof-pick-{i}">'
            f'<span class="geo-anchor" id="geo-{_esc(pick["asin"])}" tabindex="-1"></span>'
            f'<div class="bestof-visit-rank">{i}</div>'
            f'<div class="bestof-visit-main">'
            f'<div class="bestof-visit-copy"><strong>{_esc(pick["title"])}</strong>'
            f"<p>{_esc(pitch)}</p></div>{cta}</div></section>"
        )
    bits.append("</div>")
    return "".join(bits)


def inline_picks_html(picks: list[dict[str, Any]], confirm: str) -> str:
    shown = picks[: min(3, len(picks))]
    if not shown:
        return ""
    bits = ['<div class="inline-picks" aria-label="Editor shortlist">']
    for i, pick in enumerate(shown, start=1):
        href = pick.get("affiliate_link") or ""
        role = pick.get("role") or "Shortlist"
        price = pick.get("price_displayed") or ""
        pitch = f"{price}. {confirm}" if price else confirm
        cta = ""
        if href and pick.get("track_status") == "ok":
            cta = (
                f'<a class="btn btn-cta-yellow btn-sm" href="{_esc(href)}" '
                'rel="sponsored noopener noreferrer" target="_blank">Check price</a> '
            )
        bits.append(
            f'<article class="inline-pick-card"><span class="inline-pick-rank">#{i}</span>'
            f'<strong class="inline-pick-name">{_esc(_short_title(pick["title"]))}</strong>'
            f'<span class="inline-pick-role">{_esc(role)}</span>'
            f'<p class="inline-pick-pitch">{_esc(pitch)}</p>'
            f'<div class="inline-pick-actions">{cta}'
            f'<a href="#geo-{_esc(pick["asin"])}">See card</a>'
            "</div></article>"
        )
    bits.append("</div>")
    return "".join(bits)


def our_top_list_html(picks: list[dict[str, Any]], scene: dict[str, Any], confirm: str) -> str:
    if not picks:
        return ""
    n = len(picks)
    items = []
    for i, pick in enumerate(picks, start=1):
        price = f" {pick['price_displayed']}." if pick.get("price_displayed") else ""
        items.append(
            f"<li><strong>{i}. {_esc(pick['title'])}</strong> — "
            f"{_esc(confirm[:-1] if confirm.endswith('.') else confirm)}."
            f"{_esc(price)} "
            f'<a href="#geo-{_esc(pick["asin"])}">See card →</a></li>'
        )
    return (
        f'<section class="our-top-list"><h2>Our top {n} {escape(scene["name"].lower())} for this scene</h2>'
        f"<ol>{''.join(items)}</ol></section>"
    )


def who_pick_html(picks: list[dict[str, Any]], scene: dict[str, Any]) -> str:
    if not picks:
        return (
            "<p>None yet. We will scene-order products that fit this job when verified "
            "retailer links land — not a paste of the parent chart.</p>"
            f"<p>{_esc(scene['skip'])}</p>"
        )
    bits: list[str] = []
    for pick in picks[:2]:
        role = pick.get("role") or "Shortlist"
        price = pick.get("price_displayed") or ""
        extra = f" ({_esc(price)} snapshot)" if price else ""
        bits.append(
            f"<p><strong>{_esc(pick['title'])} — {_esc(role)}</strong>{extra}. "
            f"{_esc(scene['confirm'])}</p>"
        )
    bits.append(f"<p>{_esc(scene['skip'])}</p>")
    return "".join(bits)


def related_reading(scene: dict[str, Any]) -> str:
    slug = scene["slug"]
    name = scene["name"].lower()
    extras = "".join(
        f'<a href="../../{slug}/{sib["path"]}/">{_esc(sib["label"])}</a>, '
        for sib in scene.get("siblings") or []
    )
    return (
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        f'<a href="../../{slug}/">{_esc(name)} overview</a>, '
        f"{extras}"
        f'<a href="../../{slug}/reviews/">reviews hub</a>, and the '
        f'<a href="../../{slug}/comparison/">{_esc(name)} comparison</a>.</p>'
        f'<p class="article-cta-row"><a class="btn btn-primary" href="../../{slug}/comparison/">'
        "See current rankings</a></p>"
    )


def scene_article(
    scene: dict[str, Any],
    faqs: list[tuple[str, str]],
    picks: list[dict[str, Any]],
) -> str:
    slug = scene["slug"]
    name = scene["name"].lower()
    n = len(picks)
    if n == 0:
        body = (
            f"<p>{_esc(scene['lede'])} This best-of stays empty until a verified "
            "retailer link exists — we do not invent a padded Top 10.</p>"
            f"<p>Rankings follow the same shortlist rules as our main {name} comparison. "
            "Density is honest at 0 — we do not invent listings, prices, images, or discounts.</p>"
            '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
            '<ul class="card-bullets">'
            "<li><strong>Scene filter, not chart paste:</strong> This URL is a job slice, "
            "not a copy of the main chart.</li>"
            "<li><strong>Empty slot beats a guessed card:</strong> Check price appears only "
            "when a verified retailer link exists.</li>"
            "<li><strong>No accessories:</strong> Spare parts that cannot finish the buying "
            "job stay off this shortlist.</li>"
            "<li><strong>Reviews skipped:</strong> Top and Upgrade review articles do not "
            "exist for this scene, so we do not invent them.</li>"
            "</ul></section>"
            f"<h2>Which {_esc(scene['keyword'])} should you pick?</h2>"
            f"{who_pick_html(picks, scene)}"
            f'<p>Start at the <a href="../../{slug}/">{_esc(name)} overview</a> or the '
            f'<a href="../../{slug}/comparison/">{_esc(name)} comparison</a> for the live chart.</p>'
            '<div class="bestof-empty" data-fill-status="need_fill" '
            f'data-scene="{_esc(scene["path"])}">'
            "<p>No editor shortlist yet. Density is honest at 0. Check price appears when "
            "a verified retailer link exists for a scene-fit product that can live here.</p></div>"
            "<h2>What shoppers should optimize</h2>"
            f"<p>{_esc(scene['confirm'])}</p>"
            "<p>Skip accessories that cannot finish the buying job on their own.</p>"
            f"<h2>Our top {name} for this scene</h2>"
            "<p>No editor shortlist yet. An empty slot beats a stale or invented listing.</p>"
            "<h2>How we ranked these picks</h2>"
            "<p>We emphasize complete product cards and buyer roles instead of padding to ten. "
            "Density is honest at 0.</p>"
            f"<p>Last verified {DATE}. We do not invent lab scores.</p>"
        )
    else:
        body = (
            f"<p>{_esc(scene['lede'])} This best-of lists {n} verified products "
            "that fit this job.</p>"
            f"<p>Rankings follow the same shortlist rules as our main {name} comparison. "
            f"Density is honest at {n} — we do not invent listings, prices, images, or discounts.</p>"
            '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
            '<ul class="card-bullets">'
            "<li><strong>Scene filter, not chart paste:</strong> Order here follows the scene job, "
            "not the parent comparison rank.</li>"
            "<li><strong>Verified tracks only:</strong> Check price opens a verified retailer hop. "
            "Prices are a publish-time snapshot — confirm the live cart.</li>"
            "<li><strong>No accessories:</strong> Spare parts that cannot finish the buying "
            "job stay off this shortlist.</li>"
            "<li><strong>Reviews skipped:</strong> Top and Upgrade review articles do not "
            "exist for this scene, so we do not invent them.</li>"
            "</ul></section>"
            f"<h2>Which {_esc(scene['keyword'])} should you pick?</h2>"
            f"{who_pick_html(picks, scene)}"
            f'<p>Start at the <a href="../../{slug}/">{_esc(name)} overview</a> or the '
            f'<a href="../../{slug}/comparison/">{_esc(name)} comparison</a> for the live chart.</p>'
            f"{our_top_list_html(picks, scene, scene['confirm'])}"
            f"{inline_picks_html(picks, scene['confirm'])}"
            f"{visit_cards_html(picks, scene['confirm'])}"
            "<h2>What shoppers should optimize</h2>"
            f"<p>{_esc(scene['confirm'])}</p>"
            "<p>Skip accessories that cannot finish the buying job on their own.</p>"
            f"<h2>Our top {name} for this scene</h2>"
            f"<p>The {n} cards above are the honest shortlist. Empty slots were not filled with guesses.</p>"
            "<h2>How we ranked these picks</h2>"
            "<p>We emphasize complete product cards and buyer roles instead of padding to ten. "
            f"Density is honest at {n}.</p>"
            f"<p>Last verified {DATE}. We do not invent lab scores or product photos.</p>"
        )
    return f"{body}{related_reading(scene)}{faq_html(faqs)}"


def _replace_landing_article(html: str, article_inner: str) -> str:
    open_tag = '<article class="landing-article">'
    start = html.find(open_tag)
    if start < 0:
        raise SystemExit("template missing landing-article")
    i = start + len(open_tag)
    depth = 1
    while i < len(html):
        nxt_open = html.find("<article", i)
        nxt_close = html.find("</article>", i)
        if nxt_close < 0:
            raise SystemExit("template missing landing-article close")
        if nxt_open >= 0 and nxt_open < nxt_close:
            depth += 1
            i = nxt_open + len("<article")
            continue
        depth -= 1
        end = nxt_close + len("</article>")
        if depth == 0:
            return (
                html[:start]
                + f'<article class="landing-article">{article_inner}</article>'
                + html[end:]
            )
        i = end
    raise SystemExit("template missing landing-article close")


def clone_chrome(out_rel: str, slug: str) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    cfg = load_site_config()
    cats = cfg["ALL_CATS"]
    prefix = rel_prefix(out_rel)
    html = inject_nav_css(html)
    html = rewrite_non_home_nav(html, cats, prefix)
    html = rewrite_footer(html, cats, prefix)
    html = rewrite_disclosure(html)
    html = rewrite_compare_cta(html, prefix, slug, "page")
    return html


def replace_head(
    html: str,
    *,
    title: str,
    description: str,
    url: str,
    og_image: str,
    faqs: list[tuple[str, str]],
    page_desc: str,
    picks: list[dict[str, Any]],
    scene: dict[str, Any],
) -> str:
    short_desc = desc_trunc(description)
    html = re.sub(r"<title>.*?</title>", f"<title>{_esc(title)}</title>", html, count=1)
    html = re.sub(
        r'<meta name="description" content="[^"]*"/>',
        f'<meta name="description" content="{_esc(short_desc)}"/>',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]*"/>',
        f'<link rel="canonical" href="{_esc(url)}"/>',
        html,
        count=1,
    )
    for prop, val in (
        ("og:title", title),
        ("og:description", short_desc),
        ("og:url", url),
        ("og:image", og_image),
        ("twitter:title", title),
        ("twitter:description", short_desc),
        ("twitter:url", url),
        ("twitter:image", og_image),
    ):
        html = re.sub(
            rf'<meta property="{prop}" content="[^"]*"/>'
            if prop.startswith("og:")
            else rf'<meta name="{prop}" content="[^"]*"/>',
            (
                f'<meta property="{prop}" content="{_esc(val)}"/>'
                if prop.startswith("og:")
                else f'<meta name="{prop}" content="{_esc(val)}"/>'
            ),
            html,
            count=1,
        )
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{LIVE}/"},
            {
                "@type": "ListItem",
                "position": 2,
                "name": scene["name"],
                "item": f"{LIVE}/{scene['slug']}/",
            },
            {"@type": "ListItem", "position": 3, "name": "Best of", "item": url},
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": url,
        "isPartOf": {"@type": "WebSite", "name": "MoreTop10", "url": f"{LIVE}/"},
        "description": page_desc,
    }
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title,
        "url": url,
        "numberOfItems": len(picks),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i,
                "name": p.get("title") or p["asin"],
                "url": f"{url}#geo-{p['asin']}",
            }
            for i, p in enumerate(picks, start=1)
        ],
    }
    blobs = [breadcrumb, webpage, item_list, faq_ld(faqs)]

    def keep_org(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        return match.group(0) if data.get("@type") == "Organization" else ""

    html = re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        keep_org,
        html,
        flags=re.S,
    )
    insert = "".join(
        f'<script type="application/ld+json">{dumps_ld(obj)}</script>\n' for obj in blobs
    )
    return html.replace("</head>", insert + "</head>", 1)


def reviews_sidebar(slug: str) -> str:
    return (
        '<aside class="ed-reviews-sidebar">\n  <h3>Editorial Reviews</h3>\n'
        '  <div class="ed-rev-list"></div>\n'
        f'  <p class="sidebar-more"><a href="../../{slug}/reviews/">Reviews hub →</a></p>\n'
        "</aside>"
    )


def editors_picks(scene: dict[str, Any]) -> str:
    slug = scene["slug"]
    items = [
        f'<li><a href="../../{slug}/comparison/">Comparison chart</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
    ]
    for sib in scene.get("siblings") or []:
        items.append(
            f'<li><a href="../../{slug}/{sib["path"]}/">{_esc(sib["label"])}</a>'
            f'<span class="ed-pick-date">{DATE}</span></li>'
        )
    items.append(
        f'<li><a href="../../{slug}/{scene["path"]}/">{_esc(scene["label"])}</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
    )
    return (
        '<aside class="editors-picks-widget">\n  <h3>Editor\'s Picks</h3>\n'
        f'  <ul class="ed-picks-list">{"".join(items)}</ul>\n'
        f'  <p class="sidebar-more"><a href="../../{slug}/">Category overview →</a></p>\n'
        "</aside>"
    )


def replace_main(
    html: str,
    *,
    h1: str,
    article: str,
    scene: dict[str, Any],
) -> str:
    slug = scene["slug"]
    name = scene["name"]
    html = re.sub(
        r'<nav class="breadcrumb">.*?</nav>',
        (
            '<nav class="breadcrumb"><a href="../../index.html">Home</a> '
            f'<span class="sep">/</span> <a href="../../{slug}/">{_esc(name)}</a> '
            '<span class="sep">/</span> <span>Best of</span></nav>'
        ),
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(r"<h1>.*?</h1>", f"<h1>{_esc(h1)}</h1>", html, count=1)
    html = re.sub(
        r'<div class="author-avatar"[^>]*>.*?</div>',
        '<div class="author-avatar" aria-hidden="true">PN</div>',
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'<span class="author-name">.*?</span>',
        (
            '<span class="author-name">Written by '
            '<a class="author-name-link" href="../../authors/priya-nair/">'
            "Priya Nair</a></span>"
        ),
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'<span class="author-updated">.*?</span>',
        f'<span class="author-updated">Last Updated: {DATE}</span>',
        html,
        count=1,
    )
    html = re.sub(
        r'<img class="lifestyle-photo"[^>]*/?>',
        (
            f'<img class="lifestyle-photo" src="{_esc(scene["lifestyle_src"])}" '
            'alt="" width="640" height="400" loading="lazy"/>'
        ),
        html,
        count=1,
    )
    html = re.sub(
        r'<span class="lifestyle-label">.*?</span>',
        f'<span class="lifestyle-label">{_esc(name)}</span>',
        html,
        count=1,
    )
    html = _replace_landing_article(html, article)
    html = re.sub(
        r'<div class="editorial-side-stack">.*?</div>\s*</div>\s*</div>\s*</main>',
        (
            '<div class="editorial-side-stack">\n        \n'
            f"{reviews_sidebar(slug)}\n\n        \n"
            f"{editors_picks(scene)}\n\n"
            "      </div>\n    </div>\n  </div>\n</main>"
        ),
        html,
        count=1,
        flags=re.S,
    )
    return html


def assert_clean_page(
    html: str, scene: dict[str, Any], banned: set[str], picks: list[dict[str, Any]]
) -> None:
    errors: list[str] = []
    n = len(picks)
    if DRAFT_COMMENT not in html:
        errors.append("missing waiting_for_部署上线 draft comment")
    if f'name="robots" content="{ROBOTS_NOINDEX}"' not in html:
        errors.append("robots is not noindex,follow")
    leftovers = list(TEMPLATE_LEFTOVER)
    if scene["slug"] != "humidifiers":
        leftovers.extend(TEMPLATE_LEFTOVER_NON_HUMIDIFIER)
    for leak in leftovers:
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
    for asin in banned:
        if asin in html:
            errors.append(f"banned ASIN leaked {asin}")
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


def add_landing_cluster(scene: dict[str, Any]) -> None:
    path = SITE / scene["slug"] / "index.html"
    html = path.read_text(encoding="utf-8")
    cluster = re.search(
        r'(<p class="landing-related-cluster">)(.*?)(</p>)',
        html,
        re.S,
    )
    if not cluster:
        raise SystemExit(f"{scene['slug']} landing missing landing-related-cluster")
    inner = cluster.group(2)
    if f'href="../{scene["slug"]}/' in inner:
        href = f'../{scene["slug"]}/{scene["path"]}/'
    else:
        href = f'{scene["path"]}/'
    if href in inner or f'{scene["path"]}/' in inner:
        return
    addition = f' · <a href="{href}">{_esc(scene["label"])}</a>'
    html = html[: cluster.start(3)] + addition + html[cluster.start(3) :]
    path.write_text(html, encoding="utf-8")


def bump_or_insert_sitemap(paths: list[str]) -> None:
    sm = SITE / "sitemap.xml"
    xml = sm.read_text(encoding="utf-8")
    lastmod = f"{DATE}T12:00:00+00:00"
    for path in paths:
        loc = f"{LIVE}/{path}"
        if f"<loc>{loc}</loc>" in xml:
            xml = re.sub(
                rf"(<loc>{re.escape(loc)}</loc>\s*<lastmod>)[^<]+",
                rf"\g<1>{lastmod}",
                xml,
                count=1,
            )
            continue
        block = (
            "  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            "  </url>\n"
        )
        urls = list(re.finditer(r"  <url>\s*<loc>([^<]+)</loc>", xml))
        insert_at = xml.rfind("</urlset>")
        for match in urls:
            if match.group(1) > loc:
                insert_at = match.start()
                break
        xml = xml[:insert_at] + block + xml[insert_at:]
    sm.write_text(xml, encoding="utf-8")


def patch_html_sitemap() -> None:
    path = SITE / "sitemap" / "index.html"
    html = path.read_text(encoding="utf-8")
    for scene in SCENES:
        href = f'../{scene["slug"]}/{scene["path"]}/'
        if href in html:
            continue
        marker = f'<a href="../{scene["slug"]}/comparison/">Compare</a>'
        if marker not in html:
            raise SystemExit(f"sitemap/index.html missing {scene['slug']} row")
        html = html.replace(
            marker,
            f'{marker} · <a href="{href}">{_esc(scene["label"])}</a>',
            1,
        )
    path.write_text(html, encoding="utf-8")


def write_inventory(inv: dict[str, Any]) -> None:
    dest = DATA / "p4-scenario-inventory-2026-10-23.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = []
    for row in inv["pages"]:
        rows.append(
            f"| `{row['path']}` | **{row['density']}** | `{row['fill_status']}` | "
            f"{row['cta_status']} | none |"
        )
    need = inv.get("need_fill") or []
    md = DATA / "p4-scenario-inventory-2026-10-23.md"
    md.write_text(
        "\n".join(
            [
                "# P4 scenario best-of inventory (2026-10-23)",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / noindex",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Do not touch:** #48 / #49.",
                "**Pillows hub:** already exists from P2 — not recreated.",
                "",
                "## Fill status",
                "",
                f"- Global fill status: `{inv['fill_status']}`",
                f"- Fill pack: `{inv.get('fill_pack') or 'missing — need_fill shells'}`",
                f"- Affiliate tokens on VM: `{inv['sources']['1_pb']['live_query']}` / `{inv['sources']['2_yp']['live_query']}`",
                f"- Hubs that need_fill: {len(need)}",
                "",
                "## Paths",
                "",
                "| Path | Density | Fill | CTA | Reviews |",
                "| --- | --- | --- | --- | --- |",
                *rows,
                "",
                "## Hard rules kept",
                "",
                "- No invented ASINs / prices / was / % / gallery / CTAs.",
                "- No accessories as primary picks.",
                "- #2 litter main, #3 doorbells, #4 robot pet-hair, #6 baby humidifiers, #8 neck-pain pillows banned.",
                "- Reviews skipped.",
                "- Independent of Shortlist Lab.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if not TEMPLATE.exists():
        raise SystemExit(f"missing type-07 template {TEMPLATE}")
    if not (SITE / "pillows" / "index.html").exists():
        raise SystemExit("expected existing /pillows/ hub from P2 — do not invent a new hub here")
    occupied = load_occupied()
    pack_path = find_fill_pack()
    pack = None
    if pack_path:
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        if pack_path.resolve() != PACK_INREPO.resolve():
            shutil.copy2(pack_path, PACK_INREPO)
            pack_path = PACK_INREPO
    by_path: dict[str, list[dict[str, Any]]] = {}
    for scene in SCENES:
        banned = banned_for(scene, occupied)
        picks = scene_picks_from_pack(pack, scene, banned)
        by_path[scene["path"]] = picks
        write_products_shell(scene, picks)
        write_scene(scene, banned, picks)
        add_landing_cluster(scene)
    inv = build_inventory(by_path, pack_path, occupied)
    write_inventory(inv)
    bump_or_insert_sitemap([f"{s['slug']}/{s['path']}/" for s in SCENES])
    patch_html_sitemap()
    need = ",".join(p.split("/")[1] for p in inv["need_fill"]) or "none"
    print(
        "bake_p4_scenario ok "
        f"(fill={inv['fill_status']} need_fill={len(inv['need_fill'])} hubs={need})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
