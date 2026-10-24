#!/usr/bin/env python3
"""Bake P6b MT10 scenario best-of pages (5 type-07 children).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not recreate live parent hubs. Do not rebind CTA to YeahPromos.
Do not scaffold pillows/best-pillows-for-snoring (SHORTFALL n=0).
Do not scaffold ceramic-space-heaters/best-ceramic-space-heaters-for-bedroom (SHORTFALL n=3).
Do not flip #58 P6a scenes to published=true.

Hard rules:
  - Type-07 pages only. published=false / noindex until 部署上线.
  - Use L1 pack ASINs / roles / prices / tracks as given. No invented ASINs / was / %.
  - Density from pack (10/4/7/10/10). Honest shortfall counts OK; do not pad.
  - Soft parent densify: hub ASINs may appear on a scene. Sibling scene ASINs stay banned.
  - No accessories as hero picks. Lab independent.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).
  - Comparison / reviews stubs already exist on parent hubs — do not recreate or
    roll stamps earlier than 2026-10-24.

Usage:
    python3 site/scripts/bake_p6b_scenario.py
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

from stamp_guard import bake_stamp_date  # noqa: E402

DATE = bake_stamp_date("2026-10-24")
p4.DATE = DATE
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P6b scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
OCCUPIED_PATH = DATA / "p6b-occupied-asins-2026-10-24.json"
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-p6b-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-p6b-fill-pack/mt10-p6b-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-p6b-fill-pack/mt10-p6b-fill-pack-2026-10-24/p6b-l1-fill-pack-2026-10-24.json"),
    Path("/home/ubuntu/.cursor/projects/workspace/uploads/mt10-p6b-fill-pack-2026-10-24_d71a.json"),
    DATA / "mt10-p6b-fill-pack-2026-10-24.json",
    DATA / "p6b-l1-fill-pack-2026-10-24.json",
)
PACK_INREPO = DATA / "p6b-l1-fill-pack-2026-10-24.json"
PARENT_HUBS = (
    "computer-speakers",
    "litter-boxes",
    "light-therapy",
    "office-chairs",
    "dehumidifiers",
)
SKIPPED = (
    {
        "path": "best-pillows-for-snoring",
        "url": "/pillows/best-pillows-for-snoring/",
        "reason": "SHORTFALL n=0 < density 4 — skip scaffold",
    },
    {
        "path": "best-ceramic-space-heaters-for-bedroom",
        "url": "/ceramic-space-heaters/best-ceramic-space-heaters-for-bedroom/",
        "reason": "SHORTFALL n=3 < density 4 — skip scaffold",
    },
)
OUT_NICHES = (
    "best-pillows-for-snoring",
    "best-ceramic-space-heaters-for-bedroom",
    "best-hearing-aids-for-tinnitus",
    "best-mattresses-for-hanging",
    "best-red-light-therapy-masks",
    "best-robot-mops",
)
P6A_KEEP_UNPUBLISHED = (
    "products-best-robotic-pool-cleaners-for-inground-pools.json",
    "products-best-bike-racks-for-hitch.json",
    "products-best-espresso-machines-under-500.json",
    "products-best-hair-dryers-for-thick-hair.json",
    "products-best-security-cameras-for-indoor.json",
    "products-best-projectors-for-bedroom.json",
    "products-best-dehumidifiers-for-bathroom.json",
)
SOUNDBAR_RE = re.compile(r"\bsoundbar\b", re.I)
PORTABLE_BT_RE = re.compile(r"portable bluetooth|\bportable speaker\b", re.I)
MASK_VEST_RE = re.compile(r"\bmask\b|\bvest\b", re.I)
LITTER_ACC_RE = re.compile(
    r"litter filler|litter beads|airstep|litter pad|cat litter(?! box)",
    re.I,
)
DAMPRID_RE = re.compile(r"damprid|moisture absorber|hanging bag", re.I)

SCENES: list[dict[str, Any]] = [
    {
        "n": 1,
        "slug": "computer-speakers",
        "name": "Computer Speakers",
        "path": "best-computer-speakers-for-gaming",
        "label": "Best for gaming",
        "keyword": "best computer speakers for gaming",
        "title": "Best Computer Speakers for Gaming",
        "h1": "Best Computer Speakers for Gaming (2026)",
        "job": "desktop or PC gaming speakers — not a soundbar or portable Bluetooth speaker",
        "confirm": (
            "Confirm inputs (USB, 3.5 mm, Bluetooth), RGB notes, and desk footprint "
            "on the retailer page. We do not invent watt ratings."
        ),
        "skip": (
            "Skip this slice if you want a soundbar, a portable Bluetooth speaker, or the "
            "desktop-first shortlist already on Best computer speakers for desktop."
        ),
        "lede": (
            "Gaming desktop audio is a full PC speaker job — not a soundbar, not a "
            "portable Bluetooth speaker, and not a paste of the desktop shortlist."
        ),
        "ban_groups": ["speakers_siblings"],
        "soft_hub_groups": ["speakers_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-computer-speakers-for-desktop", "label": "Best for desktop"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-computer-speakers.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-computer-speakers.jpg",
    },
    {
        "n": 2,
        "slug": "litter-boxes",
        "name": "Litter Boxes",
        "path": "best-litter-boxes-for-multiple-cats",
        "label": "Best for multiple cats",
        "keyword": "best litter boxes for multiple cats",
        "title": "Best Litter Boxes for Multiple Cats",
        "h1": "Best Litter Boxes for Multiple Cats (2026)",
        "job": "automatic or self-cleaning litter boxes that can serve more than one cat",
        "confirm": (
            "Confirm cat-count notes, waste-drawer size, and what liners or bags ship "
            "in the box on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want litter filler, pads, ramps, or the automatic "
            "shortlist already on Best automatic litter boxes."
        ),
        "lede": (
            "Multi-cat litter duty is a full self-cleaning box job — not filler, pads, "
            "or ramps, and not a paste of the automatic shortlist."
        ),
        "ban_groups": ["litter_siblings"],
        "soft_hub_groups": ["litter_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-automatic-litter-boxes", "label": "Best automatic"},
        ],
        "density_expected": 4,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-litter-boxes.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-litter-boxes.jpg",
    },
    {
        "n": 3,
        "slug": "light-therapy",
        "name": "Light Therapy",
        "path": "best-light-therapy-for-face",
        "label": "Best for face",
        "keyword": "best light therapy for face",
        "title": "Best Light Therapy for Face",
        "h1": "Best Light Therapy for Face (2026)",
        "job": "face-capable light therapy panels or machines — not masks or vests",
        "confirm": (
            "Confirm wavelength notes, session guidance, and return window on the "
            "retailer page. We do not invent irradiance scores."
        ),
        "skip": (
            "Skip this slice if you want a mask, a vest, or a full-body mat already on "
            "Best light therapy."
        ),
        "lede": (
            "Face light therapy is a panel or machine job — not a mask, not a vest, "
            "and not a paste of the generic light-therapy shortlist."
        ),
        "ban_groups": [],
        "soft_hub_groups": ["light_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-light-therapy", "label": "Best light therapy"},
        ],
        "density_expected": 7,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-light-therapy.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-light-therapy.jpg",
    },
    {
        "n": 4,
        "slug": "office-chairs",
        "name": "Office Chairs",
        "path": "best-office-chairs-for-gaming",
        "label": "Best for gaming",
        "keyword": "best office chairs for gaming",
        "title": "Best Office Chairs for Gaming",
        "h1": "Best Office Chairs for Gaming (2026)",
        "job": "gaming or racing-style desk chairs, not mats or lumbar pillows alone",
        "confirm": (
            "Confirm lumbar support, weight rating, and seat depth on the retailer page. "
            "We do not invent hour-comfort scores."
        ),
        "skip": (
            "Skip this slice if you want a back-pain or long-hours task chair already on "
            "those pages, or a chair mat by itself."
        ),
        "lede": (
            "Gaming desk seating is a full chair job — not a mat or lumbar pillow, and "
            "not a paste of the back-pain or long-hours shortlists."
        ),
        "ban_groups": ["chair_siblings"],
        "soft_hub_groups": ["chair_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-office-chairs-for-back-pain", "label": "Best for back pain"},
            {"path": "best-office-chairs-for-long-hours", "label": "Best for long hours"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-office-chairs.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-office-chairs.jpg",
    },
    {
        "n": 5,
        "slug": "dehumidifiers",
        "name": "Dehumidifiers",
        "path": "best-dehumidifiers-for-crawl-space",
        "label": "Best for crawl space",
        "keyword": "best dehumidifiers for crawl space",
        "title": "Best Dehumidifiers for Crawl Space",
        "h1": "Best Dehumidifiers for Crawl Space (2026)",
        "job": "crawl-space or basement dehumidifiers with a pump or drain — not DampRid bags",
        "confirm": (
            "Confirm pint rating, pump or drain hose, and coverage notes on the retailer "
            "page. We do not invent pint ratings."
        ),
        "skip": (
            "Skip this slice if you want a compact bathroom unit or the basement-primary "
            "shortlist already on those pages, or a hanging moisture absorber."
        ),
        "lede": (
            "Crawl-space moisture control is a pump or drain dehumidifier job — not a "
            "DampRid bag and not a paste of the bathroom or basement shortlists."
        ),
        "ban_groups": ["dehumid_siblings"],
        "soft_hub_groups": ["dehumid_hub"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-dehumidifiers-for-basements", "label": "Best for basements"},
            {"path": "best-dehumidifiers-for-bathroom", "label": "Best for bathroom"},
        ],
        "density_expected": 10,
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
    if path == "best-computer-speakers-for-gaming":
        if SOUNDBAR_RE.search(title) or PORTABLE_BT_RE.search(title):
            return None
    if path == "best-light-therapy-for-face" and MASK_VEST_RE.search(title):
        return None
    if path == "best-litter-boxes-for-multiple-cats" and LITTER_ACC_RE.search(title):
        return None
    if path == "best-dehumidifiers-for-crawl-space" and DAMPRID_RE.search(title):
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
        "batch": "P6b",
        "lock": "lock-p6b-rec",
        "tip_reference": "68a6d60e",
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
            "parent hub cards",
        ],
        "parent_hubs": "exist_not_recreated",
        "soft_parent_densify": (
            "hub ASINs may appear on scene; sibling bans still hold; "
            f"hub ASINs {hub_note}; L1 pack soft_parent B0DG6KP942 on light-therapy-for-face"
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
                "speakers_siblings",
                "speakers_hub",
                "litter_siblings",
                "litter_hub",
                "light_hub",
                "heater_siblings",
                "chair_siblings",
                "chair_hub",
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
            "Pillows snoring skipped (SHORTFALL n=0).",
            "Ceramic bedroom heaters skipped (SHORTFALL n=3).",
            "Did not flip #58 P6a published=true.",
            "OUT: tinnitus · mattress hang · red-light masks · robot-mop.",
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
            "best-pillows-for-snoring",
            "best-ceramic-space-heaters-for-bedroom",
            "best-hearing-aids-for-tinnitus",
            "best-mattresses-for-hanging",
            "best-red-light-therapy-masks",
            "best-robot-mops",
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
    dest = DATA / "p6b-scenario-inventory-2026-10-24.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = []
    for row in inv["pages"]:
        rows.append(
            f"| `{row['path']}` | **{row['density']}** | `{row['fill_status']}` | "
            f"{row['cta_status']} | none |"
        )
    need = inv.get("need_fill") or []
    md = DATA / "p6b-scenario-inventory-2026-10-24.md"
    md.write_text(
        "\n".join(
            [
                "# P6b scenario best-of inventory (2026-10-24)",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / noindex",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Parent hubs:** already exist — not recreated.",
                "**Tip:** `68a6d60e` (#58+#59+IL Live).",
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
                "- `/pillows/best-pillows-for-snoring/` — SHORTFALL n=0 < density 4. Not scaffolded.",
                "- `/ceramic-space-heaters/best-ceramic-space-heaters-for-bedroom/` — SHORTFALL n=3 < density 4. Not scaffolded.",
                "",
                "## Hard rules kept",
                "",
                "- No invented ASINs / prices / was / % / gallery / CTAs.",
                "- No accessories as primary picks.",
                "- Sibling ASIN bans hold. Soft parent densify preferred (hub ASINs may appear).",
                "- Reviews skipped. Comparison / reviews stubs already exist — stamps not rolled back.",
                "- Independent of Shortlist Lab.",
                "- Did not flip #58 P6a published=true.",
                "- OUT: tinnitus · mattress hang · red-light masks · robot-mop.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def refuse_skipped_pages() -> None:
    blocked = (
        SITE / "pillows" / "best-pillows-for-snoring" / "index.html",
        SITE / "ceramic-space-heaters" / "best-ceramic-space-heaters-for-bedroom" / "index.html",
        SITE / "hearing-aids" / "best-hearing-aids-for-tinnitus" / "index.html",
        SITE / "mattresses" / "best-mattresses-for-hanging" / "index.html",
        SITE / "light-therapy" / "best-red-light-therapy-masks" / "index.html",
        SITE / "robot-vacuums" / "best-robot-mops" / "index.html",
    )
    for path in blocked:
        if path.exists():
            raise SystemExit(f"must not scaffold /{path.relative_to(SITE).as_posix().removesuffix('index.html')}")


def assert_p6a_stays_unpublished() -> None:
    for name in P6A_KEEP_UNPUBLISHED:
        path = DATA / name
        if not path.exists():
            raise SystemExit(f"expected existing P6a shell {name}")
        blob = json.loads(path.read_text(encoding="utf-8"))
        if blob.get("published") is True:
            raise SystemExit(f"must not flip #58 {name} to published=true")


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
    assert_p6a_stays_unpublished()
    inv = build_inventory(by_path, pack_path, occupied)
    write_inventory(inv)
    bump_or_insert_sitemap([f"{s['slug']}/{s['path']}/" for s in SCENES])
    patch_html_sitemap()
    counts = "/".join(str(len(by_path[s["path"]])) for s in SCENES)
    print(
        "bake_p6b_scenario ok "
        f"(fill={inv['fill_status']} counts={counts} pillows=skipped heaters=skipped p6a=unpublished)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
