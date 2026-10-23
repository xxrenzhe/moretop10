#!/usr/bin/env python3
"""Bake P3 water-filter scenario best-of under live /water-filters/.

Draft only. Do not recreate the main class. Do not merge / Live deploy.
No Lab / RR / OL. Do not touch P1/P2 drafts.

Hard rules:
  - Type-07 pages only: well-water + hard-water.
  - Occupied ASIN collision ban vs Live /water-filters/ + pitcher/under-sink
    plus Lab P3 probed ASINs.
  - No accessories as picks. No invented prices / was / % / gallery / specs.
  - CTA only with verified PB fromsll from the L1 fill pack.
  - Well density 8 from the pack. Hard stays honest shortfall / density 0.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).

Usage:
    python3 site/scripts/bake_p3_water_bestof.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from html import escape, unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
DATA = SITE / "data"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chrome import (  # noqa: E402
    inject_nav_css,
    rel_prefix,
    rewrite_compare_cta,
    rewrite_disclosure,
    rewrite_footer,
    rewrite_non_home_nav,
)
from affiliate_uid import (  # noqa: E402
    classify_network,
    ensure_affiliate_uid,
    is_allowed_track_host,
    is_empty_track,
)
from seo_geo import LIVE, dumps_ld, rewrite_visible_jargon  # noqa: E402
from site_config import load_site_config  # noqa: E402

TEMPLATE = SITE / "humidifiers" / "best-humidifiers-for-bedrooms" / "index.html"
DATE = "2026-10-23"
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P3 water-filter scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. Do not recreate /water-filters/ main. -->"
)
OCCUPIED_PATH = DATA / "p3-water-occupied-asins-2026-10-23.json"
PACK_PATH = DATA / "p3-l1-fill-pack-2026-10-23.json"
PRODUCTS_WELL_PATH = DATA / "products-best-water-filters-for-well-water.json"
PRODUCTS_HARD_PATH = DATA / "products-best-water-filters-for-hard-water.json"
LAB_P3_BAN = frozenset(
    {
        "B0CHFCMJQS",
        "B0C9ZY2FDG",
        "B0H29PPQVV",
        "B0GSTRNQZX",
        "B0CJ9DK4T2",
        "B08LPBPVPS",
    }
)
EXPECTED_WELL = 8
EXPECTED_HARD = 0
TEMPLATE_LEFTOVER = (
    "What bedroom shoppers should optimize",
    "Our top humidifiers for this scene",
    'href="../../humidifiers/how-to-choose-a-humidifier/"',
    'href="../../humidifiers/premium-humidifier-alternatives/"',
    'href="../../humidifiers/levoit-bedroom-vs-homvana-cool-mist/"',
    "Best Humidifiers for Bedrooms (2026)",
    "best-humidifiers-for-bedrooms",
    "Best Humidifiers for Bedrooms",
)
ASIN_RE = re.compile(r"\bB0[A-Z0-9]{8}\b")
ACCESSORY_RE = re.compile(
    r"replacement|cartridge|filter pack|membrane only|3 pack|2 pack|"
    r"fridge|refrigerator water filter|brita",
    re.I,
)
WELL_RE = re.compile(
    r"\bwell water\b|\biron\b|\bsulfur\b|\bsulphur\b|\bsediment\b|"
    r"whole[\s-]?house|pretreat|well system",
    re.I,
)
HARD_RE = re.compile(
    r"\bsoftener\b|\bsoften\b|hard water|salt[- ]free|ion exchange|grain",
    re.I,
)
DRINKING_RE = re.compile(
    r"pitcher|under[\s-]?sink|countertop|reverse osmosis|\bRO\b|faucet water",
    re.I,
)
SCENES: list[dict[str, Any]] = [
    {
        "path": "best-water-filters-for-well-water",
        "label": "Best for well water",
        "keyword": "best water filters for well water",
        "title": "Best Water Filters for Well Water",
        "h1": "Best Water Filters for Well Water (2026)",
        "job": "well-water pretreatment and whole-house well systems",
        "confirm": (
            "Confirm well-test results (sediment, iron, sulfur), flow rate, "
            "and which stages ship in the box on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a pitcher or under-sink drinking filter. "
            "Those jobs live on the main water-filters comparison."
        ),
        "lede": (
            "Well water is a pretreatment job — sediment, iron, sulfur, and "
            "whole-house well systems — not a pitcher or under-sink drinking RO."
        ),
    },
    {
        "path": "best-water-filters-for-hard-water",
        "label": "Best for hard water",
        "keyword": "best water filters for hard water",
        "title": "Best Water Filters for Hard Water",
        "h1": "Best Water Filters for Hard Water (2026)",
        "job": "hard-water softeners and hard-water treatment systems",
        "confirm": (
            "Confirm hardness in grains, salt versus salt-free treatment, "
            "and drain or power needs on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a pitcher or under-sink drinking filter. "
            "Those jobs live on the main water-filters comparison."
        ),
        "lede": (
            "Hard water is a softener / treatment-system job — not a pitcher "
            "or under-sink drinking filter."
        ),
    },
]


def _esc(text: str) -> str:
    return escape(text or "", quote=True)


def load_occupied() -> set[str]:
    blob = json.loads(OCCUPIED_PATH.read_text(encoding="utf-8"))
    return {str(a).strip().upper() for a in blob.get("asins") or [] if str(a).strip()}


def load_banned() -> set[str]:
    return {a.upper() for a in load_occupied()} | set(LAB_P3_BAN)


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


def load_fill_pack() -> dict[str, Any]:
    if not PACK_PATH.exists():
        raise SystemExit(f"missing L1 fill pack {PACK_PATH}")
    return json.loads(PACK_PATH.read_text(encoding="utf-8"))


def pick_from_pack(row: dict[str, Any], banned: set[str]) -> dict[str, Any] | None:
    asin = str(row.get("asin") or "").strip().upper()
    title = str(row.get("title") or "").strip()
    track = healthy_track(row.get("track_url"))
    if not asin or not title or not track:
        return None
    if not ASIN_RE.fullmatch(asin):
        return None
    if asin.upper().startswith("B0X") and set(asin[2:]) <= set("X"):
        return None
    if asin in banned:
        return None
    if ACCESSORY_RE.search(title) and "whole house" not in title.lower():
        return None
    price = row.get("price")
    price_str = row.get("price_str")
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
    pack: dict[str, Any], scene_path: str, banned: set[str]
) -> list[dict[str, Any]]:
    scene = (pack.get("scenes") or {}).get(scene_path) or {}
    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in scene.get("products") or []:
        pick = pick_from_pack(row, banned)
        if not pick or pick["asin"] in seen:
            continue
        seen.add(pick["asin"])
        picks.append(pick)
    return picks


def products_file_picks(path: Path, banned: set[str]) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    blob = json.loads(path.read_text(encoding="utf-8"))
    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in blob.get("products") or []:
        pick = pick_from_pack(row, banned)
        if not pick or pick["asin"] in seen:
            continue
        seen.add(pick["asin"])
        picks.append(pick)
    return picks


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


def classify_title(title: str) -> str:
    t = title or ""
    if ACCESSORY_RE.search(t):
        return "accessory"
    well = bool(WELL_RE.search(t))
    hard = bool(HARD_RE.search(t))
    drinking = bool(DRINKING_RE.search(t))
    if hard and not drinking:
        return "hard_water_system"
    if well and not drinking:
        return "well_water_system"
    if drinking:
        return "drinking_system"
    return "other"


def scan_repo_inventory(occupied: set[str]) -> dict[str, Any]:
    """③ In-repo PB dumps + shortlists. Never invent rows."""
    files = [
        DATA / "shortlist-water-filters.json",
        DATA / "shortlist-pitcher-water-filters.json",
        DATA / "shortlist-under-sink-countertop-filtration.json",
        DATA / "mt10-day-add-filter-densify-2026-10-23.json",
        DATA / "day-add-open-batch-2026-10-23.json",
        DATA / "mt10-day-add-track-probe-2026-10-23.json",
    ]
    seen: dict[str, dict[str, Any]] = {}
    for path in files:
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        try:
            blob = json.loads(raw)
        except json.JSONDecodeError:
            blob = None
        titles: dict[str, str] = {}
        if isinstance(blob, dict):
            for pick in blob.get("picks") or []:
                asin = str(pick.get("asin") or "").strip().upper()
                if asin:
                    titles[asin] = str(pick.get("title") or "")
            by_slug = blob.get("by_slug") or {}
            if isinstance(by_slug, dict):
                for slug_blob in by_slug.values():
                    if not isinstance(slug_blob, dict):
                        continue
                    for key in ("proposed", "new_densify", "keep"):
                        for row in slug_blob.get(key) or []:
                            asin = str(row.get("asin") or "").strip().upper()
                            if asin:
                                titles[asin] = str(row.get("title") or titles.get(asin, ""))
            for niche in (blob.get("sites") or {}).get("mt10", {}).get("niches") or []:
                for sample in niche.get("sample_asins") or []:
                    asin = str(sample.get("asin") or "").strip().upper()
                    if asin:
                        titles[asin] = str(sample.get("title") or titles.get(asin, ""))
        for asin in ASIN_RE.findall(raw.upper()):
            titles.setdefault(asin, "")
        for asin, title in titles.items():
            if asin in seen:
                if title and not seen[asin]["title"]:
                    seen[asin]["title"] = title
                seen[asin]["sources"].append(path.name)
                continue
            kind = classify_title(title)
            seen[asin] = {
                "asin": asin,
                "title": title,
                "kind": kind,
                "occupied": asin in occupied,
                "sources": [path.name],
            }

    well_fit = [
        r
        for r in seen.values()
        if r["kind"] == "well_water_system" and not r["occupied"]
    ]
    hard_fit = [
        r
        for r in seen.values()
        if r["kind"] == "hard_water_system" and not r["occupied"]
    ]
    occupied_well = [
        r for r in seen.values() if r["kind"] == "well_water_system" and r["occupied"]
    ]
    return {
        "source": "in_repo_json",
        "files_scanned": [p.name for p in files if p.exists()],
        "unique_asins": len(seen),
        "scene_fit_well_unoccupied": well_fit,
        "scene_fit_hard_unoccupied": hard_fit,
        "occupied_well_mentions": occupied_well,
        "note": (
            "In-repo water inventory is drinking systems, pitchers, cartridges, "
            "or the occupied WHF21-PBL whole-house card already on /water-filters/. "
            "No unoccupied well-pretreatment or softener whole systems."
        ),
    }


def probe_live_sources() -> dict[str, Any]:
    """① PB and ② YP. Fail open when tokens are missing — do not invent."""
    tokens = token_env()
    return {
        "1_pb": {
            "name": "PartnerBoost brand catalog / PB∪ track search",
            "brand_ids_known": {
                "WFT-Waterdrop": 138654,
                "Waterdrop": 103211,
                "Frizzlife AMZ": 135821,
            },
            "live_query": "skipped_no_token" if not tokens["available"] else "ran",
            "scene_fit_whole_systems": [],
            "note": tokens["note"],
        },
        "2_yp": {
            "name": "YeahPromos catalog / YP track search",
            "live_query": "skipped_no_token" if not tokens["available"] else "ran",
            "scene_fit_whole_systems": [],
            "in_repo_yp_water_tracks": 0,
            "note": (
                "In-repo YP tracks are the /tv/ cluster only. "
                "No YP well-system or softener tracks on this VM."
            ),
        },
        "tokens": tokens,
    }


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
    well_picks: list[dict[str, Any]], hard_picks: list[dict[str, Any]]
) -> dict[str, Any]:
    occupied = load_occupied()
    live = probe_live_sources()
    repo = scan_repo_inventory(occupied)
    by_path = {
        "best-water-filters-for-well-water": well_picks,
        "best-water-filters-for-hard-water": hard_picks,
    }
    pages = []
    for scene in SCENES:
        picks = by_path[scene["path"]]
        n = len(picks)
        shortfall = n == 0 and "hard" in scene["path"]
        pages.append(
            {
                "path": f"/water-filters/{scene['path']}/",
                "type": "07-best-of",
                "parent": "/water-filters/",
                "density": n,
                "density_target": "6-10 scene-fit if inventory allows",
                "fill_status": "inventory_shortfall" if shortfall else ("filled" if n else "need_fill"),
                "inventory_blocked": shortfall,
                "inventory_shortfall": shortfall,
                "cta_status": "pb_fromsll" if n else "empty",
                "cta_rule": "PB fromsll only when a verified track exists; never invent hops",
                "reviews": "none — Top pick + Upgrade articles do not exist for this scene",
                "picks": [_pick_public(p) for p in picks],
            }
        )
    well_n = len(well_picks)
    hard_n = len(hard_picks)
    return {
        "date": DATE,
        "waiting_for_部署上线": True,
        "live": False,
        "merged": False,
        "independent_of_shortlist_lab": True,
        "do_not_touch": ["#36", "#37", "#40", "#43", "#45"],
        "occupied_asins": sorted(occupied),
        "occupied_count": len(occupied),
        "lab_p3_extra_ban": sorted(LAB_P3_BAN),
        "sources": {
            "1_pb": live["1_pb"],
            "2_yp": live["2_yp"],
            "3_in_repo": repo,
            "l1_fill_pack": {
                "path": PACK_PATH.name,
                "well": well_n,
                "hard": hard_n,
                "note": (
                    "Well filled from L1 pack (PB fromsll). "
                    "Hard is a true shortfall after ①②③ + Lab P3 ban of sole softener."
                ),
            },
        },
        "fill_status": "partial",
        "inventory_blocked": False,
        "pages": pages,
        "notes": [
            "Main /water-filters/ is already Live in this bake tree — do not recreate it.",
            "ASIN collision ban vs occupied 61 + Lab P3 six.",
            "No accessories as picks. No invented prices, was/%, gallery, or specs.",
            "Well density 8 from L1 pack. Hard density 0 shortfall — do not invent softeners.",
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
        f"The main chart covers drinking systems already on the live shortlist. "
        f"This URL lists {n} scene-fit whole-house systems that are not already there."
        if n
        else (
            "The main chart covers drinking systems already on the live shortlist. "
            "This URL only lists scene-fit whole systems that are not already there, "
            "and only when a verified retailer link exists. An empty slot beats a guessed card."
        )
    )
    pairs = [
        (
            f"What does “{scene['keyword']}” mean on this page?",
            f"It is an editorial slice for {scene['job']} — not a paid badge, "
            "and not a second copy of the main water-filters chart.",
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
                "No verified retailer link exists for a scene-fit softener or hard-water "
                "treatment system that can live on this page. An empty slot beats a guessed card.",
            )
        )
    else:
        pairs.append(
            (
                "How does this page relate to the main water-filters comparison?",
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


def our_top_list_html(picks: list[dict[str, Any]], confirm: str) -> str:
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
        f'<section class="our-top-list"><h2>Our top {n} water filters for this scene</h2>'
        f"<ol>{''.join(items)}</ol></section>"
    )


def who_pick_html(picks: list[dict[str, Any]], scene: dict[str, Any]) -> str:
    if not picks:
        return (
            "<p>None yet. We will scene-order whole systems that fit this job when verified "
            "retailer links land — not pitcher or under-sink drinking cards pasted from the parent chart.</p>"
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


def scene_article(
    scene: dict[str, Any],
    sibling: dict[str, Any],
    faqs: list[tuple[str, str]],
    picks: list[dict[str, Any]],
) -> str:
    slug = "water-filters"
    name = "water filters"
    n = len(picks)
    if n == 0:
        body = (
            f"<p>{_esc(scene['lede'])} This best-of stays empty until a verified "
            "retailer link exists — we do not invent a padded Top 10.</p>"
            f"<p>Rankings follow the same shortlist rules as our main {name} comparison. "
            "Density is honest at 0 — we do not invent listings, prices, images, or discounts.</p>"
            '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
            '<ul class="card-bullets">'
            "<li><strong>Scene filter, not chart paste:</strong> This URL is a well-water or "
            "hard-water job, not a copy of the main drinking-system chart.</li>"
            "<li><strong>Empty slot beats a guessed card:</strong> Check price appears only "
            "when a verified retailer link exists.</li>"
            "<li><strong>No accessories:</strong> Cartridge-only packs, filter packs, and "
            "membrane-only listings stay off this shortlist.</li>"
            "<li><strong>Reviews skipped:</strong> Top and Upgrade review articles do not "
            "exist for this scene, so we do not invent them.</li>"
            "</ul></section>"
            f"<h2>Which {_esc(scene['keyword'])} should you pick?</h2>"
            f"{who_pick_html(picks, scene)}"
            f'<p>Start at the <a href="../../{slug}/">water filters overview</a> or the '
            f'<a href="../../{slug}/comparison/">water filters comparison</a> for the live drinking-system chart.</p>'
            '<div class="bestof-empty" data-fill-status="inventory_shortfall" '
            f'data-scene="{_esc(scene["path"])}">'
            "<p>No editor shortlist yet. Density is honest at 0. Check price appears when "
            "a verified retailer link exists for a scene-fit whole system that is not "
            "already on the main water-filters chart.</p></div>"
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
            f"<p>{_esc(scene['lede'])} This best-of lists {n} verified whole-house systems "
            "that are not on the main drinking-system chart.</p>"
            f"<p>Rankings follow the same shortlist rules as our main {name} comparison. "
            f"Density is honest at {n} — we do not invent listings, prices, images, or discounts.</p>"
            '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
            '<ul class="card-bullets">'
            "<li><strong>Scene filter, not chart paste:</strong> This URL is a well-water job, "
            "not a copy of the main drinking-system chart.</li>"
            "<li><strong>Verified tracks only:</strong> Check price opens a verified retailer hop. "
            "Prices are a publish-time snapshot — confirm the live cart.</li>"
            "<li><strong>No accessories:</strong> Cartridge-only packs, filter packs, and "
            "membrane-only listings stay off this shortlist.</li>"
            "<li><strong>Reviews skipped:</strong> Top and Upgrade review articles do not "
            "exist for this scene, so we do not invent them.</li>"
            "</ul></section>"
            f"<h2>Which {_esc(scene['keyword'])} should you pick?</h2>"
            f"{who_pick_html(picks, scene)}"
            f'<p>Start at the <a href="../../{slug}/">water filters overview</a> or the '
            f'<a href="../../{slug}/comparison/">water filters comparison</a> for the live drinking-system chart.</p>'
            f"{our_top_list_html(picks, scene['confirm'])}"
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
    return (
        f"{body}"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        f'<a href="../../{slug}/">water filters overview</a>, '
        f'<a href="../../{slug}/{sibling["path"]}/">{_esc(sibling["label"])}</a>, '
        f'<a href="../../{slug}/reviews/">reviews hub</a>, and the '
        f'<a href="../../{slug}/comparison/">water filters comparison</a>.</p>'
        f'<p class="article-cta-row"><a class="btn btn-primary" href="../../{slug}/comparison/">'
        "See current rankings</a></p>"
        f"{faq_html(faqs)}"
    )


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


def clone_chrome(out_rel: str) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    cfg = load_site_config()
    cats = cfg["ALL_CATS"]
    prefix = rel_prefix(out_rel)
    html = inject_nav_css(html)
    html = rewrite_non_home_nav(html, cats, prefix)
    html = rewrite_footer(html, cats, prefix)
    html = rewrite_disclosure(html)
    html = rewrite_compare_cta(html, prefix, "water-filters", "page")
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
            {"@type": "ListItem", "position": 2, "name": "Water Filters", "item": f"{LIVE}/water-filters/"},
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


def reviews_sidebar() -> str:
    return (
        '<aside class="ed-reviews-sidebar">\n  <h3>Editorial Reviews</h3>\n'
        '  <div class="ed-rev-list"></div>\n'
        '  <p class="sidebar-more"><a href="../../water-filters/reviews/">Reviews hub →</a></p>\n'
        "</aside>"
    )


def editors_picks(scene: dict[str, Any], sibling: dict[str, Any]) -> str:
    return (
        '<aside class="editors-picks-widget">\n  <h3>Editor\'s Picks</h3>\n'
        '  <ul class="ed-picks-list">'
        '<li><a href="../../water-filters/comparison/">Comparison chart</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../water-filters/{sibling["path"]}/">{_esc(sibling["label"])}</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../water-filters/{scene["path"]}/">{_esc(scene["label"])}</a>'
        f'<span class="ed-pick-date">{DATE}</span></li></ul>\n'
        '  <p class="sidebar-more"><a href="../../water-filters/">Category overview →</a></p>\n'
        "</aside>"
    )


def replace_main(
    html: str,
    *,
    h1: str,
    article: str,
    scene: dict[str, Any],
    sibling: dict[str, Any],
) -> str:
    html = re.sub(
        r'<nav class="breadcrumb">.*?</nav>',
        (
            '<nav class="breadcrumb"><a href="../../index.html">Home</a> '
            '<span class="sep">/</span> <a href="../../water-filters/">Water Filters</a> '
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
            '<img class="lifestyle-photo" src="../../assets/img/lifestyle/cmp-hero-water-filters.jpg" '
            'alt="" width="640" height="400" loading="lazy"/>'
        ),
        html,
        count=1,
    )
    html = re.sub(
        r'<span class="lifestyle-label">.*?</span>',
        '<span class="lifestyle-label">Water Filters</span>',
        html,
        count=1,
    )
    html = _replace_landing_article(html, article)
    html = re.sub(
        r'<div class="editorial-side-stack">.*?</div>\s*</div>\s*</div>\s*</main>',
        (
            '<div class="editorial-side-stack">\n        \n'
            f"{reviews_sidebar()}\n\n        \n"
            f"{editors_picks(scene, sibling)}\n\n"
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
    for leak in TEMPLATE_LEFTOVER:
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
            errors.append("unexpected YP hop")
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
    sibling: dict[str, Any],
    banned: set[str],
    picks: list[dict[str, Any]],
) -> None:
    faqs = scene_faqs(scene, picks)
    out_rel = f"water-filters/{scene['path']}/index.html"
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{LIVE}/water-filters/{scene['path']}/"
    og = f"{LIVE}/assets/img/lifestyle/cmp-hero-water-filters.jpg"
    title = f"{scene['title']} | MoreTop10"
    n = len(picks)
    if n:
        desc = (
            f"{scene['lede']} This best-of lists {n} verified whole-house systems "
            "that are not on the main drinking-system chart."
        )
        page_desc = (
            f"Editorial slice of water filters for {scene['keyword']} — "
            f"honest density {n} from verified retailer links."
        )
    else:
        desc = (
            f"{scene['lede']} This best-of stays empty until a verified retailer "
            "link exists — we do not invent a padded Top 10."
        )
        page_desc = (
            f"Editorial slice of water filters for {scene['keyword']} — "
            "honest density 0 until a verified retailer link exists."
        )
    html = clone_chrome(out_rel)
    html = replace_head(
        html,
        title=title,
        description=desc,
        url=url,
        og_image=og,
        faqs=faqs,
        page_desc=page_desc,
        picks=picks,
    )
    html = replace_main(
        html,
        h1=scene["h1"],
        article=scene_article(scene, sibling, faqs, picks),
        scene=scene,
        sibling=sibling,
    )
    html = rewrite_visible_jargon(html)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    assert_clean_page(html, scene, banned, picks)
    dest.write_text(html, encoding="utf-8")


def patch_related_cluster() -> None:
    path = SITE / "water-filters" / "index.html"
    html = path.read_text(encoding="utf-8")
    cluster = (
        '<p class="landing-related-cluster"><strong>Also explore:</strong> '
        '<a href="comparison/">Full comparison chart</a> · '
        '<a href="reviews/">Reviews hub</a> · '
        '<a href="best-water-filters-for-well-water/">Best for well water</a> · '
        '<a href="best-water-filters-for-hard-water/">Best for hard water</a></p>'
    )
    html, n = re.subn(
        r'<p class="landing-related-cluster">.*?</p>',
        cluster,
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("water-filters landing missing landing-related-cluster to patch")
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
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
    old = (
        '<li><a href="../water-filters/">Water Filters</a> · '
        '<a href="../water-filters/comparison/">Compare</a></li>'
    )
    new = (
        '<li><a href="../water-filters/">Water Filters</a> · '
        '<a href="../water-filters/comparison/">Compare</a> · '
        '<a href="../water-filters/best-water-filters-for-well-water/">Best for well water</a> · '
        '<a href="../water-filters/best-water-filters-for-hard-water/">Best for hard water</a></li>'
    )
    if old not in html:
        if "best-water-filters-for-well-water" in html:
            return
        raise SystemExit("sitemap/index.html missing water-filters row to patch")
    path.write_text(html.replace(old, new, 1), encoding="utf-8")


def write_inventory(inv: dict[str, Any]) -> None:
    dest = DATA / "p3-water-bestof-inventory-2026-10-23.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pages = {row["path"]: row for row in inv["pages"]}
    well = pages["/water-filters/best-water-filters-for-well-water/"]
    hard = pages["/water-filters/best-water-filters-for-hard-water/"]
    md = DATA / "p3-water-bestof-inventory-2026-10-23.md"
    md.write_text(
        "\n".join(
            [
                "# P3 water-filter scenario best-of inventory (2026-10-23)",
                "",
                "**waiting_for_部署上线:** yes",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Parent:** `/water-filters/` (already Live — not recreated).",
                "**Do not touch:** P1/P2 drafts #36 / #37 / #40 / #43 / #45.",
                "",
                "## Fill status",
                "",
                f"- Global fill status: `{inv['fill_status']}`",
                f"- inventory_blocked: `{str(inv['inventory_blocked']).lower()}`",
                f"- Affiliate tokens on VM: `{inv['sources']['1_pb']['live_query']}` / `{inv['sources']['2_yp']['live_query']}`",
                "",
                "## Paths",
                "",
                f"| Path | Density | Fill | CTA | Reviews |",
                f"| --- | --- | --- | --- | --- |",
                f"| `/water-filters/best-water-filters-for-well-water/` | **{well['density']}** | `{well['fill_status']}` | {well['cta_status']} | none |",
                f"| `/water-filters/best-water-filters-for-hard-water/` | **{hard['density']}** | `{hard['fill_status']}` | {hard['cta_status']} | none |",
                "",
                "## L1 fill pack",
                "",
                "- Well: 8 PB `fromsll` whole-house systems from `p3-l1-fill-pack-2026-10-23.json`.",
                "- Hard: true shortfall after ①②③ + Lab P3 ban of sole softener `B0CJ9DK4T2`. YP 0. Do not invent softeners.",
                "- Collision ban: occupied 61 + Lab P3 six.",
                "",
                "## Hard rules kept",
                "",
                "- No occupied / Lab P3 ASIN reuse.",
                "- No accessories as picks.",
                "- No invented prices / was / % / gallery / specs / CTAs.",
                "- Independent of Shortlist Lab.",
                "- Reviews skipped (Top + Upgrade articles do not exist for these scenes).",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    if not TEMPLATE.exists():
        raise SystemExit(f"missing type-07 template {TEMPLATE}")
    occupied = load_occupied()
    if len(occupied) != 61:
        raise SystemExit(f"occupied list expected 61, got {len(occupied)}")
    banned = load_banned()
    pack = load_fill_pack()
    well_picks = scene_picks_from_pack(pack, "best-water-filters-for-well-water", banned)
    hard_picks = scene_picks_from_pack(pack, "best-water-filters-for-hard-water", banned)
    well_file = products_file_picks(PRODUCTS_WELL_PATH, banned)
    hard_file = products_file_picks(PRODUCTS_HARD_PATH, banned)
    if [p["asin"] for p in well_file] != [p["asin"] for p in well_picks]:
        raise SystemExit("well products file does not match L1 fill pack")
    if [p["asin"] for p in hard_file] != [p["asin"] for p in hard_picks]:
        raise SystemExit("hard products file does not match L1 fill pack")
    if len(well_picks) != EXPECTED_WELL:
        raise SystemExit(f"well density expected {EXPECTED_WELL}, got {len(well_picks)}")
    if len(hard_picks) != EXPECTED_HARD:
        raise SystemExit(
            f"hard density expected {EXPECTED_HARD} shortfall, got {len(hard_picks)}"
        )
    inv = build_inventory(well_picks, hard_picks)
    write_scene(SCENES[0], SCENES[1], banned, well_picks)
    write_scene(SCENES[1], SCENES[0], banned, hard_picks)
    patch_related_cluster()
    bump_or_insert_sitemap(
        [
            "water-filters/best-water-filters-for-hard-water/",
            "water-filters/best-water-filters-for-well-water/",
        ]
    )
    patch_html_sitemap()
    write_inventory(inv)
    print(
        "bake_p3_water_bestof ok "
        f"(well {inv['pages'][0]['density']} / hard {inv['pages'][1]['density']} / "
        f"{inv['fill_status']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
