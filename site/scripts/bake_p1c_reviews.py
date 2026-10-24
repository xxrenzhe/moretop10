#!/usr/bin/env python3
"""Bake P1c Top pick + Upgrade deep reviews from in-repo SoT only.

Draft only. No wrangler / no Live deploy. No Lab / RR / OL edits.
No Gemini — GEMINI_API_KEY is not required. Copy is authored from
shortlist/L2/landing titles, bullets, and P1c ceramic inventory.
Do not invent specs, was/%, ratings, awards, or ASINs.

Creates three unique `/{cat}/reviews/{slug}/` files (ceramic has no
existing review HTML) by cloning category chrome, then reusing the
review gallery / facts-bar / mid-cta pattern with the one SoT packshot
and the live `pboost.me?uid=fromsll` track.

Usage:
    python3 site/scripts/bake_p1c_reviews.py
"""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from bake_p1c_ceramic import (  # noqa: E402
    BY_ASIN,
    DATE,
    NAME,
    SLUG,
    bump_or_insert_sitemap,
    clone_chrome,
    healthy_track,
    score_for,
    ul_from_amazon,
)
from chrome import rewrite_compare_cta  # noqa: E402
from seo_geo import LIVE, apply_hub_page, dumps_ld  # noqa: E402
from site_config import load_site_config  # noqa: E402

DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P1c deep reviews draft only. "
    "Do not merge. Do not Cloudflare Live deploy. -->"
)
from stamp_guard import bake_stamp_date  # noqa: E402

CHECKED = bake_stamp_date("2026-10-20")
TIP_SHA = "f23596ced1a4681996736db1baa01e242680e01b79ebb6357a0b9edecef3307d"


def _esc(text: str) -> str:
    return escape(text or "", quote=False)


def _qa(href: str, label: str) -> str:
    return f'<a href="{escape(href, quote=True)}">{_esc(label)}</a>'


def insights_html(items: list[tuple[str, str]]) -> str:
    lis = "".join(
        f"<li><strong>{_esc(title)}:</strong> {_esc(body)}</li>" for title, body in items
    )
    return (
        '<section class="key-insights prose-block" aria-label="Key insights">'
        f"<h2>Key insights</h2><ul class=\"card-bullets\">{lis}</ul></section>"
    )


def pros_cons_html(name: str, pros: list[str], cons: list[str]) -> str:
    p = "".join(f"<li>{_esc(x)}</li>" for x in pros)
    c = "".join(f"<li>{_esc(x)}</li>" for x in cons)
    return (
        '<section class="review-section">'
        f"<h2>Should you buy the {_esc(name)}?</h2>"
        '<div class="pros-cons review-pros-cons">'
        f'<div><div class="pc-col-title pros">Pros</div><ul>{p}</ul></div>'
        f'<div><div class="pc-col-title cons">Cons</div><ul>{c}</ul></div>'
        "</div></section>"
    )


def section_html(title: str, body: str) -> str:
    return f'<section class="review-section"><h2>{_esc(title)}</h2>{body}</section>'


def faq_html(name: str, pairs: list[tuple[str, str]]) -> str:
    bits = [
        f'<section class="review-section review-faq"><h2>FAQ: {_esc(name)}</h2>'
        '<div class="faq">'
    ]
    for i, (q, a) in enumerate(pairs):
        open_attr = " open" if i == 0 else ""
        bits.append(
            f"<details{open_attr}><summary>{_esc(q)}</summary><p>{_esc(a)}</p></details>"
        )
    bits.append("</div></section>")
    return "".join(bits)


def faq_ld(pairs: list[tuple[str, str]]) -> str:
    return dumps_ld(
        {
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
    )


def how_we_html(score_line: str, checked: str) -> str:
    return section_html(
        "How we evaluated this product",
        "<ul class=\"review-bullets\">"
        "<li>We only publish products with a title, gallery, and price snapshot.</li>"
        f"<li>Scores map from retailer ratings when available ({_esc(score_line)}). "
        "Rank order follows score—not paid awards.</li>"
        f"<li>Last verified {_esc(checked)}. Prices and stock move—always re-check at the retailer.</li>"
        "</ul>"
        "<p>For live scores and neighboring ranks, open the category comparison. "
        "Deep reviews expand the card with context that does not fit in a ranking row.</p>",
    )


def next_html(links: list[tuple[str, str]], cta: tuple[str, str], extra: str) -> str:
    row = (
        f'<p class="review-cta-row">'
        f'<a class="btn btn-primary" href="{escape(cta[0], quote=True)}">{_esc(cta[1])}</a> '
        f'<a class="btn btn-ghost btn-sm" href="{escape(links[0][0], quote=True)}">{_esc(links[0][1])}</a>'
        "</p>"
    )
    cluster = " · ".join(_qa(href, label) for href, label in links)
    return section_html(
        "Next steps",
        f"<p>{extra} Related: {cluster}.</p>{row}",
    )


_DEPTH2_ATTR_RE = re.compile(r'(?P<attr>href|src)="\.\./\.\./(?!\.\./)')
_TEMPLATE_LD_RE = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>',
    re.S,
)
HUB_SLOT_ORDER = (
    (f"/{SLUG}/", "Top pick"),
    (f"/{SLUG}/", "Upgrade"),
    (f"/{SLUG}/best-ceramic-space-heaters-for-large-rooms/", "Top pick"),
    (f"/{SLUG}/best-ceramic-space-heaters-for-large-rooms/", "Upgrade"),
    (f"/{SLUG}/best-ceramic-space-heaters-for-garages/", "Top pick"),
    (f"/{SLUG}/best-ceramic-space-heaters-for-garages/", "Upgrade"),
)


def strip_template_ld(html: str) -> str:
    """Keep Organization JSON-LD; drop humidifier bedroom leftovers."""

    def keep_org(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return "" if "humidifier" in match.group(1).lower() else match.group(0)
        return match.group(0) if data.get("@type") == "Organization" else ""

    return _TEMPLATE_LD_RE.sub(keep_org, html)


def fix_chrome_depth(html: str) -> str:
    """Rewrite leftover depth-2 chrome prefixes. Do not touch <main>."""
    start = html.find("<main")
    end = html.rfind("</main>")
    if start < 0 or end < 0:
        raise SystemExit("clone chrome missing <main>")
    end += len("</main>")
    before, main, after = html[:start], html[start:end], html[end:]

    def rewrite(chunk: str) -> str:
        chunk = chunk.replace('href="../../index.html"', 'href="../../../"')
        return _DEPTH2_ATTR_RE.sub(r'\g<attr>="../../../', chunk)

    return rewrite(before) + main + rewrite(after)


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return '<ul class="review-bullets">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def desc_trunc(text: str, n: int = 155) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rsplit(" ", 1)[0] + "…"


def score_label(score: str) -> str:
    n = float(score)
    if n >= 9.0:
        return f"{score} Excellent"
    if n >= 8.0:
        return f"{score} Very good"
    return score


def star_chars(rating: float) -> str:
    filled = min(5, int(rating + 0.5))
    return ("★" * filled) + ("☆" * (5 - filled))


def amazon_srcset(src: str) -> tuple[str, str, str]:
    return ul_from_amazon(src, 160), ul_from_amazon(src, 320), ul_from_amazon(src, 480)


def packshot_img(src: str, alt: str, width: int, sizes_px: str, cls: str) -> str:
    u160, u320, u480 = amazon_srcset(src)
    return (
        f'<img class="{cls}" src="{escape(u480 if width >= 300 else u320, quote=True)}" '
        f'alt="{escape(alt, quote=True)}" width="{width}" height="{width}" '
        f'srcset="{escape(u160, quote=True)} 160w, {escape(u320, quote=True)} 320w, '
        f'{escape(u480, quote=True)} 480w" sizes="{sizes_px}" loading="lazy" '
        f'decoding="async" referrerpolicy="no-referrer"/>'
    )


def gallery_html(src: str, alt: str) -> str:
    return f'<div class="review-gallery">{packshot_img(src, alt, 140, "140px", "thumb")}</div>'


def mid_cta_html(src: str, alt: str, name: str, track: str) -> str:
    return (
        '<div class="review-mid-cta">'
        f"{packshot_img(src, alt, 300, '300px', 'review-hero-img')}"
        f'<strong class="review-mid-name">{_esc(name)}</strong>'
        f'<a class="btn btn-cta-yellow" href="{escape(track, quote=True)}" '
        f'rel="sponsored noopener noreferrer" target="_blank"><span>Check price</span></a>'
        "</div>"
    )


def facts_bar(price: str, score_line: str, reviews: int) -> str:
    return (
        '<div class="review-facts-bar"><div class="container review-facts">'
        '<div class="review-fact"><span class="review-fact-check" aria-hidden="true">✓</span>'
        f"<div><strong>Price snapshot</strong><span>${_esc(price)}"
        f'<span class="review-price-checked"> · checked {CHECKED}</span></span></div></div>'
        '<div class="review-fact"><span class="review-fact-check" aria-hidden="true">✓</span>'
        f"<div><strong>Chart score</strong><span>{_esc(score_line)}</span></div></div>"
        '<div class="review-fact"><span class="review-fact-check" aria-hidden="true">✓</span>'
        f"<div><strong>Retailer reviews</strong><span>{reviews:,} reviews</span></div></div>"
        "</div></div>"
    )


def render_main(review: dict[str, Any], gallery: str, mid_cta: str) -> str:
    parts = [
        f'<p class="review-summary">{_esc(review["summary"])}</p>',
        insights_html(review["insights"]),
        gallery,
        pros_cons_html(review["short_name"], review["pros"], review["cons"]),
        mid_cta,
    ]
    for title, body in review["sections"]:
        parts.append(section_html(title, body))
    parts.append(how_we_html(review["score_line"], review["checked"]))
    parts.append(faq_html(review["short_name"], review["faqs"]))
    parts.append(next_html(review["cluster"], review["cta"], review["next_extra"]))
    return "".join(parts)


def sidebar_html(review: dict[str, Any]) -> str:
    rows = []
    for sibling in review["siblings"]:
        rows.append(
            '<div class="ed-rev-row"><div class="ed-rev-text">'
            f"<strong>{_esc(sibling['name'])}</strong>"
            f'<a href="../{escape(sibling["slug"], quote=True)}/">Read Review</a>'
            "</div></div>"
        )
    picks = "".join(
        f'<li><a href="{escape(href, quote=True)}">{_esc(label)}</a>'
        f'<span class="ed-pick-date">{DATE}</span></li>'
        for href, label in review["editor_picks"]
    )
    return (
        '<aside class="review-side sticky-side">'
        '<aside class="ed-reviews-sidebar"><h3>Editorial Reviews</h3>'
        f'<div class="ed-rev-list">{"".join(rows)}</div></aside>'
        '<aside class="editors-picks-widget"><h3>Editor\'s Picks</h3>'
        f'<ul class="ed-picks-list">{picks}</ul>'
        f'<p class="sidebar-more"><a href="../../">Category overview →</a></p>'
        "</aside></aside>"
    )


def review_main_shell(review: dict[str, Any], feed: dict[str, Any]) -> str:
    track = review["track"]
    title = feed["title"]
    image = feed["image"]
    rating = float(feed["rating"])
    score = score_for(rating)
    label = review["score_line"]
    gallery = gallery_html(image, title)
    mid = mid_cta_html(image, title, review["short_name"], track)
    hero_img = packshot_img(image, title, 300, "300px", "review-hero-img")
    return (
        f'<main class="product-review-page">'
        f'<span class="geo-anchor" id="geo-{review["asin"]}" tabindex="-1"></span>'
        '<div class="review-hero-band"><div class="container review-hero-grid">'
        '<div class="review-hero-copy-col">'
        '<nav class="breadcrumb"><a href="../../../">Home</a> <span class="sep">/</span> '
        f'<a href="../../../{SLUG}/">{_esc(NAME)}</a> <span class="sep">/</span> '
        f'<a href="../">Reviews</a> <span class="sep">/</span> <span>{_esc(title)}</span></nav>'
        '<header class="page-head review-head">'
        f'<p class="badge">{_esc(review["badge"])}</p>'
        f"<h1>{_esc(title)}</h1>"
        '<div class="author-byline"><div class="author-avatar" aria-hidden="true">PN</div>'
        '<div class="author-meta">'
        '<span class="author-name">Written by '
        '<a class="author-name-link" href="../../../authors/priya-nair/">Priya Nair</a></span>'
        f'<span class="author-updated">Last Updated: {DATE}</span>'
        "</div></div>"
        f'<div class="meta-row"><span class="stars" aria-label="{rating} out of 5">'
        f"{star_chars(rating)}</span> "
        f'<span class="meta-score">{_esc(label)}</span> '
        f'<span class="meta-price">${_esc(feed["price"])}</span></div>'
        "</header></div>"
        '<aside class="review-cta-card">'
        f"{hero_img}"
        f'<a class="btn btn-cta-yellow review-cta-card-btn" href="{escape(track, quote=True)}" '
        'rel="sponsored noopener noreferrer" target="_blank"><span>Check price</span></a>'
        f'<a class="review-cta-card-link" href="../../comparison/">See comparison →</a>'
        "</aside></div></div>"
        f'{facts_bar(feed["price"], label, int(feed["review_count"]))}'
        '<div class="container review-body layout-sidebar">'
        f'<div class="review-main">{render_main(review, gallery, mid)}</div>'
        f"{sidebar_html(review)}"
        "</div></main>"
    )


def replace_main_block(html: str, new_main: str) -> str:
    start = html.find("<main")
    end = html.rfind("</main>")
    if start < 0 or end < 0:
        raise SystemExit("clone chrome missing <main>")
    return html[:start] + new_main + html[end + len("</main>") :]


def patch_review_head(html: str, review: dict[str, Any], feed: dict[str, Any]) -> str:
    url = f"{LIVE}/{SLUG}/reviews/{review['slug']}/"
    title = f"{feed['title']} Review | MoreTop10"
    desc = desc_trunc(review["summary"])
    html = re.sub(r"<title>.*?</title>", f"<title>{_esc(title)}</title>", html, count=1)
    html = re.sub(
        r'<meta name="description" content="[^"]*"/>',
        f'<meta name="description" content="{escape(desc, quote=True)}"/>',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]*"/>',
        f'<link rel="canonical" href="{escape(url, quote=True)}"/>',
        html,
        count=1,
    )
    for prop, val in (
        ("og:title", title),
        ("og:description", desc),
        ("og:url", url),
        ("og:image", feed["image"]),
        ("og:type", "article"),
        ("twitter:title", title),
        ("twitter:description", desc),
        ("twitter:url", url),
        ("twitter:image", feed["image"]),
    ):
        attr = "property" if prop.startswith("og:") else "name"
        html = re.sub(
            rf'<meta {attr}="{prop}" content="[^"]*"/>',
            f'<meta {attr}="{prop}" content="{escape(val, quote=True)}"/>',
            html,
            count=1,
        )
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"{feed['title']} Review",
        "description": review["summary"],
        "dateModified": DATE,
        "author": {"@type": "Organization", "name": "MoreTop10", "url": f"{LIVE}/"},
        "publisher": {
            "@type": "Organization",
            "name": "MoreTop10",
            "url": f"{LIVE}/",
            "logo": f"{LIVE}/icon-512.png",
        },
        "mainEntityOfPage": url,
        "mainEntity": {
            "@type": "Product",
            "name": feed["title"],
            "brand": {"@type": "Brand", "name": feed["brand"]},
            "sku": review["asin"],
            "image": feed["image"],
            "description": review["summary"],
            "offers": {
                "@type": "Offer",
                "url": review["track"],
                "price": feed["price"],
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
            },
        },
        "url": url,
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{LIVE}/"},
            {"@type": "ListItem", "position": 2, "name": NAME, "item": f"{LIVE}/{SLUG}/"},
            {"@type": "ListItem", "position": 3, "name": "Reviews", "item": f"{LIVE}/{SLUG}/reviews/"},
            {"@type": "ListItem", "position": 4, "name": feed["title"], "item": url},
        ],
    }
    blobs = (
        f'<script type="application/ld+json">{dumps_ld(crumbs)}</script>\n'
        f'<script type="application/ld+json">{dumps_ld(article)}</script>\n'
        f'<script type="application/ld+json">{faq_ld(review["faqs"])}</script>\n'
    )
    html = html.replace("</head>", blobs + "</head>", 1)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    return html


# --- SoT-bounded review payloads (shortlist / L2 / landing / P1c inventory) ---

REVIEWS: list[dict[str, Any]] = [
    {
        "asin": "B0C6FFK1GV",
        "slug": "dreo-space-heater-portable-electric-remote",
        "short_name": "DREO white remote 34dB heater",
        "badge": "Top pick",
        "slots": [
            (f"/{SLUG}/", "Top pick"),
        ],
        "checked": CHECKED,
        "score_line": "8.8 Very good on this card",
        "summary": (
            "The white DREO remote heater is the Top pick on our ceramic space heaters "
            "shortlist when you want 34dB quiet heat for a bedroom or office plus a remote, "
            "ECO, child lock, and a 41–95°F thermostat from the listing we checked. "
            "It is a 1500W PTC ceramic unit with tilt-detection tip-over protection and a "
            "reminder to plug directly into a wall outlet. Skip it if you need 70° oscillation, "
            "or if the lowest verified snapshot on this list (Best value Gold) is the only job."
        ),
        "insights": [
            (
                "Category Top pick, not a scene lead",
                "The landing leads here for quiet bedside and office heat. Large-room and garage slices demote this compact stack and keep it as a neighbor.",
            ),
            (
                "34dB quiet heat on the listing",
                "The live feature list quotes 34dB quiet heat for bedrooms and offices. We do not invent a second noise number.",
            ),
            (
                "Remote stack already on the card",
                "1500W PTC ceramic heat ships with a remote, ECO, child lock, and a 41–95°F thermostat on the listing we checked.",
            ),
            (
                "Tip-over and wall-outlet copy",
                "The card names tilt-detection tip-over protection and tells you to plug directly into a wall outlet.",
            ),
            (
                "Oscillation is the Upgrade fork",
                "This listing does not claim 70° wide-angle oscillation. Atom One is the category Upgrade when a sweep for garage, basement, or office is the job.",
            ),
            (
                "Price and score snapshot",
                f"Chart score 8.8 from a 4.4 retailer rating across 21,514 reviews. Price snapshot $39.99, checked {CHECKED}.",
            ),
        ],
        "pros": [
            "Category Top pick for 34dB quiet heat with a remote, ECO, child lock, and a 41–95°F thermostat.",
            "1500W PTC ceramic heat plus tilt-detection tip-over protection on the listing.",
            "Wall-outlet reminder is already on the card — confirm the live listing via Check price.",
        ],
        "cons": [
            "Skip it if you need 70° oscillation for a garage, basement, or larger sweep.",
            "Skip it if the lowest verified snapshot (Best value Gold) is the only job.",
        ],
        "sections": [
            (
                "Who should skip this white remote heater?",
                ul(
                    [
                        "Skip it if you need 70° wide-angle oscillation. Atom One is the category Upgrade and the garage Top pick for that sweep.",
                        "Skip it if the lowest verified snapshot is the only job. Best value Gold keeps the same 34dB / 1500W / 41–95°F remote stack at a lower check.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like with a compact 34dB stack?",
                p(
                    "Plan on a wall outlet, not an extension cord. The listing’s tilt-detection tip-over line is the ownership cue: keep the unit where a bump will shut it off, and confirm child lock if the room is shared."
                )
                + p(
                    "ECO and the 41–95°F thermostat are the listing’s set-and-forget pitch. We do not invent a filter, a runtime hour, or a wattage beyond 1500W. If you will not use the remote, Gold is the cheaper same-stack neighbor."
                ),
            ),
            (
                "How quiet is this versus Atom One?",
                p(
                    "This card quotes 34dB for bedrooms and offices. Atom One quotes 37.5dB and adds 70° oscillation. Stay here when bedside quiet is the priority; step up when a sweep matters more than two extra decibels on the listing."
                ),
            ),
            (
                "Why is this the category Top pick instead of the oscillation Upgrade?",
                p(
                    "The landing leads with quiet remote heat for most bedrooms and offices. Atom One is the Upgrade when the listing’s 70° sweep for garage, basement, and office is the job you actually have."
                )
                + p(
                    "Read the "
                    + _qa("../dreo-atom-one-space-heater-thermostat/", "Atom One review")
                    + " or return to the "
                    + _qa("../../", "ceramic space heaters landing")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the white DREO remote heater?",
                "Skip it if you need 70° oscillation, or if the lowest verified Gold snapshot is the only job. Those are the Atom One Upgrade and the Best value neighbor.",
            ),
            (
                "Does the listing name a noise level?",
                "Yes. The feature list quotes 34dB quiet heat for bedrooms and offices. Confirm the live listing via Check price. We do not invent a second measurement.",
            ),
            (
                "What controls are on this card?",
                "The listing pairs 1500W PTC ceramic heat with a remote, ECO, child lock, and a 41–95°F thermostat, plus tilt-detection tip-over protection.",
            ),
            (
                "When should I step to Atom One?",
                "Step to Atom One when you want 70° wide-angle oscillation the white card does not list. That review is the category Upgrade and the garage Top pick.",
            ),
        ],
        "next_extra": (
            "If you need a 70° sweep, read the Atom One Upgrade. "
            "If coverage language matters more than a compact stack, open the large-room Premium review."
        ),
        "cluster": [
            ("../", "All ceramic heater reviews"),
            ("../../comparison/", "Ceramic space heaters comparison"),
            ("../../", "Category landing"),
            ("../dreo-atom-one-space-heater-thermostat/", "Atom One review"),
        ],
        "siblings": [
            {"name": "DREO Atom One 70° oscillation", "slug": "dreo-atom-one-space-heater-thermostat"},
            {"name": "DREO 270 sq.ft Premium", "slug": "dreo-space-heaters-indoor-thermostat-1500w"},
        ],
        "editor_picks": [
            ("../../comparison/", "Comparison chart"),
            ("../../best-ceramic-space-heaters-for-large-rooms/", "Best for large rooms"),
            ("../../best-ceramic-space-heaters-for-garages/", "Best for garages"),
        ],
        "cta": ("../../comparison/", "Back to Ceramic Space Heaters comparison"),
    },
    {
        "asin": "B097RG67QB",
        "slug": "dreo-atom-one-space-heater-thermostat",
        "short_name": "DREO Atom One 70° oscillation",
        "badge": "Upgrade",
        "slots": [
            (f"/{SLUG}/", "Upgrade"),
            (f"/{SLUG}/best-ceramic-space-heaters-for-large-rooms/", "Upgrade"),
            (f"/{SLUG}/best-ceramic-space-heaters-for-garages/", "Top pick"),
        ],
        "checked": CHECKED,
        "score_line": "9.2 Excellent on this card",
        "summary": (
            "DREO Atom One is the Upgrade on the category shortlist when you want 70° "
            "wide-angle oscillation the white Top pick does not list. The same card is "
            "Top pick on our garage best-of because the listing names garage, basement, "
            "office, and desktop coverage. The listing quotes 37.5dB with ECO, a 41–95°F "
            "digital thermostat, and Shield360 tip-over plus overheat protection. Skip it "
            "if you do not need oscillation, or if 34dB bedside quiet is the priority."
        ),
        "insights": [
            (
                "Category Upgrade, garage Top pick",
                "One article covers three recommend slots. The landing and large-room slice use this as Upgrade for the 70° sweep; the garage slice leads here because the listing names garage coverage.",
            ),
            (
                "70° sweep is the fork",
                "The live feature list states 70° wide-angle oscillation for bedroom, garage, basement, office, and desktop. The compact white and Gold cards do not list that sweep.",
            ),
            (
                "37.5dB on the listing",
                "The card quotes 37.5dB. The white Top pick quotes 34dB. Stay with white when two quieter decibels matter more than oscillation.",
            ),
            (
                "Shield360 plus overheat",
                "The listing names Shield360 tip-over and overheat protection with 1500W PTC heat, ECO, and a 41–95°F digital thermostat.",
            ),
            (
                "Premium is the coverage step",
                "Pay the large-room card when you want a 270 sq.ft claim plus the same 70° sweep. Atom One does not list that square-footage line.",
            ),
            (
                "Price and score snapshot",
                f"Chart score 9.2 from a 4.6 retailer rating across 29,035 reviews. Price snapshot $44.94, checked {CHECKED}.",
            ),
        ],
        "pros": [
            "Category and large-room Upgrade when 70° oscillation is the job the white card does not list.",
            "Garage Top pick because the listing names garage, basement, office, and desktop coverage.",
            "1500W PTC heat with ECO, a 41–95°F digital thermostat, 37.5dB, and Shield360 tip-over plus overheat protection.",
        ],
        "cons": [
            "Skip it if you do not need oscillation, or if 34dB bedside quiet is the priority.",
            "Skip it if you want a 270 sq.ft coverage claim — that is the Premium large-room card.",
        ],
        "sections": [
            (
                "Who should skip this Atom One Upgrade?",
                ul(
                    [
                        "Skip it if you do not need oscillation, or if 34dB bedside quiet is the priority. The white remote card is the category Top pick for that job.",
                        "Skip it if you want a 270 sq.ft claim. The Premium large-room card is the coverage Upgrade on garages and the Top pick on the large-room slice.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like with a 70° oscillating heater?",
                p(
                    "Give the sweep room. The listing names bedroom, garage, basement, office, and desktop — a corner that blocks the 70° arc wastes the Upgrade. Confirm Shield360 tip-over and overheat copy still appear on the retailer page via Check price."
                )
                + p(
                    "ECO and the 41–95°F digital thermostat are the set-and-forget line. We do not invent a garage insulation rating or a wattage beyond 1500W. If the space is a finished bedroom, the quieter white card is enough."
                ),
            ),
            (
                "How should I read garage language versus a 270 sq.ft claim?",
                p(
                    "This listing names garage, basement, and office coverage with 70° oscillation. It does not state 270 sq.ft. The Premium card adds that coverage claim plus the same sweep, 34dB, and a 24-hour auto-off. Lead here for a typical garage; pay Premium when the claimed square footage is the constraint."
                ),
            ),
            (
                "Why is this Upgrade on the landing and Top pick in a garage?",
                p(
                    "The category leads with quiet remote heat. A garage slice leads with cards that already name garage coverage or a 70° sweep. Same SKU, two jobs — one article."
                )
                + p(
                    "Read the "
                    + _qa("../dreo-space-heater-portable-electric-remote/", "white remote review")
                    + " or the "
                    + _qa("../dreo-space-heaters-indoor-thermostat-1500w/", "Premium 270 sq.ft review")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip DREO Atom One?",
                "Skip it if you do not need 70° oscillation, or if 34dB bedside quiet is the priority. The white remote card is the category Top pick for that job.",
            ),
            (
                "Does the listing name garage use?",
                "Yes. The feature list names bedroom, garage, basement, office, and desktop with 70° wide-angle oscillation. Confirm the live listing via Check price.",
            ),
            (
                "How is this different from the 270 sq.ft Premium card?",
                "Both list 70° oscillation. Premium adds a 270 sq.ft coverage claim, 34dB, and a 24-hour auto-off. Atom One does not list that square-footage line.",
            ),
            (
                "Why is this Top pick on the garage slice?",
                "The garage best-of leads with cards whose listings already name garage coverage or 70° oscillation. The white category Top pick does not list either, so this card moves first there.",
            ),
        ],
        "next_extra": (
            "If you do not need oscillation, read the white remote Top pick. "
            "If you want a 270 sq.ft claim, read the Premium large-room review."
        ),
        "cluster": [
            ("../", "All ceramic heater reviews"),
            ("../../comparison/", "Ceramic space heaters comparison"),
            ("../../best-ceramic-space-heaters-for-garages/", "Best for garages"),
            ("../../best-ceramic-space-heaters-for-large-rooms/", "Best for large rooms"),
            ("../dreo-space-heaters-indoor-thermostat-1500w/", "Premium 270 sq.ft review"),
        ],
        "siblings": [
            {"name": "DREO white remote 34dB heater", "slug": "dreo-space-heater-portable-electric-remote"},
            {"name": "DREO 270 sq.ft Premium", "slug": "dreo-space-heaters-indoor-thermostat-1500w"},
        ],
        "editor_picks": [
            ("../../comparison/", "Comparison chart"),
            ("../../best-ceramic-space-heaters-for-large-rooms/", "Best for large rooms"),
            ("../../best-ceramic-space-heaters-for-garages/", "Best for garages"),
        ],
        "cta": ("../../comparison/", "Back to Ceramic Space Heaters comparison"),
    },
    {
        "asin": "B095PP1GZR",
        "slug": "dreo-space-heaters-indoor-thermostat-1500w",
        "short_name": "DREO 270 sq.ft Premium heater",
        "badge": "Top pick",
        "slots": [
            (f"/{SLUG}/best-ceramic-space-heaters-for-large-rooms/", "Top pick"),
            (f"/{SLUG}/best-ceramic-space-heaters-for-garages/", "Upgrade"),
        ],
        "checked": CHECKED,
        "score_line": "9.0 Excellent on this card",
        "summary": (
            "The DREO 1500W large-room heater is Top pick on our large-room best-of when "
            "the listing’s 270 sq.ft claim plus 70° oscillation matters more than a compact "
            "bedside stack. It is also the garage Upgrade when you want that coverage claim "
            "on top of the same sweep Atom One already lists for garages and basements. "
            "Skip it if you only need a compact bedroom or desk heater."
        ),
        "insights": [
            (
                "Large-room Top pick, garage Upgrade",
                "One article covers two recommend slots. The large-room slice leads here for the 270 sq.ft line; the garage slice uses it as Upgrade when claimed coverage beats Atom One’s sweep-only card.",
            ),
            (
                "270 sq.ft is the listing claim",
                "The live feature list states 270 sq.ft heating coverage with 1500W PTC ceramic heat. We do not invent a second square-footage number.",
            ),
            (
                "Same 70° sweep as Atom One",
                "The card lists 70° wide-angle oscillation and names bedrooms, basements, and garages. Atom One lists the same sweep without the 270 sq.ft claim.",
            ),
            (
                "34dB plus 24-hour auto-off",
                "The listing quotes 34dB quiet heat, a 24-hour auto-off, and a reminder not to use an extension cord. Scene copy also names a 6ft flat cord.",
            ),
            (
                "Compact 34dB cards stay neighbors",
                "The white remote and Gold cards share a quiet bedside stack. They stay last on both slices so we do not invent garage or large-room coverage for them.",
            ),
            (
                "Price and score snapshot",
                f"Chart score 9.0 from a 4.5 retailer rating across 15,432 reviews. Price snapshot $67.46, checked {CHECKED}.",
            ),
        ],
        "pros": [
            "Large-room Top pick for a 270 sq.ft claim plus 70° oscillation and 1500W PTC ceramic heat.",
            "Garage Upgrade when you want that coverage line on top of sweep language Atom One already lists.",
            "34dB quiet heat, 24-hour auto-off, and a reminder not to use an extension cord on the listing.",
        ],
        "cons": [
            "Skip it if you only need a compact bedroom or desk heater.",
            "Skip it if 70° oscillation without a 270 sq.ft claim is enough — that is Atom One.",
        ],
        "sections": [
            (
                "Who should skip this 270 sq.ft Premium card?",
                ul(
                    [
                        "Skip it if you only need a compact bedroom or desk heater. The white remote card is the category Top pick for that job.",
                        "Skip it if 70° oscillation without a 270 sq.ft claim is enough. Atom One is the cheaper sweep Upgrade on the landing and the garage Top pick.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like on a large-room ceramic heater?",
                p(
                    "Plan a wall outlet and cord path. The listing reminds you not to use an extension cord and scene copy names a 6ft flat cord — measure the outlet before you treat 270 sq.ft as a floor plan."
                )
                + p(
                    "The 24-hour auto-off is the listing’s overnight shutoff. We do not invent a runtime beyond that line. If the room is closer to a bedroom than a living room, the compact 34dB stack is the lighter daily job."
                ),
            ),
            (
                "How should I read 270 sq.ft versus Atom One’s garage language?",
                p(
                    "This is the only card on the shortlist that states 270 sq.ft coverage plus 70° oscillation. Atom One lists the same sweep for garage, basement, and office without that square-footage claim. Lead here when claimed coverage is the constraint; stay with Atom One when the sweep is enough."
                ),
            ),
            (
                "Why is this Top pick on large rooms and Upgrade in a garage?",
                p(
                    "A large-room slice leads with the only 270 sq.ft claim. A garage slice already has Atom One naming garage coverage, so this card is the coverage Upgrade there — not a second copy of the category Top 4."
                )
                + p(
                    "Read the "
                    + _qa("../dreo-atom-one-space-heater-thermostat/", "Atom One review")
                    + " or return to the "
                    + _qa("../../best-ceramic-space-heaters-for-large-rooms/", "large-room best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the DREO 270 sq.ft heater?",
                "Skip it if you only need a compact bedroom or desk heater, or if 70° oscillation without a 270 sq.ft claim is enough. Those are the white remote card and Atom One.",
            ),
            (
                "What coverage does the listing claim?",
                "The feature list states 270 sq.ft heating coverage with 1500W PTC ceramic heat and 70° wide-angle oscillation. Confirm the live listing via Check price.",
            ),
            (
                "Does this card name garages?",
                "Yes. The listing names bedrooms, basements, and garages with the 70° sweep, plus a reminder not to use an extension cord.",
            ),
            (
                "When should I stay with Atom One?",
                "Stay with Atom One when the 70° sweep and garage language are enough and you do not need the 270 sq.ft claim. That card is the garage Top pick and the category Upgrade.",
            ),
        ],
        "next_extra": (
            "If you do not need the 270 sq.ft claim, read the Atom One review. "
            "If the room is a bedroom, read the white remote Top pick."
        ),
        "cluster": [
            ("../", "All ceramic heater reviews"),
            ("../../comparison/", "Ceramic space heaters comparison"),
            ("../../best-ceramic-space-heaters-for-large-rooms/", "Best for large rooms"),
            ("../../best-ceramic-space-heaters-for-garages/", "Best for garages"),
            ("../dreo-atom-one-space-heater-thermostat/", "Atom One review"),
        ],
        "siblings": [
            {"name": "DREO Atom One 70° oscillation", "slug": "dreo-atom-one-space-heater-thermostat"},
            {"name": "DREO white remote 34dB heater", "slug": "dreo-space-heater-portable-electric-remote"},
        ],
        "editor_picks": [
            ("../../comparison/", "Comparison chart"),
            ("../../best-ceramic-space-heaters-for-large-rooms/", "Best for large rooms"),
            ("../../best-ceramic-space-heaters-for-garages/", "Best for garages"),
        ],
        "cta": ("../../comparison/", "Back to Ceramic Space Heaters comparison"),
    },
]


def attach_tracks() -> None:
    for review in REVIEWS:
        feed = BY_ASIN[review["asin"]]
        track = healthy_track(feed["affiliate_link"])
        if not track:
            raise SystemExit(f"unhealthy review track {review['asin']}")
        review["track"] = track


def bake_one(review: dict[str, Any], cfg: dict[str, Any]) -> Path:
    feed = BY_ASIN[review["asin"]]
    rel = Path(SLUG) / "reviews" / review["slug"] / "index.html"
    dest = SITE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    html = clone_chrome(str(rel))
    html = strip_template_ld(html)
    html = fix_chrome_depth(html)
    html = replace_main_block(html, review_main_shell(review, feed))
    html = patch_review_head(html, review, feed)
    html = rewrite_compare_cta(html, "../../../", SLUG, "review")
    cat = cfg["CATS_BY_SLUG"][SLUG]
    cmp_html = (SITE / SLUG / "comparison" / "index.html").read_text(encoding="utf-8")
    html = apply_hub_page(
        html,
        kind="review",
        cat=cat,
        cmp_html=cmp_html,
        prefix="../../../",
        review_slug=review["slug"],
        site_root=SITE,
    )
    dest.write_text(html, encoding="utf-8")
    return dest


def _wire_landing() -> None:
    path = SITE / SLUG / "index.html"
    html = path.read_text(encoding="utf-8")
    pairs = (
        ("pick-1", "pick-2", "dreo-space-heater-portable-electric-remote"),
        ("pick-2", "pick-3", "dreo-atom-one-space-heater-thermostat"),
    )
    for this, nxt, slug in pairs:
        already = f'<a href="reviews/{slug}/">Read review →</a>'
        if already in html:
            continue
        old = (
            f'<p class="landing-pick-links"><a href="comparison/">See in comparison →</a>'
            f'</p></section><section class="landing-pick" id="{nxt}"'
        )
        new = (
            f'<p class="landing-pick-links"><a href="comparison/">See in comparison →</a> · '
            f'<a href="reviews/{slug}/">Read review →</a></p></section>'
            f'<section class="landing-pick" id="{nxt}"'
        )
        if old not in html:
            raise SystemExit(f"landing missing pick-links for {this}")
        html = html.replace(old, new, 1)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    path.write_text(html, encoding="utf-8")


def _inject_skip_review(html: str, skip: str, href: str) -> str:
    marker = (
        f'<li><strong>Deep review:</strong> <a href="{escape(href, quote=True)}">'
        "Read the review →</a></li>"
    )
    if marker in html:
        return html
    old = f"<li><strong>Who should skip:</strong> {_esc(skip)}</li></ul>"
    new = (
        f"<li><strong>Who should skip:</strong> {_esc(skip)}</li>"
        f"{marker}</ul>"
    )
    if old not in html:
        raise SystemExit(f"scene missing skip {skip!r}")
    return html.replace(old, new, 1)


def _wire_scene(rel: str, slots: list[tuple[str, str, str]]) -> None:
    path = SITE / rel
    html = path.read_text(encoding="utf-8")
    for skip, slug, _asin in slots:
        href = f"../../{SLUG}/reviews/{slug}/"
        html = _inject_skip_review(html, skip, href)
    by_asin = {r["asin"]: r for r in REVIEWS}
    rows = []
    for _skip, slug, asin in slots:
        name = BY_ASIN[asin]["title"]
        rows.append(
            '<div class="ed-rev-row"><div class="ed-rev-text">'
            f"<strong>{_esc(name)}</strong>"
            f'<a href="../../{SLUG}/reviews/{slug}/">Read Review</a></div></div>'
        )
    ed_new = f'<div class="ed-rev-list">{"".join(rows)}</div>'
    if ed_new not in html:
        if '<div class="ed-rev-list"></div>' in html:
            html = html.replace('<div class="ed-rev-list"></div>', ed_new, 1)
        else:
            html = re.sub(
                r'<div class="ed-rev-list">.*?</div>',
                ed_new,
                html,
                count=1,
                flags=re.S,
            )
    # Inline / visit cards: first two recommend slots get Read review next to Check price.
    for i, (_skip, slug, asin) in enumerate(slots, start=1):
        href = f"../../{SLUG}/reviews/{slug}/"
        track = by_asin[asin]["track"]
        visit_old = (
            f'<a class="btn btn-cta-yellow" href="{escape(track, quote=True)}" '
            'rel="sponsored noopener noreferrer" target="_blank"><span>Check price</span></a>'
            "</div></section>"
        )
        visit_new = (
            f'<a class="btn btn-cta-yellow" href="{escape(track, quote=True)}" '
            'rel="sponsored noopener noreferrer" target="_blank"><span>Check price</span></a>'
            f' <a class="btn btn-ghost btn-sm" href="{escape(href, quote=True)}">Read review</a>'
            "</div></section>"
        )
        if visit_old in html:
            html = html.replace(visit_old, visit_new, 1)
        inline_old = (
            f'<a class="btn btn-cta-yellow btn-sm" href="{escape(track, quote=True)}" '
            'rel="sponsored noopener noreferrer" target="_blank">Check price</a> '
            "</div></article>"
        )
        inline_new = (
            f'<a class="btn btn-cta-yellow btn-sm" href="{escape(track, quote=True)}" '
            'rel="sponsored noopener noreferrer" target="_blank">Check price</a> '
            f'<a href="{escape(href, quote=True)}">Read review</a>'
            "</div></article>"
        )
        if inline_old in html:
            html = html.replace(inline_old, inline_new, 1)
        _ = i
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    path.write_text(html, encoding="utf-8")


def _wire_reviews_hub() -> None:
    path = SITE / SLUG / "reviews" / "index.html"
    html = path.read_text(encoding="utf-8")
    by_asin = {r["asin"]: r for r in REVIEWS}
    for asin, review in by_asin.items():
        feed = BY_ASIN[asin]
        old = (
            f'<article class="rev-hub-card" id="geo-{asin}"><div class="rev-hub-copy">'
            f'<h2 class="rev-hub-title">{_esc(feed["title"])}</h2>'
        )
        if f'<a class="rev-hub-read" href="{review["slug"]}/">' in html:
            continue
        if old not in html:
            raise SystemExit(f"reviews hub missing {asin}")
        html = html.replace(
            (
                f'<article class="rev-hub-card" id="geo-{asin}"><div class="rev-hub-copy">'
                f'<h2 class="rev-hub-title">{_esc(feed["title"])}</h2>'
                f'<p class="rev-hub-date">{DATE}</p>'
                f'<p class="rev-hub-excerpt">Confirm wattage, oscillation, noise, and tip-over '
                f"protection on the retailer page. ${feed['price_displayed'].lstrip('$')}. "
                "A deeper review will follow.</p></div></article>"
            ),
            (
                f'<article class="rev-hub-card" id="geo-{asin}"><div class="rev-hub-copy">'
                f'<h2 class="rev-hub-title">{_esc(feed["title"])}</h2>'
                f'<p class="rev-hub-date">{DATE}</p>'
                f'<p class="rev-hub-excerpt">{_esc(review["summary"].split(". ")[0])}. '
                "Open the full review for who should skip, day-two notes, and Check price.</p>"
                f'<a class="rev-hub-read" href="{review["slug"]}/">Read {_esc(review["short_name"])} Review</a>'
                "</div></article>"
            ),
            1,
        )
    # Honest ItemList: drop leftover kids-bike schema leftovers if present.
    html = re.sub(
        r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"ItemList","name":"Ceramic Space Heaters Reviews".*?</script>',
        "",
        html,
        count=1,
        flags=re.S,
    )
    items = []
    for i, review in enumerate(REVIEWS, start=1):
        items.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": review["short_name"],
                "url": f"{LIVE}/{SLUG}/reviews/{review['slug']}/",
            }
        )
    item_list = dumps_ld(
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "Ceramic Space Heaters Reviews",
            "url": f"{LIVE}/{SLUG}/reviews/",
            "numberOfItems": len(items),
            "itemListElement": items,
        }
    )
    html = html.replace(
        "</head>",
        f'<script type="application/ld+json">{item_list}</script>\n</head>',
        1,
    )
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    path.write_text(html, encoding="utf-8")


def _wire_comparison() -> None:
    path = SITE / SLUG / "comparison" / "index.html"
    html = path.read_text(encoding="utf-8")
    for review in REVIEWS:
        count = int(BY_ASIN[review["asin"]]["review_count"])
        row = (
            f'<div class="pc-reviews-row"><a class="pc-reviews-link" '
            f'href="../reviews/{review["slug"]}/">{count:,} reviews</a></div>'
        )
        needle = f'data-asin="{review["asin"]}"'
        at = html.find(needle)
        if at < 0:
            raise SystemExit(f"comparison missing {review['asin']}")
        tag = html.find('<p class="pc-tagline">', at)
        close = html.find("</p>", tag)
        if tag < 0 or close < 0:
            raise SystemExit(f"comparison missing tagline {review['asin']}")
        insert_at = close + 4
        if "pc-reviews-link" not in html[at : insert_at + 80]:
            html = html[:insert_at] + row + html[insert_at:]
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    path.write_text(html, encoding="utf-8")


def write_notes(rows: list[dict[str, Any]]) -> Path:
    dest = ROOT / "notes" / "p1c-deep-reviews-2026-10-23.md"
    lines = [
        "# P1c deep reviews (Top pick + Upgrade only)",
        "",
        "**waiting_for_部署上线:** yes",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live. Do not merge.",
        "**Gemini:** not used (`GEMINI_API_KEY` unset; `site/scripts/gemini_review_write.py` is not in this repo).",
        "**SoT:** shortlist/L2/landing titles, bullets, prices, scores, and P1c ceramic inventory.",
        f"**Tip:** `p1c-ceramic-inventory-2026-10-23` SHA-256 `{TIP_SHA}`.",
        "",
        "| Hub | Role | ASIN | Path |",
        "| --- | --- | --- | --- |",
    ]
    by_slot = {(hub, role): r for r in rows for hub, role in r["slots"]}
    for hub, role in HUB_SLOT_ORDER:
        r = by_slot[(hub, role)]
        path = f"/{SLUG}/reviews/{r['slug']}/"
        lines.append(f"| `{hub}` | {role} | `{r['asin']}` | `{path}` |")
    lines += [
        "",
        "## Unique paths (3)",
        "",
    ]
    for i, r in enumerate(rows, start=1):
        lines.append(f"{i}. `{r['asin']}` — `/{SLUG}/reviews/{r['slug']}/`")
    lines += [
        "",
        "## Skips",
        "",
        "- No P1c hubs skipped. Category + large-rooms + garages exist on main with honest density 4.",
        "- No deep review for Best-value Gold `B0C6FCKQML`. Review default is Top pick + Upgrade only.",
        "- No ASINs invented. Slots come from the Live tip inventory `p1c-ceramic-inventory-2026-10-23`.",
        "- 6 recommend slots map to 3 unique `/{cat}/reviews/{slug}/` files. One article per ASIN.",
        "",
        "## Quality bar",
        "",
        "- Answer-first 2–4 sentences in `.review-summary`.",
        "- 5–8 bounded facts in Key insights from shortlist/L2/P1c SoT only.",
        "- H2s are purchase questions + Key insights + FAQ; cluster links match sibling reviews.",
        "- Day-two, who should skip, and why-this-slot are on every page.",
        "- No invented specs, was/%, ratings, awards, or ASINs in visitor copy.",
        "- Amazon `【】` PDP leftovers stripped from Pros/Cons and glance (no glance leftover shipped).",
        "- Type-06 FAQ: 4 product-specific questions; no lab-test FAQ; no price-snapshot FAQ.",
        "",
        "## Honest limits",
        "",
        "- Ceramic had no existing review HTML. Chrome is cloned from the humidifier bedroom template, then leftover humidifier JSON-LD is stripped and depth-3 chrome prefixes (`favicon` / CSS / logo / Categories / blog / footer legal) are rewritten to `../../../` without touching review-main `../../comparison/` links. Gallery and facts bar reuse the one SoT packshot and the live `pboost.me?uid=fromsll` track. Extra gallery thumbs were not invented.",
        "- Shared ASINs keep one badge (category Upgrade for Atom One; first Top pick for the other two) and cluster-link every P1c hub they recommend.",
        "- Full Top 4 / Top 10 reviews were not written. Hubs stay density 4; recommend slots are two per hub.",
        "",
    ]
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest


def update_inventory() -> None:
    inv_path = SITE / "data" / "p1c-ceramic-inventory-2026-10-23.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    by_asin = {r["asin"]: r for r in REVIEWS}
    for page in inv.get("pages", []):
        rewritten = []
        for key in ("top_pick", "upgrade"):
            slot = page.get(key) or {}
            asin = slot.get("asin")
            if asin in by_asin:
                slug = by_asin[asin]["slug"]
                slot["review"] = slug
                slot["review_exists"] = True
                rewritten.append(slug)
        page["new_reviews"] = rewritten
        page["reused_reviews"] = []
        page["deep_reviews"] = "p1c_top_pick_upgrade_only"
    inv["waiting_for_部署上线"] = True
    inv["deep_reviews"] = "p1c_top_pick_upgrade_only"
    inv["tip_sha256"] = TIP_SHA
    inv_path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")

    md = SITE / "data" / "p1c-ceramic-inventory-2026-10-23.md"
    text = md.read_text(encoding="utf-8")
    text = text.replace(
        "- New reviews: none (MT10 review articles do not exist; Lab reviews are out of scope)",
        "- Deep reviews: Top pick + Upgrade only (3 unique paths; see notes/p1c-deep-reviews-2026-10-23.md)",
    )
    text = text.replace(
        "- Top pick: DREO Space Heaters for Indoor Use with Thermostat, 1500W Electric Heaters `B095PP1GZR` review skipped (none on MT10)",
        "- Top pick: DREO Space Heaters for Indoor Use with Thermostat, 1500W Electric Heaters `B095PP1GZR` review `dreo-space-heaters-indoor-thermostat-1500w`",
    )
    text = text.replace(
        "- Upgrade: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` review skipped (none on MT10)",
        "- Upgrade: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` review `dreo-atom-one-space-heater-thermostat`",
    )
    text = text.replace(
        "- Top pick: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` review skipped (none on MT10)",
        "- Top pick: DREO Space Heater, Portable Electric Heaters for Indoor Use with Thermostat `B097RG67QB` review `dreo-atom-one-space-heater-thermostat`",
    )
    text = text.replace(
        "- Upgrade: DREO Space Heaters for Indoor Use with Thermostat, 1500W Electric Heaters `B095PP1GZR` review skipped (none on MT10)",
        "- Upgrade: DREO Space Heaters for Indoor Use with Thermostat, 1500W Electric Heaters `B095PP1GZR` review `dreo-space-heaters-indoor-thermostat-1500w`",
    )
    text = text.replace("- New reviews: none\n", "- New reviews: Top pick + Upgrade deep articles (unique paths, not a full Top 4)\n")
    text = text.replace(
        "- Reviews: skipped. Existing type-07 chrome does not require new review HTML when reviews do not exist.",
        "- Reviews: Top pick + Upgrade deep articles at new `/{cat}/reviews/{slug}/` paths. Not a full Top 4. Gold `B0C6FCKQML` has no deep review.",
    )
    md.write_text(text, encoding="utf-8")

    shortlist = SITE / "data" / f"shortlist-{SLUG}.json"
    if shortlist.exists():
        blob = json.loads(shortlist.read_text(encoding="utf-8"))
        notes = blob.get("notes") or []
        blob["notes"] = [
            (
                "P1c ceramic deep reviews 2026-10-23. Top pick + Upgrade only (3 unique paths). "
                "waiting_for_部署上线=yes. No Live. No Gold review."
            )
            if "No new MT10 review articles" in n
            else n
            for n in notes
        ]
        shortlist.write_text(json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    attach_tracks()
    cfg = load_site_config()
    for review in REVIEWS:
        dest = bake_one(review, cfg)
        print(f"wrote {dest.relative_to(ROOT)}")
    _wire_landing()
    _wire_scene(
        f"{SLUG}/best-ceramic-space-heaters-for-large-rooms/index.html",
        [
            (
                "Skip if you only need a compact bedroom or desk heater.",
                "dreo-space-heaters-indoor-thermostat-1500w",
                "B095PP1GZR",
            ),
            (
                "Skip if you do not need oscillation, or if 34dB bedside quiet is the priority.",
                "dreo-atom-one-space-heater-thermostat",
                "B097RG67QB",
            ),
        ],
    )
    _wire_scene(
        f"{SLUG}/best-ceramic-space-heaters-for-garages/index.html",
        [
            (
                "Skip if you do not need oscillation, or if 34dB bedside quiet is the priority.",
                "dreo-atom-one-space-heater-thermostat",
                "B097RG67QB",
            ),
            (
                "Skip if you only need a compact bedroom or desk heater.",
                "dreo-space-heaters-indoor-thermostat-1500w",
                "B095PP1GZR",
            ),
        ],
    )
    _wire_reviews_hub()
    _wire_comparison()
    bump_or_insert_sitemap(
        [f"{SLUG}/reviews/{r['slug']}/" for r in REVIEWS]
    )
    notes = write_notes(REVIEWS)
    update_inventory()
    print(f"notes {notes.relative_to(ROOT)}")
    print("hubs wired (Top pick + Upgrade only)")
    print("inventory updated (waiting_for_部署上线=yes)")


if __name__ == "__main__":
    main()
