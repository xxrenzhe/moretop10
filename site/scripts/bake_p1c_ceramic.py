#!/usr/bin/env python3
"""Bake P1c MT10 ceramic space heaters — new plural category + two scene best-ofs.

Draft only. No wrangler / no Live deploy. No Lab / RR / OL edits.

Hard rules:
  - Plural main category first from the healthy Lab ceramic feed (4 PB fromsll cards).
  - Honest density 4 — do not invent ASINs, prices, images, or was/%.
  - Scene-filter that shortlist (do not paste comparison order).
  - No accessories. No new review articles (MT10 reviews do not exist).
  - waiting_for_部署上线=yes.

Usage:
    python3 site/scripts/bake_p1c_ceramic.py
"""

from __future__ import annotations

import json
import re
import sys
from html import escape, unescape
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
from scaffold_day_add import COVER_COLORS, DATE, gradient_jpg  # noqa: E402
from seo_geo import LIVE, apply_hub_page, dumps_ld, rewrite_visible_jargon  # noqa: E402
from site_config import load_site_config  # noqa: E402

SLUG = "ceramic-space-heaters"
NAME = "Ceramic Space Heaters"
TEMPLATE = SITE / "humidifiers" / "best-humidifiers-for-bedrooms" / "index.html"
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P1c draft only. Do not merge. "
    "Do not Cloudflare Live deploy. -->"
)
TEMPLATE_LEFTOVER = (
    "What bedroom shoppers should optimize",
    "Our top humidifiers for this scene",
    'href="../../humidifiers/how-to-choose-a-humidifier/"',
    'href="../../humidifiers/premium-humidifier-alternatives/"',
    'href="../../humidifiers/levoit-bedroom-vs-homvana-cool-mist/"',
    "Best Humidifiers for Bedrooms (2026)",
)

# Lab ceramic feed (shortlistlab.io/data/shortlist-ceramic-space-heaters.json),
# checked ZIP 10001 ~2026-10-20. All four tracks are healthy PB fromsll.
# Comparison order = Lab role_sort. Scene pages reorder these four only.
FEED: list[dict[str, Any]] = [
    {
        "asin": "B0C6FFK1GV",
        "title": "DREO Space Heater, Portable Electric Heaters for Indoor Use with Remote",
        "brand": "DREO",
        "role": "Top pick",
        "price": "39.99",
        "price_displayed": "$39.99",
        "rating": 4.4,
        "review_count": 21514,
        "image": "https://m.media-amazon.com/images/I/81yZOnHdynL._AC_SL1500_.jpg",
        "affiliate_link": "https://pboost.me/C5qeREta?uid=fromsll",
        "availability": "In Stock",
        "why": (
            "DREO white PTC ceramic heater is Top pick for most bedrooms and offices "
            "that want 34dB quiet heat, a remote, ECO, child lock, and a 41–95°F "
            "thermostat from the listing we checked."
        ),
        "who_should_skip": "Skip if you need 70° oscillation, or the lowest verified price on this list (Best value Gold).",
        "feature_bullets": [
            "1500W PTC ceramic heat with remote, ECO, child lock, and a 41–95°F thermostat.",
            "Listing quotes 34dB quiet heat for bedrooms and offices.",
            "Tilt-detection tip-over protection; plug directly into a wall outlet.",
        ],
    },
    {
        "asin": "B097RG67QB",
        "title": "DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat",
        "brand": "DREO",
        "role": "Upgrade",
        "price": "44.94",
        "price_displayed": "$44.94",
        "rating": 4.6,
        "review_count": 29035,
        "image": "https://m.media-amazon.com/images/I/81oqGEsMPGL._AC_SL1500_.jpg",
        "affiliate_link": "https://pboost.me/O5qeSat9?uid=fromsll",
        "availability": "In Stock",
        "why": (
            "DREO Atom One is Upgrade when you want 70° wide-angle oscillation the "
            "Top pick does not list. The listing quotes 37.5dB and names garage, "
            "basement, and office coverage."
        ),
        "who_should_skip": "Skip if you do not need oscillation, or if 34dB bedside quiet is the priority.",
        "feature_bullets": [
            "70° wide-angle oscillation for bedroom, garage, basement, office, and desktop.",
            "1500W PTC heat with ECO and a 41–95°F digital thermostat.",
            "Listing quotes 37.5dB; Shield360 tip-over and overheat protection.",
        ],
    },
    {
        "asin": "B0C6FCKQML",
        "title": "DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat",
        "brand": "DREO",
        "role": "Best value",
        "price": "35.13",
        "price_displayed": "$35.13",
        "rating": 4.6,
        "review_count": 21514,
        "image": "https://m.media-amazon.com/images/I/81Ha7nqu+bL._AC_SL1500_.jpg",
        "affiliate_link": "https://pboost.me/j5qe7QvtD?uid=fromsll",
        "availability": "In Stock",
        "why": (
            "DREO Gold PTC ceramic heater is Best value as the lowest verified price "
            "here ($35.13) with the same 34dB / 1500W / 41–95°F remote stack the listing describes."
        ),
        "who_should_skip": "Skip if you want the white finish, or 70° oscillation for a larger sweep.",
        "feature_bullets": [
            "Same 34dB / 1500W / 41–95°F remote stack as the white Top pick.",
            "Lowest verified snapshot on this shortlist.",
            "Tip-over protection; plug directly into a wall outlet.",
        ],
    },
    {
        "asin": "B095PP1GZR",
        "title": "DREO Space Heaters for Indoor Use with Thermostat, 1500W Electric Heaters",
        "brand": "DREO",
        "role": "Premium",
        "price": "67.46",
        "price_displayed": "$67.46",
        "rating": 4.5,
        "review_count": 15432,
        "image": "https://m.media-amazon.com/images/I/818x7g6vSEL._AC_SL1500_.jpg",
        "affiliate_link": "https://pboost.me/N5qe9P4ta?uid=fromsll",
        "availability": "In Stock",
        "why": (
            "DREO large-room PTC heater is Premium for 270 sq.ft claimed coverage plus "
            "70° oscillation, 24-hour auto-off, and a 6ft flat cord from the listing."
        ),
        "who_should_skip": "Skip if you only need a compact bedroom or desk heater.",
        "feature_bullets": [
            "Listing claims 270 sq.ft heating coverage with 1500W PTC ceramic heat.",
            "70° wide-angle oscillation; listing names bedrooms, basements, and garages.",
            "34dB quiet heat, 24-hour auto-off, and a reminder not to use an extension cord.",
        ],
    },
]

CMP_ORDER = ["B0C6FFK1GV", "B097RG67QB", "B0C6FCKQML", "B095PP1GZR"]
SCENE_ASINS: dict[str, list[str]] = {
    "ceramic-large-rooms": ["B095PP1GZR", "B097RG67QB", "B0C6FFK1GV", "B0C6FCKQML"],
    "ceramic-garages": ["B097RG67QB", "B095PP1GZR", "B0C6FFK1GV", "B0C6FCKQML"],
}
BY_ASIN = {row["asin"]: row for row in FEED}


def _esc(text: str) -> str:
    return escape(text or "", quote=True)


def healthy_track(url: str | None) -> str | None:
    if is_empty_track(url):
        return None
    raw = (url or "").strip()
    if not is_allowed_track_host(raw):
        return None
    if classify_network(raw) == "pb":
        out = ensure_affiliate_uid(raw, "pb")
        return out if "uid=fromsll" in out else None
    return raw


def score_for(rating: float) -> str:
    return f"{float(rating) * 2:.1f}"


def l2_picks() -> list[dict[str, Any]]:
    picks = []
    for asin in CMP_ORDER:
        row = BY_ASIN[asin]
        track = healthy_track(row["affiliate_link"])
        if not track:
            raise SystemExit(f"unhealthy Lab track {asin}")
        rating = float(row["rating"])
        picks.append(
            {
                "asin": asin,
                "title": row["title"],
                "title_source": "lab_feed",
                "brand": row["brand"],
                "affiliate_network": "pb",
                "affiliate_link": track,
                "track_status": "ok",
                "l2_status": "ok",
                "price": row["price"],
                "price_raw": row["price_displayed"],
                "price_displayed": row["price_displayed"],
                "list_price": None,
                "image": row["image"],
                "availability": row["availability"],
                "in_stock": True,
                "rating": rating,
                "review_count": row["review_count"],
                "feature_bullets": row["feature_bullets"][:3],
                "l2": {
                    "ok": True,
                    "method": "lab_feed_zip_10001",
                    "zip": "10001",
                    "fetched_at": "2026-10-20T09:38:00+08:00",
                },
            }
        )
    return picks


def write_shortlist(picks: list[dict[str, Any]]) -> Path:
    notes = [
        f"P1c ceramic plural category {DATE}. waiting_for_部署上线=yes. No Live.",
        "Top 4 from healthy Lab ceramic feed (PB pboost.me?uid=fromsll). Density is honest — not padded to 10.",
        "No invented ASINs, prices, images, or was/%. list_price omitted on cards.",
        "No accessories. No new MT10 review articles (Lab reviews exist; MT10 reviews do not).",
        "Lifestyle cover remains a gradient placeholder.",
    ]
    payload = {
        "generated": DATE,
        "slug": SLUG,
        "name": NAME,
        "amazon_category": "Home & Kitchen",
        "density": len(picks),
        "density_target": 10,
        "density_shortfall": True,
        "status": "unpublished_scaffold",
        "waiting_for_部署上线": "yes",
        "inventory": "density_shortfall",
        "baked": True,
        "live": False,
        "publishable": False,
        "cta_label": "Check price",
        "cta_rule": "PB pboost.me keeps uid=fromsll when the Lab feed track is healthy; no invented hops",
        "l2": {
            "status": "ok",
            "method": "lab_feed_zip_10001",
            "ok_count": len(picks),
            "blocked": [],
        },
        "notes": notes,
        "dropped_accessory_asins": [],
        "picks": picks,
        "l2_ok_asins": [p["asin"] for p in picks],
        "l2_pending_asins": [],
        "track_pending_asins": [],
    }
    dest = DATA / f"shortlist-{SLUG}.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def patch_related_cluster() -> None:
    path = SITE / SLUG / "index.html"
    html = path.read_text(encoding="utf-8")
    cluster = (
        '<p class="landing-related-cluster"><strong>Also explore:</strong> '
        '<a href="comparison/">Full comparison chart</a> · '
        '<a href="reviews/">Reviews hub</a> · '
        '<a href="best-ceramic-space-heaters-for-large-rooms/">Best for large rooms</a> · '
        '<a href="best-ceramic-space-heaters-for-garages/">Best for garages</a></p>'
    )
    html, n = re.subn(
        r'<p class="landing-related-cluster">.*?</p>',
        cluster,
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("ceramic landing missing landing-related-cluster to patch")
    path.write_text(html, encoding="utf-8")


def polish_category_pages() -> None:
    cfg = load_site_config()
    cats = cfg["ALL_CATS"]
    cat = cfg["CATS_BY_SLUG"][SLUG]
    paths = {
        "landing": SITE / SLUG / "index.html",
        "comparison": SITE / SLUG / "comparison" / "index.html",
        "reviews": SITE / SLUG / "reviews" / "index.html",
    }
    cmp_html = paths["comparison"].read_text(encoding="utf-8")
    for kind, path in paths.items():
        out_rel = str(path.relative_to(SITE))
        prefix = rel_prefix(out_rel)
        text = path.read_text(encoding="utf-8")
        text = inject_nav_css(text)
        text = rewrite_non_home_nav(text, cats, prefix)
        text = rewrite_footer(text, cats, prefix)
        text = rewrite_compare_cta(text, prefix, SLUG, kind)
        text = rewrite_disclosure(text)
        text = apply_hub_page(
            text,
            kind=kind,
            cat=cat,
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
    patch_related_cluster()


def ul_from_amazon(src: str, size: int) -> str:
    return re.sub(r"\._AC_[A-Z]{2}\d+_\.", f"._AC_UL{size}_.", src)


def packshot_img(src: str, alt: str, width: int, sizes_px: str) -> str:
    alt_e = _esc(alt)
    if "m.media-amazon.com" in src:
        u160 = ul_from_amazon(src, 160)
        u320 = ul_from_amazon(src, 320)
        u480 = ul_from_amazon(src, 480)
        return (
            f'<img class="inline-pick-logo inline-packshot" src="{_esc(u320)}" '
            f'alt="{alt_e}" width="{width}" height="100" '
            f'srcset="{_esc(u160)} 160w, {_esc(u320)} 320w, {_esc(u480)} 480w" '
            f'sizes="{sizes_px}" loading="lazy" decoding="async" referrerpolicy="no-referrer"/>'
        )
    return (
        f'<img class="inline-pick-logo inline-packshot" src="{_esc(src)}" '
        f'alt="{alt_e}" width="{width}" height="100" loading="lazy" '
        f'decoding="async" referrerpolicy="no-referrer"/>'
    )


def visit_img(src: str, alt: str) -> str:
    html = packshot_img(src, alt, 140, "140px")
    return html.replace("inline-pick-logo inline-packshot", "bestof-visit-logo bestof-packshot")


def scene_pick(asin: str) -> dict[str, Any]:
    row = BY_ASIN[asin]
    track = healthy_track(row["affiliate_link"])
    if not track:
        raise SystemExit(f"unhealthy scene track {asin}")
    rating = float(row["rating"])
    return {
        "asin": asin,
        "name": row["title"],
        "full_name": row["title"],
        "cta": track,
        "image": row["image"],
        "thumb": row["image"],
        "alt": row["title"],
        "score": score_for(rating),
        "price": row["price"],
        "checked": f"Checked {DATE}",
        "tagline": row["why"],
        "feats": row["feature_bullets"][:3],
        "landing_role": row["role"],
        "who_should_skip": row["who_should_skip"],
        "review_slug": None,
        "review_href": "",
        "review_exists": False,
        "stars": str(row["rating"]),
        "track": track,
        "track_network": "pb",
    }


def ordered_scene(scene_key: str) -> list[dict[str, Any]]:
    return [scene_pick(asin) for asin in SCENE_ASINS[scene_key]]


def money(price: str | None) -> str:
    return f"${price}" if price else "snapshot on Check price"


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


def our_top_list(title: str, picks: list[dict]) -> str:
    items = []
    for i, p in enumerate(picks, start=1):
        pitch = (p.get("tagline") or "Confirm wattage, oscillation, noise, and tip-over protection on the retailer page.")[:110]
        if not pitch.endswith((".", "…")):
            pitch += "…"
        items.append(
            f"<li><strong>{i}. {_esc(p['name'])}</strong> — {_esc(pitch)} "
            f'<a href="../../{SLUG}/comparison/">See comparison ↓</a></li>'
        )
    return f'<section class="our-top-list"><h2>{_esc(title)}</h2><ol>{"".join(items)}</ol></section>'


def inline_picks(picks: list[dict]) -> str:
    cards = []
    for i, p in enumerate(picks[:3], start=1):
        score = p.get("score") or "—"
        pitch = (p.get("tagline") or "Confirm wattage, oscillation, noise, and tip-over protection on the retailer page.")[:140]
        cta = ""
        if p.get("track"):
            cta = (
                f'<a class="btn btn-cta-yellow btn-sm" href="{_esc(p["track"])}" '
                f'rel="sponsored noopener noreferrer" target="_blank">Check price</a> '
            )
        cards.append(
            '<article class="inline-pick-card">'
            f'<span class="inline-pick-rank">#{i}</span>'
            f'{packshot_img(p.get("thumb") or p.get("image") or "", p.get("alt") or p["name"], 120, "120px")}'
            f'<strong class="inline-pick-name">{_esc(p["name"])}</strong>'
            f'<span class="inline-pick-role">Score {escape(score)}</span>'
            f'<p class="inline-pick-pitch">{_esc(pitch)}</p>'
            f'<div class="inline-pick-actions">{cta}</div></article>'
        )
    return f'<div class="inline-picks" aria-label="Editor shortlist">{"".join(cards)}</div>'


def visit_stack(picks: list[dict]) -> str:
    cards = []
    for i, p in enumerate(picks, start=1):
        score = p.get("score") or "—"
        pitch = (p.get("tagline") or "Confirm wattage, oscillation, noise, and tip-over protection on the retailer page.")[:160]
        cta = ""
        if p.get("track"):
            cta = (
                f'<a class="btn btn-cta-yellow" href="{_esc(p["track"])}" '
                f'rel="sponsored noopener noreferrer" target="_blank"><span>Check price</span></a>'
            )
        cards.append(
            f'<section class="bestof-visit-card" id="bestof-pick-{i}">'
            f'<div class="bestof-visit-rank">{i}</div>'
            f'<div class="bestof-visit-main">'
            f'{visit_img(p.get("thumb") or p.get("image") or "", p.get("alt") or p["name"])}'
            f'<div class="bestof-visit-copy"><strong>{_esc(p["name"])}</strong>'
            f"<p>{_esc(pitch)}</p></div>"
            f'<span class="bestof-visit-score">{escape(score)}</span>'
            f"{cta}</div></section>"
        )
    return f'<div class="bestof-visit-stack">{"".join(cards)}</div>'


def role_block(label: str, pick: dict) -> str:
    score = pick.get("score") or "—"
    stars = pick.get("stars")
    rating = f" (User rating: {stars})" if stars else ""
    price = money(pick.get("price"))
    why = pick.get("tagline") or "Confirm wattage, oscillation, noise, and tip-over protection on the retailer page."
    feat = ""
    if pick.get("feats"):
        feat = " " + pick["feats"][0][:180]
    skip = pick.get("who_should_skip") or "Skip if this scene is not your job — use the parent comparison for the full shortlist."
    return (
        f"<p>### {_esc(pick['name'])} — {escape(label)}</p>\n"
        "<ul>"
        f"<li><strong>Editorial score:</strong> {escape(score)} / 10{escape(rating)}</li>"
        f"<li><strong>Snapshot price:</strong> {escape(price)}</li>"
        f"<li><strong>Why it fits this scene:</strong> {_esc(why)}{_esc(feat)}</li>"
        f"<li><strong>Who should skip:</strong> {_esc(skip)}</li>"
        "</ul>"
    )


def reviews_sidebar() -> str:
    return (
        '<aside class="ed-reviews-sidebar">\n  <h3>Editorial Reviews</h3>\n'
        "  <div class=\"ed-rev-list\"></div>\n"
        f'  <p class="sidebar-more"><a href="../../{SLUG}/reviews/">Reviews hub →</a></p>\n'
        "</aside>"
    )


def editors_picks(scene_path: str, scene_label: str) -> str:
    return (
        '<aside class="editors-picks-widget">\n  <h3>Editor\'s Picks</h3>\n'
        f'  <ul class="ed-picks-list">'
        f'<li><a href="../../{SLUG}/comparison/">Comparison chart</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../{SLUG}/reviews/">Reviews hub</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../{scene_path}/">{_esc(scene_label)}</a>'
        f'<span class="ed-pick-date">{DATE}</span></li></ul>\n'
        f'  <p class="sidebar-more"><a href="../../{SLUG}/">Category overview →</a></p>\n'
        "</aside>"
    )


def desc_trunc(text: str, n: int = 155) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    cut = text[: n - 1].rsplit(" ", 1)[0]
    return cut + "…"


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


def assert_clean_page(html: str, meta: dict) -> None:
    errors: list[str] = []
    if DRAFT_COMMENT not in html:
        errors.append("missing waiting_for_部署上线 draft comment")
    for leak in TEMPLATE_LEFTOVER:
        if leak in html:
            errors.append(f"template leftover {leak!r}")
    visits = html.count('class="bestof-visit-card"')
    if visits != 4:
        errors.append(f"visit cards={visits} (need 4)")
    if html.count('class="inline-pick-card"') != 3:
        errors.append("need 3 inline pick cards")
    for p in meta["picks"]:
        if not p.get("track"):
            errors.append(f"unhealthy track {p.get('asin')}")
        elif _esc(p["track"]) not in html and p["track"] not in html:
            errors.append(f"track URL missing for {p.get('asin')}")
        if p.get("name") and _esc(p["name"]) not in html:
            errors.append(f"name missing for {p.get('asin')}")
    if "waiting_for_部署上线" not in html:
        errors.append("draft gate string missing")
    if "10%" in html or "12%" in html or "$49.99" in html or "$74.99" in html:
        errors.append("invented or leftover was/% price leaked")
    start = html.find('<article class="landing-article">')
    side = html.find('<div class="editorial-side-stack">')
    chunk = html[start:side] if start >= 0 and side > start else ""
    if not chunk:
        errors.append("could not isolate landing-article")
    elif "What bedroom shoppers" in chunk or "how-to-choose-a-humidifier" in chunk:
        errors.append("bedroom leftover inside article")
    if errors:
        raise SystemExit(f"{meta['path']} bake assert failed: " + "; ".join(errors))


def clone_chrome(out_rel: str) -> str:
    html = TEMPLATE.read_text(encoding="utf-8")
    cfg = load_site_config()
    cats = cfg["ALL_CATS"]
    prefix = rel_prefix(out_rel)
    html = inject_nav_css(html)
    html = rewrite_non_home_nav(html, cats, prefix)
    html = rewrite_footer(html, cats, prefix)
    html = rewrite_disclosure(html)
    html = rewrite_compare_cta(html, prefix, SLUG, "page")
    return html


def replace_head(
    html: str,
    *,
    title: str,
    description: str,
    url: str,
    og_image: str,
    crumb_name: str,
    picks: list[dict],
    faqs: list[tuple[str, str]],
    page_desc: str,
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
            {"@type": "ListItem", "position": 2, "name": NAME, "item": f"{LIVE}/{SLUG}/"},
            {"@type": "ListItem", "position": 3, "name": crumb_name, "item": url},
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
                "name": p["name"],
                "url": f"{LIVE}/{SLUG}/comparison/#geo-{p['asin']}",
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
    html = html.replace("</head>", insert + "</head>", 1)
    return html


def replace_main(
    html: str,
    *,
    crumb: str,
    h1: str,
    article: str,
    scene_path: str,
    scene_label: str,
) -> str:
    html = re.sub(
        r'<nav class="breadcrumb">.*?</nav>',
        (
            f'<nav class="breadcrumb"><a href="../../index.html">Home</a> '
            f'<span class="sep">/</span> <a href="../../{SLUG}/">{_esc(NAME)}</a> '
            f'<span class="sep">/</span> <span>{_esc(crumb)}</span></nav>'
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
            f'<img class="lifestyle-photo" src="../../assets/img/lifestyle/cmp-hero-{SLUG}.jpg" '
            f'alt="" width="640" height="400" loading="lazy"/>'
        ),
        html,
        count=1,
    )
    html = re.sub(
        r'<span class="lifestyle-label">.*?</span>',
        f'<span class="lifestyle-label">{_esc(NAME)}</span>',
        html,
        count=1,
    )
    html = _replace_landing_article(html, article)
    html = re.sub(
        r'<div class="editorial-side-stack">.*?</div>\s*</div>\s*</div>\s*</main>',
        (
            '<div class="editorial-side-stack">\n        \n'
            f"{reviews_sidebar()}\n\n        \n"
            f"{editors_picks(scene_path, scene_label)}\n\n"
            "      </div>\n    </div>\n  </div>\n</main>"
        ),
        html,
        count=1,
        flags=re.S,
    )
    return html


def write_scene(meta: dict) -> Path:
    out_rel = meta["path"] + "index.html"
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = clone_chrome(out_rel)
    url = f"{LIVE}/{meta['path']}"
    html = replace_head(
        html,
        title=meta["title"],
        description=meta["description"],
        url=url,
        og_image=meta["picks"][0]["image"],
        crumb_name=meta["crumb_name"],
        picks=meta["picks"],
        faqs=meta["faqs"],
        page_desc=meta["page_desc"],
    )
    html = replace_main(
        html,
        crumb=meta["crumb"],
        h1=meta["h1"],
        article=meta["article"],
        scene_path=meta["path"].rstrip("/"),
        scene_label=meta["scene_label"],
    )
    html = rewrite_visible_jargon(html)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    assert_clean_page(html, meta)
    dest.write_text(html, encoding="utf-8")
    return dest


def page_large_rooms() -> dict:
    picks = ordered_scene("ceramic-large-rooms")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best ceramic space heater for a large room” mean on this page?",
            "It is an editorial slice of the ceramic space heaters shortlist for rooms "
            "that need claimed 270 sq.ft coverage or 70° oscillation — not a paid badge. "
            "We lead with the Premium large-room card and demote compact bedside units.",
        ),
        (
            "Who should skip this large-room slice?",
            "Skip it if you only need a quiet bedroom or desk heater. The compact white "
            f"and Gold cards ({money(picks[2].get('price'))} and {money(picks[3].get('price'))} "
            "snapshots) stay as neighbors. The parent comparison is the better start for small rooms.",
        ),
        (
            "Why isn’t the category Top pick first here?",
            f"The white DREO remote card is category Top pick at {money(picks[2].get('price'))} "
            "and 34dB, but it does not list 70° oscillation or 270 sq.ft coverage. "
            "This scene leads with the Premium large-room card that does.",
        ),
        (
            "What should I confirm before I buy?",
            "Confirm wattage, claimed coverage, oscillation, tip-over protection, and that "
            "you can plug directly into a wall outlet — listings warn against extension cords.",
        ),
    ]
    lede = (
        "<p>Large rooms punish compact bedside heaters that do not list oscillation or "
        "coverage. This best-of highlights ceramic space heaters on our shortlist aimed "
        "at living rooms and open layouts that need 270 sq.ft language or a 70° sweep — "
        "not a second copy of the category Top 4.</p>"
        "<p>We emphasize coverage and oscillation language already on the cards. "
        "We do not invent lab scores or square-footage beyond the shortlist copy.</p>"
        "<p>Rankings follow the same shortlist rules as our main ceramic space heaters "
        "comparison, reordered for this scene. Density is honest at 4.</p>"
    )
    densify = (
        f"<p>For a typical large room, start with the DREO large-room PTC heater "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The listing claims 270 sq.ft coverage plus 70° oscillation. "
        f"Step to Atom One ({money(upg.get('price'))} snapshot) when you want the same "
        f"70° sweep without the Premium price, or keep the compact white card when the "
        f"room is closer to a bedroom than a living room.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Scene filter, not chart paste:</strong> The category leads with the "
        "quiet white remote card; this page leads with the Premium 270 sq.ft card.</li>"
        "<li><strong>Oscillation beats brochure modes:</strong> 70° sweep on Premium and "
        "Atom One matters more than a bedside remote you will not use in a living room.</li>"
        "<li><strong>Upgrade is sweep without Premium price:</strong> Atom One lists garage, "
        "basement, and office coverage at a lower snapshot.</li>"
        "<li><strong>Compact 34dB units stay neighbors:</strong> White and Gold cards stay "
        "on this slice for small-room shoppers, not as large-room defaults.</li>"
        "</ul></section>"
        "<h2>Which large-room ceramic heater should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Quiet compact', picks[2])}"
        f"{role_block('Best value neighbor', picks[3])}"
        "<p>To evaluate how these large-room picks compare across the full shortlist, "
        f'check our <a href="../../{SLUG}/comparison/">ceramic space heaters comparison</a>.</p>'
        "<h2>How coverage changes the shortlist</h2>"
        "<ol>"
        "<li><strong>270 sq.ft Premium:</strong> The large-room card is the only listing "
        "that states 270 sq.ft coverage plus 70° oscillation.</li>"
        "<li><strong>70° Atom One:</strong> Same sweep language for garage, basement, and "
        "office without the 270 sq.ft claim.</li>"
        "<li><strong>Compact 34dB stack:</strong> White and Gold cards share the quiet "
        "remote stack. Skip them when the room is larger than a bedroom.</li>"
        "</ol>"
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}"
        f'<div class="gemini-shell-densify">{densify}</div>'
        f"{our_top_list('Our top 4 best ceramic space heaters for large rooms', picks)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        "<h2>What large-room shoppers should optimize</h2>"
        "<p>Claimed coverage and 70° oscillation beat a bedside remote you will not walk over to use.</p>"
        "<p>Match the listing’s square-footage language to the room you will actually run — "
        "not a whole-house brochure number.</p>"
        "<p>Plug directly into a wall outlet. Listings warn against extension cords.</p>"
        "<h2>Our top ceramic space heaters for this scene</h2>"
        "<p>Start with the Premium 270 sq.ft card, then scan Atom One if you want the same "
        "sweep at a lower snapshot.</p>"
        "<p>Pay for Premium coverage only when a compact bedroom heater cannot cover the footprint.</p>"
        "<p>White and Gold cards stay on the chart as neighbors, not as large-room defaults.</p>"
        "<h2>Quick shortlist from our ceramic chart</h2>"
        "<p>The cards below reuse the category tracks, images, and price snapshots, ordered for large rooms. "
        "Use Check price to confirm the live retailer offer.</p>"
        "<p>Scores map from retailer ratings when available. Roles are editorial labels, not paid awards.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of padding to ten. "
        "An empty slot beats a stale listing. Density is honest at 4.</p>"
        f"<p>Last verified {DATE}. Prices move — open Check price before you buy.</p>"
        "<p>We do not invent lab scores. We skip listings that are missing a title, gallery, or price snapshot.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        f'<a href="../../{SLUG}/">ceramic space heaters overview</a>, '
        f'<a href="../../{SLUG}/reviews/">reviews hub</a>, '
        f'<a href="../../{SLUG}/best-ceramic-space-heaters-for-garages/">best for garages</a>, and the '
        f'<a href="../../{SLUG}/comparison/">ceramic space heaters comparison</a>.</p>'
        f'<p class="article-cta-row"><a class="btn btn-primary" href="../../{SLUG}/comparison/">See current rankings</a></p>'
    )
    return {
        "path": f"{SLUG}/best-ceramic-space-heaters-for-large-rooms/",
        "title": "Best Ceramic Space Heaters for Large Rooms | MoreTop10",
        "h1": "Best Ceramic Space Heaters for Large Rooms (2026)",
        "crumb": "Best of",
        "crumb_name": "Best of",
        "scene_label": "Best for large rooms",
        "picks": picks,
        "faqs": faqs,
        "article": article,
        "description": (
            "Large rooms punish compact bedside heaters. This best-of highlights ceramic "
            "space heaters on our shortlist aimed at 270 sq.ft coverage or 70° oscillation."
        ),
        "page_desc": (
            "Editorial slice of ceramic space heaters for large rooms — 270 sq.ft coverage "
            "and 70° oscillation from the category shortlist, density honest at 4."
        ),
        "top": top,
        "upgrade": upg,
    }


def page_garages() -> dict:
    picks = ordered_scene("ceramic-garages")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best ceramic space heater for a garage” mean on this page?",
            "It is an editorial slice of the ceramic space heaters shortlist for garages "
            "and similar unfinished spaces — not a paid badge. We lead with cards whose "
            "listings already name garage coverage or 70° oscillation.",
        ),
        (
            "Who should skip this garage slice?",
            "Skip it if you only need a quiet bedroom heater. The compact white and Gold "
            "cards stay as neighbors. Confirm the listing still names garage use before you buy.",
        ),
        (
            "Why isn’t the category Top pick first here?",
            f"The white DREO remote card is category Top pick at {money(picks[2].get('price'))} "
            "and 34dB, but it does not list garage coverage or 70° oscillation. "
            "Atom One’s listing names garage, basement, and office, so this scene leads with that card.",
        ),
        (
            "What should I confirm before I buy?",
            "Confirm wattage, oscillation, tip-over protection, and that you can plug "
            "directly into a wall outlet — listings warn against extension cords.",
        ),
    ]
    lede = (
        "<p>Garages punish compact bedside heaters that never mention the space. "
        "This best-of highlights ceramic space heaters on our shortlist aimed at "
        "garages that need 70° oscillation or listed garage coverage — not a second "
        "copy of the category Top 4.</p>"
        "<p>We emphasize garage, basement, and oscillation language already on the cards. "
        "We do not invent lab scores or square-footage beyond the shortlist copy.</p>"
        "<p>Rankings follow the same shortlist rules as our main ceramic space heaters "
        "comparison, reordered for this scene. Density is honest at 4.</p>"
    )
    densify = (
        f"<p>For a typical garage, start with DREO Atom One "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The listing names garage, basement, and office coverage with 70° oscillation. "
        f"Step to the Premium large-room card ({money(upg.get('price'))} snapshot) when "
        f"you want the 270 sq.ft claim plus the same sweep, or keep a compact 34dB card "
        f"only for a small attached workshop corner.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Scene filter, not chart paste:</strong> The category leads with the "
        "quiet white remote card; this page leads with Atom One because that listing names garage.</li>"
        "<li><strong>Sweep and garage copy beat bedside quiet:</strong> 70° oscillation "
        "matters more than 34dB if the space is unfinished and open.</li>"
        "<li><strong>Upgrade is claimed coverage:</strong> The Premium card adds 270 sq.ft "
        "language and still names garages on the listing.</li>"
        "<li><strong>Compact 34dB units stay neighbors:</strong> White and Gold cards stay "
        "last so we do not invent garage claims they do not list.</li>"
        "</ul></section>"
        "<h2>Which garage ceramic heater should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Quiet compact', picks[2])}"
        f"{role_block('Best value neighbor', picks[3])}"
        "<p>To evaluate how these garage picks compare across the full shortlist, "
        f'check our <a href="../../{SLUG}/comparison/">ceramic space heaters comparison</a>.</p>'
        "<h2>How garage copy changes the shortlist</h2>"
        "<ol>"
        "<li><strong>Atom One:</strong> 70° oscillation and listing language for garage, "
        "basement, and office.</li>"
        "<li><strong>Premium 270 sq.ft:</strong> Same sweep plus claimed coverage; listing "
        "also names garages and basements.</li>"
        "<li><strong>Compact 34dB stack:</strong> White and Gold cards do not list garage "
        "coverage. They stay neighbors.</li>"
        "</ol>"
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}"
        f'<div class="gemini-shell-densify">{densify}</div>'
        f"{our_top_list('Our top 4 best ceramic space heaters for garages', picks)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        "<h2>What garage shoppers should optimize</h2>"
        "<p>Listed garage coverage and 70° oscillation beat a bedside remote you will not walk over to use.</p>"
        "<p>Tip-over protection and a wall outlet matter more in an unfinished space. "
        "Listings warn against extension cords.</p>"
        "<p>A 34dB compact card is a neighbor, not a garage default.</p>"
        "<h2>Our top ceramic space heaters for this scene</h2>"
        "<p>Start with Atom One for garage language and 70° sweep, then the Premium card "
        "if you want the 270 sq.ft claim.</p>"
        "<p>Pay for Premium coverage only when one compact heater cannot cover the footprint.</p>"
        "<p>White and Gold cards stay on the chart as neighbors, not as garage defaults.</p>"
        "<h2>Quick shortlist from our ceramic chart</h2>"
        "<p>The cards below reuse the category tracks, images, and price snapshots, ordered for garages. "
        "Use Check price to confirm the live retailer offer.</p>"
        "<p>Scores map from retailer ratings when available. Roles are editorial labels, not paid awards.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of padding to ten. "
        "An empty slot beats a stale listing. Density is honest at 4.</p>"
        f"<p>Last verified {DATE}. Prices move — open Check price before you buy.</p>"
        "<p>We do not invent lab scores. We skip listings that are missing a title, gallery, or price snapshot.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        f'<a href="../../{SLUG}/">ceramic space heaters overview</a>, '
        f'<a href="../../{SLUG}/reviews/">reviews hub</a>, '
        f'<a href="../../{SLUG}/best-ceramic-space-heaters-for-large-rooms/">best for large rooms</a>, and the '
        f'<a href="../../{SLUG}/comparison/">ceramic space heaters comparison</a>.</p>'
        f'<p class="article-cta-row"><a class="btn btn-primary" href="../../{SLUG}/comparison/">See current rankings</a></p>'
    )
    return {
        "path": f"{SLUG}/best-ceramic-space-heaters-for-garages/",
        "title": "Best Ceramic Space Heaters for Garages | MoreTop10",
        "h1": "Best Ceramic Space Heaters for Garages (2026)",
        "crumb": "Best of",
        "crumb_name": "Best of",
        "scene_label": "Best for garages",
        "picks": picks,
        "faqs": faqs,
        "article": article,
        "description": (
            "Garages punish compact bedside heaters. This best-of highlights ceramic "
            "space heaters on our shortlist aimed at garage coverage or 70° oscillation."
        ),
        "page_desc": (
            "Editorial slice of ceramic space heaters for garages — 70° oscillation and "
            "listed garage coverage from the category shortlist, density honest at 4."
        ),
        "top": top,
        "upgrade": upg,
    }


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


def write_inventory(rows: list[dict]) -> Path:
    dest = DATA / "p1c-ceramic-inventory-2026-10-23.json"
    dest.write_text(
        json.dumps({"date": DATE, "waiting_for_部署上线": True, "pages": rows}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    md = DATA / "p1c-ceramic-inventory-2026-10-23.md"
    lines = [
        "# P1c MT10 ceramic space heaters inventory (2026-10-23)",
        "",
        "**waiting_for_部署上线:** yes",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
        "",
        "## /ceramic-space-heaters/",
        "",
        "- Type: new plural main category (landing + comparison + reviews hub)",
        "- Density: 4 (honest Lab feed; not padded to 10)",
        "- Comparison order: B0C6FFK1GV, B097RG67QB, B0C6FCKQML, B095PP1GZR",
        "- Top pick: DREO Space Heater, Portable Electric Heaters for Indoor Use with Remote `B0C6FFK1GV`",
        "- Upgrade: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` (Atom One)",
        "- New reviews: none (MT10 review articles do not exist; Lab reviews are out of scope)",
        "- Tracks: B0C6FFK1GV=ok/pb, B097RG67QB=ok/pb, B0C6FCKQML=ok/pb, B095PP1GZR=ok/pb",
        "- Cards omit was/% even when the Lab feed listed a list price.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['path']}",
            "",
            f"- Density: {row['density']} (scene-reordered; not comparison order)",
            f"- Top pick: {row['top_pick']['name']} `{row['top_pick']['asin']}` review skipped (none on MT10)",
            f"- Upgrade: {row['upgrade']['name']} `{row['upgrade']['asin']}` review skipped (none on MT10)",
            "- New reviews: none",
            "- Tracks: "
            + ", ".join(
                f"{t['asin']}={'ok/' + (t['network'] or '?') if t['ok'] else 'MISSING'}"
                for t in row["tracks"]
            ),
            "",
        ]
    lines += [
        "## Shortfalls (honest)",
        "",
        "- Density is 4 healthy Lab feed cards, not a padded Top 10. No invented ASINs, prices, images, or was/%.",
        "- Role blocks keep the live densify `###` inside `<p>` and append a truncated feed feature sentence.",
        "- Neighbor slots include compact 34dB cards that do not list garage / 270 sq.ft so we do not invent claims.",
        "- Reviews: skipped. Existing type-07 chrome does not require new review HTML when reviews do not exist.",
        "- Lab `/shortlists/*` paths from the locked batch are out of scope (MT10 draft only).",
        "- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    return dest


def inventory_row(scene: str, path: str, picks: list[dict], top: dict, upg: dict) -> dict:
    return {
        "scene": scene,
        "path": "/" + path,
        "density": len(picks),
        "order_asins": [p["asin"] for p in picks],
        "top_pick": {
            "asin": top["asin"],
            "name": top["name"],
            "review": None,
            "review_exists": False,
            "track_network": top.get("track_network"),
            "track_ok": bool(top.get("track")),
        },
        "upgrade": {
            "asin": upg["asin"],
            "name": upg["name"],
            "review": None,
            "review_exists": False,
            "track_network": upg.get("track_network"),
            "track_ok": bool(upg.get("track")),
        },
        "tracks": [
            {
                "asin": p["asin"],
                "network": p.get("track_network"),
                "ok": bool(p.get("track")),
                "price": p.get("price"),
                "score": p.get("score"),
            }
            for p in picks
        ],
        "new_reviews": [],
        "reused_reviews": [],
    }


def patch_cover_map() -> None:
    dest = DATA / f"day-add-cover-map-{DATE}.json"
    if dest.exists():
        blob = json.loads(dest.read_text(encoding="utf-8"))
    else:
        blob = {"generated": DATE, "notes": [], "covers": {}}
    blob.setdefault("covers", {})[SLUG] = {
        "status": "placeholder",
        "lifestyle": f"assets/img/lifestyle/cmp-hero-{SLUG}.jpg",
        "product_photos": "Lab packshots on cards only — cover is a gradient placeholder",
        "todo": "Replace gradient placeholder with a real lifestyle cover after deploy. Do not invent product photos.",
    }
    dest.write_text(json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    picks = l2_picks()
    write_shortlist(picks)
    top, bot = COVER_COLORS[SLUG]
    gradient_jpg(SITE / "assets" / "img" / "lifestyle" / f"cmp-hero-{SLUG}.jpg", top, bot)
    write_pages(SLUG, NAME, picks)
    polish_category_pages()
    print(f"wrote {SLUG}/ landing + comparison + reviews hub (density={len(picks)})")

    metas = [page_large_rooms(), page_garages()]
    for meta in metas:
        dest = write_scene(meta)
        print(f"wrote {dest.relative_to(ROOT)}")

    sitemap_paths = [
        f"{SLUG}/",
        f"{SLUG}/comparison/",
        f"{SLUG}/reviews/",
        metas[0]["path"],
        metas[1]["path"],
    ]
    bump_or_insert_sitemap(sitemap_paths)
    patch_cover_map()
    inv = write_inventory(
        [
            inventory_row(
                "best ceramic space heater for large rooms",
                metas[0]["path"],
                metas[0]["picks"],
                metas[0]["top"],
                metas[0]["upgrade"],
            ),
            inventory_row(
                "best ceramic space heater for garages",
                metas[1]["path"],
                metas[1]["picks"],
                metas[1]["top"],
                metas[1]["upgrade"],
            ),
        ]
    )
    print(f"inventory {inv.relative_to(ROOT)}")
    print("bake_p1c_ceramic done (draft only; no Live)")


if __name__ == "__main__":
    main()
