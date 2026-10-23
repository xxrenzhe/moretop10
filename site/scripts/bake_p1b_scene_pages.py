#!/usr/bin/env python3
"""Bake P1b MT10 scenario best-of pages from in-repo comparison + landing cards.

Draft only. No wrangler / no Live deploy. No Lab / RR / OL edits.

Hard rules:
  - Scene-filter existing plural-category shortlists (do not paste chart order).
  - Healthy PB tracks only; PB keep uid=fromsll.
  - No accessories; no invented prices, images, or was-prices.
  - Deep reviews: reuse existing Top pick + Upgrade HTML; do not invent SKUs.

Usage:
    python3 site/scripts/bake_p1b_scene_pages.py
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
from seo_geo import (  # noqa: E402
    LIVE,
    dumps_ld,
    rewrite_visible_jargon,
    slug_from_href,
)
from site_config import load_site_config  # noqa: E402

DATE = "2026-10-23"
TEMPLATE = SITE / "humidifiers" / "best-humidifiers-for-bedrooms" / "index.html"
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P1b draft only. Do not merge. "
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
_CARD_RE = re.compile(r'<article class="product-card"[^>]*>.*?</article>', re.S)
_PICK_RE = re.compile(
    r'<section class="landing-pick" id="(pick-\d+)">(.*?)</section>',
    re.S,
)
_ATTR_RE = re.compile(
    r'\b(data-asin|data-position|data-product-name|data-img|data-cta)="([^"]*)"'
)

# Explicit scene order — not comparison rank, not landing 1–10.
SCENE_ASINS: dict[str, list[str]] = {
    "air-purifiers-allergies": [
        "B0GXKSC38S",  # Vital Pet Pro — dander + TVOC/PM2.5 incl. smoke
        "B07X25BNBR",  # LEVOIT bedroom — 3-stage dust/pollen
        "B0F2G5DPJN",  # PM10 — 4-layer pollen/dust/dander/smoke
        "B08BR1CR78",  # LV-H128 — allergy-symptoms copy + pollen CADR 52
        "B09LMF648R",  # dorm — pet dander + pollutants
        "B0CXJ97TV1",  # MOOKA HEPA bedroom
        "B0F32TGRMR",  # PM20 4-layer
        "B0FS68R44C",  # AP10 dander
        "B0FK53C7B9",  # AEOCKY neighbor (filter longevity)
        "B0H4SVJ2RF",  # compact neighbor
    ],
    "air-purifiers-mold": [
        "B0CXJ97TV1",  # MOOKA HEPA 3-stage — Top (no card names mold)
        "B0F32TGRMR",  # PM20 0.1μm 4-layer Upgrade
        "B0F2G5DPJN",  # PM10 same 4-layer
        "B0FK53C7B9",  # AEOCKY year-change 5-layer (cmp #1 demoted)
        "B0H4SVJ2RF",  # Energy Star continuous
        "B0GXKSC38S",  # Vital Pet carbon
        "B07X25BNBR",  # bedroom 3-stage
        "B09LMF648R",  # fine pollutants
        "B0FS68R44C",  # AP10
        "B08BR1CR78",  # 47 ft2 last
    ],
    "air-purifiers-bedrooms": [
        "B07X25BNBR",  # LEVOIT small bedroom quiet 24 dB — Top
        "B0CXJ97TV1",  # MOOKA bedroom large — Upgrade
        "B08BR1CR78",  # dorm / babies-woken copy
        "B09LMF648R",  # quiet dorm
        "B0H4SVJ2RF",  # 34 dBA compact
        "B0GXKSC38S",  # Vital Pet
        "B0FK53C7B9",  # AEOCKY
        "B0FS68R44C",  # AP10
        "B0F2G5DPJN",  # PM10
        "B0F32TGRMR",  # 3-in-1 last
    ],
    "air-purifiers-dust": [
        "B07X25BNBR",  # pre-filter hair + dust/pollen — Top
        "B0FS68R44C",  # AP10 hair and dust — Upgrade
        "B09LMF648R",  # lint, hair, dander
        "B0F2G5DPJN",  # dust in 4-layer
        "B0FK53C7B9",  # Dust CADR 240
        "B0CXJ97TV1",  # HEPA
        "B08BR1CR78",  # dust CADR 41
        "B0GXKSC38S",  # Vital Pet
        "B0F32TGRMR",  # PM20
        "B0H4SVJ2RF",  # compact
    ],
    "air-purifiers-smoke": [
        "B0F2G5DPJN",  # PM10 4-layer names smoke — Top
        "B0GXKSC38S",  # 140 g carbon + smoke sensors — Upgrade
        "B09LMF648R",  # smoke particles + neutralize smoke
        "B0FK53C7B9",  # Smoke CADR 224
        "B0F32TGRMR",  # PM20 4-layer smoke
        "B08BR1CR78",  # smoke CADR 30 (tiny room)
        "B0CXJ97TV1",  # HEPA
        "B0FS68R44C",  # AP10
        "B07X25BNBR",  # bedroom
        "B0H4SVJ2RF",  # compact
    ],
    "air-purifiers-large-rooms": [
        "B0CXJ97TV1",  # MOOKA 2200 ft² — Top
        "B0F32TGRMR",  # PM20 large-room Premium — Upgrade
        "B0FK53C7B9",  # AEOCKY 2300 (cmp #1 demoted)
        "B0F2G5DPJN",  # PM10 large
        "B0GXKSC38S",  # Vital Pet large-room title
        "B0H4SVJ2RF",  # compact / large-room title
        "B0FS68R44C",  # AP10
        "B07X25BNBR",  # small-room neighbor
        "B09LMF648R",  # dorm
        "B08BR1CR78",  # 47 ft2 last
    ],
    "humidifiers-babies": [
        "B0DF567NW8",  # Homvana 3.6L Baby / nursery — Top
        "B0C369CCDY",  # Homvana 7L nursery in title — Upgrade
        "B0DSP78FG4",  # Homvana top-fill cool mist
        "B0C2GKJ9RT",  # LEVOIT 3L Dual 200S quiet bedroom
        "B0B1DQ8KV3",  # LEVOIT bedroom (category #1 demoted)
        "B0C4GHYH2M",  # LEVOIT 6L
        "B09C24TYGQ",  # Classic300S
        "B095KGXPW5",  # LV600S
        "B0BLV8BM5J",  # OasisMist 10L
        "B0GSR397Z7",  # Dreame H40 mist-free neighbor
    ],
    "standing-desks-home-office": [
        "B0B68QSN6Y",  # 60×30 drawers — landing Top pick for home offices
        "B0GD75Y6SC",  # 63×37 dual-monitor Upgrade
        "B0GWKF4M1T",  # CubiCubi 55×30
        "B0FJXWQ3Y7",  # 55×24
        "B0F8MHPVPH",  # 48×24 Best value
        "B0GCNG1PK8",  # 63×37 sibling
        "B0GWKCG1SS",  # CubiCubi 40×24 (cmp #1 demoted)
        "B0GCNPGWPL",  # 83×37 freight
        "B0CJ313Q9P",  # glass 48
        "B0H4LCLJXL",  # 32×19 last
    ],
}

def _esc(text: str) -> str:
    return escape(text or "", quote=True)


def _plain(html_text: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", " ", html_text or ""))
    return re.sub(r"\s+", " ", text).strip()


def _fix_asset_prefix(src: str) -> str:
    if not src:
        return src
    if src.startswith("http://") or src.startswith("https://"):
        return src
    src = re.sub(r"^(\.\./)+assets/", "../../assets/", src)
    if src.startswith("assets/"):
        return "../../" + src
    return src


def healthy_track(url: str | None) -> str | None:
    if is_empty_track(url):
        return None
    raw = (url or "").strip()
    if not is_allowed_track_host(raw):
        return None
    if classify_network(raw) == "pb":
        out = ensure_affiliate_uid(raw, "pb")
        return out if "uid=fromsll" in out else None
    return raw  # YP / Amazon maas as-is


def ul_from_amazon(src: str, size: int) -> str:
    return re.sub(r"\._AC_[A-Z]{2}\d+_\.", f"._AC_UL{size}_.", src)


def packshot_img(src: str, alt: str, width: int, sizes_px: str) -> str:
    src = _fix_asset_prefix(src)
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


def extract_comparison_cards(html_text: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for i, card in enumerate(_CARD_RE.findall(html_text), start=1):
        attrs = {k: unescape(v) for k, v in _ATTR_RE.findall(card)}
        asin = (attrs.get("data-asin") or "").strip()
        if not asin:
            continue
        name = (attrs.get("data-product-name") or "").strip()
        nm = re.search(r'class="pc-name"[^>]*>([^<]+)', card)
        full_name = unescape(nm.group(1)).strip() if nm else name
        img_m = re.search(r'<img class="pc-logo[^"]*"[^>]+src="([^"]+)"', card)
        alt_m = re.search(r'<img class="pc-logo[^"]*"[^>]+alt="([^"]*)"', card)
        score_m = re.search(r'class="avg-score">([0-9.]+)<', card)
        price_m = re.search(
            r'class="pc-price-value">\$([0-9][0-9,]*(?:\.[0-9]{2})?)<', card
        )
        checked_m = re.search(r'class="pc-price-checked">([^<]+)<', card)
        tag_m = re.search(r"class=['\"]pc-tagline['\"]>([^<]+)", card)
        review_slug = None
        for href in re.findall(r'href="([^"]+)"', card):
            if "/reviews/" in href and not href.rstrip("/").endswith("/reviews"):
                review_slug = slug_from_href(href)
                if review_slug:
                    break
        stars_m = re.search(r'aria-label="([0-9.]+) out of 5"', card)
        out[asin] = {
            "asin": asin,
            "name": name or full_name,
            "full_name": full_name or name,
            "cta": attrs.get("data-cta") or "",
            "image": attrs.get("data-img") or (img_m.group(1) if img_m else ""),
            "thumb": img_m.group(1) if img_m else attrs.get("data-img") or "",
            "alt": unescape(alt_m.group(1)) if alt_m else full_name or name,
            "score": score_m.group(1) if score_m else "",
            "price": price_m.group(1).replace(",", "") if price_m else None,
            "checked": (checked_m.group(1) if checked_m else "").strip(),
            "tagline": unescape(tag_m.group(1)).strip() if tag_m else "",
            "review_slug": review_slug,
            "cmp_position": int(attrs.get("data-position") or i),
            "stars": stars_m.group(1) if stars_m else None,
        }
    return out


def extract_landing_picks(html_text: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for pick_id, body in _PICK_RE.findall(html_text):
        asin_m = re.search(r'id="geo-([A-Z0-9]{10})"', body)
        if not asin_m:
            continue
        asin = asin_m.group(1)
        hm = re.search(
            r"<h2>(?:<span class=\"landing-pick-num\">\d+</span>\s*)?(.*?)</h2>",
            body,
            re.S,
        )
        name = _plain(hm.group(1)) if hm else ""
        tag = re.search(r'class="landing-pick-tagline">(.*?)</p>', body, re.S)
        feats = [_plain(x) for x in re.findall(r"<li>(.*?)</li>", body, re.S)]
        role = ""
        tagline = _plain(tag.group(1)) if tag else ""
        blob = f"{name} {tagline} {' '.join(feats)}".lower()
        if "top pick" in blob:
            role = "Top pick"
        elif "upgrade" in blob:
            role = "Upgrade"
        elif "best value" in blob:
            role = "Best value"
        elif "premium" in blob:
            role = "Premium"
        out[asin] = {
            "landing_id": pick_id,
            "landing_name": name,
            "tagline": tagline,
            "feats": feats[:4],
            "landing_role": role,
        }
    return out


def merge_pick(asin: str, cmp: dict, land: dict | None) -> dict[str, Any]:
    track = healthy_track(cmp.get("cta"))
    return {
        **cmp,
        "tagline": (land or {}).get("tagline") or cmp.get("tagline") or "",
        "feats": (land or {}).get("feats") or [],
        "landing_role": (land or {}).get("landing_role") or "",
        "track": track,
        "track_network": classify_network(track) if track else None,
    }


def load_category(slug: str) -> tuple[dict[str, dict], dict[str, dict]]:
    cmp_html = (SITE / slug / "comparison" / "index.html").read_text(encoding="utf-8")
    land_html = (SITE / slug / "index.html").read_text(encoding="utf-8")
    return extract_comparison_cards(cmp_html), extract_landing_picks(land_html)


def ordered_picks(slug: str, scene_key: str) -> list[dict[str, Any]]:
    cmp, land = load_category(slug)
    picks: list[dict[str, Any]] = []
    for asin in SCENE_ASINS[scene_key]:
        if asin not in cmp:
            raise SystemExit(f"missing comparison card {asin} in {slug}")
        row = merge_pick(asin, cmp[asin], land.get(asin))
        row["review_href"] = (
            f"../../{slug}/reviews/{row['review_slug']}/" if row.get("review_slug") else ""
        )
        row["review_exists"] = bool(
            row.get("review_slug")
            and (SITE / slug / "reviews" / row["review_slug"] / "index.html").exists()
        )
        picks.append(row)
    return picks


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


def our_top_list(title: str, picks: list[dict], slug: str) -> str:
    items = []
    for i, p in enumerate(picks, start=1):
        pitch = (p.get("tagline") or "Confirm current specs, stock, and returns on the retailer page.")[:110]
        if not pitch.endswith((".", "…")):
            pitch += "…"
        href = p["review_href"] if p.get("review_exists") else f"../../{slug}/comparison/"
        label = "View details ↓" if p.get("review_exists") else "See comparison ↓"
        items.append(
            f"<li><strong>{i}. {_esc(p['name'])}</strong> — {_esc(pitch)} "
            f'<a href="{_esc(href)}">{label}</a></li>'
        )
    return f'<section class="our-top-list"><h2>{_esc(title)}</h2><ol>{"".join(items)}</ol></section>'


def inline_picks(picks: list[dict]) -> str:
    cards = []
    for i, p in enumerate(picks[:3], start=1):
        score = p.get("score") or "—"
        pitch = (p.get("tagline") or "Confirm current specs, stock, and returns on the retailer page.")[:140]
        cta = ""
        if p.get("track"):
            cta = (
                f'<a class="btn btn-cta-yellow btn-sm" href="{_esc(p["track"])}" '
                f'rel="sponsored noopener noreferrer" target="_blank">Check price</a> '
            )
        rev = (
            f'<a href="{_esc(p["review_href"])}">Read review</a>'
            if p.get("review_exists")
            else ""
        )
        cards.append(
            '<article class="inline-pick-card">'
            f'<span class="inline-pick-rank">#{i}</span>'
            f'{packshot_img(p.get("thumb") or p.get("image") or "", p.get("alt") or p["name"], 120, "120px")}'
            f'<strong class="inline-pick-name">{_esc(p["name"])}</strong>'
            f'<span class="inline-pick-role">Score {escape(score)}</span>'
            f'<p class="inline-pick-pitch">{_esc(pitch)}</p>'
            f'<div class="inline-pick-actions">{cta}{rev}</div></article>'
        )
    return f'<div class="inline-picks" aria-label="Editor shortlist">{"".join(cards)}</div>'


def visit_stack(picks: list[dict]) -> str:
    cards = []
    for i, p in enumerate(picks, start=1):
        score = p.get("score") or "—"
        pitch = (p.get("tagline") or "Confirm current specs, stock, and returns on the retailer page.")[:160]
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
    why = pick.get("tagline") or "Confirm current specs, stock, and returns on the retailer page."
    feat = ""
    if pick.get("feats"):
        feat = " " + pick["feats"][0][:180]
    return (
        f"<p>### {_esc(pick['name'])} — {escape(label)}</p>\n"
        "<ul>"
        f"<li><strong>Editorial score:</strong> {escape(score)} / 10{escape(rating)}</li>"
        f"<li><strong>Snapshot price:</strong> {escape(price)}</li>"
        f"<li><strong>Why it fits this scene:</strong> {_esc(why)}{_esc(feat)}</li>"
        "<li><strong>Who should skip:</strong> Skip if this scene is not your job — "
        "use the parent comparison for the full shortlist.</li>"
        "</ul>"
    )


def reviews_sidebar(picks: list[dict]) -> str:
    rows = []
    for p in picks[:5]:
        if not p.get("review_exists"):
            continue
        rows.append(
            '<div class="ed-rev-row"><div class="ed-rev-text">'
            f"<strong>{_esc(p['name'])}</strong>"
            f'<a href="{_esc(p["review_href"])}">Read Review</a></div></div>'
        )
    return (
        '<aside class="ed-reviews-sidebar">\n  <h3>Editorial Reviews</h3>\n'
        f'  <div class="ed-rev-list">{"".join(rows)}</div>\n</aside>'
    )


def editors_picks(slug: str, scene_path: str, scene_label: str) -> str:
    return (
        '<aside class="editors-picks-widget">\n  <h3>Editor\'s Picks</h3>\n'
        f'  <ul class="ed-picks-list">'
        f'<li><a href="../../{slug}/comparison/">Comparison chart</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../{slug}/reviews/">Reviews hub</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../{scene_path}/">{_esc(scene_label)}</a>'
        f'<span class="ed-pick-date">{DATE}</span></li></ul>\n'
        f'  <p class="sidebar-more"><a href="../../{slug}/">Category overview →</a></p>\n'
        "</aside>"
    )


def desc_trunc(text: str, n: int = 155) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    cut = text[: n - 1].rsplit(" ", 1)[0]
    return cut + "…"


def _replace_landing_article(html: str, article_inner: str) -> str:
    """Swap the outer landing-article only. Nested inline-pick <article> tags stay irrelevant."""
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
    if visits != 10:
        errors.append(f"visit cards={visits} (need 10)")
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
    start = html.find('<article class="landing-article">')
    side = html.find('<div class="editorial-side-stack">')
    chunk = html[start:side] if start >= 0 and side > start else ""
    if not chunk:
        errors.append("could not isolate landing-article")
    elif meta["slug"] != "humidifiers" and (
        "What bedroom shoppers" in chunk or "how-to-choose-a-humidifier" in chunk
    ):
        errors.append("bedroom leftover inside article")
    if errors:
        raise SystemExit(f"{meta['path']} bake assert failed: " + "; ".join(errors))


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
    crumb_name: str,
    crumb_cat: str,
    cat_name: str,
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
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": f"{LIVE}/{crumb_cat}/"},
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
                "url": (
                    f"{LIVE}/{crumb_cat}/reviews/{p['review_slug']}/"
                    if p.get("review_slug")
                    else f"{LIVE}/{crumb_cat}/comparison/"
                ),
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
        t = data.get("@type")
        return match.group(0) if t == "Organization" else ""

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
    slug: str,
    cat_name: str,
    crumb: str,
    h1: str,
    author_slug: str,
    author_name: str,
    author_initials: str,
    lifestyle: str,
    article: str,
    picks: list[dict],
    scene_path: str,
    scene_label: str,
) -> str:
    html = re.sub(
        r'<nav class="breadcrumb">.*?</nav>',
        (
            f'<nav class="breadcrumb"><a href="../../index.html">Home</a> '
            f'<span class="sep">/</span> <a href="../../{slug}/">{_esc(cat_name)}</a> '
            f'<span class="sep">/</span> <span>{_esc(crumb)}</span></nav>'
        ),
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(r"<h1>.*?</h1>", f"<h1>{_esc(h1)}</h1>", html, count=1)
    html = re.sub(
        r'<div class="author-avatar"[^>]*>.*?</div>',
        f'<div class="author-avatar" aria-hidden="true">{escape(author_initials)}</div>',
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r'<span class="author-name">.*?</span>',
        (
            f'<span class="author-name">Written by '
            f'<a class="author-name-link" href="../../authors/{author_slug}/">'
            f"{_esc(author_name)}</a></span>"
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
            f'<img class="lifestyle-photo" src="../../assets/img/lifestyle/{lifestyle}" '
            f'alt="" width="640" height="400" loading="lazy"/>'
        ),
        html,
        count=1,
    )
    html = re.sub(
        r'<span class="lifestyle-label">.*?</span>',
        f'<span class="lifestyle-label">{_esc(cat_name)}</span>',
        html,
        count=1,
    )
    html = _replace_landing_article(html, article)
    html = re.sub(
        r'<div class="editorial-side-stack">.*?</div>\s*</div>\s*</div>\s*</main>',
        (
            '<div class="editorial-side-stack">\n        \n'
            f"{reviews_sidebar(picks)}\n\n        \n"
            f"{editors_picks(slug, scene_path, scene_label)}\n\n"
            "      </div>\n    </div>\n  </div>\n</main>"
        ),
        html,
        count=1,
        flags=re.S,
    )
    return html


def og_image_for(pick: dict) -> str:
    img = pick.get("image") or pick.get("thumb") or ""
    img = _fix_asset_prefix(img)
    if img.startswith("http"):
        return img
    if img.startswith("../../"):
        return f"{LIVE}/{img[6:]}"
    return f"{LIVE}/icon-512.png"


def _ap_shared_tail(slug: str, picks: list[dict], our_h2: str, optimize_h2: str, optimize: list[str], scene_paras: list[str]) -> str:
    return (
        f"{our_top_list(our_h2, picks, slug)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        f"<h2>{_esc(optimize_h2)}</h2>"
        + "".join(f"<p>{p}</p>" for p in optimize)
        + f"<h2>Our top air purifiers for this slice</h2>"
        + "".join(f"<p>{p}</p>" for p in scene_paras)
        + "<h2>Quick shortlist from our live chart</h2>"
        "<p>Cards reuse live comparison tracks, images, and price snapshots, ordered for this scene. "
        "Use Check price to confirm the live retailer offer.</p>"
        "<p>Scores map from retailer ratings when available. Roles are editorial labels, not paid awards.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of ten near-duplicates. "
        "An empty slot beats a stale listing.</p>"
        f"<p>Last verified {DATE}. Prices move — open Check price before you buy.</p>"
        "<p>We do not invent lab scores. We skip listings that are missing a title, gallery, or price snapshot.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        '<a href="../../air-purifiers/">air purifiers overview</a>, '
        '<a href="../../air-purifiers/reviews/">reviews hub</a>, and the '
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        '<p class="article-cta-row"><a class="btn btn-primary" href="../../air-purifiers/comparison/">See current rankings</a></p>'
    )


def _ap_meta(path: str, title: str, h1: str, description: str, page_desc: str, scene_label: str, picks, faqs, article, top, upg) -> dict:
    return {
        "path": path,
        "slug": "air-purifiers",
        "title": title,
        "h1": h1,
        "crumb": "Best of",
        "crumb_name": "Best of",
        "cat_name": "Air Purifiers",
        "author_slug": "riley-park",
        "author_name": "Riley Park",
        "author_initials": "RP",
        "lifestyle": "cmp-hero-air-purifiers.jpg",
        "description": description,
        "page_desc": page_desc,
        "scene_label": scene_label,
        "picks": picks,
        "faqs": faqs,
        "article": article,
        "top": top,
        "upgrade": upg,
        "keyword": title.replace(" | MoreTop10", "").lower(),
    }


def page_allergies() -> tuple[str, dict]:
    slug = "air-purifiers"
    picks = ordered_picks(slug, "air-purifiers-allergies")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best air purifier for allergies” mean here?",
            "It is an editorial slice of the live air-purifiers shortlist for dander, pollen, and fine-particle copy already on the cards — not a paid badge. We do not invent CADR beyond the shortlist.",
        ),
        (
            "Who should skip this allergy slice?",
            f"Skip it if the only job is floating pet hair on floors. Dreame AP10 sits mid-chart here "
            f"({money(picks[7].get('price'))} snapshot) because its card is hair collection, not pollen.",
        ),
        (
            "Why isn’t comparison #1 the allergy Top pick?",
            f"AEOCKY YearChange leads the comparison on score ({picks[8].get('score')} at {money(picks[8].get('price'))}) "
            "but its on-page copy is filter longevity. LEVOIT Vital Pet Pro is the landing Top pick with dander and odor language, so this page leads there.",
        ),
        (
            "Does the 47 ft2 dorm card belong on an allergy page?",
            "Yes as a neighbor. LV-H128 lists pollen CADR of 52 CFM and allergy-symptom copy, but AHAM sizes it at 47 ft2. Confirm room size on the retailer page.",
        ),
    ]
    lede = (
        "<p>Allergy season punishes bedroom towers that only mention HEPA in passing. "
        "This best-of highlights air purifiers on our shortlist whose titles or why-copy already name dander, pollen, or fine particles — not a paste of the score-sorted comparison.</p>"
        "<p>We lean on language already on the cards. We do not invent pollen counts or medical claims.</p>"
        "<p>Rankings follow the same shortlist rules as our main air purifiers comparison, reordered for allergies.</p>"
    )
    densify = (
        f"<p>For most allergy rooms, start with LEVOIT Vital Pet Pro "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The landing already calls out 140 g of activated carbon plus sensors that watch pet dander, smoke, and TVOC. "
        f"Step to the LEVOIT small-bedroom card ({money(upg.get('price'))} snapshot) when the 3-stage filter’s dust and pollen line is the overnight job.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Dander and pollen copy lead:</strong> Vital Pet Pro, the bedroom 3-stage card, and PM10’s 4-layer list (dust, pet dander, pollen, smoke) earn the top slots.</li>"
        "<li><strong>Score order is the wrong allergy order:</strong> Comparison #1 is AEOCKY YearChange. This page keeps it as a neighbor.</li>"
        "<li><strong>AHAM room size still matters:</strong> LV-H128 names allergy symptoms and pollen CADR 52 CFM, but only for 47 ft2.</li>"
        "<li><strong>Hair-collection towers are secondary:</strong> AP10 stays on the page for dander, not as the default pollen pick.</li>"
        "</ul></section>"
        "<h2>Which allergy air purifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('4-layer pollen neighbor', picks[2])}"
        f"{role_block('Tiny-room pollen CADR', picks[3])}"
        "<p>To see climate hybrids and score order together, open the live "
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}<div class=\"gemini-shell-densify\">{densify}</div>"
        + _ap_shared_tail(
            slug,
            picks,
            "Our top 10 best air purifiers for allergies",
            "What allergy shoppers should optimize",
            [
                "Dander, pollen, and fine-particle language on the card beat a heater/fan hybrid you will not run in summer.",
                "Confirm AHAM room size on the retailer page — a 47 ft2 dorm card is a poor default for a whole bedroom.",
                "Carbon load helps odor; it is not a substitute for a filter stage that names pollen or dander.",
            ],
            [
                "Start with Vital Pet Pro for dander, then the LEVOIT small-bedroom card when quiet pollen filtration is the overnight job.",
                "PM10 stays as the 4-layer neighbor when the listing’s pollen and smoke line matches a larger room.",
                "AEOCKY YearChange stays last among the scored towers because its card is filter longevity, not allergy copy.",
            ],
        )
    )
    return article, _ap_meta(
        "air-purifiers/best-air-purifiers-for-allergies/",
        "Best Air Purifiers for Allergies | MoreTop10",
        "Best Air Purifiers for Allergies (2026)",
        "Allergy season punishes generic bedroom towers. This best-of highlights air purifiers on our shortlist aimed at dander, pollen, and fine particles.",
        "Allergy season punishes generic bedroom towers. This best-of highlights air purifiers on our shortlist aimed at dander, pollen, and fine particles — not a paste of the score-sorted comparison.",
        "Best for allergies",
        picks, faqs, article, top, upg,
    )


def page_mold() -> tuple[str, dict]:
    slug = "air-purifiers"
    picks = ordered_picks(slug, "air-purifiers-mold")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "Do any shortlist cards name mold?",
            "No. This slice is honest about that. We reorder HEPA, 0.1μm, 5-layer, and year-change filter language already on the cards. We do not invent mold-kill rates.",
        ),
        (
            "Who should skip this mold slice?",
            f"Skip it if you only need a 47 ft2 dorm tower. LV-H128 sits last "
            f"({money(picks[9].get('price'))} snapshot) because the card sizes it at 47 ft2.",
        ),
        (
            "Why isn’t comparison #1 the mold Top pick?",
            f"AEOCKY YearChange is comparison #1 ({picks[3].get('score')} at {money(picks[3].get('price'))}) "
            "and its 5-layer year-change copy is useful here, but the card is written as filter longevity, not room coverage. MOOKA is the landing Best value HEPA bedroom card, so this page leads there.",
        ),
        (
            "When is the Dreame PM20 the better buy?",
            f"Choose PM20 when the 4-layer 0.1μm line and a large-room 3-in-1 footprint match the space "
            f"({money(upg.get('price'))} snapshot). Stay with MOOKA when you want HEPA coverage without a heater/fan hybrid.",
        ),
    ]
    lede = (
        "<p>Damp rooms punish neglected filters and undersized HEPA towers. "
        "This best-of highlights air purifiers on our shortlist whose cards already name HEPA, 0.1μm particles, or year-change filters — not a second copy of the category Top 10.</p>"
        "<p>No live card on this shortlist names mold. We do not invent kill-rates or square-footage beyond the cards.</p>"
        "<p>Rankings follow the same shortlist rules as our main air purifiers comparison, reordered for this slice.</p>"
    )
    densify = (
        f"<p>Start with MOOKA "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The landing already calls it Best value HEPA for bedrooms and medium rooms with a washable pre-filter. "
        f"Step to Dreame PM20 ({money(upg.get('price'))} snapshot) when the 4-layer 0.1μm line and a large-room footprint are the job.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>No card says mold:</strong> HEPA, 0.1μm, and year-change copy are the honest filter — not invented sporicidal claims.</li>"
        "<li><strong>Comparison #1 is demoted, not dropped:</strong> AEOCKY’s 5-layer year-change filter stays mid-chart as a longevity neighbor.</li>"
        "<li><strong>0.1μm 4-layer sits high:</strong> PM20 and PM10 both list dust, pet dander, pollen, and smoke at 0.1μm.</li>"
        "<li><strong>47 ft2 dorm cards stay last:</strong> A tiny AHAM room size is a poor default for a damp living area.</li>"
        "</ul></section>"
        "<h2>Which air purifier should you pick for this slice?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('4-layer neighbor', picks[2])}"
        f"{role_block('Year-change neighbor', picks[3])}"
        "<p>For score order and climate hybrids, open the live "
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}<div class=\"gemini-shell-densify\">{densify}</div>"
        + _ap_shared_tail(
            slug,
            picks,
            "Our top 10 best air purifiers for mold-prone rooms",
            "What shoppers on this slice should optimize",
            [
                "HEPA or 0.1μm filter language on the card beats a brochure mode list.",
                "Year-change filters help if you will actually replace them on schedule — they do not name mold.",
                "Skip the 47 ft2 dorm card unless the room is that small. Confirm coverage on the retailer page.",
            ],
            [
                "Start with MOOKA for HEPA bedroom coverage, then PM20 when the 0.1μm 4-layer line matches a larger room.",
                "AEOCKY stays as the year-change neighbor, not the default, because its card is filter longevity.",
                "Pet-named and hair-collection towers stay mid-to-low because this slice is filtration language, not pet hair.",
            ],
        )
    )
    return article, _ap_meta(
        "air-purifiers/best-air-purifiers-for-mold/",
        "Best Air Purifiers for Mold | MoreTop10",
        "Best Air Purifiers for Mold (2026)",
        "Damp rooms punish neglected filters. This best-of highlights air purifiers on our shortlist whose cards already name HEPA, 0.1μm particles, or year-change filters.",
        "Damp rooms punish neglected filters. This best-of highlights air purifiers on our shortlist whose cards already name HEPA, 0.1μm particles, or year-change filters — no card on the shortlist names mold.",
        "Best for mold",
        picks, faqs, article, top, upg,
    )


def page_ap_bedrooms() -> tuple[str, dict]:
    slug = "air-purifiers"
    picks = ordered_picks(slug, "air-purifiers-bedrooms")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best air purifier for bedrooms” mean here?",
            "It is an editorial slice of the live shortlist for bedroom, quiet, and dorm-room language already on titles and why-copy — not a paid award.",
        ),
        (
            "Who should skip this bedroom slice?",
            f"Skip it if you want a 3-in-1 heater/fan hybrid as the main job. Dreame PM20 sits last "
            f"({money(picks[9].get('price'))} snapshot) because the card is climate-plus-filtration for large rooms.",
        ),
        (
            "Why isn’t comparison #1 the bedroom Top pick?",
            f"AEOCKY YearChange leads the comparison ({picks[6].get('score')} at {money(picks[6].get('price'))}) "
            "but its copy is filter longevity, not quiet overnight use. The LEVOIT small-bedroom card names bedroom and 24 dB-class noise, so this page leads there.",
        ),
        (
            "When is MOOKA the better bedroom buy?",
            f"Choose MOOKA when the listing’s 2200 ft² HEPA bedroom coverage matches a larger sleep space "
            f"({money(upg.get('price'))} snapshot). Stay with the LEVOIT small-room card for a compact nightstand footprint.",
        ),
    ]
    lede = (
        "<p>Bedrooms punish loud motors and towers sized for open living rooms. "
        "This best-of highlights air purifiers on our shortlist aimed at bedrooms that need quiet overnight filtration — not a paste of the score-sorted comparison.</p>"
        "<p>We emphasize bedroom, quiet, and dorm language from titles and why-copy. We do not invent decibel claims beyond the cards.</p>"
        "<p>Rankings follow the same shortlist rules as our main air purifiers comparison, reordered for bedrooms.</p>"
    )
    densify = (
        f"<p>For most bedrooms, start with the LEVOIT small-room card "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The live card names bedroom use, a pre-filter for hair, and noise as low as 24 dB. "
        f"Step to MOOKA ({money(upg.get('price'))} snapshot) when the listing’s 2200 ft² HEPA bedroom coverage matches a larger sleep space.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Bedroom-titled cards lead:</strong> LEVOIT small-room, MOOKA, and the two dorm cards all name bedroom or dorm in the title.</li>"
        "<li><strong>Score order is the wrong night order:</strong> Comparison #1 is AEOCKY YearChange. This page keeps it as a neighbor.</li>"
        "<li><strong>Quiet copy matters more than CADR peaks:</strong> 24 dB and 34 dBA lines beat a 3-in-1 heater you will not run at 2 a.m.</li>"
        "<li><strong>Climate hybrids sit last:</strong> PM20 is written as a large-room heater/fan, not a nightstand default.</li>"
        "</ul></section>"
        "<h2>Which bedroom air purifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Dorm-quiet neighbor', picks[2])}"
        f"{role_block('Compact 34 dBA', picks[4])}"
        "<p>To see climate hybrids and score order together, open the live "
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}<div class=\"gemini-shell-densify\">{densify}</div>"
        + _ap_shared_tail(
            slug,
            picks,
            "Our top 10 best air purifiers for bedrooms",
            "What bedroom air-purifier shoppers should optimize",
            [
                "Night noise on the card beats a peak CADR number you never run.",
                "Match claimed room size to the bedroom you will actually close the door on.",
                "Heater/fan hybrids only pay off if you will use those modes weekly.",
            ],
            [
                "Start with the LEVOIT small-bedroom card, then MOOKA if the room is closer to the 2200 ft² HEPA claim.",
                "Dorm cards stay as quiet neighbors, not as defaults for a master bedroom.",
                "PM20 stays last because the card is a 3-in-1 climate unit.",
            ],
        )
    )
    return article, _ap_meta(
        "air-purifiers/best-air-purifiers-for-bedrooms/",
        "Best Air Purifiers for Bedrooms | MoreTop10",
        "Best Air Purifiers for Bedrooms (2026)",
        "Bedrooms punish loud motors and oversized towers. This best-of highlights air purifiers on our shortlist aimed at quiet overnight filtration.",
        "Bedrooms punish loud motors and oversized towers. This best-of highlights air purifiers on our shortlist aimed at bedrooms that need quiet overnight filtration.",
        "Best for bedrooms",
        picks, faqs, article, top, upg,
    )


def page_dust() -> tuple[str, dict]:
    slug = "air-purifiers"
    picks = ordered_picks(slug, "air-purifiers-dust")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best air purifier for dust” mean here?",
            "It is a scene slice of the live shortlist for dust, lint, hair, and Dust CADR language already on the cards — not a paid badge.",
        ),
        (
            "Who should skip this dust slice?",
            "Skip it if the daily complaint is odor without visible dust. Vital Pet Pro stays mid-chart because its card leads with carbon and dander, not Dust CADR.",
        ),
        (
            "Why isn’t comparison #1 the dust Top pick?",
            f"AEOCKY lists Dust CADR 240 m3/h (141 CFM) on the card and sits mid-chart here "
            f"({money(picks[4].get('price'))} snapshot) as a CADR neighbor. The LEVOIT small-bedroom card leads because its 3-stage copy names dust and a hair pre-filter at a bedroom footprint.",
        ),
        (
            "When is the Dreame AP10 the better dust buy?",
            f"Choose AP10 when floating hair and dust on floors is the daily complaint "
            f"({money(upg.get('price'))} snapshot). The card’s triple-layer line names hair and dust plus a visible collection compartment.",
        ),
    ]
    lede = (
        "<p>Dusty rooms punish towers that only advertise a generic HEPA badge. "
        "This best-of highlights air purifiers on our shortlist whose cards already name dust, lint, hair, or Dust CADR — not a paste of the score-sorted comparison.</p>"
        "<p>We lean on that shortlist language. We do not invent CADR beyond the cards.</p>"
        "<p>Rankings follow the same shortlist rules as our main air purifiers comparison, reordered for dust.</p>"
    )
    densify = (
        f"<p>Start with the LEVOIT small-bedroom card "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The live 3-stage copy names a hair pre-filter plus a main filter that captures dust and pollen. "
        f"Step to Dreame AP10 ({money(upg.get('price'))} snapshot) when hair and dust on floors is the daily complaint.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Dust-named stages lead:</strong> LEVOIT 3-stage, AP10 hair-and-dust, and the dorm lint/hair card earn the top slots.</li>"
        "<li><strong>AEOCKY is a CADR neighbor:</strong> Dust CADR 240 m3/h is on the card, but the why-copy is filter longevity.</li>"
        "<li><strong>PM10’s 4-layer lists dust:</strong> It stays mid-high as a large-room neighbor, not the default bedroom dust pick.</li>"
        "<li><strong>Tiny-room Dust CADR stays mid-low:</strong> LV-H128 lists dust CADR 41 CFM at 47 ft2.</li>"
        "</ul></section>"
        "<h2>Which dust air purifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Lint-and-hair neighbor', picks[2])}"
        f"{role_block('Dust CADR neighbor', picks[4])}"
        "<p>For score order across all ten cards, open the live "
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}<div class=\"gemini-shell-densify\">{densify}</div>"
        + _ap_shared_tail(
            slug,
            picks,
            "Our top 10 best air purifiers for dust",
            "What dust shoppers should optimize",
            [
                "A named dust or lint stage on the card beats a peak brochure CADR you never run.",
                "Hair pre-filters clog first — confirm replacement filters on the retailer page.",
                "A 47 ft2 Dust CADR is a neighbor, not a whole-home default.",
            ],
            [
                "Start with the LEVOIT small-bedroom 3-stage card, then AP10 if hair-and-dust on floors is the job.",
                "AEOCKY stays as the high Dust CADR neighbor because its why-copy is filter longevity.",
                "Climate hybrids sit low because dust is one line on a larger feature list.",
            ],
        )
    )
    return article, _ap_meta(
        "air-purifiers/best-air-purifiers-for-dust/",
        "Best Air Purifiers for Dust | MoreTop10",
        "Best Air Purifiers for Dust (2026)",
        "Dusty rooms punish generic HEPA badges. This best-of highlights air purifiers on our shortlist whose cards already name dust, lint, hair, or Dust CADR.",
        "Dusty rooms punish generic HEPA badges. This best-of highlights air purifiers on our shortlist whose cards already name dust, lint, hair, or Dust CADR — not a paste of the score-sorted comparison.",
        "Best for dust",
        picks, faqs, article, top, upg,
    )


def page_smoke() -> tuple[str, dict]:
    slug = "air-purifiers"
    picks = ordered_picks(slug, "air-purifiers-smoke")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best air purifier for smoke” mean here?",
            "It is a scene slice of the live shortlist for smoke CADR, smoke particles, carbon, or 4-layer copy that already names smoke — not a paid award. We do not invent wildfire ratings.",
        ),
        (
            "Who should skip this smoke slice?",
            f"Skip it if you only need a quiet 47 ft2 dorm tower. LV-H128 lists smoke CADR 30 CFM "
            f"({money(picks[5].get('price'))} snapshot) and stays mid-chart as a tiny-room neighbor.",
        ),
        (
            "Why isn’t comparison #1 the smoke Top pick?",
            f"AEOCKY lists Smoke CADR 224 m3/h (131 CFM) and sits mid-chart "
            f"({money(picks[3].get('price'))} snapshot). The why-copy is filter longevity. PM10’s 4-layer line names smoke alongside dust, dander, and pollen, so this page leads there.",
        ),
        (
            "When is Vital Pet Pro the better smoke buy?",
            f"Choose Vital Pet Pro when odor and smoke sensors matter more than a 3-in-1 climate tower "
            f"({money(upg.get('price'))} snapshot). The card lists 140 g of activated carbon and sensors that watch smoke and TVOC.",
        ),
    ]
    lede = (
        "<p>Smoke and lingering odor punish towers that only advertise a quiet night mode. "
        "This best-of highlights air purifiers on our shortlist whose cards already name smoke, smoke CADR, or a carbon load — not a paste of the score-sorted comparison.</p>"
        "<p>We lean on that shortlist language. We do not invent wildfire CADR or outdoor-air claims.</p>"
        "<p>Rankings follow the same shortlist rules as our main air purifiers comparison, reordered for smoke.</p>"
    )
    densify = (
        f"<p>Start with Dreame PM10 "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The 4-layer line already names dust, pet dander, pollen, and smoke at 0.1μm. "
        f"Step to LEVOIT Vital Pet Pro ({money(upg.get('price'))} snapshot) when 140 g of carbon and smoke/TVOC sensors are the overnight job.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Cards that name smoke lead:</strong> PM10/PM20 4-layer, Vital Pet sensors, the dorm smoke-particle card, and AEOCKY’s Smoke CADR.</li>"
        "<li><strong>Comparison #1 is a CADR neighbor:</strong> AEOCKY’s Smoke CADR 224 m3/h is real card copy; the why-line is still filter longevity.</li>"
        "<li><strong>Carbon vs CADR is the fork:</strong> Vital Pet Pro is odor carbon; AEOCKY and LV-H128 publish smoke CADR figures.</li>"
        "<li><strong>Tiny-room smoke CADR stays mid-chart:</strong> 30 CFM at 47 ft2 is not a living-room default.</li>"
        "</ul></section>"
        "<h2>Which smoke air purifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Smoke-particle neighbor', picks[2])}"
        f"{role_block('Smoke CADR neighbor', picks[3])}"
        "<p>For score order across all ten cards, open the live "
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}<div class=\"gemini-shell-densify\">{densify}</div>"
        + _ap_shared_tail(
            slug,
            picks,
            "Our top 10 best air purifiers for smoke",
            "What smoke shoppers should optimize",
            [
                "A named smoke stage, smoke CADR, or carbon load on the card beats a quiet-night brochure line.",
                "Confirm room size on the retailer page — 47 ft2 smoke CADR is a neighbor, not a living-room default.",
                "We do not invent wildfire or outdoor-air ratings. Use Check price for the live listing.",
            ],
            [
                "Start with PM10 for the 4-layer smoke line, then Vital Pet Pro when carbon and smoke sensors are the job.",
                "AEOCKY stays as the high Smoke CADR neighbor because its why-copy is filter longevity.",
                "Bedroom-only quiet cards sit low unless the room is actually that small.",
            ],
        )
    )
    return article, _ap_meta(
        "air-purifiers/best-air-purifiers-for-smoke/",
        "Best Air Purifiers for Smoke | MoreTop10",
        "Best Air Purifiers for Smoke (2026)",
        "Smoke and lingering odor punish quiet-only towers. This best-of highlights air purifiers on our shortlist whose cards already name smoke, smoke CADR, or carbon load.",
        "Smoke and lingering odor punish quiet-only towers. This best-of highlights air purifiers on our shortlist whose cards already name smoke, smoke CADR, or a carbon load — not a paste of the score-sorted comparison.",
        "Best for smoke",
        picks, faqs, article, top, upg,
    )


def page_large_rooms() -> tuple[str, dict]:
    slug = "air-purifiers"
    picks = ordered_picks(slug, "air-purifiers-large-rooms")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best air purifier for large rooms” mean here?",
            "It is a scene slice of the live shortlist for 2200/2300 ft² titles, large-room names, and landing Premium climate towers — not a paid badge.",
        ),
        (
            "Who should skip this large-room slice?",
            f"Skip it if you only need a 47 ft2 dorm tower. LV-H128 sits last "
            f"({money(picks[9].get('price'))} snapshot) because AHAM sizes it at 47 ft2.",
        ),
        (
            "Why isn’t comparison #1 the large-room Top pick?",
            f"AEOCKY is titled 2300 ft² and leads the comparison ({picks[2].get('score')} at {money(picks[2].get('price'))}), "
            "but its why-copy is filter longevity. MOOKA is the landing Best value with 2200 ft² HEPA bedroom coverage, so this page leads there.",
        ),
        (
            "When is the Dreame PM20 the better large-room buy?",
            f"Choose PM20 when a 3-in-1 purifier/heater/fan footprint is the job "
            f"({money(upg.get('price'))} snapshot). The landing already calls it Premium for large rooms. Stay with MOOKA when you want HEPA coverage without climate modes.",
        ),
    ]
    lede = (
        "<p>Large rooms punish 47 ft2 dorm towers and nightstand units sized for a single pillow. "
        "This best-of highlights air purifiers on our shortlist whose titles already name large rooms or 2200–2300 ft² coverage — not a paste of the score-sorted comparison.</p>"
        "<p>We emphasize room-size language already on the cards. We do not invent CADR beyond the shortlist.</p>"
        "<p>Rankings follow the same shortlist rules as our main air purifiers comparison, reordered for large rooms.</p>"
    )
    densify = (
        f"<p>Start with MOOKA "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The title lists 2200 ft² HEPA coverage and the landing already calls it Best value for bedrooms and medium rooms. "
        f"Step to Dreame PM20 ({money(upg.get('price'))} snapshot) when the Premium 3-in-1 large-room card matches an open living space.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Square-footage titles lead:</strong> MOOKA 2200 ft² and AEOCKY 2300 ft² are the only cards that print a large coverage number in the name.</li>"
        "<li><strong>Comparison #1 is demoted:</strong> AEOCKY’s why-copy is filter longevity, so it sits behind MOOKA and PM20.</li>"
        "<li><strong>Landing Premium is the Upgrade:</strong> PM20 is written as a large-room 3-in-1, not a nightstand HEPA.</li>"
        "<li><strong>47 ft2 dorm cards stay last:</strong> A tiny AHAM room size is the opposite of this slice.</li>"
        "</ul></section>"
        "<h2>Which large-room air purifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('2300 ft² neighbor', picks[2])}"
        f"{role_block('Large-room dual-flow', picks[3])}"
        "<p>For score order across all ten cards, open the live "
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}<div class=\"gemini-shell-densify\">{densify}</div>"
        + _ap_shared_tail(
            slug,
            picks,
            "Our top 10 best air purifiers for large rooms",
            "What large-room shoppers should optimize",
            [
                "Printed coverage on the title (2200 / 2300 ft²) beats a 47 ft2 dorm CADR.",
                "Pay for a 3-in-1 climate tower only if you will use heat or fan modes weekly.",
                "Confirm the live coverage claim on the retailer page before you treat ft² as a floor plan.",
            ],
            [
                "Start with MOOKA for 2200 ft² HEPA, then PM20 when the Premium large-room 3-in-1 is the job.",
                "AEOCKY stays as the 2300 ft² neighbor because its why-copy is filter longevity.",
                "Dorm and small-bedroom cards stay at the bottom of this slice.",
            ],
        )
    )
    return article, _ap_meta(
        "air-purifiers/best-air-purifiers-for-large-rooms/",
        "Best Air Purifiers for Large Rooms | MoreTop10",
        "Best Air Purifiers for Large Rooms (2026)",
        "Large rooms punish 47 ft2 dorm towers. This best-of highlights air purifiers on our shortlist whose titles already name large rooms or 2200–2300 ft² coverage.",
        "Large rooms punish 47 ft2 dorm towers. This best-of highlights air purifiers on our shortlist whose titles already name large rooms or 2200–2300 ft² coverage — not a paste of the score-sorted comparison.",
        "Best for large rooms",
        picks, faqs, article, top, upg,
    )


def page_babies() -> tuple[str, dict]:
    slug = "humidifiers"
    picks = ordered_picks(slug, "humidifiers-babies")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best humidifier for babies” mean here?",
            "It is an editorial slice of the live humidifiers shortlist for cards that already say Baby, nursery, or cool mist for small rooms — not a medical rating. We do not invent safety certifications.",
        ),
        (
            "Who should skip this nursery slice?",
            f"Skip it if you need a 10 L open-plan tank. OasisMist sits near the bottom "
            f"({money(picks[8].get('price'))} snapshot) because the landing calls it Premium for large rooms, not a crib-side cool-mist default.",
        ),
        (
            "Why isn’t comparison #1 the baby Top pick?",
            f"LEVOIT’s smart warm/cool mist leads the comparison for bedrooms "
            f"({money(picks[4].get('price'))} snapshot). Homvana 3.6L is the landing Best value for nurseries and small rooms with cool mist and wide-fill cleaning, so this page leads there.",
        ),
        (
            "When is the Homvana 7L the better nursery buy?",
            f"Choose the 7L card when the title’s Baby Nursery line and 807 ft² coverage match a larger nursery "
            f"({money(upg.get('price'))} snapshot). Stay with 3.6L when you want simple cool mist without warm-mist complexity.",
        ),
    ]
    lede = (
        "<p>Nurseries punish bulky warm-mist tanks and units you cannot clean with one hand. "
        "This best-of highlights humidifiers on our shortlist whose titles or why-copy already say Baby, nursery, or cool mist for small rooms — not a second copy of the category Top 10.</p>"
        "<p>We do not invent pediatric safety claims. We only promote language already on the cards.</p>"
        "<p>Rankings follow the same shortlist rules as our main humidifiers comparison, reordered for this scene.</p>"
    )
    densify = (
        f"<p>Start with Homvana 3.6L "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The landing already calls it Best value for nurseries: cool mist, a 5.3-inch wide fill, and fast comfort without warm-mist complexity. "
        f"Step to Homvana 7L ({money(upg.get('price'))} snapshot) when the title’s Baby Nursery line and 807 ft² coverage match a larger room.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Baby-named cards lead:</strong> Homvana 3.6L says Baby in the title; Homvana 7L’s listing title includes Baby Nursery.</li>"
        "<li><strong>Category #1 is demoted:</strong> LEVOIT bedroom warm/cool mist stays mid-chart as a symptom-relief neighbor, not the nursery default.</li>"
        "<li><strong>Cool mist and cleanability first:</strong> Wide-fill Homvana cards beat a 10 L tank you will not empty after a short night.</li>"
        "<li><strong>Mist-free H40 stays last:</strong> The Dreame card is evaporative white-dust copy, not a baby-named nursery pick.</li>"
        "</ul></section>"
        "<h2>Which nursery humidifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Cool-mist neighbor', picks[2])}"
        f"{role_block('Quiet-bedroom neighbor', picks[3])}"
        "<p>To see warm-mist and 10 L tanks in score order, open the live "
        '<a href="../../humidifiers/comparison/">humidifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}"
        f'<div class="gemini-shell-densify">{densify}</div>'
        f"{our_top_list('Our top 10 best humidifiers for babies', picks, slug)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        "<h2>What nursery shoppers should optimize</h2>"
        "<p>Cool mist and a tank you can actually clean beat a warm-mist app you will not open at 2 a.m.</p>"
        "<p>Match tank size to the nursery, not a 10 L open-plan brochure number.</p>"
        "<p>We do not invent safety certifications. Confirm current specs on the retailer page via Check price.</p>"
        "<h2>Our top humidifiers for this nursery slice</h2>"
        "<p>Start with Homvana 3.6L for nursery cool mist, then the 7L card when the Baby Nursery title matches a larger room.</p>"
        "<p>LEVOIT bedroom warm/cool mist stays as a neighbor if you already want symptom-relief modes.</p>"
        "<p>Mist-free and 10 L cards stay last so we do not invent nursery claims.</p>"
        "<h2>Quick shortlist from our live chart</h2>"
        "<p>Cards reuse live comparison tracks, images, and price snapshots, ordered for nurseries. "
        "Use Check price to confirm the live retailer offer.</p>"
        "<p>Scores map from retailer ratings when available. Roles are editorial labels, not paid awards.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of ten near-duplicates. "
        "An empty slot beats a stale listing.</p>"
        f"<p>Last verified {DATE}. Prices move — open Check price before you buy.</p>"
        "<p>We do not invent lab scores. We skip listings that are missing a title, gallery, or price snapshot.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        '<a href="../../humidifiers/">humidifiers overview</a>, '
        '<a href="../../humidifiers/reviews/">reviews hub</a>, and the '
        '<a href="../../humidifiers/comparison/">humidifiers comparison</a>.</p>'
        '<p class="article-cta-row"><a class="btn btn-primary" href="../../humidifiers/comparison/">See current rankings</a></p>'
    )
    meta = {
        "path": "humidifiers/best-humidifiers-for-babies/",
        "slug": slug,
        "title": "Best Humidifiers for Babies | MoreTop10",
        "h1": "Best Humidifiers for Babies (2026)",
        "crumb": "Best of",
        "crumb_name": "Best of",
        "cat_name": "Humidifiers",
        "author_slug": "riley-park",
        "author_name": "Riley Park",
        "author_initials": "RP",
        "lifestyle": "cmp-hero-humidifiers.jpg",
        "description": (
            "Nurseries punish bulky warm-mist tanks. This best-of highlights humidifiers "
            "on our shortlist whose cards already say Baby, nursery, or cool mist for small rooms."
        ),
        "page_desc": (
            "Nurseries punish bulky warm-mist tanks. This best-of highlights humidifiers "
            "on our shortlist whose cards already say Baby, nursery, or cool mist for small rooms — not a second copy of the category Top 10."
        ),
        "scene_label": "Best for babies",
        "picks": picks,
        "faqs": faqs,
        "article": article,
        "top": top,
        "upgrade": upg,
    }
    return article, meta


def page_home_office() -> tuple[str, dict]:
    slug = "standing-desks"
    picks = ordered_picks(slug, "standing-desks-home-office")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best standing desk for a home office” mean here?",
            "It is an editorial slice of the live standing-desks shortlist for daily sit-stand work — drawers, monitor stands, and mid-width tops — not a paid badge.",
        ),
        (
            "Who should skip this home-office slice?",
            f"Skip it if you only have a 32×19 alcove. That card sits last "
            f"({money(picks[9].get('price'))} snapshot). The small-office best-of is the better starting point for tiny footprints.",
        ),
        (
            "Why isn’t comparison #1 the home-office Top pick?",
            f"CubiCubi 40×24 leads the comparison on score ({picks[6].get('score')} at {money(picks[6].get('price'))}) "
            "but its copy is a compact height-range card. The 60×30 FEZIBO with drawers is the landing Top pick for daily home offices, so this page leads there.",
        ),
        (
            "When is the 63×37 the better home-office buy?",
            f"Choose 63×37 when dual monitors need a thicker, wider top without jumping to 83-inch freight "
            f"({money(upg.get('price'))} snapshot). Stay with 60×30 when drawer storage and a monitor stand are the daily job.",
        ),
    ]
    lede = (
        "<p>Home offices punish compact alcove tops and freight-scale 83-inch slabs you cannot turn in a stairwell. "
        "This best-of highlights standing desks on our shortlist aimed at daily sit-stand work with drawers or a mid-width top — not a paste of the score-sorted comparison.</p>"
        "<p>We emphasize home-office, drawer, and dual-monitor language already on the cards. We do not invent load ratings beyond the shortlist.</p>"
        "<p>Rankings follow the same shortlist rules as our main standing desks comparison, reordered for home offices.</p>"
    )
    densify = (
        f"<p>Start with the FEZIBO 60×30 "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The landing already calls it Top pick for daily home offices that still need charger storage and a monitor stand. "
        f"Step to the 63×37 ({money(upg.get('price'))} snapshot) when dual-monitor width is the constraint and you want to stay off 83-inch freight.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Drawers and mid-width lead:</strong> 60×30 is the landing home-office Top pick; 63×37 is the dual-monitor Upgrade.</li>"
        "<li><strong>Comparison #1 is demoted:</strong> CubiCubi 40×24 is a compact height-range card, not the daily home-office default.</li>"
        "<li><strong>48×24 stays Best value:</strong> It is the apartment/alcove neighbor, not the drawer-and-monitor default.</li>"
        "<li><strong>32×19 and glass sit last:</strong> Tiny footprints and a glass-top 48 belong on the small-office slice or as neighbors.</li>"
        "</ul></section>"
        "<h2>Which home-office standing desk should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('55-inch neighbor', picks[2])}"
        f"{role_block('Best-value alcove', picks[4])}"
        "<p>For score order and the small-office slice, open the live "
        '<a href="../../standing-desks/comparison/">standing desks comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}"
        f'<div class="gemini-shell-densify">{densify}</div>'
        f"{our_top_list('Our top 10 best standing desks for home offices', picks, slug)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        "<h2>What home-office shoppers should optimize</h2>"
        "<p>Drawer storage and a mid-width top beat a peak width number you cannot carry upstairs.</p>"
        "<p>Measure the wall and the doorway before you pay for 83-inch freight.</p>"
        "<p>32×19 alcove cards stay last — use the small-office best-of if that is the real footprint.</p>"
        "<h2>Our top standing desks for this slice</h2>"
        "<p>Start with 60×30 for drawers and a monitor stand, then 63×37 when dual monitors need more width.</p>"
        "<p>48×24 stays as the alcove Best value neighbor if you do not need drawers.</p>"
        "<p>Comparison #1 CubiCubi 40×24 stays as a compact neighbor, not the home-office default.</p>"
        "<h2>Quick shortlist from our live chart</h2>"
        "<p>Cards reuse live comparison tracks, images, and price snapshots, ordered for home offices. "
        "Use Check price to confirm the live retailer offer.</p>"
        "<p>Scores map from retailer ratings when available. Roles are editorial labels, not paid awards.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of ten near-duplicates. "
        "An empty slot beats a stale listing.</p>"
        f"<p>Last verified {DATE}. Prices move — open Check price before you buy.</p>"
        "<p>We do not invent lab scores. We skip listings that are missing a title, gallery, or price snapshot.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        '<a href="../../standing-desks/">standing desks overview</a>, '
        '<a href="../../standing-desks/reviews/">reviews hub</a>, and the '
        '<a href="../../standing-desks/comparison/">standing desks comparison</a>.</p>'
        '<p class="article-cta-row"><a class="btn btn-primary" href="../../standing-desks/comparison/">See current rankings</a></p>'
    )
    meta = {
        "path": "standing-desks/best-standing-desks-for-home-office/",
        "slug": slug,
        "title": "Best Standing Desks for Home Office | MoreTop10",
        "h1": "Best Standing Desks for Home Office (2026)",
        "crumb": "Best of",
        "crumb_name": "Best of",
        "cat_name": "Standing Desks",
        "author_slug": "sam-chen",
        "author_name": "Sam Chen",
        "author_initials": "SC",
        "lifestyle": "picks/office.jpg",
        "description": (
            "Home offices punish alcove tops and freight-scale slabs. This best-of highlights standing desks "
            "on our shortlist aimed at daily sit-stand work with drawers or a mid-width top."
        ),
        "page_desc": (
            "Home offices punish alcove tops and freight-scale slabs. This best-of highlights standing desks "
            "on our shortlist aimed at daily sit-stand work with drawers or a mid-width top — not a paste of the score-sorted comparison."
        ),
        "scene_label": "Best for home office",
        "picks": picks,
        "faqs": faqs,
        "article": article,
        "top": top,
        "upgrade": upg,
    }
    return article, meta
def write_page(meta: dict) -> Path:
    out_rel = meta["path"] + "index.html"
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = clone_chrome(out_rel, meta["slug"])
    url = f"{LIVE}/{meta['path']}"
    html = replace_head(
        html,
        title=meta["title"],
        description=meta["description"],
        url=url,
        og_image=og_image_for(meta["picks"][0]),
        crumb_name=meta["crumb_name"],
        crumb_cat=meta["slug"],
        cat_name=meta["cat_name"],
        picks=meta["picks"],
        faqs=meta["faqs"],
        page_desc=meta["page_desc"],
    )
    html = replace_main(
        html,
        slug=meta["slug"],
        cat_name=meta["cat_name"],
        crumb=meta["crumb"],
        h1=meta["h1"],
        author_slug=meta["author_slug"],
        author_name=meta["author_name"],
        author_initials=meta["author_initials"],
        lifestyle=meta["lifestyle"],
        article=meta["article"],
        picks=meta["picks"],
        scene_path=meta["path"].rstrip("/"),
        scene_label=meta["scene_label"],
    )
    html = rewrite_visible_jargon(html)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    assert_clean_page(html, meta)
    dest.write_text(html, encoding="utf-8")
    return dest


def add_landing_cluster(slug: str, href: str, label: str) -> bool:
    path = SITE / slug / "index.html"
    html = path.read_text(encoding="utf-8")
    if href in html and f">{label}<" in html:
        return False
    cluster = re.search(
        r'(<p class="landing-related-cluster">)(.*?)(</p>)',
        html,
        re.S,
    )
    if not cluster:
        return False
    inner = cluster.group(2)
    if href in inner:
        return False
    addition = f' · <a href="{href}">{escape(label)}</a>'
    html = html[: cluster.start(3)] + addition + html[cluster.start(3) :]
    path.write_text(html, encoding="utf-8")
    return True


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


def inventory_rows(scene: str, path: str, picks: list[dict], top: dict, upg: dict) -> dict:
    return {
        "scene": scene,
        "path": "/" + path,
        "density": len(picks),
        "order_asins": [p["asin"] for p in picks],
        "top_pick": {
            "asin": top["asin"],
            "name": top["name"],
            "review": top.get("review_slug"),
            "review_exists": top.get("review_exists"),
            "track_network": top.get("track_network"),
            "track_ok": bool(top.get("track")),
        },
        "upgrade": {
            "asin": upg["asin"],
            "name": upg["name"],
            "review": upg.get("review_slug"),
            "review_exists": upg.get("review_exists"),
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
        "reused_reviews": [
            p["review_slug"]
            for p in (top, upg)
            if p.get("review_exists")
        ],
    }


def write_inventory(rows: list[dict]) -> Path:
    dest = SITE / "data" / "p1b-scene-inventory-2026-10-23.json"
    dest.write_text(
        json.dumps({"date": DATE, "waiting_for_部署上线": True, "pages": rows}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    md = SITE / "data" / "p1b-scene-inventory-2026-10-23.md"
    lines = [
        "# P1b MT10 scenario inventory (2026-10-23)",
        "",
        "**waiting_for_部署上线:** yes",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
        "",
    ]
    for row in rows:
        lines += [
            f"## {row['path']}",
            "",
            f"- Density: {row['density']} (scene-reordered; not comparison order)",
            f"- Top pick: {row['top_pick']['name']} `{row['top_pick']['asin']}` review `{row['top_pick']['review']}` (reused)",
            f"- Upgrade: {row['upgrade']['name']} `{row['upgrade']['asin']}` review `{row['upgrade']['review']}` (reused)",
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
        "- Density is 10 scene-reordered live cards (type-07 / bedroom humidifier pattern). Not a 4-item Lab shortlist.",
        "- Role blocks keep the live densify `###` inside `<p>` and append a truncated live-card feature sentence. No invented prices/images/was.",
        "- No live air-purifier card names mold. That slice uses HEPA / 0.1μm / year-change language already on the cards.",
        "- Neighbor slots include thin-copy cards (AEOCKY YearChange why-copy, 47 ft2 dorm, CubiCubi compact, Dreame H40 mist-free). They stay last or demoted so we do not invent claims.",
        "- Reviews: Top pick + Upgrade reused only. No new `/{cat}/reviews/{slug}/` files.",
        "- Lab `/shortlists/*` paths from the locked batch are out of scope (MT10 draft only).",
        "- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    return dest


CLUSTER_LINKS = (
    ("air-purifiers", "../air-purifiers/best-air-purifiers-for-allergies/", "Best for allergies"),
    ("air-purifiers", "../air-purifiers/best-air-purifiers-for-mold/", "Best for mold"),
    ("air-purifiers", "../air-purifiers/best-air-purifiers-for-bedrooms/", "Best for bedrooms"),
    ("air-purifiers", "../air-purifiers/best-air-purifiers-for-dust/", "Best for dust"),
    ("air-purifiers", "../air-purifiers/best-air-purifiers-for-smoke/", "Best for smoke"),
    ("air-purifiers", "../air-purifiers/best-air-purifiers-for-large-rooms/", "Best for large rooms"),
    ("humidifiers", "../humidifiers/best-humidifiers-for-babies/", "Best for babies"),
    ("standing-desks", "../standing-desks/best-standing-desks-for-home-office/", "Best for home office"),
)

SCENE_KEYWORDS = (
    "best air purifier for allergies",
    "best air purifier for mold",
    "best air purifier for bedrooms",
    "best air purifier for dust",
    "best air purifier for smoke",
    "best air purifier for large rooms",
    "best humidifier for babies",
    "best standing desk for home office",
)


def main() -> None:
    builders = (
        page_allergies,
        page_mold,
        page_ap_bedrooms,
        page_dust,
        page_smoke,
        page_large_rooms,
        page_babies,
        page_home_office,
    )
    metas = []
    for build in builders:
        _article, meta = build()
        dest = write_page(meta)
        print(f"wrote {dest.relative_to(ROOT)}")
        metas.append(meta)

    for slug, href, label in CLUSTER_LINKS:
        add_landing_cluster(slug, href, label)

    paths = [m["path"] for m in metas]
    bump_or_insert_sitemap(paths)

    rows = [
        inventory_rows(keyword, meta["path"], meta["picks"], meta["top"], meta["upgrade"])
        for keyword, meta in zip(SCENE_KEYWORDS, metas)
    ]
    inv = write_inventory(rows)
    print(f"inventory {inv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
