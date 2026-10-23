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
            "This best-of stays empty until a verified retail track exists — we do not invent a padded Top 10."
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
            "This best-of stays empty until a verified retail track exists — we do not invent a padded Top 10."
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
            "This best-of stays empty until a verified retail track exists — we do not invent a padded Top 10."
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


def write_shortlist(cat: dict[str, Any], picks: list[dict[str, Any]]) -> Path:
    slug = cat["slug"]
    notes = [
        f"P2 greenfield {slug} {DATE}. waiting_for_部署上线=yes. No Live.",
        "Healthy PB fromsll only. Density is honest — not padded to 10.",
        "No invented ASINs, prices, images, or was/%. list_price omitted on cards.",
        "No accessories. No new MT10 review articles (none exist on MT10).",
        "Lifestyle cover remains a gradient placeholder.",
        "Sources checked: in-repo shortlists, live moretop10.com/data, public Lab/RR/OL shortlist JSON. None had healthy tracks.",
    ]
    payload = {
        "generated": DATE,
        "slug": slug,
        "name": cat["name"],
        "amazon_category": cat["amazon_category"],
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
        "cta_rule": "PB pboost.me keeps uid=fromsll when a verified track exists; no invented hops",
        "l2": {
            "status": "shortfall",
            "method": "pb_fromsll_only",
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
                "name": p["name"],
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


def scene_faqs(cat: dict[str, Any]) -> list[tuple[str, str]]:
    name = cat["name"].lower()
    scene = cat["scene_keyword"]
    confirm = {
        "pillows": "Confirm loft, fill, and firmness on the retailer page.",
        "mattresses": "Confirm size, firmness, and trial window on the retailer page.",
        "office-chairs": "Confirm lumbar support, weight rating, and seat depth on the retailer page.",
        "water-flossers": "Confirm tank size, pressure settings, and tip count on the retailer page.",
    }[cat["slug"]]
    return [
        (
            f"What does “{scene}” mean on this page?",
            f"It is an editorial slice of the {name} shortlist for this job — not a paid badge. "
            "We only reorder cards that already have a verified retail track.",
        ),
        (
            "Why is this shortlist empty?",
            "We checked in-repo inventory and public shortlist feeds for healthy retail tracks. "
            "None passed. An empty slot beats an invented Top 10.",
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


def scene_article(cat: dict[str, Any], faqs: list[tuple[str, str]]) -> str:
    slug = cat["slug"]
    name = cat["name"]
    scene = cat["scene_keyword"]
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
        f"<p>{escape(scene_faqs(cat)[-1][1])}</p>"
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


def write_scene(cat: dict[str, Any]) -> dict[str, Any]:
    slug = cat["slug"]
    name = cat["name"]
    scene_path = f"{slug}/{cat['scene_path']}/"
    faqs = scene_faqs(cat)
    picks: list[dict] = []
    og = f"{LIVE}/assets/img/lifestyle/cmp-hero-{slug}.jpg"
    meta = {
        "path": scene_path,
        "title": f"{cat['scene_title']} | MoreTop10",
        "h1": cat["scene_h1"],
        "crumb": "Best of",
        "crumb_name": "Best of",
        "scene_label": cat["scene_label"],
        "picks": picks,
        "faqs": faqs,
        "density": 0,
        "article": scene_article(cat, faqs),
        "description": cat["scene_desc"],
        "page_desc": (
            f"Editorial slice of {name.lower()} for {cat['scene_keyword']} — "
            "honest density 0 until a verified retail track exists."
        ),
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


def write_inventory(pages: list[dict[str, Any]]) -> Path:
    dest = DATA / "p2-greenfield-inventory-2026-10-23.json"
    dest.write_text(
        json.dumps({"date": DATE, "waiting_for_部署上线": True, "pages": pages}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    md = DATA / "p2-greenfield-inventory-2026-10-23.md"
    lines = [
        "# P2 MT10 greenfield inventory (2026-10-23)",
        "",
        "**waiting_for_部署上线:** yes",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
        "**Do not touch:** ceramic P1c #40 files, blog hub, authors CSS (beyond coexistence).",
        "",
    ]
    for cat in CATS:
        lines += [
            f"## /{cat['slug']}/",
            "",
            "- Type: new plural main category (landing + comparison + reviews hub)",
            "- Density: 0 (honest shortfall; not padded to 10)",
            "- Comparison order: (none)",
            "- Top pick: none",
            "- Upgrade: none",
            "- New reviews: none (MT10 review articles do not exist)",
            "- Tracks: none",
            "- Sources checked: in-repo shortlists; live moretop10.com/data; public Lab/RR/OL shortlist JSON. All 404 or empty for this slug.",
            "",
            f"## /{cat['slug']}/{cat['scene_path']}/",
            "",
            f"- Scene: {cat['scene_keyword']}",
            "- Density: 0 (scene page exists; no cards to reorder)",
            "- Top pick: none — review skipped",
            "- Upgrade: none — review skipped",
            "- New reviews: none",
            "- Tracks: none",
            "",
        ]
    lines += [
        "## Shortfalls (honest)",
        "",
        "- Density is 0 healthy PB fromsll cards per category, not a padded Top 10. No invented ASINs, prices, images, or was/%.",
        "- PARTNERBOOST_API_TOKEN is unset in this environment, so get_fba_products was not used to invent a catalog.",
        "- Accessories (pillowcases, mattress toppers, chair mats/casters, flosser tips-only) stay excluded.",
        "- Reviews: skipped. Existing type-07 chrome does not require new review HTML when reviews do not exist.",
        "- Lab `/shortlists/*` paths from the locked batch are out of scope (MT10 draft only).",
        "- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    return dest


def inventory_row(cat: dict[str, Any], path: str) -> dict[str, Any]:
    return {
        "scene": cat["scene_keyword"],
        "path": "/" + path,
        "density": 0,
        "order_asins": [],
        "top_pick": None,
        "upgrade": None,
        "tracks": [],
        "new_reviews": [],
        "reused_reviews": [],
        "shortfall": "no_healthy_pb_fromsll",
    }


def main() -> None:
    from scaffold_day_add import CONFIRM  # local — after dict patches

    sitemap_paths: list[str] = []
    inv_pages: list[dict[str, Any]] = []
    slugs: list[str] = []

    for cat in CATS:
        slug = cat["slug"]
        slugs.append(slug)
        picks: list[dict[str, Any]] = []
        for row in cat["feed"]:
            track = healthy_track(row.get("affiliate_link"))
            if not track:
                continue
            picks.append(row)
        if len(picks) > 10:
            picks = picks[:10]
        write_shortlist(cat, picks)
        top, bot = COVER_COLORS[slug]
        gradient_jpg(SITE / "assets" / "img" / "lifestyle" / f"cmp-hero-{slug}.jpg", top, bot)
        write_pages(slug, cat["name"], picks)
        polish_category_pages(cat, CONFIRM[slug])
        print(f"wrote {slug}/ landing + comparison + reviews hub (density={len(picks)})")

        meta = write_scene(cat)
        print(f"wrote {meta['path']}")
        sitemap_paths.extend(
            [
                f"{slug}/",
                f"{slug}/comparison/",
                f"{slug}/reviews/",
                meta["path"],
            ]
        )
        inv_pages.append(inventory_row(cat, meta["path"]))

    bump_or_insert_sitemap(sitemap_paths)
    patch_html_sitemap()
    patch_cover_map(slugs)
    inv = write_inventory(inv_pages)
    print(f"inventory {inv.relative_to(ROOT)}")
    print("bake_p2_greenfield done (draft only; no Live)")


if __name__ == "__main__":
    main()
