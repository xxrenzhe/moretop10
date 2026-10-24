#!/usr/bin/env python3
"""Bake P5a MT10 scenario best-of pages (8 type-07 children).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not recreate live parent hubs. Do not rebind CTA to YeahPromos.

Hard rules:
  - Type-07 pages only. published=false / noindex until 部署上线.
  - Use L1 pack ASINs / roles / prices / tracks as given. No invented ASINs / was / %.
  - Density 10 per scene from pack (8 × 10 = 80).
  - Collision bans: P4 curly / outdoor projector / for-home espresso / pet-hair + robot;
    fine↛travel; car↛hardwood; outdoor-BT↛#8 desktop.
  - No accessories as hero picks. #8 must not take outdoor BT portables.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).

Usage:
    python3 site/scripts/bake_p5_scenario.py
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
    related_reading,
    replace_head,
    replace_main,
    scene_article,
    scene_faqs,
    token_env,
)
from seo_geo import LIVE, ROBOTS_NOINDEX, rewrite_visible_jargon, set_robots_meta  # noqa: E402

from stamp_guard import bake_stamp_date  # noqa: E402

DATE = bake_stamp_date("2026-10-23")
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P5a scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
OCCUPIED_PATH = DATA / "p5-occupied-asins-2026-10-23.json"
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-p5-fill-pack-2026-10-23.json"),
    DATA / "mt10-p5-fill-pack-2026-10-23.json",
    DATA / "p5-l1-fill-pack-2026-10-23.json",
)
PACK_INREPO = DATA / "p5-l1-fill-pack-2026-10-23.json"
PARENT_HUBS = (
    "hair-dryers",
    "projectors",
    "espresso-machines",
    "bluetooth-speakers",
    "cordless-vacuums",
    "computer-speakers",
)
ROBOT_RE = re.compile(r"robot vacuum|robovac|self[\s-]?empty dock", re.I)
PORTABLE_BT_RE = re.compile(
    r"portable bluetooth|outdoor bluetooth|saltwater|ipx[0-9]|tribit|"
    r"wireless portable speak|boom 2 plus|boom 3i|boom 2 by",
    re.I,
)
VACUUM_PATHS = {
    "best-cordless-vacuums-for-cars",
    "best-cordless-vacuums-for-hardwood-floors",
}

SCENES: list[dict[str, Any]] = [
    {
        "n": 1,
        "slug": "hair-dryers",
        "name": "Hair Dryers",
        "path": "best-hair-dryers-for-fine-hair",
        "label": "Best for fine hair",
        "keyword": "best hair dryers for fine hair",
        "title": "Best Hair Dryers for Fine Hair",
        "h1": "Best Hair Dryers for Fine Hair (2026)",
        "job": "full hair dryers for fine or easily weighed-down hair",
        "confirm": (
            "Confirm heat settings and whether a diffuser ships in the box on the retailer page."
        ),
        "skip": (
            "Skip this slice if you only need a spare diffuser, or a curly-hair dryer already "
            "on Best hair dryers for curly hair."
        ),
        "lede": (
            "Fine-hair drying is a full dryer job — a complete unit, not a standalone diffuser "
            "and not a paste of the curly-hair shortlist."
        ),
        "ban_groups": ["p4_curly"],
        "cross_ban_scenes": ["best-hair-dryers-for-travel"],
        "siblings": [
            {"path": "best-hair-dryers-for-curly-hair", "label": "Best for curly hair"},
            {"path": "best-hair-dryers-for-travel", "label": "Best for travel"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
    },
    {
        "n": 2,
        "slug": "projectors",
        "name": "Projectors",
        "path": "best-projectors-for-home-theater",
        "label": "Best for home theater",
        "keyword": "best projectors for home theater",
        "title": "Best Projectors for Home Theater",
        "h1": "Best Projectors for Home Theater (2026)",
        "job": "home-theater projectors you can confirm brightness and inputs for",
        "confirm": (
            "Confirm brightness, throw, and HDMI or smart-TV notes on the retailer page. "
            "We do not invent lumens."
        ),
        "skip": (
            "Skip this slice if you want an outdoor-only projector. That job lives on "
            "Best projectors for outdoor."
        ),
        "lede": (
            "Home-theater projection is a living-room projector job — not a screen-only "
            "accessory and not a paste of the outdoor shortlist."
        ),
        "ban_groups": ["p4_outdoor_proj"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-projectors-for-outdoor", "label": "Best for outdoor"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-projectors.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-projectors.jpg",
    },
    {
        "n": 3,
        "slug": "espresso-machines",
        "name": "Espresso Machines",
        "path": "best-espresso-machines-for-beginners",
        "label": "Best for beginners",
        "keyword": "best espresso machines for beginners",
        "title": "Best Espresso Machines for Beginners",
        "h1": "Best Espresso Machines for Beginners (2026)",
        "job": "beginner espresso machines you can run on a kitchen counter",
        "confirm": (
            "Confirm boiler type, portafilter size, and whether a grinder ships in the box "
            "on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a café-only prosumer deck. Home-counter decks that "
            "are already on Best espresso machines for home stay there."
        ),
        "lede": (
            "Beginner espresso is a countertop machine job — not a spare portafilter and "
            "not a paste of the for-home shortlist."
        ),
        "ban_groups": ["p4_espresso_home"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-espresso-machines-for-home", "label": "Best for home"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/espresso.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/espresso.jpg",
    },
    {
        "n": 4,
        "slug": "bluetooth-speakers",
        "name": "Bluetooth Speakers",
        "path": "best-bluetooth-speakers-for-outdoor",
        "label": "Best for outdoor",
        "keyword": "best bluetooth speakers for outdoor",
        "title": "Best Bluetooth Speakers for Outdoor",
        "h1": "Best Bluetooth Speakers for Outdoor (2026)",
        "job": "portable outdoor bluetooth speakers with a weather note you can confirm",
        "confirm": (
            "Confirm water rating and playtime on the retailer page. We do not invent IP ratings."
        ),
        "skip": (
            "Skip this slice if you want powered desktop or bookshelf computer speakers. "
            "That job lives on Best computer speakers for desktop."
        ),
        "lede": (
            "Outdoor bluetooth is a portable speaker job — not earbuds and not a desktop "
            "bookshelf pair."
        ),
        "ban_groups": [],
        "cross_ban_scenes": ["best-computer-speakers-for-desktop"],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-bluetooth-speakers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-bluetooth-speakers.jpg",
    },
    {
        "n": 5,
        "slug": "cordless-vacuums",
        "name": "Cordless Vacuums",
        "path": "best-cordless-vacuums-for-cars",
        "label": "Best for cars",
        "keyword": "best cordless vacuums for cars",
        "title": "Best Cordless Vacuums for Cars",
        "h1": "Best Cordless Vacuums for Cars (2026)",
        "job": "cordless vacuums you can use in a car, not robot vacs",
        "confirm": (
            "Confirm runtime, attachments, and whether a crevice or handheld mode ships in "
            "the box on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a robot vacuum or a hardwood wet-dry mop. Those "
            "jobs live on their own pages."
        ),
        "lede": (
            "Car cleanup is a stick or handheld cordless job — not a robot vacuum and not "
            "a spare dust bag."
        ),
        "ban_groups": ["p4_pet_hair", "robot_pet_hair"],
        "cross_ban_scenes": ["best-cordless-vacuums-for-hardwood-floors"],
        "siblings": [
            {"path": "best-cordless-vacuums-for-pet-hair", "label": "Best for pet hair"},
            {"path": "best-cordless-vacuums-for-hardwood-floors", "label": "Best for hardwood floors"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-cordless-vacuums.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-cordless-vacuums.jpg",
    },
    {
        "n": 6,
        "slug": "hair-dryers",
        "name": "Hair Dryers",
        "path": "best-hair-dryers-for-travel",
        "label": "Best for travel",
        "keyword": "best hair dryers for travel",
        "title": "Best Hair Dryers for Travel",
        "h1": "Best Hair Dryers for Travel (2026)",
        "job": "travel hair dryers you can confirm dual-voltage or compact notes for",
        "confirm": (
            "Confirm dual voltage, weight, and what attachments ship in the box on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a fine-hair or curly-hair dryer that is already on "
            "those slices. Accessories are not a primary pick here."
        ),
        "lede": (
            "Travel drying is a full compact dryer job — not a spare bag and not a paste of "
            "the fine-hair shortlist."
        ),
        "ban_groups": ["p4_curly"],
        "cross_ban_scenes": ["best-hair-dryers-for-fine-hair"],
        "siblings": [
            {"path": "best-hair-dryers-for-curly-hair", "label": "Best for curly hair"},
            {"path": "best-hair-dryers-for-fine-hair", "label": "Best for fine hair"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-hair-dryers.jpg",
    },
    {
        "n": 7,
        "slug": "cordless-vacuums",
        "name": "Cordless Vacuums",
        "path": "best-cordless-vacuums-for-hardwood-floors",
        "label": "Best for hardwood floors",
        "keyword": "best cordless vacuums for hardwood floors",
        "title": "Best Cordless Vacuums for Hardwood Floors",
        "h1": "Best Cordless Vacuums for Hardwood Floors (2026)",
        "job": "cordless vacuums for hardwood floors, including wet-dry floor cleaners that are not robot vacs",
        "confirm": (
            "Confirm floor-type notes, runtime, and whether a hard-floor head ships in the box "
            "on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a car handheld or a robot vacuum. Those jobs live "
            "on their own pages."
        ),
        "lede": (
            "Hardwood cleanup is a stick or wet-dry cordless job — not a robot vacuum and "
            "not a paste of the car shortlist."
        ),
        "ban_groups": ["p4_pet_hair", "robot_pet_hair"],
        "cross_ban_scenes": ["best-cordless-vacuums-for-cars"],
        "siblings": [
            {"path": "best-cordless-vacuums-for-pet-hair", "label": "Best for pet hair"},
            {"path": "best-cordless-vacuums-for-cars", "label": "Best for cars"},
        ],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-cordless-vacuums.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-cordless-vacuums.jpg",
    },
    {
        "n": 8,
        "slug": "computer-speakers",
        "name": "Computer Speakers",
        "path": "best-computer-speakers-for-desktop",
        "label": "Best for desktop",
        "keyword": "best computer speakers for desktop",
        "title": "Best Computer Speakers for Desktop",
        "h1": "Best Computer Speakers for Desktop (2026)",
        "job": "powered desktop or bookshelf computer speakers, not portable outdoor bluetooth",
        "confirm": (
            "Confirm inputs (3.5 mm, RCA, optical, USB) and whether a remote ships in the box "
            "on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a portable outdoor bluetooth speaker. That job lives "
            "on Best bluetooth speakers for outdoor."
        ),
        "lede": (
            "Desktop computer speakers are a powered bookshelf or monitor pair — not a "
            "portable outdoor bluetooth speaker and not earbuds."
        ),
        "ban_groups": [],
        "cross_ban_scenes": ["best-bluetooth-speakers-for-outdoor"],
        "siblings": [],
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-computer-speakers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-computer-speakers.jpg",
    },
]


OCCUPIED_SOURCE_MAP = {
    "p4_curly": (
        "p4:best-hair-dryers-for-curly-hair",
        "tip:products-best-hair-dryers-for-curly-hair",
    ),
    "p4_outdoor_proj": (
        "p4:best-projectors-for-outdoor",
        "tip:products-best-projectors-for-outdoor",
    ),
    "p4_espresso_home": (
        "p4:best-espresso-machines-for-home",
        "tip:products-best-espresso-machines-for-home",
    ),
    "p4_pet_hair": (
        "p4:best-cordless-vacuums-for-pet-hair",
        "tip:products-best-cordless-vacuums-for-pet-hair",
    ),
    "robot_pet_hair": (
        "hub:robot-vacuums",
        "scene:pet-homes",
        "prior:hub:robot-vacuums",
        "prior:inv:/robot-vacuums/pet-homes/",
        "prior:scene:pet-homes",
    ),
}


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
    if scene["path"] in VACUUM_PATHS and ROBOT_RE.search(title):
        return None
    if scene["path"] == "best-computer-speakers-for-desktop" and PORTABLE_BT_RE.search(title):
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
                "density_target": 10,
                "fill_status": "filled" if n else "need_fill",
                "cta_status": "pb_fromsll" if n else "empty",
                "cta_rule": "PB fromsll only when a verified track exists; never invent hops; do not rebind to YP",
                "reviews": "none — Top pick + Upgrade articles do not exist for this scene",
                "ban_groups": scene["ban_groups"],
                "cross_ban_scenes": scene["cross_ban_scenes"],
                "picks": [_pick_public(p) for p in picks],
            }
        )
    filled = sum(1 for row in pages if row["fill_status"] == "filled")
    return {
        "date": DATE,
        "batch": "P5a",
        "waiting_for_部署上线": True,
        "published": False,
        "live": False,
        "merged": False,
        "independent_of_shortlist_lab": True,
        "do_not_touch": ["Lab", "RR", "OL", "P4 pages", "parent hub cards"],
        "parent_hubs": "exist_not_recreated",
        "fill_pack": str(pack_path) if pack_path else None,
        "fill_status": "partial" if 0 < filled < len(pages) else ("filled" if filled else "need_fill"),
        "need_fill": [row["path"] for row in pages if row["fill_status"] == "need_fill"],
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
        "occupied_groups": {k: sorted(v) for k, v in occupied.items() if k != "global"},
        "occupied_global_n": len(occupied.get("global") or ()),
        "pages": pages,
        "notes": [
            "No invented ASINs, prices, was/%, gallery, or Check price hops.",
            "Parent hubs already exist. Not recreated.",
            "published=false / noindex until a later 部署上线 order.",
            "Independent of Shortlist Lab.",
        ],
    }


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
    for asin in banned:
        if asin in html:
            errors.append(f"banned ASIN leaked {asin}")
    if scene["path"] == "best-computer-speakers-for-desktop":
        for pick in picks:
            if PORTABLE_BT_RE.search(pick.get("title") or ""):
                errors.append(f"desktop hero is an outdoor BT portable {pick['asin']}")
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
    dest = DATA / "p5-scenario-inventory-2026-10-23.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = []
    for row in inv["pages"]:
        rows.append(
            f"| `{row['path']}` | **{row['density']}** | `{row['fill_status']}` | "
            f"{row['cta_status']} | none |"
        )
    need = inv.get("need_fill") or []
    md = DATA / "p5-scenario-inventory-2026-10-23.md"
    md.write_text(
        "\n".join(
            [
                "# P5a scenario best-of inventory (2026-10-23)",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / noindex",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Parent hubs:** already exist — not recreated.",
                "",
                "## Fill status",
                "",
                f"- Global fill status: `{inv['fill_status']}`",
                f"- Fill pack: `{inv.get('fill_pack') or 'missing — need_fill shells'}`",
                f"- Occupied collision set: `{inv.get('occupied_global_n')} ASINs`",
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
                "- P4 curly / outdoor projector / for-home espresso / pet-hair + robot banned.",
                "- fine↛travel; car↛hardwood; outdoor-BT↛#8 desktop.",
                "- #8 desktop has no outdoor bluetooth portable bleed.",
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
    for hub in PARENT_HUBS:
        if not (SITE / hub / "index.html").exists():
            raise SystemExit(f"expected existing /{hub}/ hub — do not invent a new hub here")
    occupied = load_occupied()
    pack_path = find_fill_pack()
    pack = None
    if pack_path:
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        if pack_path.resolve() != PACK_INREPO.resolve():
            shutil.copy2(pack_path, PACK_INREPO)
            pack_path = PACK_INREPO
    siblings = sibling_asins_from_pack(pack)
    by_path: dict[str, list[dict[str, Any]]] = {}
    for scene in SCENES:
        banned = banned_for(scene, occupied, siblings)
        picks = scene_picks_from_pack(pack, scene, banned)
        if pack and len(picks) != 10:
            raise SystemExit(
                f"{scene['path']} expected density 10 from L1 pack, got {len(picks)}"
            )
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
        "bake_p5_scenario ok "
        f"(fill={inv['fill_status']} need_fill={len(inv['need_fill'])} hubs={need})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
