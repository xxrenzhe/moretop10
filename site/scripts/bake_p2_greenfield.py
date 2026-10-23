#!/usr/bin/env python3
"""Bake P2 MT10 greenfield — plural mains + one scene best-of each.

Draft only. No wrangler / no Live deploy. No Lab / RR / OL edits.
Does not rewrite ceramic P1c (#40), blog hub, or authors CSS.

Hard rules:
  - Plural main category first from healthy PB fromsll tracks only.
  - Honest density — do not invent ASINs, prices, images, or was/%.
  - Scene-filter that shortlist (do not paste comparison order) when cards exist.
  - No accessories. No new review articles unless Top+Upgrade already exist.
  - waiting_for_部署上线=yes.

Usage:
    python3 site/scripts/bake_p2_greenfield.py
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
from landing_faq import faqs_for  # noqa: E402
from scaffold_day_add import COVER_COLORS, DATE, gradient_jpg  # noqa: E402
from seo_geo import LIVE, apply_hub_page, dumps_ld, rewrite_visible_jargon  # noqa: E402
from site_config import load_site_config  # noqa: E402

TEMPLATE = SITE / "humidifiers" / "best-humidifiers-for-bedrooms" / "index.html"
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P2 draft only. Do not merge. "
    "Do not Cloudflare Live deploy. -->"
)
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

# Inventory sources checked 2026-10-23. No healthy PB fromsll cards exist
# in-repo, on live MoreTop10, or on public Lab/RR/OL shortlist JSON for
# these slugs. Do not invent ASINs, prices, images, or hops to fill Top 10.
CATS: list[dict[str, Any]] = [
    {
        "slug": "pillows",
        "name": "Pillows",
        "amazon_category": "Home & Kitchen",
        "scene_key": "neck-pain",
        "scene_path": "best-pillows-for-neck-pain",
        "scene_label": "Best for neck pain",
        "scene_keyword": "best pillows for neck pain",
        "scene_title": "Best Pillows for Neck Pain",
        "scene_h1": "Best Pillows for Neck Pain (2026)",
        "scene_desc": (
            "Neck-pain shoppers need loft and fill they can confirm on the listing. "
            "This best-of reorders verified pillow tracks for that job — we do not invent a padded Top 10."
        ),
        "feed": [],
        "cmp_order": [],
        "scene_order": [],
    },
    {
        "slug": "mattresses",
        "name": "Mattresses",
        "amazon_category": "Home & Kitchen",
        "scene_key": "side-sleepers",
        "scene_path": "best-mattresses-for-side-sleepers",
        "scene_label": "Best for side sleepers",
        "scene_keyword": "best mattresses for side sleepers",
        "scene_title": "Best Mattresses for Side Sleepers",
        "scene_h1": "Best Mattresses for Side Sleepers (2026)",
        "scene_desc": (
            "Side sleepers need firmness and height they can confirm on the listing. "
            "This best-of reorders verified mattress tracks for that job — we do not invent a padded Top 10."
        ),
        "feed": [],
        "cmp_order": [],
        "scene_order": [],
    },
    {
        "slug": "office-chairs",
        "name": "Office Chairs",
        "amazon_category": "Home & Kitchen",
        "scene_key": "back-pain",
        "scene_path": "best-office-chairs-for-back-pain",
        "scene_label": "Best for back pain",
        "scene_keyword": "best office chairs for back pain",
        "scene_title": "Best Office Chairs for Back Pain",
        "scene_h1": "Best Office Chairs for Back Pain (2026)",
        "scene_desc": (
            "Back-pain shoppers need lumbar support and seat depth they can confirm on the listing. "
            "This best-of reorders verified office-chair tracks for that job — we do not invent a padded Top 10."
        ),
        "feed": [],
        "cmp_order": [],
        "scene_order": [],
    },
    {
        "slug": "water-flossers",
        "name": "Water Flossers",
        "amazon_category": "Health & Household",
        "scene_key": "braces",
        "scene_path": "best-water-flossers-for-braces",
        "scene_label": "Best for braces",
        "scene_keyword": "best water flossers for braces",
        "scene_title": "Best Water Flossers for Braces",
        "scene_h1": "Best Water Flossers for Braces (2026)",
        "scene_desc": (
            "Braces shoppers need tip kits and pressure settings they can confirm on the listing. "
            "This best-of stays empty until a verified retail track exists — we do not invent a padded Top 10."
        ),
        "feed": [],
        "cmp_order": [],
        "scene_order": [],
    },
]


PACK_PATH = DATA / "p2-l1-fill-pack-2026-10-23.json"
ROLE_MAIN_RANK = {
    "Top pick": 0,
    "Upgrade": 1,
    "Premium": 2,
    "Best value": 3,
    "Editor pick": 4,
    "Alternative": 5,
    "Budget": 6,
    "Budget cooling": 7,
    "Also consider": 8,
}
EXPECTED_DENSITY = {
    "pillows": 6,
    "mattresses": 8,
    "office-chairs": 8,
    "water-flossers": 0,
}


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


def load_fill_pack() -> dict[str, Any]:
    if not PACK_PATH.exists():
        raise SystemExit(f"missing L1 fill pack {PACK_PATH}")
    return json.loads(PACK_PATH.read_text(encoding="utf-8"))


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
        "l2": {"ok": False, "method": "l1_pb_api", "status": "pending_cdp"},
    }


def scene_picks_from_pack(pack: dict[str, Any], scene_path: str) -> list[dict[str, Any]]:
    scene = (pack.get("scenes") or {}).get(scene_path) or {}
    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in scene.get("products") or []:
        pick = pick_from_pack(row)
        if not pick or pick["asin"] in seen:
            continue
        seen.add(pick["asin"])
        picks.append(pick)
    return picks


def main_order(picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        picks,
        key=lambda p: (ROLE_MAIN_RANK.get(p.get("role") or "", 50), p["asin"]),
    )


def write_shortlist(cat: dict[str, Any], picks: list[dict[str, Any]]) -> Path:
    slug = cat["slug"]
    n = len(picks)
    notes = [
        f"P2 L1 fill {slug} {DATE}. waiting_for_部署上线=yes. No Live.",
        "Healthy PB fromsll only. Density is honest — not padded to 10.",
        "Prices are L1 API snapshots from the fill pack. No invented ASINs, images, or was/%. list_price omitted.",
        "No Mac CDP gallery — product photos stay empty until L2. Lifestyle cover is a gradient placeholder.",
        "No accessories. No new MT10 review articles (Top/Upgrade reviews do not exist).",
    ]
    if slug == "water-flossers":
        notes.append(
            "True shortfall after pack tiers 1–3: PB∪YP returned 0 water-flosser mains. Empty scaffold kept."
        )
    elif slug == "mattresses":
        notes.append(
            "Honest Sweetnight-only concentration: other mattress brands were absent from the L1 pack networks."
        )
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
        "inventory": "l1_fill" if n else "density_shortfall",
        "baked": True,
        "live": False,
        "publishable": False,
        "cta_label": "Check price",
        "cta_rule": "PB pboost.me keeps uid=fromsll when a verified track exists; no invented hops",
        "l2": {
            "status": "l1_api" if n else "shortfall",
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


def inject_empty_watchouts(html: str, confirm: str) -> str:
    if 'class="pc-col-title cons"' in html:
        return html
    block = (
        '<div class="pros-cons landing-pick-pc"><div>'
        f'<div class="pc-col-title cons">Watch-outs</div>'
        f"<ul><li>{_esc(confirm)}</li></ul>"
        "</div></div>"
    )
    marker = '<h2>How to use this '
    if marker in html:
        return html.replace(marker, block + "\n        " + marker, 1)
    return html.replace("</article>", block + "\n      </article>", 1)


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


def polish_category_pages(cat: dict[str, Any], confirm: str) -> None:
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
        if kind == "landing":
            text = inject_empty_watchouts(text, confirm)
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
        text = strip_empty_best_widget(text)
        if DRAFT_COMMENT not in text:
            text = text.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
        path.write_text(text, encoding="utf-8")
    patch_related_cluster(slug, cat["scene_path"], cat["scene_label"])


def strip_empty_best_widget(html: str) -> str:
    """Honest density 0: do not keep a Best rail with invented names."""

    def _keep(match: re.Match[str]) -> str:
        block = match.group(0)
        if 'class="best-widget-name"' in block:
            return block
        return ""

    return re.sub(r'<aside class="best-widget">.*?</aside>', _keep, html, flags=re.S)


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
    crumb_name: str,
    cat_name: str,
    slug: str,
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
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": f"{LIVE}/{slug}/"},
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
                "name": p.get("title") or p.get("name") or p["asin"],
                "url": f"{LIVE}/{slug}/comparison/#geo-{p['asin']}",
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


def reviews_sidebar(slug: str) -> str:
    return (
        '<aside class="ed-reviews-sidebar">\n  <h3>Editorial Reviews</h3>\n'
        '  <div class="ed-rev-list"></div>\n'
        f'  <p class="sidebar-more"><a href="../../{slug}/reviews/">Reviews hub →</a></p>\n'
        "</aside>"
    )


def editors_picks(slug: str, scene_path: str, scene_label: str) -> str:
    return (
        '<aside class="editors-picks-widget">\n  <h3>Editor\'s Picks</h3>\n'
        f'  <ul class="ed-picks-list">'
        f'<li><a href="../../{slug}/comparison/">Comparison chart</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../{slug}/reviews/">Reviews hub</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        f'<li><a href="../../{slug}/{scene_path}/">{_esc(scene_label)}</a>'
        f'<span class="ed-pick-date">{DATE}</span></li></ul>\n'
        f'  <p class="sidebar-more"><a href="../../{slug}/">Category overview →</a></p>\n'
        "</aside>"
    )


def replace_main(
    html: str,
    *,
    crumb: str,
    h1: str,
    article: str,
    slug: str,
    name: str,
    scene_path: str,
    scene_label: str,
) -> str:
    html = re.sub(
        r'<nav class="breadcrumb">.*?</nav>',
        (
            f'<nav class="breadcrumb"><a href="../../index.html">Home</a> '
            f'<span class="sep">/</span> <a href="../../{slug}/">{_esc(name)}</a> '
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
            f'<img class="lifestyle-photo" src="../../assets/img/lifestyle/cmp-hero-{slug}.jpg" '
            f'alt="" width="640" height="400" loading="lazy"/>'
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
            f"{editors_picks(slug, scene_path, scene_label)}\n\n"
            "      </div>\n    </div>\n  </div>\n</main>"
        ),
        html,
        count=1,
        flags=re.S,
    )
    return html


def assert_clean_page(html: str, meta: dict) -> None:
    errors: list[str] = []
    if DRAFT_COMMENT not in html:
        errors.append("missing waiting_for_部署上线 draft comment")
    for leak in TEMPLATE_LEFTOVER:
        if leak in html:
            errors.append(f"template leftover {leak!r}")
    density = meta["density"]
    visits = html.count('class="bestof-visit-card"')
    if visits != density:
        errors.append(f"visit cards={visits} (need {density})")
    inline_need = min(3, density)
    if html.count('class="inline-pick-card"') != inline_need:
        errors.append(f"inline picks != {inline_need}")
    if "10%" in html or "12%" in html:
        errors.append("invented or leftover was/% leaked")
    if errors:
        raise SystemExit(f"{meta['path']} bake assert failed: " + "; ".join(errors))


def scene_confirm(slug: str) -> str:
    return {
        "pillows": "Confirm loft, fill, and firmness on the retailer page.",
        "mattresses": "Confirm size, firmness, and trial window on the retailer page.",
        "office-chairs": "Confirm lumbar support, weight rating, and seat depth on the retailer page.",
        "water-flossers": "Confirm tank size, pressure settings, and tip count on the retailer page.",
    }[slug]


def scene_faqs(cat: dict[str, Any], picks: list[dict[str, Any]]) -> list[tuple[str, str]]:
    name = cat["name"].lower()
    scene = cat["scene_keyword"]
    confirm = scene_confirm(cat["slug"])
    n = len(picks)
    if n == 0:
        return [
            (
                f"What does “{scene}” mean on this page?",
                f"It is an editorial slice of the {name} shortlist for this job — not a paid badge. "
                "We only reorder cards that already have a verified retail track.",
            ),
            (
                "Why is this shortlist empty?",
                "We checked the L1 fill pack after three discovery tiers. No healthy retail track "
                "passed. An empty slot beats an invented Top 10.",
            ),
            (
                "Who should skip this slice?",
                f"Skip it if you need a buy-now card today. Use the parent {name} overview when "
                "we publish verified tracks, or confirm the listing yourself on the retailer page.",
            ),
            (
                "What should I confirm before I buy?",
                confirm,
            ),
        ]
    return [
        (
            f"What does “{scene}” mean on this page?",
            f"It is an editorial slice of the {name} shortlist for this job — not a paid badge. "
            "Cards here are the same verified tracks as the parent shortlist, reordered for this scene.",
        ),
        (
            "Who should skip this slice?",
            f"Skip it if you need a product this shortlist does not list, or if you only want an "
            f"accessory. Start at the parent {name} overview for the full chart.",
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


def _short_title(title: str, n: int = 52) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    return title if len(title) <= n else title[: n - 1].rsplit(" ", 1)[0] + "…"


def visit_cards_html(picks: list[dict[str, Any]], confirm: str) -> str:
    bits = ['<div class="bestof-visit-stack">']
    for i, pick in enumerate(picks, start=1):
        href = pick.get("affiliate_link") or ""
        role = pick.get("role") or "Shortlist"
        price = pick.get("price_displayed") or ""
        pitch = f"{role}."
        if price:
            pitch += f" Snapshot {price}."
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


def inline_picks_html(picks: list[dict[str, Any]], slug: str, confirm: str) -> str:
    shown = picks[: min(3, len(picks))]
    if not shown:
        return ""
    bits = ['<div class="inline-picks" aria-label="Editor shortlist">']
    for i, pick in enumerate(shown, start=1):
        href = pick.get("affiliate_link") or ""
        role = pick.get("role") or "Shortlist"
        price = pick.get("price_displayed") or ""
        pitch = f"Snapshot {price}. {confirm}" if price else confirm
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
            f'<a href="../../{slug}/comparison/#geo-{_esc(pick["asin"])}">See in comparison</a>'
            "</div></article>"
        )
    bits.append("</div>")
    return "".join(bits)


def our_top_list_html(picks: list[dict[str, Any]], slug: str, name: str, confirm: str) -> str:
    n = len(picks)
    items = []
    for i, pick in enumerate(picks, start=1):
        price = f" Snapshot {pick['price_displayed']}." if pick.get("price_displayed") else ""
        items.append(
            f"<li><strong>{i}. {_esc(pick['title'])}</strong> — {_esc(confirm[:-1] if confirm.endswith('.') else confirm)}."
            f"{_esc(price)} "
            f'<a href="../../{slug}/comparison/#geo-{_esc(pick["asin"])}">See in comparison →</a></li>'
        )
    return (
        f'<section class="our-top-list"><h2>Our top {n} {escape(name.lower())} for this scene</h2>'
        f"<ol>{''.join(items)}</ol></section>"
    )


def scene_article(cat: dict[str, Any], picks: list[dict[str, Any]], faqs: list[tuple[str, str]]) -> str:
    slug = cat["slug"]
    name = cat["name"]
    scene = cat["scene_keyword"]
    confirm = scene_confirm(slug)
    n = len(picks)
    if n == 0:
        return (
            f"<p>{_esc(cat['scene_desc'])}</p>"
            f"<p>Rankings follow the same shortlist rules as our main {escape(name.lower())} "
            "comparison. Density is honest at 0 — we do not invent ASINs, prices, images, or discounts.</p>"
            '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
            '<ul class="card-bullets">'
            "<li><strong>Scene filter, not chart paste:</strong> This page exists so the URL is real. "
            "It does not copy a padded ranking.</li>"
            "<li><strong>Empty slot beats a guessed card:</strong> Check price appears only when a "
            "verified retail track exists.</li>"
            "<li><strong>No accessories:</strong> Pillowcases, toppers, chair mats, and replacement "
            "tips stay off this shortlist.</li>"
            "<li><strong>Reviews skipped:</strong> Top and Upgrade review articles do not exist on "
            "MoreTop10, so we do not invent them.</li>"
            "</ul></section>"
            f"<h2>Which {escape(scene)} should you pick?</h2>"
            "<p>None yet. We will scene-reorder the parent shortlist when healthy tracks land — "
            "not comparison order pasted into this URL.</p>"
            f'<p>Start at the <a href="../../{slug}/">{escape(name.lower())} overview</a> or the '
            f'<a href="../../{slug}/comparison/">{escape(name.lower())} comparison</a> once cards exist.</p>'
            "<h2>What shoppers should optimize</h2>"
            f"<p>{escape(confirm)}</p>"
            "<p>Skip accessories that cannot finish the buying job on their own.</p>"
            f"<h2>Our top {escape(name.lower())} for this scene</h2>"
            "<p>No editor shortlist yet. An empty slot beats a stale or invented listing.</p>"
            "<h2>How we ranked these picks</h2>"
            "<p>We emphasize complete product cards and buyer roles instead of padding to ten. "
            "Density is honest at 0.</p>"
            f"<p>Last verified {DATE}. We do not invent lab scores.</p>"
            "<h2>Related reading</h2>"
            "<p>Pair this best-of with the "
            f'<a href="../../{slug}/">{escape(name.lower())} overview</a>, '
            f'<a href="../../{slug}/reviews/">reviews hub</a>, and the '
            f'<a href="../../{slug}/comparison/">{escape(name.lower())} comparison</a>.</p>'
            f'<p class="article-cta-row"><a class="btn btn-primary" href="../../{slug}/comparison/">See current rankings</a></p>'
            f"{faq_html(faqs)}"
        )

    top = next((p for p in picks if p.get("role") == "Top pick"), picks[0])
    upgrade = next((p for p in picks if p.get("role") == "Upgrade"), None)
    who_bits = [
        f"<p>Start with <strong>{_esc(top['title'])}</strong>"
        + (f" ({_esc(top['price_displayed'])} snapshot)" if top.get("price_displayed") else "")
        + f" as the {escape((top.get('role') or 'lead').lower())} on this scene.</p>"
    ]
    if upgrade:
        who_bits.append(
            f"<p>Step up to <strong>{_esc(upgrade['title'])}</strong>"
            + (f" ({_esc(upgrade['price_displayed'])} snapshot)" if upgrade.get("price_displayed") else "")
            + " only if that listing’s extras match a job you will use.</p>"
        )
    mattress_note = ""
    if slug == "mattresses":
        mattress_note = (
            "<li><strong>One brand, honest spread:</strong> Every card is Sweetnight. "
            "Diversity here is size and construction, not a guessed extra brand.</li>"
        )
    return (
        f"<p>{_esc(cat['scene_desc'])}</p>"
        f"<p>Rankings follow the same shortlist rules as our main {escape(name.lower())} "
        f"comparison. Density is honest at {n} — we do not invent ASINs, prices, images, or discounts.</p>"
        '<section class="key-insights prose-block" aria-label="Key insights"><h2>Key insights</h2>'
        '<ul class="card-bullets">'
        "<li><strong>Scene filter, not chart paste:</strong> Order here follows the scene fill, "
        "not the parent comparison rank.</li>"
        "<li><strong>Verified tracks only:</strong> Check price opens a verified retailer hop. "
        "Prices are a publish-time snapshot — confirm the live cart.</li>"
        "<li><strong>No accessories:</strong> Pillowcases, toppers, chair mats, and replacement "
        "tips stay off this shortlist.</li>"
        f"{mattress_note}"
        "<li><strong>Reviews skipped:</strong> Top and Upgrade review articles do not exist on "
        "MoreTop10, so we do not invent them.</li>"
        "</ul></section>"
        f"<h2>Which {escape(scene)} should you pick?</h2>"
        f"{''.join(who_bits)}"
        f'<p>Use the <a href="../../{slug}/comparison/">{escape(name.lower())} comparison</a> '
        "to scan the same ASINs in parent-category order.</p>"
        f"{our_top_list_html(picks, slug, name, confirm)}"
        f"{inline_picks_html(picks, slug, confirm)}"
        f"{visit_cards_html(picks, confirm)}"
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
        f"{faq_html(faqs)}"
    )


def write_scene(cat: dict[str, Any], picks: list[dict[str, Any]]) -> dict[str, Any]:
    slug = cat["slug"]
    name = cat["name"]
    scene_path = f"{slug}/{cat['scene_path']}/"
    faqs = scene_faqs(cat, picks)
    n = len(picks)
    og = f"{LIVE}/assets/img/lifestyle/cmp-hero-{slug}.jpg"
    if n:
        desc = (
            f"{cat['scene_title']} — {n} verified {name.lower()} with retail tracks. "
            "Honest density, no invented photos or discounts."
        )
        page_desc = (
            f"Editorial slice of {name.lower()} for {cat['scene_keyword']} — "
            f"honest density {n} from verified retail tracks."
        )
    else:
        desc = cat["scene_desc"]
        page_desc = (
            f"Editorial slice of {name.lower()} for {cat['scene_keyword']} — "
            "honest density 0 until a verified retail track exists."
        )
    meta = {
        "path": scene_path,
        "title": f"{cat['scene_title']} | MoreTop10",
        "h1": cat["scene_h1"],
        "crumb": "Best of",
        "crumb_name": "Best of",
        "scene_label": cat["scene_label"],
        "picks": picks,
        "faqs": faqs,
        "density": n,
        "article": scene_article(cat, picks, faqs),
        "description": desc,
        "page_desc": page_desc,
    }
    out_rel = scene_path + "index.html"
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = clone_chrome(out_rel, slug)
    url = f"{LIVE}/{scene_path}"
    html = replace_head(
        html,
        title=meta["title"],
        description=meta["description"],
        url=url,
        og_image=og,
        crumb_name=meta["crumb_name"],
        cat_name=name,
        slug=slug,
        picks=picks,
        faqs=faqs,
        page_desc=meta["page_desc"],
    )
    html = replace_main(
        html,
        crumb=meta["crumb"],
        h1=meta["h1"],
        article=meta["article"],
        slug=slug,
        name=name,
        scene_path=cat["scene_path"],
        scene_label=cat["scene_label"],
    )
    html = rewrite_visible_jargon(html)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    assert_clean_page(html, meta)
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
        '<li><a href="../document-scanners/">Document Scanners</a> · '
        '<a href="../document-scanners/comparison/">Compare</a></li>'
    )
    extras: list[str] = []
    for cat in CATS:
        row = (
            f'<li><a href="../{cat["slug"]}/">{_esc(cat["name"])}</a> · '
            f'<a href="../{cat["slug"]}/comparison/">Compare</a></li>'
        )
        if f'href="../{cat["slug"]}/"' not in html:
            extras.append(row)
    if extras:
        if marker not in html:
            raise SystemExit("sitemap/index.html missing document-scanners row to patch")
        html = html.replace(marker, marker + "\n" + "\n".join(extras), 1)
        path.write_text(html, encoding="utf-8")


def patch_cover_map(slugs: list[str]) -> None:
    dest = DATA / f"day-add-cover-map-{DATE}.json"
    if dest.exists():
        blob = json.loads(dest.read_text(encoding="utf-8"))
    else:
        blob = {"generated": DATE, "notes": [], "covers": {}}
    for slug in slugs:
        blob.setdefault("covers", {})[slug] = {
            "status": "placeholder",
            "lifestyle": f"assets/img/lifestyle/cmp-hero-{slug}.jpg",
            "product_photos": "none — no healthy product cards",
            "todo": "Replace gradient placeholder with a real lifestyle cover after deploy. Do not invent product photos.",
        }
    dest.write_text(json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_inventory(pages: list[dict[str, Any]], by_slug: dict[str, dict[str, Any]]) -> Path:
    dest = DATA / "p2-greenfield-inventory-2026-10-23.json"
    dest.write_text(
        json.dumps(
            {
                "date": DATE,
                "waiting_for_部署上线": True,
                "source_pack": "site/data/p2-l1-fill-pack-2026-10-23.json",
                "pages": pages,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    md = DATA / "p2-greenfield-inventory-2026-10-23.md"
    lines = [
        "# P2 MT10 L1 fill inventory (2026-10-23)",
        "",
        "**waiting_for_部署上线:** yes",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
        "**Pack:** `site/data/p2-l1-fill-pack-2026-10-23.json`",
        "**Do not touch:** ceramic P1c #40 files, blog hub, authors CSS, GSC #45 (beyond coexistence).",
        "",
    ]
    for cat in CATS:
        blob = by_slug[cat["slug"]]
        main_picks = blob["main"]
        scene_picks = blob["scene"]
        top = next((p for p in scene_picks if p.get("role") == "Top pick"), None)
        upgrade = next((p for p in scene_picks if p.get("role") == "Upgrade"), None)
        lines += [
            f"## /{cat['slug']}/",
            "",
            "- Type: plural main category (landing + comparison + reviews hub)",
            f"- Density: {len(main_picks)} (honest; not padded to 10)",
            f"- Comparison order: {', '.join(p['asin'] for p in main_picks) or '(none)'}",
            f"- Top pick: {top['asin'] if top else 'none'}",
            f"- Upgrade: {upgrade['asin'] if upgrade else 'none'}",
            "- New reviews: none (MT10 Top/Upgrade review articles do not exist)",
            f"- Tracks: {len(main_picks)} PB fromsll" if main_picks else "- Tracks: none",
            "",
            f"## /{cat['slug']}/{cat['scene_path']}/",
            "",
            f"- Scene: {cat['scene_keyword']}",
            f"- Density: {len(scene_picks)} (scene order from L1 pack)",
            f"- Scene order: {', '.join(p['asin'] for p in scene_picks) or '(none)'}",
            f"- Top pick: {top['asin'] if top else 'none'} — review skipped",
            f"- Upgrade: {upgrade['asin'] if upgrade else 'none'} — review skipped",
            "- New reviews: none",
            f"- Tracks: {len(scene_picks)} PB fromsll" if scene_picks else "- Tracks: none",
            "",
        ]
    lines += [
        "## Shortfalls (honest)",
        "",
        "- water-flossers stays density 0 after pack tiers 1–3. Do not invent ASINs.",
        "- mattresses is Sweetnight-only — documented concentration, not padded with other brands.",
        "- No invented galleries, was/%, or review articles. Product photos wait for Mac L2.",
        "- Accessories (pillowcases, mattress toppers, chair mats/casters, flosser tips-only) stay excluded.",
        "- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    return dest


def inventory_row(cat: dict[str, Any], path: str, picks: list[dict[str, Any]]) -> dict[str, Any]:
    top = next((p for p in picks if p.get("role") == "Top pick"), None)
    upgrade = next((p for p in picks if p.get("role") == "Upgrade"), None)
    return {
        "scene": cat["scene_keyword"],
        "path": "/" + path,
        "density": len(picks),
        "order_asins": [p["asin"] for p in picks],
        "top_pick": top["asin"] if top else None,
        "upgrade": upgrade["asin"] if upgrade else None,
        "tracks": [p["affiliate_link"] for p in picks if p.get("affiliate_link")],
        "new_reviews": [],
        "reused_reviews": [],
        "shortfall": None if picks else "no_healthy_pb_fromsll",
    }


def main() -> None:
    from scaffold_day_add import CONFIRM  # local — after dict patches

    pack = load_fill_pack()
    sitemap_paths: list[str] = []
    inv_pages: list[dict[str, Any]] = []
    slugs: list[str] = []
    by_slug: dict[str, dict[str, Any]] = {}

    for cat in CATS:
        slug = cat["slug"]
        slugs.append(slug)
        scene_picks = scene_picks_from_pack(pack, cat["scene_path"])
        expected = EXPECTED_DENSITY[slug]
        if len(scene_picks) != expected:
            raise SystemExit(
                f"{slug}: pack admitted {len(scene_picks)} healthy tracks, expected {expected}"
            )
        if len(scene_picks) > 10:
            scene_picks = scene_picks[:10]
        main_picks = main_order(scene_picks)
        by_slug[slug] = {"main": main_picks, "scene": scene_picks}
        write_shortlist(cat, main_picks)
        top, bot = COVER_COLORS[slug]
        gradient_jpg(SITE / "assets" / "img" / "lifestyle" / f"cmp-hero-{slug}.jpg", top, bot)
        write_pages(slug, cat["name"], main_picks)
        polish_category_pages(cat, CONFIRM[slug])
        print(f"wrote {slug}/ landing + comparison + reviews hub (density={len(main_picks)})")

        meta = write_scene(cat, scene_picks)
        print(f"wrote {meta['path']}")
        sitemap_paths.extend(
            [
                f"{slug}/",
                f"{slug}/comparison/",
                f"{slug}/reviews/",
                meta["path"],
            ]
        )
        inv_pages.append(inventory_row(cat, meta["path"], scene_picks))

    bump_or_insert_sitemap(sitemap_paths)
    patch_html_sitemap()
    patch_cover_map(slugs)
    inv = write_inventory(inv_pages, by_slug)
    print(f"inventory {inv.relative_to(ROOT)}")
    print("bake_p2_greenfield done (draft only; no Live)")


if __name__ == "__main__":
    main()
