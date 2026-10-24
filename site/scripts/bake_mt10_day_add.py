#!/usr/bin/env python3
"""Bake MT10 day-add new hubs (9 niches · 2026-10-24).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not scaffold 3d-printing-filament, floor-lamps, or chef-s-knives (brand_gate FAIL).
Do not touch open #54 (home nav) or #55 (stamp).

Pattern on tip: P2 new-hub (landing + comparison + reviews) + type-07 best-of.
Hubs stay unpublished_scaffold / published=false. Type-07 uses noindex like P4/P5b.
Hub/comparison/reviews keep index,follow after apply_hub_page so seo_geo_p1 stays green
(same as P2 unpublished hubs). Deploy gate is the draft PR + waiting_for_部署上线.

Hard rules:
  - Honest pack counts only. Do not invent ASINs to pad shortfalls.
  - Live CTA PB ?uid=fromsll. Do not rebind to YP.
  - No fake was/%. No Amazon gallery. No accessories as invented heroes.
  - Lab independent. Collision ban from occupied flat.

Usage:
    python3 site/scripts/bake_mt10_day_add.py
"""

from __future__ import annotations

import json
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

import apply_day_add_l2  # noqa: E402
import bake_p2_greenfield as p2  # noqa: E402
import scaffold_day_add  # noqa: E402
from affiliate_uid import (  # noqa: E402
    classify_network,
    ensure_affiliate_uid,
    is_allowed_track_host,
    is_empty_track,
)
from apply_day_add_l2 import write_pages  # noqa: E402
from build import rewrite_best_widget  # noqa: E402
from chrome import (  # noqa: E402
    inject_nav_css,
    rel_prefix,
    rewrite_compare_cta,
    rewrite_disclosure,
    rewrite_footer,
    rewrite_non_home_nav,
)
from scaffold_day_add import COVER_COLORS, gradient_jpg  # noqa: E402
from seo_geo import (  # noqa: E402
    LIVE,
    ROBOTS_NOINDEX,
    apply_hub_page,
    rewrite_visible_jargon,
    set_robots_meta,
)
from site_config import load_site_config  # noqa: E402

from stamp_guard import bake_stamp_date  # noqa: E402

DATE = bake_stamp_date("2026-10-24")
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. MT10 day-add draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-day-add-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-pack-new/mt10-day-add-fill-pack-2026-10-24/day-add-l1-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-pack-new/mt10-day-add-fill-pack-2026-10-24.json"),
    Path("/tmp/mt10-pack/mt10-day-add-fill-pack-2026-10-24.json"),
    DATA / "mt10-day-add-l1-fill-pack-2026-10-24.json",
)
PACK_INREPO = DATA / "mt10-day-add-l1-fill-pack-2026-10-24.json"
OCCUPIED_CANDIDATES = (
    Path("/workspace/shared/mt10-day-add-occupied-2026-10-24.json"),
    Path("/home/ubuntu/.cursor/projects/workspace/uploads/mt10-day-add-occupied-2026-10-24_1d25.json"),
    Path("/tmp/mt10-pack-new/mt10-day-add-occupied-2026-10-24.json"),
    Path("/tmp/mt10-pack/mt10-day-add-occupied-2026-10-24.json"),
    DATA / "mt10-day-add-occupied-2026-10-24.json",
)
OCCUPIED_INREPO = DATA / "mt10-day-add-occupied-2026-10-24.json"
REPORT_CANDIDATES = (
    Path("/workspace/shared/mt10-day-add-fill-report-2026-10-24.md"),
    Path("/home/ubuntu/.cursor/projects/workspace/uploads/mt10-day-add-fill-report-2026-10-24_8d16.md"),
    Path("/tmp/mt10-pack-new/mt10-day-add-fill-pack-2026-10-24/REPORT.md"),
    Path("/tmp/mt10-pack/mt10-day-add-fill-report-2026-10-24.md"),
    DATA / "mt10-day-add-l1-fill-report-2026-10-24.md",
)
REPORT_INREPO = DATA / "mt10-day-add-l1-fill-report-2026-10-24.md"

SKIP_BRAND_GATE = ("3d-printing-filament", "floor-lamps", "chef-s-knives")
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

NICHES: list[dict[str, Any]] = [
    {
        "slug": "pool-heat-pumps",
        "name": "Pool Heat Pumps",
        "amazon_category": "Patio, Lawn & Garden",
        "expected": 10,
        "scene_path": "best-pool-heat-pumps",
        "scene_label": "Best pool heat pumps",
        "scene_keyword": "best pool heat pumps",
        "scene_title": "Best Pool Heat Pumps",
        "scene_h1": "Best Pool Heat Pumps (2026)",
        "scene_desc": (
            "Shoppers comparing inverter pool heat pumps need BTU, voltage, and gallon "
            "coverage they can confirm on the listing. This best-of keeps the honest "
            "shortlist — we do not invent a padded Top 10."
        ),
        "job": "inverter pool heat pumps for above-ground and inground pools",
        "skip": (
            "Skip this slice if you want a pool cover, solar blanket, or a robotic "
            "cleaner. Those jobs are not this shortlist."
        ),
        "confirm": "Confirm BTU, voltage, and pool gallon rating on the retailer page.",
    },
    {
        "slug": "kitchen-rugs",
        "name": "Kitchen Rugs",
        "amazon_category": "Home & Kitchen",
        "expected": 10,
        "scene_path": "best-kitchen-rugs",
        "scene_label": "Best kitchen rugs",
        "scene_keyword": "best kitchen rugs",
        "scene_title": "Best Kitchen Rugs",
        "scene_h1": "Best Kitchen Rugs (2026)",
        "scene_desc": (
            "Kitchen rugs are a size, wash-method, and non-slip job. This best-of keeps "
            "the honest shortlist — we do not invent a padded Top 10."
        ),
        "job": "washable kitchen rugs and runners, not bath mats sold as kitchen décor",
        "skip": (
            "Skip this slice if you want a bath mat or a living-room area rug. Those "
            "jobs are not this shortlist."
        ),
        "confirm": "Confirm size, wash method, and non-slip backing on the retailer page.",
    },
    {
        "slug": "light-therapy",
        "name": "Light Therapy",
        "amazon_category": "Health & Household",
        "expected": 8,
        "scene_path": "best-light-therapy",
        "scene_label": "Best light therapy",
        "scene_keyword": "best light therapy",
        "scene_title": "Best Light Therapy",
        "scene_h1": "Best Light Therapy (2026)",
        "scene_desc": (
            "Red and near-infrared light therapy is a wavelength and form-factor job. "
            "Density is honest at 8 — we do not invent listings to pad to 10."
        ),
        "job": "red and near-infrared light therapy mats, panels, and masks",
        "skip": (
            "Skip this slice if you want a generic desk lamp or a sunrise alarm clock. "
            "Those jobs are not this shortlist."
        ),
        "confirm": "Confirm wavelength, session notes, and return window on the retailer page.",
    },
    {
        "slug": "bike-racks",
        "name": "Bike Racks",
        "amazon_category": "Sports & Outdoors",
        "expected": 10,
        "scene_path": "best-bike-racks",
        "scene_label": "Best bike racks",
        "scene_keyword": "best bike racks",
        "scene_title": "Best Bike Racks",
        "scene_h1": "Best Bike Racks (2026)",
        "scene_desc": (
            "Hitch-mount and garage bike racks need hitch class, bike count, and weight "
            "rating you can confirm on the listing. This best-of keeps the honest shortlist."
        ),
        "job": "hitch-mount and garage bike racks, not spare straps or hitch balls",
        "skip": (
            "Skip this slice if you want a spare hitch ball or a strap-only kit. Those "
            "jobs are not this shortlist."
        ),
        "confirm": "Confirm hitch class, bike count, and weight rating on the retailer page.",
    },
    {
        "slug": "nightstands",
        "name": "Nightstands",
        "amazon_category": "Home & Kitchen",
        "expected": 9,
        "scene_path": "best-nightstands",
        "scene_label": "Best nightstands",
        "scene_keyword": "best nightstands",
        "scene_title": "Best Nightstands",
        "scene_h1": "Best Nightstands (2026)",
        "scene_desc": (
            "Bedside nightstands are a size and drawer job. Density is honest at 9 — "
            "we do not invent listings to pad to 10."
        ),
        "job": "bedside nightstands, not mattress toppers or lamp-only accessories",
        "skip": (
            "Skip this slice if you want a dresser, a lamp, or a mattress topper. Those "
            "jobs are not this shortlist."
        ),
        "confirm": "Confirm dimensions, drawer count, and assembly notes on the retailer page.",
    },
    {
        "slug": "robotic-pool-cleaners",
        "name": "Robotic Pool Cleaners",
        "amazon_category": "Patio, Lawn & Garden",
        "expected": 8,
        "scene_path": "best-robotic-pool-cleaners",
        "scene_label": "Best robotic pool cleaners",
        "scene_keyword": "best robotic pool cleaners",
        "scene_title": "Best Robotic Pool Cleaners",
        "scene_h1": "Best Robotic Pool Cleaners (2026)",
        "scene_desc": (
            "Cordless robotic pool vacuums are a pool-type and runtime job. Density is "
            "honest at 8 — we do not invent listings to pad to 10."
        ),
        "job": "cordless robotic pool vacuums, not hoses, bags, or skimmer accessories",
        "skip": (
            "Skip this slice if you want a pool heat pump, a hose, or a skimmer bag. "
            "Those jobs are not this shortlist."
        ),
        "confirm": "Confirm pool type, cordless runtime, and coverage notes on the retailer page.",
    },
    {
        "slug": "barstools",
        "name": "Barstools",
        "amazon_category": "Home & Kitchen",
        "expected": 10,
        "scene_path": "best-barstools",
        "scene_label": "Best barstools",
        "scene_keyword": "best barstools",
        "scene_title": "Best Barstools",
        "scene_h1": "Best Barstools (2026)",
        "scene_desc": (
            "Counter-height and bar-height stools need seat height and set count you can "
            "confirm on the listing. This best-of keeps the honest shortlist."
        ),
        "job": "counter-height and bar-height stools, not table-only or cushion-only accessories",
        "skip": (
            "Skip this slice if you want a dining chair, a table, or a cushion-only kit. "
            "Those jobs are not this shortlist."
        ),
        "confirm": "Confirm seat height, set count, and weight rating on the retailer page.",
    },
    {
        "slug": "docking-stations",
        "name": "Docking Stations",
        "amazon_category": "Electronics",
        "expected": 8,
        "scene_path": "best-docking-stations",
        "scene_label": "Best docking stations",
        "scene_keyword": "best docking stations",
        "scene_title": "Best Docking Stations",
        "scene_h1": "Best Docking Stations (2026)",
        "scene_desc": (
            "USB-C and KVM docks are a monitor-count and port job. Density is honest at "
            "8 — we do not invent listings to pad to 10."
        ),
        "job": "USB-C and KVM laptop docking stations, not spare cables or dongles",
        "skip": (
            "Skip this slice if you want a spare HDMI cable or a single-port dongle. "
            "Those jobs are not this shortlist."
        ),
        "confirm": "Confirm monitor count, ports, and laptop compatibility on the retailer page.",
    },
    {
        "slug": "bookcases",
        "name": "Bookcases",
        "amazon_category": "Home & Kitchen",
        "expected": 10,
        "scene_path": "best-bookcases",
        "scene_label": "Best bookcases",
        "scene_keyword": "best bookcases",
        "scene_title": "Best Bookcases",
        "scene_h1": "Best Bookcases (2026)",
        "scene_desc": (
            "Tall bookcases and display cabinets need height and shelf rating you can "
            "confirm on the listing. This best-of keeps the honest shortlist."
        ),
        "job": "tall bookcases and display storage cabinets, not floating shelves or bookends",
        "skip": (
            "Skip this slice if you want a floating shelf, a bookend, or a TV stand. "
            "Those jobs are not this shortlist."
        ),
        "confirm": "Confirm height, shelf rating, and assembly notes on the retailer page.",
    },
]


def _esc(text: str) -> str:
    return escape(text or "", quote=True)


def first_existing(paths: tuple[Path, ...]) -> Path:
    for path in paths:
        if path.exists():
            return path
    raise SystemExit(f"missing file; looked in {', '.join(str(p) for p in paths)}")


def copy_sot() -> tuple[Path, Path, Path]:
    pack_src = first_existing(PACK_CANDIDATES)
    occupied_src = first_existing(OCCUPIED_CANDIDATES)
    report_src = first_existing(REPORT_CANDIDATES)
    if pack_src.resolve() != PACK_INREPO.resolve():
        PACK_INREPO.write_bytes(pack_src.read_bytes())
    if occupied_src.resolve() != OCCUPIED_INREPO.resolve():
        OCCUPIED_INREPO.write_bytes(occupied_src.read_bytes())
    if report_src.resolve() != REPORT_INREPO.resolve():
        REPORT_INREPO.write_bytes(report_src.read_bytes())
    return PACK_INREPO, OCCUPIED_INREPO, REPORT_INREPO


def load_occupied_flat(path: Path) -> set[str]:
    blob = json.loads(path.read_text(encoding="utf-8"))
    flat = blob.get("flat") or []
    return {str(a).strip().upper() for a in flat if a}


def healthy_track(url: str | None) -> str | None:
    if is_empty_track(url):
        return None
    raw = (url or "").strip()
    if not is_allowed_track_host(raw):
        return None
    if classify_network(raw) == "pb":
        out = ensure_affiliate_uid(raw, "pb")
        return out if "uid=fromsll" in out else None
    return None


def pick_from_pack(row: dict[str, Any]) -> dict[str, Any] | None:
    asin = (row.get("asin") or "").strip()
    title = (row.get("title") or "").strip()
    track = healthy_track(row.get("track_url"))
    if not asin or not title or not track:
        return None
    if asin.upper().startswith("B0X") and set(asin[2:]) <= set("X"):
        return None
    price = row.get("price")
    price_str = row.get("price_str")
    if price is not None and not price_str:
        price_str = f"${price}"
    return {
        "asin": asin,
        "title": title,
        "title_source": "l1_pack",
        "brand": (row.get("brand") or "").strip() or None,
        "role": (row.get("role") or "").strip() or None,
        "affiliate_network": "pb",
        "affiliate_link": track,
        "track_status": "ok",
        "l2_status": "l1_api",
        "price": f"{price}" if price is not None else None,
        "price_raw": price_str,
        "price_displayed": price_str,
        "image": None,
        "availability": row.get("availability"),
        "feature_bullets": [],
        "l2": {"ok": False, "method": "l1_pb_api", "status": "pending_listing_check"},
    }


def products_for(pack: dict[str, Any], slug: str) -> list[dict[str, Any]]:
    scene = (pack.get("scenes") or {}).get(slug) or {}
    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in scene.get("products") or []:
        pick = pick_from_pack(row)
        if not pick or pick["asin"] in seen:
            continue
        seen.add(pick["asin"])
        picks.append(pick)
    return picks


def write_shortlist(cat: dict[str, Any], picks: list[dict[str, Any]]) -> Path:
    slug = cat["slug"]
    n = len(picks)
    notes = [
        f"MT10 day-add L1 fill {slug} {DATE}. waiting_for_部署上线=yes. No Live.",
        "Healthy PB fromsll only. Density is honest — not padded to 10.",
        "Prices are L1 API snapshots from the fill pack. No invented listings, photos, or was/%. list_price omitted.",
        "Lifestyle cover is a gradient placeholder. Product photos wait for a later listing check.",
        "No accessories invented as heroes. Lab independent. No YP CTA rebind.",
    ]
    if n < 10:
        notes.append(f"Honest shortfall {n}/10 — do not invent listings to pad.")
    payload = {
        "generated": DATE,
        "slug": slug,
        "name": cat["name"],
        "amazon_category": cat["amazon_category"],
        "density": n,
        "density_target": 10,
        "density_shortfall": n < 10,
        "status": "unpublished_scaffold",
        "waiting_for_部署上线": "yes",
        "inventory": "l1_fill",
        "baked": True,
        "live": False,
        "publishable": False,
        "published": False,
        "cta_label": "Check price",
        "cta_rule": "PB pboost.me keeps uid=fromsll when a verified track exists; no invented hops; no YP rebind",
        "l2": {
            "status": "l1_api",
            "method": "l1_pb_fromsll_pack",
            "ok_count": n,
            "blocked": [],
        },
        "notes": notes,
        "dropped_accessory_asins": [],
        "picks": picks,
        "l2_ok_asins": [p["asin"] for p in picks],
        "l2_pending_asins": [],
        "track_pending_asins": [],
    }
    dest = DATA / f"shortlist-{slug}.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def polish_category_pages(cat: dict[str, Any]) -> None:
    cfg = load_site_config()
    cats = cfg["ALL_CATS"]
    slug = cat["slug"]
    site_cat = cfg["CATS_BY_SLUG"][slug]
    paths = {
        "landing": SITE / slug / "index.html",
        "comparison": SITE / slug / "comparison" / "index.html",
        "reviews": SITE / slug / "reviews" / "index.html",
    }
    cmp_html = paths["comparison"].read_text(encoding="utf-8")
    for kind, path in paths.items():
        out_rel = str(path.relative_to(SITE))
        prefix = rel_prefix(out_rel)
        text = path.read_text(encoding="utf-8")
        text = inject_nav_css(text)
        text = rewrite_non_home_nav(text, cats, prefix)
        text = rewrite_footer(text, cats, prefix)
        text = rewrite_compare_cta(text, prefix, slug, kind)
        text = rewrite_disclosure(text)
        text = apply_hub_page(
            text,
            kind=kind,
            cat=site_cat,
            cmp_html=cmp_html if kind != "comparison" else None,
            prefix=prefix,
            review_slug=None,
            site_root=SITE,
        )
        text = rewrite_best_widget(text)
        text = rewrite_visible_jargon(text)
        if DRAFT_COMMENT not in text:
            text = text.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
        path.write_text(text, encoding="utf-8")
    patch_related_cluster(slug, cat["scene_path"], cat["scene_label"])


def patch_related_cluster(slug: str, scene_path: str, scene_label: str) -> None:
    path = SITE / slug / "index.html"
    html = path.read_text(encoding="utf-8")
    cluster = (
        '<p class="landing-related-cluster"><strong>Also explore:</strong> '
        '<a href="comparison/">Full comparison chart</a> · '
        '<a href="reviews/">Reviews hub</a> · '
        f'<a href="{scene_path}/">{_esc(scene_label)}</a></p>'
    )
    html, n = re.subn(
        r'<p class="landing-related-cluster">.*?</p>',
        cluster,
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"{slug} landing missing landing-related-cluster to patch")
    path.write_text(html, encoding="utf-8")


def scene_faqs(cat: dict[str, Any], picks: list[dict[str, Any]]) -> list[tuple[str, str]]:
    name = cat["name"].lower()
    scene = cat["scene_keyword"]
    confirm = cat["confirm"]
    return [
        (
            f"What does “{scene}” mean on this page?",
            f"It is an editorial slice of the {name} shortlist for this job — not a paid badge. "
            "Cards here are the same verified tracks as the parent shortlist.",
        ),
        (
            "Who should skip this slice?",
            cat["skip"],
        ),
        (
            "What should I confirm before I buy?",
            confirm,
        ),
        (
            "Why are there no review articles or product photos?",
            "Top and Upgrade review pages do not exist on MoreTop10 yet, and this fill has no "
            "verified gallery. We do not invent reviews, photos, or discount badges.",
        ),
    ]


def scene_article(cat: dict[str, Any], picks: list[dict[str, Any]], faqs: list[tuple[str, str]]) -> str:
    slug = cat["slug"]
    name = cat["name"]
    scene = cat["scene_keyword"]
    confirm = cat["confirm"]
    n = len(picks)
    top = next((p for p in picks if p.get("role") == "Top pick"), picks[0])
    upgrade = next((p for p in picks if p.get("role") == "Upgrade"), None)
    who_bits = [
        f"<p>Start with <strong>{_esc(top['title'])}</strong>"
        + (f" ({_esc(top['price_displayed'])} snapshot)" if top.get("price_displayed") else "")
        + f" as the {escape((top.get('role') or 'lead').lower())} on this shortlist.</p>"
    ]
    if upgrade:
        who_bits.append(
            f"<p>Step up to <strong>{_esc(upgrade['title'])}</strong>"
            + (f" ({_esc(upgrade['price_displayed'])} snapshot)" if upgrade.get("price_displayed") else "")
            + " only if that listing’s extras match a job you will use.</p>"
        )
    shortfall = ""
    if n < 10:
        shortfall = (
            f"<li><strong>Honest shortfall:</strong> Density is {n}, not padded to 10. "
            "Empty slots stay empty.</li>"
        )
    return (
        f"<p>{_esc(cat['scene_desc'])}</p>"
        f"<p>Rankings follow the same shortlist rules as our main {escape(name.lower())} "
        f"comparison. Density is honest at {n} — we do not invent product listings, prices, images, or discounts.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Same verified tracks:</strong> Check price opens a verified retailer hop. "
        "Prices are a publish-time snapshot — confirm the live cart.</li>"
        "<li><strong>No accessories as heroes:</strong> Spare parts, cables, hoses, and "
        "mount-only kits stay off this shortlist.</li>"
        f"{shortfall}"
        "<li><strong>Reviews skipped:</strong> Top and Upgrade review articles do not exist on "
        "MoreTop10, so we do not invent them.</li>"
        "</ul></section>"
        f"<h2>Which {escape(scene)} should you pick?</h2>"
        f"{''.join(who_bits)}"
        f'<p>Use the <a href="../../{slug}/comparison/">{escape(name.lower())} comparison</a> '
        "to scan the same products in parent-category order.</p>"
        f"{p2.our_top_list_html(picks, slug, name, confirm)}"
        f"{p2.inline_picks_html(picks, slug, confirm)}"
        f"{p2.visit_cards_html(picks, confirm)}"
        "<h2>What shoppers should optimize</h2>"
        f"<p>{escape(confirm)}</p>"
        "<p>Skip accessories that cannot finish the buying job on their own.</p>"
        f"<h2>Our top {escape(name.lower())} for this scene</h2>"
        f"<p>The {n} cards above are the honest shortlist. Empty slots were not filled with guesses.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of padding to ten. "
        f"Density is honest at {n}.</p>"
        f"<p>Last verified {DATE}. We do not invent lab scores or product photos.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        f'<a href="../../{slug}/">{escape(name.lower())} overview</a>, '
        f'<a href="../../{slug}/reviews/">reviews hub</a>, and the '
        f'<a href="../../{slug}/comparison/">{escape(name.lower())} comparison</a>.</p>'
        f'<p class="article-cta-row"><a class="btn btn-primary" href="../../{slug}/comparison/">See current rankings</a></p>'
        f"{p2.faq_html(faqs)}"
    )


def write_bestof(cat: dict[str, Any], picks: list[dict[str, Any]]) -> dict[str, Any]:
    slug = cat["slug"]
    name = cat["name"]
    scene_path = f"{slug}/{cat['scene_path']}/"
    faqs = scene_faqs(cat, picks)
    n = len(picks)
    og = f"{LIVE}/assets/img/lifestyle/cmp-hero-{slug}.jpg"
    desc = (
        f"{cat['scene_title']} — {n} verified {name.lower()} with retail tracks. "
        "Honest density, no invented photos or discounts."
    )
    page_desc = (
        f"Editorial slice of {name.lower()} for {cat['scene_keyword']} — "
        f"honest density {n} from verified retail tracks."
    )
    meta = {
        "path": scene_path,
        "title": f"{cat['scene_title']} | MoreTop10",
        "h1": cat["scene_h1"],
        "density": n,
    }
    out_rel = scene_path + "index.html"
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = p2.clone_chrome(out_rel, slug)
    url = f"{LIVE}/{scene_path}"
    html = p2.replace_head(
        html,
        title=meta["title"],
        description=desc,
        url=url,
        og_image=og,
        crumb_name="Best of",
        cat_name=name,
        slug=slug,
        picks=picks,
        faqs=faqs,
        page_desc=page_desc,
    )
    html = p2.replace_main(
        html,
        crumb="Best of",
        h1=meta["h1"],
        article=scene_article(cat, picks, faqs),
        slug=slug,
        name=name,
        scene_path=cat["scene_path"],
        scene_label=cat["scene_label"],
    )
    html = rewrite_visible_jargon(html)
    html = set_robots_meta(html, ROBOTS_NOINDEX)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    errors: list[str] = []
    if DRAFT_COMMENT not in html:
        errors.append("missing draft comment")
    if f'name="robots" content="{ROBOTS_NOINDEX}"' not in html:
        errors.append("robots is not noindex,follow")
    for leak in TEMPLATE_LEFTOVER:
        if leak in html:
            errors.append(f"template leftover {leak!r}")
    if html.count('class="bestof-visit-card"') != n:
        errors.append(f"visit cards != {n}")
    if html.count('class="inline-pick-card"') != min(3, n):
        errors.append("inline picks mismatch")
    if "10%" in html or "12%" in html:
        errors.append("was/% leaked")
    if "amazon.com/dp/" in html or "m.media-amazon.com" in html:
        errors.append("Amazon gallery or hop")
    if "yeahpromos.com" in html:
        errors.append("YP rebind")
    if html.count("pboost.me") < n or "uid=fromsll" not in html:
        errors.append("missing PB fromsll tracks")
    if f"Density is honest at {n}" not in html:
        errors.append("missing honest density copy")
    if errors:
        raise SystemExit(f"{scene_path} bake assert failed: " + "; ".join(errors))
    dest.write_text(html, encoding="utf-8")
    return meta


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
    marker = (
        '<li><a href="../water-flossers/">Water Flossers</a> · '
        '<a href="../water-flossers/comparison/">Compare</a></li>'
    )
    extras: list[str] = []
    for cat in NICHES:
        row = (
            f'<li><a href="../{cat["slug"]}/">{_esc(cat["name"])}</a> · '
            f'<a href="../{cat["slug"]}/comparison/">Compare</a> · '
            f'<a href="../{cat["slug"]}/{cat["scene_path"]}/">{_esc(cat["scene_label"])}</a></li>'
        )
        if f'href="../{cat["slug"]}/"' not in html:
            extras.append(row)
    if extras:
        if marker not in html:
            raise SystemExit("sitemap/index.html missing water-flossers row to patch")
        html = html.replace(marker, marker + "\n" + "\n".join(extras), 1)
        path.write_text(html, encoding="utf-8")


def write_cover_map(slugs: list[str]) -> None:
    dest = DATA / f"day-add-cover-map-{DATE}.json"
    mapping = {}
    for slug in slugs:
        mapping[slug] = {
            "status": "placeholder",
            "lifestyle": f"assets/img/lifestyle/cmp-hero-{slug}.jpg",
            "product_photos": "none — do not invent packshots",
            "todo": "Replace gradient placeholder with a real lifestyle cover after deploy. Do not invent product photos.",
        }
    dest.write_text(
        json.dumps(
            {
                "generated": DATE,
                "notes": [
                    "Cover slots only. Gradient placeholders, not product photos.",
                    "waiting_for_部署上线=yes. No Live.",
                    "3d-printing-filament, floor-lamps, and chef-s-knives skipped (brand_gate FAIL).",
                ],
                "covers": mapping,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def write_inventory(pages: list[dict[str, Any]], by_slug: dict[str, list[dict[str, Any]]]) -> None:
    dest = DATA / f"mt10-day-add-inventory-{DATE}.json"
    counts = {cat["slug"]: len(by_slug[cat["slug"]]) for cat in NICHES}
    dest.write_text(
        json.dumps(
            {
                "date": DATE,
                "batch": "MT10-day-add",
                "waiting_for_部署上线": True,
                "published": False,
                "live": False,
                "merged": False,
                "independent_of_shortlist_lab": True,
                "do_not_touch": ["Lab", "RR", "OL", "#54 home nav", "#55 stamp"],
                "skipped": [
                    {
                        "path": "/3d-printing-filament/",
                        "reason": "brand_gate FAIL · R QIDI Technology-only — do not scaffold until multi-brand",
                    },
                    {
                        "path": "/floor-lamps/",
                        "reason": "brand_gate FAIL · Honeywell-only — do not scaffold until multi-brand",
                    },
                    {
                        "path": "/chef-s-knives/",
                        "reason": "brand_gate FAIL · Paudin-only — do not scaffold until multi-brand",
                    },
                ],
                "fill_pack": "site/data/mt10-day-add-l1-fill-pack-2026-10-24.json",
                "occupied": "site/data/mt10-day-add-occupied-2026-10-24.json",
                "counts": counts,
                "total_admitted": sum(counts.values()),
                "pages": pages,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    md = DATA / f"mt10-day-add-inventory-{DATE}.md"
    lines = [
        "# MT10 day-add inventory (2026-10-24)",
        "",
        "**waiting_for_部署上线:** yes",
        "**published:** false",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
        "**Pack:** `site/data/mt10-day-add-l1-fill-pack-2026-10-24.json`",
        "**Do not touch:** open #54 (home nav) and #55 (stamp).",
        "",
    ]
    for cat in NICHES:
        picks = by_slug[cat["slug"]]
        top = next((p for p in picks if p.get("role") == "Top pick"), None)
        upgrade = next((p for p in picks if p.get("role") == "Upgrade"), None)
        lines += [
            f"## /{cat['slug']}/",
            "",
            "- Type: new hub (landing + comparison + reviews hub) + type-07 best-of",
            f"- Density: {len(picks)} (honest; not padded to 10)",
            f"- Comparison order: {', '.join(p['asin'] for p in picks)}",
            f"- Top pick: {top['asin'] if top else 'none'}",
            f"- Upgrade: {upgrade['asin'] if upgrade else 'none'}",
            "- New reviews: none",
            f"- Tracks: {len(picks)} PB fromsll",
            "",
            f"## /{cat['slug']}/{cat['scene_path']}/",
            "",
            f"- Best-of: {cat['scene_keyword']}",
            f"- Density: {len(picks)}",
            f"- published=false / noindex on the type-07 page",
            "",
        ]
    lines += [
        "## Skipped (brand_gate FAIL)",
        "",
        "- `/3d-printing-filament/` — R QIDI Technology-only. Do not scaffold.",
        "- `/floor-lamps/` — Honeywell-only. Do not scaffold.",
        "- `/chef-s-knives/` — Paudin-only. Do not scaffold.",
        "",
        "## Shortfalls (honest)",
        "",
        "- light-therapy 8/10",
        "- nightstands 9/10",
        "- robotic-pool-cleaners 8/10",
        "- docking-stations 8/10",
        "- No invented galleries, was/%, or review articles.",
        "- Hub/comparison/reviews keep index,follow after apply_hub_page (P2 unpublished-hub pattern).",
        "- Type-07 best-of pages use noindex,follow (P4/P5b unpublished best-of pattern).",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")


def write_notes(by_slug: dict[str, list[dict[str, Any]]]) -> None:
    dest = ROOT / "notes" / f"mt10-day-add-draft-{DATE}.md"
    rows = []
    for i, cat in enumerate(NICHES, start=1):
        n = len(by_slug[cat["slug"]])
        fill = "filled" if n == 10 else f"filled honest stub ({n})"
        rows.append(
            f"| {i} | `/{cat['slug']}/` | **{n}** | `{fill}` (PB fromsll) |"
        )
    dest.write_text(
        "\n".join(
            [
                "# MT10 day-add draft — 2026-10-24",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / type-07 `noindex,follow`; hubs match P2 unpublished-hub chrome",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.",
                "**Do not touch:** open #54 (home nav) and #55 (stamp).",
                "",
                "## Lock",
                "",
                "User day-add 9 niches from the L1 fill pack. Three brand_gate fails skipped.",
                "",
                "| # | Path | Density | Fill |",
                "|---|------|---------|------|",
                *rows,
                "",
                "**Skipped:** `/3d-printing-filament/` — brand_gate FAIL · R QIDI Technology-only.",
                "**Skipped:** `/floor-lamps/` — brand_gate FAIL · Honeywell-only.",
                "**Skipped:** `/chef-s-knives/` — brand_gate FAIL · Paudin-only.",
                "",
                f"**Total:** {sum(len(v) for v in by_slug.values())} distinct ASINs.",
                "",
                "## L1 fill",
                "",
                "Applied pack `site/data/mt10-day-add-l1-fill-pack-2026-10-24.json` "
                "(report: `site/data/mt10-day-add-l1-fill-report-2026-10-24.md`). "
                "YP site 11767 was discovery-only. Live CTA stays PB `?uid=fromsll`.",
                "",
                "Occupied collision set: `site/data/mt10-day-add-occupied-2026-10-24.json` (772 ASINs). Pack hits = 0.",
                "",
                "```bash",
                "python3 site/scripts/bake_mt10_day_add.py",
                "python3 tests/mt10_day_add_assert.py",
                "```",
                "",
                "## Collision bans kept",
                "",
                "- Global occupied flat (772)",
                "- Brand-gate fails not scaffolded",
                "",
                "No accessories invented as heroes. No invented was / %. Reviews skipped. "
                "`list_price` from the pack is not rendered as a strike/was. Shortfalls are not padded.",
                "",
                "## Bake ≠ deploy",
                "",
                "Pages stay `published=false` until a later 部署上线 order. Do not merge. "
                "Do not Cloudflare Live / wrangler deploy. #54 home nav and #55 stamp were not touched.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def bind_runtime_dates() -> None:
    scaffold_day_add.DATE = DATE
    apply_day_add_l2.DATE = DATE
    p2.DATE = DATE
    p2.DRAFT_COMMENT = DRAFT_COMMENT


def delete_skip_paths() -> None:
    for slug in SKIP_BRAND_GATE:
        hub = SITE / slug
        if hub.exists():
            shutil.rmtree(hub)
        shortlist = DATA / f"shortlist-{slug}.json"
        if shortlist.exists():
            shortlist.unlink()
        cover = SITE / "assets" / "img" / "lifestyle" / f"cmp-hero-{slug}.jpg"
        if cover.exists():
            cover.unlink()


def assert_skips_absent() -> None:
    for slug in SKIP_BRAND_GATE:
        if (SITE / slug / "index.html").exists():
            raise SystemExit(f"brand_gate skip created {slug}/ — remove it")
        if (DATA / f"shortlist-{slug}.json").exists():
            raise SystemExit(f"brand_gate skip wrote shortlist-{slug}.json — remove it")


def main() -> None:
    bind_runtime_dates()
    delete_skip_paths()
    pack_path, occupied_path, _report = copy_sot()
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    occupied = load_occupied_flat(occupied_path)
    if len(occupied) < 700:
        raise SystemExit(f"occupied flat too small: {len(occupied)}")

    sitemap_paths: list[str] = []
    inv_pages: list[dict[str, Any]] = []
    slugs: list[str] = []
    by_slug: dict[str, list[dict[str, Any]]] = {}

    for cat in NICHES:
        slug = cat["slug"]
        if slug in SKIP_BRAND_GATE:
            raise SystemExit(f"{slug} is a brand_gate skip — do not bake")
        picks = products_for(pack, slug)
        expected = cat["expected"]
        if len(picks) != expected:
            raise SystemExit(f"{slug}: pack admitted {len(picks)} healthy tracks, expected {expected}")
        hits = [p["asin"] for p in picks if p["asin"].upper() in occupied]
        if hits:
            raise SystemExit(f"{slug} collision with occupied flat: {hits}")
        by_slug[slug] = picks
        slugs.append(slug)
        write_shortlist(cat, picks)
        top, bot = COVER_COLORS[slug]
        gradient_jpg(SITE / "assets" / "img" / "lifestyle" / f"cmp-hero-{slug}.jpg", top, bot)
        write_pages(slug, cat["name"], picks)
        polish_category_pages(cat)
        print(f"wrote {slug}/ landing + comparison + reviews hub (density={len(picks)})")
        meta = write_bestof(cat, picks)
        print(f"wrote {meta['path']}")
        sitemap_paths.extend(
            [
                f"{slug}/",
                f"{slug}/comparison/",
                f"{slug}/reviews/",
                meta["path"],
            ]
        )
        inv_pages.append(
            {
                "path": f"/{slug}/",
                "best_of": f"/{slug}/{cat['scene_path']}/",
                "density": len(picks),
                "order_asins": [p["asin"] for p in picks],
                "published": False,
            }
        )

    assert_skips_absent()
    bump_or_insert_sitemap(sitemap_paths)
    patch_html_sitemap()
    write_cover_map(slugs)
    write_inventory(inv_pages, by_slug)
    write_notes(by_slug)
    print("bake_mt10_day_add ok (draft only; no Live)")
    for slug, picks in by_slug.items():
        print(f"  {slug}: {len(picks)}")


if __name__ == "__main__":
    main()
