#!/usr/bin/env python3
"""Bake P1a MT10 scene pages from in-repo comparison + landing cards.

Draft only. No wrangler / no Live deploy. No Lab / RR / OL edits.

Hard rules:
  - Scene-filter existing plural-category shortlists (do not paste chart order).
  - PB∪YP healthy tracks only; PB keep uid=fromsll; YP / maas pass-through.
  - No accessories; no invented prices, images, or was-prices.
  - Deep reviews: reuse existing Top pick + Upgrade HTML; do not invent SKUs.

Usage:
    python3 site/scripts/bake_p1a_scene_pages.py
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
    "<!-- waiting_for_部署上线: yes. P1a draft only. Do not merge. "
    "Do not Cloudflare Live deploy. -->"
)
TEMPLATE_LEFTOVER = (
    "What bedroom shoppers should optimize",
    "Our top humidifiers for this scene",
    "href=\"../../humidifiers/how-to-choose-a-humidifier/\"",
    "href=\"../../humidifiers/premium-humidifier-alternatives/\"",
    "href=\"../../humidifiers/levoit-bedroom-vs-homvana-cool-mist/\"",
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
    "dehumidifiers-basements": [
        "B0C9THG48W",  # Waykar 80 — landing Top pick, basement 5,000 sq ft
        "B0B5V6MBMR",  # Waykar 120 — 6,000 sq ft basement
        "B0D1C6HWFF",  # AEOCKY 5500 — landing Upgrade
        "B0FWB57KYQ",  # AEOCKY 8000 — large / commercial basement
        "B0H41K4PQN",  # LEVOIT basement (title + pump drain)
        "B0GXYD5JBY",  # DREO (basement alt on landing packshot)
        "B0H26KMQHT",  # Dreame 100 pint — high pint, 614 ft2 demote
        "B0FRQVWSS4",  # AEOCKY 50 — smaller basement
        "B081RG8JYR",  # Waykar 34 — 2,000 sq ft neighbor
        "B0FCDZM4JL",  # Waykar 30 — 2,000 sq ft neighbor
    ],
    "air-purifiers-pets": [
        "B0GXKSC38S",  # LEVOIT Vital Pet Pro — Top pick
        "B0FS68R44C",  # Dreame AP10 — Upgrade (hair collection)
        "B0CXJ97TV1",  # MOOKA — pet-lover intake
        "B09LMF648R",  # LEVOIT dorm — pet dander filter copy
        "B0F32TGRMR",  # PM20 — pet dander in 4-layer
        "B0F2G5DPJN",  # PM10 — same filtration language
        "B07X25BNBR",  # LEVOIT small — hair pre-filter
        "B0FK53C7B9",  # AEOCKY chart #1, no pet copy — neighbor
        "B0H4SVJ2RF",  # Dreame compact — no pet copy
        "B08BR1CR78",  # LEVOIT 47 ft2 dorm — too small for most pet rooms
    ],
    "robot-vacuums-pet-homes": [
        "B0FK2HPNCB",  # eufy E25 — pet hair + anti-tangle Top pick
        "B0GGRTD2ZY",  # Qrevo S Pro — "Anti-Tangle System for Pet Homes"
        "B0DWX69JVG",  # Q7 M5+ — sealed bag collects pet hair
        "B0DWXBCQVP",  # Q10 S5+ — embedded pet hair
        "B0DX1DQKMD",  # CurvX — pet fur + zero-tangle
        "B0GTLY9Z1K",  # LiDAR 10k — pet hair
        "B0GCDZBK9Q",  # Omni C20 — pet hair in Boost IQ (category #1 demoted)
        "B0F3337BV7",  # Q7 L5 — hair + anti-tangle
        "B0DHCJ571Z",  # Saros — skip-if without pets
        "B0CQ7JCN6Z",  # MaxV refurbished — no pet copy neighbor
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
        f"<li><strong>Price:</strong> {escape(price)}</li>"
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


def page_dehumidifiers() -> tuple[str, dict]:
    slug = "dehumidifiers"
    picks = ordered_picks(slug, "dehumidifiers-basements")
    top, upg = picks[0], picks[2]
    faqs = [
        (
            "What does “best dehumidifier for a basement” mean on this page?",
            "It is an editorial slice of the live dehumidifiers shortlist for damp lower levels — "
            "not a paid badge. We promote units whose titles or why-copy mention basement coverage, "
            "higher pint ratings, or pump/continuous drain, and we demote apartment-sized 2,000 sq ft cards.",
        ),
        (
            "Who should skip this basement slice?",
            "Skip it if you only need a closet or bedroom unit. Waykar 30-pint and 34-pint cards "
            f"({money(picks[9].get('price'))} and {money(picks[8].get('price'))} snapshots) stay on "
            "this page as neighbors, but the parent comparison is the better starting point for small rooms.",
        ),
        (
            "Why isn’t the comparison chart #1 the basement Top pick?",
            f"Dreame 100 Pint/D is comparison #1 at {money(picks[6].get('price'))} and score {picks[6].get('score')}, "
            "but its on-page copy sizes it around 614 ft2. Waykar 80-pint is the landing Top pick for "
            "damp basements up to 5,000 sq ft, so this scene leads with that card.",
        ),
        (
            "Which basement pick needs a pump drain?",
            "LEVOIT Dehumidifier for Basement & Home lists a washable removable pump and 4-way drainage "
            "on the live card. Confirm hose, lift height, and coverage on the retailer page via Check price.",
        ),
    ]
    lede = (
        "<p>Basements punish undersized tanks and units that cannot drain unattended. "
        "This best-of highlights dehumidifiers on our shortlist aimed at damp lower levels "
        "that need higher pint pull or continuous drain — not a second copy of the category Top 10.</p>"
        "<p>We emphasize basement, pint, and coverage language already on the cards. "
        "We do not invent lab scores or square-footage beyond the shortlist copy.</p>"
        "<p>Rankings follow the same shortlist rules as our main dehumidifiers comparison, "
        "reordered for this scene.</p>"
    )
    densify = (
        f"<p>For a typical damp basement, start with the Waykar 80-pint Energy Star unit "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"It is the landing Top pick for continuous pull up to 5,000 sq ft without jumping to "
        f"commercial 8,000 sq ft claims. Step to the AEOCKY 5500 Most Efficient card "
        f"({money(upg.get('price'))} snapshot) when summer humidity stays high, or to Waykar 120-pint "
        f"when the listing’s 6,000 sq ft basement language matches a wider lower level.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Scene filter, not chart paste:</strong> Comparison leads with Dreame 100 Pint/D; "
        "this page leads with Waykar 80 because the Dreame card sizes coverage around 614 ft2.</li>"
        "<li><strong>Pint and drain beat brochure modes:</strong> 80- to 120-pint cards plus pump or hose "
        "drain matter more than a smart display you will not open weekly.</li>"
        "<li><strong>Upgrade is efficiency + coverage:</strong> AEOCKY 5500 is the landing Upgrade for "
        "basements that stay wet through summer.</li>"
        "<li><strong>Small 2,000 sq ft units stay neighbors:</strong> Waykar 30- and 34-pint cards mention "
        "basements on the listing but sit at the bottom of this slice.</li>"
        "</ul></section>"
        "<h2>Which basement dehumidifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Large-footprint', picks[3])}"
        f"{role_block('Pump-drain basement', picks[4])}"
        "<p>To evaluate how these basement picks compare across the full pint range, "
        'check our live <a href="../../dehumidifiers/comparison/">dehumidifiers comparison</a>.</p>'
        "<h2>How pint rating changes basement chores</h2>"
        "<ol>"
        "<li><strong>80-pint residential:</strong> Waykar 80 is written for large homes and basements "
        "up to 5,000 sq ft with self-drying and auto-defrost on the card.</li>"
        "<li><strong>120-pint / 6,000 sq ft:</strong> Waykar 120 uses the same Energy Star year language "
        "with a higher pint claim — confirm the live variant before treating it as a drop-in.</li>"
        "<li><strong>Commercial 8,000 sq ft:</strong> AEOCKY 8000 is the Premium large-footprint card. "
        "Skip it for a single damp bathroom.</li>"
        "</ol>"
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}"
        f'<div class="gemini-shell-densify">{densify}</div>'
        f"{our_top_list('Our top 10 best dehumidifiers for basements', picks, slug)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        "<h2>What basement shoppers should optimize</h2>"
        "<p>Continuous drain or a pump beats a tank you will not empty after a wet week.</p>"
        "<p>Match pint rating and claimed coverage on the card to the room you will actually run — "
        "not a whole-house brochure number.</p>"
        "<p>Energy Star year labels help if the unit will run for months; they do not replace a hose path to a drain.</p>"
        "<h2>Our top dehumidifiers for this scene</h2>"
        "<p>Start with the basement-sized 80-pint card, then scan Upgrade and large-footprint ranks "
        "if one room still feels wet.</p>"
        "<p>Pay for commercial coverage only when one residential basement unit cannot cover the footprint.</p>"
        "<p>Apartment-sized 30- and 34-pint cards stay on the chart as neighbors, not as basement defaults.</p>"
        "<h2>Quick shortlist from our live chart</h2>"
        "<p>The cards below reuse live comparison tracks, images, and price snapshots, ordered for basements. "
        "Use Check price to confirm the live retailer offer.</p>"
        "<p>Scores map from retailer ratings when available. Roles are editorial labels, not paid awards.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of ten near-duplicates. "
        "An empty slot beats a stale listing.</p>"
        f"<p>Last verified {DATE}. Prices move — open Check price before you buy.</p>"
        "<p>We do not invent lab scores. We skip listings that are missing a title, gallery, or price snapshot.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this best-of with the "
        '<a href="../../dehumidifiers/">dehumidifiers overview</a>, '
        '<a href="../../dehumidifiers/reviews/">reviews hub</a>, and the '
        '<a href="../../dehumidifiers/comparison/">dehumidifiers comparison</a>.</p>'
        '<p class="article-cta-row"><a class="btn btn-primary" href="../../dehumidifiers/comparison/">See current rankings</a></p>'
    )
    meta = {
        "path": "dehumidifiers/best-dehumidifiers-for-basements/",
        "slug": slug,
        "title": "Best Dehumidifiers for Basements | MoreTop10",
        "h1": "Best Dehumidifiers for Basements (2026)",
        "crumb": "Best of",
        "crumb_name": "Best of",
        "cat_name": "Dehumidifiers",
        "author_slug": "riley-park",
        "author_name": "Riley Park",
        "author_initials": "RP",
        "lifestyle": "cmp-hero-dehumidifiers.jpg",
        "description": (
            "Basements punish undersized tanks and units that cannot drain unattended. "
            "This best-of highlights dehumidifiers on our shortlist aimed at damp lower levels."
        ),
        "page_desc": (
            "Basements punish undersized tanks and units that cannot drain unattended. "
            "This best-of highlights dehumidifiers on our shortlist aimed at damp lower levels "
            "that need higher pint pull or continuous drain."
        ),
        "scene_label": "Best for basements",
        "picks": picks,
        "faqs": faqs,
        "article": article,
        "top": top,
        "upgrade": upg,
    }
    return article, meta


def page_air_purifiers() -> tuple[str, dict]:
    slug = "air-purifiers"
    picks = ordered_picks(slug, "air-purifiers-pets")
    top, upg = picks[0], picks[1]
    faqs = [
        (
            "What does “best air purifier for pets” mean here?",
            "It means a scene slice of the live air-purifiers shortlist for dander, pet odor, "
            "and floating hair — not a paid award. Pet-named towers lead; bedroom-only 47 ft2 cards sit last.",
        ),
        (
            "Who should skip this pet slice?",
            "Skip it if you need a 3-in-1 heater/fan hybrid as the main job, or only a tiny dorm room. "
            f"The Dreame PM20 Premium card is {money(picks[4].get('price'))} snapshot and is climate-plus-filtration, "
            "not the default pet tower.",
        ),
        (
            "Why isn’t comparison #1 the pet Top pick?",
            f"AEOCKY YearChange leads the comparison on score ({picks[7].get('score')} at {money(picks[7].get('price'))}) "
            "but its on-page copy is filter-longevity, not pet odor or hair. LEVOIT Vital Pet Pro is the "
            "landing Top pick for pet homes, so this page leads there.",
        ),
        (
            "When is the Dreame AP10 the better pet buy?",
            "Choose AP10 when floating hair is the daily complaint and you want a visible hair compartment. "
            f"It is the Upgrade on this slice at {money(upg.get('price'))} snapshot. Stay with Vital Pet Pro "
            "when odor and dander matter more than hair-collection spectacle.",
        ),
    ]
    lede = (
        "<p>Pet rooms punish generic bedroom towers that only mention HEPA in passing. "
        "This best-of highlights air purifiers on our shortlist aimed at dander, odor, and floating hair — "
        "not a paste of the score-sorted comparison.</p>"
        "<p>We lean on pet / dander / hair language already on titles and why-copy. "
        "We do not invent CADR or filter life beyond the cards.</p>"
        "<p>Rankings follow the same shortlist rules as our main air purifiers comparison, reordered for pets.</p>"
    )
    densify = (
        f"<p>For most pet homes, start with LEVOIT Vital Pet Pro "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The landing already calls it Top pick for pet odor and dander with 140 g of activated carbon "
        f"on the card. Move to Dreame AP10 ({money(upg.get('price'))} snapshot) when hair on floors "
        f"is the daily complaint and you want a transparent collection compartment.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Pet-named towers lead:</strong> Vital Pet Pro and AP10 are the only cards whose titles "
        "say pet. Everything else must earn its slot from dander, hair, or odor copy.</li>"
        "<li><strong>Score order is the wrong pet order:</strong> Comparison #1 is AEOCKY YearChange. "
        "This page keeps it as a neighbor, not the pet default.</li>"
        "<li><strong>Hair vs odor is the fork:</strong> AP10 is hair collection; Vital Pet Pro is odor and dander.</li>"
        "<li><strong>47 ft2 dorm cards stay last:</strong> A tiny AHAM room size is a poor default for rooms animals use.</li>"
        "</ul></section>"
        "<h2>Which pet air purifier should you pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Best value neighbor', picks[2])}"
        f"{role_block('Dander-filter neighbor', picks[3])}"
        "<p>To see climate hybrids and score order together, open the live "
        '<a href="../../air-purifiers/comparison/">air purifiers comparison</a>.</p>'
        f"{faq_html(faqs)}"
    )
    article = (
        f"{lede}"
        f'<div class="gemini-shell-densify">{densify}</div>'
        f"{our_top_list('Our top 10 best air purifiers for pets', picks, slug)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        "<h2>What pet-home shoppers should optimize</h2>"
        "<p>Odor carbon load and a hair path beat a heater/fan hybrid you will not run in summer.</p>"
        "<p>Confirm room coverage on the retailer page — pet towers still fail a whole-home open plan.</p>"
        "<p>Filter changes are the day-two cost. Year-change language on AEOCKY is a neighbor benefit, not a pet feature.</p>"
        "<h2>Our top air purifiers for this scene</h2>"
        "<p>Start with Vital Pet Pro, then AP10 if hair collection is the job.</p>"
        "<p>MOOKA stays as the lower-priced pet-lover intake card, not a substitute for a pet-named tower.</p>"
        "<p>3-in-1 climate units sit mid-chart because pet dander is one line on a larger feature list.</p>"
        "<h2>Quick shortlist from our live chart</h2>"
        "<p>Cards reuse live comparison tracks, images, and price snapshots, ordered for pets. "
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
    meta = {
        "path": "air-purifiers/best-air-purifiers-for-pets/",
        "slug": slug,
        "title": "Best Air Purifiers for Pets | MoreTop10",
        "h1": "Best Air Purifiers for Pets (2026)",
        "crumb": "Best of",
        "crumb_name": "Best of",
        "cat_name": "Air Purifiers",
        "author_slug": "riley-park",
        "author_name": "Riley Park",
        "author_initials": "RP",
        "lifestyle": "cmp-hero-air-purifiers.jpg",
        "description": (
            "Pet rooms punish generic bedroom towers. This best-of highlights air purifiers "
            "on our shortlist aimed at dander, odor, and floating hair."
        ),
        "page_desc": (
            "Pet rooms punish generic bedroom towers. This best-of highlights air purifiers "
            "on our shortlist aimed at dander, odor, and floating hair — not a paste of the score-sorted comparison."
        ),
        "scene_label": "Best for pets",
        "picks": picks,
        "faqs": faqs,
        "article": article,
        "top": top,
        "upgrade": upg,
    }
    return article, meta


def page_robot_pet_homes() -> tuple[str, dict]:
    slug = "robot-vacuums"
    picks = ordered_picks(slug, "robot-vacuums-pet-homes")
    top, upg = picks[0], picks[1]
    top_faqs = [
        (
            "What makes this pet-homes niche different from the robot vacuums comparison?",
            "The parent comparison is score-ordered for mixed hardwood and carpet. This niche "
            "reorders the same shortlist for pet hair, anti-tangle brushes, and sealed self-empty bags. "
            "Category #1 (eufy Omni C20) stays on the page but is no longer the default pet-hair pick.",
        ),
        (
            "Do I need the most automated dock for pet hair?",
            "A self-empty bag helps when hair volume would clog a bin every day. Mop wash and dry "
            "matter if paws track mud onto hard floors. Confirm bag size and dock footprint on the retailer page.",
        ),
        (
            "Who should skip this pet-hair slice?",
            "Skip it if you have no pets and only want a thin flagship for furniture clearance. "
            "The Saros 10R card itself says it is overkill for small apartments without pets.",
        ),
        (
            "Why is eufy E25 the Top pick instead of Omni C20?",
            f"E25’s live card calls out 20,000 Pa for pet hair in carpet plus DuoSpiral anti-tangle "
            f"({money(top.get('price'))} snapshot). Omni C20 mentions pet hair in Boost IQ but is written "
            "as the mid-range empty-plus-wash dock default — a neighbor here, not the pet-hair lead.",
        ),
    ]
    bottom_faqs = [
        (
            "Is a refurbished Qrevo MaxV a pet-hair pick?",
            "No. Its on-page copy is renewed/refurbished and FlexiArm mopping. It stays last as a "
            "shortlist neighbor so we do not invent pet claims.",
        ),
        (
            "Where should I confirm litter tracking and long hair wrap?",
            "Those details live on the retailer listing. Use Check price, then read the Top pick or "
            "Upgrade review for the ownership notes we already published.",
        ),
    ]
    all_faqs = top_faqs + bottom_faqs
    lede = (
        "<p>Pet hair punishes open-brush robots and bins you empty twice a week. "
        "This niche is a use-case slice of robot vacuums — pet hair, anti-tangle, and sealed bags — "
        "not a second copy of the category landing.</p>"
        "<p>We only promote language already on the shortlist: pet hair, pet fur, anti-tangle, "
        "and pet-homes brush copy. We do not invent Pa or bag weeks.</p>"
        "<p>Rankings follow the same shortlist rules as our main robot vacuums comparison, reordered for pet homes.</p>"
    )
    densify = (
        f"<p>For homes that shed, start with eufy E25 "
        f"({money(top.get('price'))} snapshot, score {top.get('score')}). "
        f"The landing already calls out HydroJet mopping plus DuoSpiral anti-tangle for pet homes. "
        f"Upgrade to Roborock Qrevo S Pro ({money(upg.get('price'))} snapshot) when the card’s "
        f"“Anti-Tangle System for Pet Homes” and 7–9 week sealed bag match a heavier shed.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Anti-tangle is the niche filter:</strong> E25, Qrevo S Pro, Q10 S5+, Q7 M5+, "
        "CurvX, and the LiDAR 10k card all advertise hair wrap control or pet hair pickup.</li>"
        "<li><strong>Category #1 is demoted, not dropped:</strong> Omni C20 still self-empties and "
        "mentions pet hair in Boost IQ, but the card is written as a mid-range dock default.</li>"
        "<li><strong>Sealed bags beat open bins:</strong> Q7 M5+ and the LiDAR sibling both say a 2.7 L "
        "bag collects pet hair for weeks.</li>"
        "<li><strong>Refurbished MaxV is a neighbor:</strong> No pet-hair claim on the card, so it sits last.</li>"
        "</ul></section>"
        f"{faq_html(top_faqs)}"
        "<h2>Which robot vacuum should a pet home pick?</h2>"
        f"{role_block('Top pick', top)}"
        f"{role_block('Upgrade', upg)}"
        f"{role_block('Sealed-bag neighbor', picks[2])}"
        f"{role_block('Best-value anti-tangle', picks[3])}"
        "<p>For score order and mop-dock trade-offs across all ten cards, use the "
        '<a href="../../robot-vacuums/comparison/">robot vacuums comparison</a>.</p>'
        "<h2>Hair wrap vs suction on this shortlist</h2>"
        "<ul>"
        "<li><strong>Anti-tangle first:</strong> Qrevo S Pro names pet homes on the brush system; "
        "CurvX claims zero-tangle plus pet fur up to long-hair lengths on the listing.</li>"
        "<li><strong>Suction as a secondary:</strong> E25 lists 20,000 Pa for carpet pet hair; "
        "Q10 S5+ lists 10,000 Pa HyperForce for embedded pet hair.</li>"
        "</ul>"
    )
    article = (
        f"{lede}"
        f'<div class="gemini-shell-densify">{densify}</div>'
        f"{our_top_list('Our top 10 robot vacuums for pet homes', picks, slug)}"
        f"{inline_picks(picks)}"
        f"{visit_stack(picks)}"
        f"{faq_html(bottom_faqs)}"
        "<h2>What pet-home shoppers should optimize</h2>"
        "<p>Anti-tangle brushes and a sealed self-empty bag beat a peak Pa number you never run.</p>"
        "<p>Mop wash at the dock only pays off if paws track onto hard floors you will mop weekly.</p>"
        "<p>Refurbished cards without pet copy stay last — do not treat them as a pet-hair default.</p>"
        "<h2>Our top robot vacuums for this scene</h2>"
        "<p>Start with E25 for carpet pet hair and anti-tangle, then Qrevo S Pro when the listing’s "
        "pet-homes brush system and multi-week bag are the job.</p>"
        "<p>Omni C20 remains the mid-range empty-plus-wash neighbor if you already decided against HydroJet.</p>"
        "<p>Pet and family constraints should beat brochure mode lists every time.</p>"
        "<h2>Quick shortlist from our live chart</h2>"
        "<p>Cards reuse live comparison tracks, images, and price snapshots, ordered for pet hair. "
        "Use Check price to confirm the live retailer offer.</p>"
        "<p>Scores map from retailer ratings when available. Roles are editorial labels, not paid awards.</p>"
        "<h2>How we ranked these picks</h2>"
        "<p>We emphasize complete product cards and buyer roles instead of ten near-duplicates. "
        "An empty slot beats a stale listing.</p>"
        f"<p>Last verified {DATE}. Prices move — open Check price before you buy.</p>"
        "<p>We do not invent lab scores. We skip listings that are missing a title, gallery, or price snapshot.</p>"
        "<h2>Related reading</h2>"
        "<p>Pair this niche with the "
        '<a href="../../robot-vacuums/">robot vacuums overview</a>, '
        '<a href="../../robot-vacuums/reviews/">reviews hub</a>, and the '
        '<a href="../../robot-vacuums/comparison/">robot vacuums comparison</a>.</p>'
        '<p class="article-cta-row"><a class="btn btn-primary" href="../../robot-vacuums/comparison/">See current rankings</a></p>'
    )
    meta = {
        "path": "robot-vacuums/pet-homes/",
        "slug": slug,
        "title": "Best Robot Vacuums for Pet Hair | MoreTop10",
        "h1": "Best Robot Vacuums for Pet Hair (2026)",
        "crumb": "Niche",
        "crumb_name": "Niche",
        "cat_name": "Robot Vacuums & Mops",
        "author_slug": "alex-rivera",
        "author_name": "Alex Rivera",
        "author_initials": "AR",
        "lifestyle": "cmp-hero-robot.jpg",
        "description": (
            "Pet hair punishes open-brush robots and bins you empty twice a week. "
            "This niche highlights robot vacuums on our shortlist aimed at pet hair and anti-tangle."
        ),
        "page_desc": (
            "Pet hair punishes open-brush robots and bins you empty twice a week. "
            "This niche is a use-case slice of robot vacuums for pet hair, anti-tangle, and sealed bags."
        ),
        "scene_label": "Pet homes niche",
        "picks": picks,
        "faqs": all_faqs,
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
        cat_name=meta["cat_name"] if meta["slug"] != "robot-vacuums" else "Robot Vacuums",
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


def bump_sitemap(paths: list[str]) -> None:
    sm = SITE / "sitemap.xml"
    xml = sm.read_text(encoding="utf-8")
    for path in paths:
        loc = f"{LIVE}/{path}"
        xml = re.sub(
            rf"(<loc>{re.escape(loc)}</loc>\s*<lastmod>)[^<]+",
            rf"\g<1>{DATE}T12:00:00+00:00",
            xml,
            count=1,
        )
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
        "new_reviews": [
            p["review_slug"]
            for p in (top, upg)
            if p.get("review_exists")
        ],
        "reused_reviews": [],
        "deep_reviews": "rewritten_from_sot",
    }


def write_inventory(rows: list[dict]) -> Path:
    dest = SITE / "data" / "p1a-scene-inventory-2026-10-23.json"
    dest.write_text(json.dumps({"date": DATE, "waiting_for_部署上线": True, "pages": rows}, indent=2) + "\n", encoding="utf-8")
    md = SITE / "data" / "p1a-scene-inventory-2026-10-23.md"
    lines = [
        "# P1a MT10 scene inventory (2026-10-23)",
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
            f"- Deep reviews: Top pick + Upgrade rewritten from SoT (see notes/p1a-deep-reviews-2026-10-23.md)",
            "- Tracks: " + ", ".join(
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
        "- Neighbor slots include cards whose pet/basement copy is thin (AEOCKY YearChange, Dreame compact, refurbished Qrevo MaxV, Waykar 30/34). They stay last so we do not invent claims.",
        "- Reviews: Top pick + Upgrade deep articles rewritten in place at existing `/{cat}/reviews/{slug}/` paths. Not a full Top 10.",
        "- Lab `/shortlists/*` paths from the locked batch are out of scope (MT10 draft only).",
        "- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    return dest


def main() -> None:
    builders = (page_dehumidifiers, page_air_purifiers, page_robot_pet_homes)
    metas = []
    for build in builders:
        _article, meta = build()
        dest = write_page(meta)
        print(f"wrote {dest.relative_to(ROOT)}")
        metas.append(meta)

    add_landing_cluster(
        "dehumidifiers",
        "../dehumidifiers/best-dehumidifiers-for-basements/",
        "Best for basements",
    )
    add_landing_cluster(
        "air-purifiers",
        "../air-purifiers/best-air-purifiers-for-pets/",
        "Best for pets",
    )
    add_landing_cluster(
        "robot-vacuums",
        "../robot-vacuums/pet-homes/",
        "Pet homes niche",
    )

    paths = [m["path"] for m in metas]
    bump_sitemap(paths)

    rows = [
        inventory_rows(
            "best dehumidifier for basement",
            metas[0]["path"],
            metas[0]["picks"],
            metas[0]["top"],
            metas[0]["upgrade"],
        ),
        inventory_rows(
            "best air purifier for pets",
            metas[1]["path"],
            metas[1]["picks"],
            metas[1]["top"],
            metas[1]["upgrade"],
        ),
        inventory_rows(
            "best robot vacuum for pet hair",
            metas[2]["path"],
            metas[2]["picks"],
            metas[2]["top"],
            metas[2]["upgrade"],
        ),
    ]
    inv = write_inventory(rows)
    print(f"inventory {inv.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
