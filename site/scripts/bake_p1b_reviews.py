#!/usr/bin/env python3
"""Bake P1b Top pick + Upgrade deep reviews from in-repo SoT only.

Draft only. No wrangler / no Live deploy. No Lab / RR / OL edits.
No Gemini — GEMINI_API_KEY is not required. Copy is authored from
landing taglines, title fields, visible bullets, L2 price/score/stars,
and P1b scene inventory. Do not invent specs, was/%, ratings, awards, or ASINs.

Usage:
    python3 site/scripts/bake_p1b_reviews.py
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

from seo_geo import apply_hub_page, dumps_ld  # noqa: E402
from site_config import load_site_config  # noqa: E402

DATE = "2026-10-23"
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P1b deep reviews draft only. "
    "Do not merge. Do not Cloudflare Live deploy. -->"
)

_MAIN_OPEN = '<div class="review-main">'
_SIDE_OPEN = '<aside class="review-side'
_GALLERY_RE = re.compile(r'<div class="review-gallery">.*?</div>', re.S)
_MID_CTA_RE = re.compile(r'<div class="review-mid-cta">.*?</div>\s*', re.S)
_FAQ_LD_RE = re.compile(
    r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"FAQPage".*?</script>',
    re.S,
)
_DESC_RE = re.compile(
    r'(<(?:meta name="description"|meta property="og:description"|meta name="twitter:description") content=")[^"]*("/>)'
)
_BADGE_RE = re.compile(r'(<p class="badge">)(.*?)(</p>)')
_UPDATED_RE = re.compile(
    r'(<span class="author-updated">Last Updated: )[^<]+(</span>)'
)


def _esc(text: str) -> str:
    return escape(text or "", quote=False)


def _a(href: str, label: str) -> str:
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
    cluster = " · ".join(_a(href, label) for href, label in links)
    return section_html(
        "Next steps",
        f"<p>{extra} Related: {cluster}.</p>{row}",
    )


def p(text: str) -> str:
    return f"<p>{text}</p>"


def ul(items: list[str]) -> str:
    return "<ul class=\"review-bullets\">" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


# --- SoT-bounded review payloads (title / tagline / bullets / L2 / P1b scene) ---

REVIEWS: list[dict[str, Any]] = [
    {
        "asin": "B0GXKSC38S",
        "cat": "air-purifiers",
        "slug": "levoit-smart-pet-air-purifier-home",
        "short_name": "LEVOIT Smart Pet Air Purifier for Home Pets",
        "badge": "Top pick",
        "hub": "/air-purifiers/best-air-purifiers-for-allergies/",
        "slots": [
            ("/air-purifiers/best-air-purifiers-for-allergies/", "Top pick"),
            ("/air-purifiers/best-air-purifiers-for-smoke/", "Upgrade"),
        ],
        "checked": "2026-10-20",
        "score_line": "9.2 Excellent on this card",
        "summary": (
            "Vital Pet Pro is the Top pick on our allergy best-of when dander and odor language already on the card "
            "matters more than a quiet-only nightstand tower. The listing pairs 140 g of activated carbon with TVOC "
            "and PM2.5 sensors that watch pet dander, smoke, and fine dust. It is also the smoke-slice Upgrade when "
            "carbon and smoke sensors beat a 3-in-1 climate hybrid. Skip it if floating hair on floors is the daily job."
        ),
        "insights": [
            (
                "Allergy Top pick, smoke Upgrade",
                "One article covers two P1b recommend slots. The allergy slice leads here for dander copy; the smoke slice uses it as Upgrade for carbon plus smoke sensors.",
            ),
            (
                "Carbon load already on the bullet",
                "The live feature list states 140 g of activated carbon aimed at dog odor and cat-litter smell.",
            ),
            (
                "Dual sensors on the card",
                "TVOC and PM2.5 sensors are listed for pet odors, smoke, dander, and fine dust. We do not invent CADR.",
            ),
            (
                "Hair vs odor is the fork",
                "Stay here for odor and dander. Move to the AP10 dust Upgrade when floating hair on floors is the daily complaint.",
            ),
            (
                "Skip climate hybrids",
                "The landing tagline writes this as the pet-first tower when you do not need a heater or fan hybrid. Those 3-in-1 cards sit as neighbors.",
            ),
            (
                "Price and score snapshot",
                "Chart score 9.2 from a 4.6 retailer rating across 5,229 reviews. Price snapshot $179.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Allergy Top pick for dander and odor copy already on the card, without a heater or fan hybrid.",
            "Listing states 140 g of activated carbon plus TVOC and PM2.5 sensors that watch smoke and dander.",
            "Also the smoke-slice Upgrade when carbon and smoke sensors are the overnight job.",
        ],
        "cons": [
            "Skip it if floating hair on floors is the daily complaint — that is the AP10 dust slot.",
            "Skip a 3-in-1 climate tower if you only wanted heat or fan modes in one footprint.",
        ],
        "sections": [
            (
                "Who should skip this Vital Pet Pro?",
                ul(
                    [
                        "Skip it if the daily complaint is floating hair on floors. Dreame AP10 is the dust Upgrade for a visible hair compartment.",
                        "Skip it if you want a heater and fan in the same tower. Dreame PM20 is the large-room 3-in-1 neighbor, not this card.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like with a carbon-and-sensor tower?",
                p(
                    "Plan filter changes around odor, not only dust. A 140 g carbon load is the listing’s odor claim; when litter or cooking smoke lingers, "
                    "that is the layer that saturates first. Confirm replacement filters and the auto-clean pre-filter interval on the retailer page via Check price."
                )
                + p(
                    "The card lists TVOC and PM2.5 sensors that raise fan speed when air changes. We do not invent a filter-life month. "
                    "If you will not replace carbon on schedule, a quieter bedroom 3-stage card is the cheaper overnight job."
                ),
            ),
            (
                "How does this handle allergy dander versus lingering smoke?",
                p(
                    "Allergy season and smoke both show up on this card: dander in the sensor line, smoke in the same TVOC and PM2.5 copy, "
                    "and 140 g of carbon for odor. That is why the allergy slice leads here and the smoke slice keeps it as Upgrade."
                ),
            ),
            (
                "Why is this the allergy Top pick instead of the LEVOIT bedroom Upgrade?",
                p(
                    "The allergy best-of leads with dander and odor language. The LEVOIT Vital 100 bedroom card is the Upgrade when a 3-stage dust and pollen line "
                    "plus a 24 dB rest claim is the overnight job without the carbon load."
                )
                + p(
                    "Read the "
                    + _a("../levoit-air-purifier-home-bedroom-small/", "LEVOIT bedroom review")
                    + " or open the "
                    + _a("../../best-air-purifiers-for-allergies/", "allergy best-of")
                    + " and the "
                    + _a("../../best-air-purifiers-for-smoke/", "smoke best-of")
                    + " to see both recommend slots."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the LEVOIT Vital Pet Pro?",
                "Skip it if floating hair on floors is the daily job, or if you want a 3-in-1 heater and fan. Those are AP10 and PM20 neighbors, not this card.",
            ),
            (
                "Does the card list sensors for smoke as well as dander?",
                "Yes. The live feature list names TVOC and PM2.5 sensors for pet odors, smoke, dander, and fine dust. We do not invent a wildfire rating.",
            ),
            (
                "How much activated carbon does the listing claim?",
                "The feature list states 140 g of activated carbon aimed at dog odor and cat-litter smell. Confirm the live listing via Check price.",
            ),
            (
                "When should I stay with the LEVOIT bedroom Vital 100 instead?",
                "Stay with Vital 100 when a compact 3-stage dust and pollen filter plus a 24 dB rest line is the overnight job and you do not need this carbon load.",
            ),
        ],
        "next_extra": (
            "If quiet pollen filtration is the overnight job, read the LEVOIT bedroom Upgrade. "
            "If smoke CADR on a longevity card is the fork, scan AEOCKY on the comparison."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-allergies/", "Best for allergies"),
            ("../../best-air-purifiers-for-smoke/", "Best for smoke"),
            ("../levoit-air-purifier-home-bedroom-small/", "LEVOIT bedroom review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B07X25BNBR",
        "cat": "air-purifiers",
        "slug": "levoit-air-purifier-home-bedroom-small",
        "short_name": "LEVOIT Air Purifier for Home Bedroom Small Room",
        "badge": "Top pick",
        "hub": "/air-purifiers/best-air-purifiers-for-bedrooms/",
        "slots": [
            ("/air-purifiers/best-air-purifiers-for-bedrooms/", "Top pick"),
            ("/air-purifiers/best-air-purifiers-for-dust/", "Top pick"),
            ("/air-purifiers/best-air-purifiers-for-allergies/", "Upgrade"),
        ],
        "checked": "2026-10-18",
        "score_line": "9.2 Excellent on this card",
        "summary": (
            "The LEVOIT Vital 100 bedroom card is the Top pick on our bedroom and dust best-ofs when a 3-stage filter "
            "that names dust and pollen plus a 24 dB rest line is the overnight job. The listing sizes it at 105 CFM CADR "
            "and up to 788 ft², with a pre-filter for hair and large debris. It is the allergy Upgrade when you want that "
            "pollen stage without Vital Pet Pro’s carbon load. Skip a 3-in-1 large-room hybrid if you only need a compact footprint."
        ),
        "insights": [
            (
                "Three P1b recommend slots, one path",
                "Bedroom Top pick, dust Top pick, and allergy Upgrade share this existing review path. The scene does not paste comparison rank 8.",
            ),
            (
                "3-stage copy already names dust and pollen",
                "The live feature list says the pre-filter traps hair and large debris, and the main filter captures dust, pollen, and fine airborne particles.",
            ),
            (
                "Quiet overnight line on the card",
                "The glance states noise as low as 24 decibels and a display you can turn off. We do not invent a second decibel number.",
            ),
            (
                "CADR and room size the listing claims",
                "The compact-home bullet names Vital 100, 105 CFM CADR, and up to 788 ft². Confirm the live AHAM room size on the retailer page.",
            ),
            (
                "AHAM VERIFIDE is a listing label",
                "The card includes an AHAM VERIFIDE heading. That is manufacturer accreditation language on the shortlist, not a MoreTop10 award.",
            ),
            (
                "Price and score snapshot",
                "Chart score 9.2 from a 4.6 retailer rating across 128,094 reviews. Price snapshot $119.99, checked 2026-10-18.",
            ),
        ],
        "pros": [
            "Bedroom and dust Top pick for a 3-stage card that names dust, pollen, and a hair pre-filter.",
            "Listing states 105 CFM CADR, up to 788 ft², and noise as low as 24 dB.",
            "Allergy Upgrade when you want that pollen stage without paying for Vital Pet Pro carbon.",
        ],
        "cons": [
            "Skip a 3-in-1 heater and fan if you only needed a nightstand HEPA.",
            "Skip AP10 if floating hair on floors, not quiet overnight dust, is the daily complaint.",
        ],
        "sections": [
            (
                "Who should skip this Vital 100 bedroom card?",
                ul(
                    [
                        "Skip it if you want a heater and fan in one large-room tower. PM20 is the climate Upgrade on the large-room slice, not this card.",
                        "Skip it if floating hair on floors is the daily complaint. AP10 is the dust Upgrade for a visible hair compartment.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like in a closed bedroom?",
                p(
                    "A hair pre-filter clogs first in a dusty room. Vacuum or rinse that stage on the schedule the retailer listing shows; "
                    "the card already names the pre-filter as the hair and debris layer. Confirm replacement filters via Check price — we do not invent a month interval."
                )
                + p(
                    "The 24 dB rest line is why this leads the bedroom slice. If you will run turbo all night, that quiet claim is not the reason to buy. "
                    "Match the 788 ft² listing to the room you actually close the door on."
                ),
            ),
            (
                "How does this handle bedroom dust versus allergy pollen?",
                p(
                    "The same 3-stage bullet names dust and pollen. That is why bedrooms and dust share this Top pick, and why allergies keep it as Upgrade "
                    "when you want pollen filtration without Vital Pet Pro’s 140 g carbon load."
                ),
            ),
            (
                "Why is this the bedroom Top pick instead of the MOOKA Upgrade?",
                p(
                    "The bedroom best-of leads with a compact card that names bedroom use and 24 dB. MOOKA is the Upgrade when the listing’s 2200 ft² HEPA "
                    "bedroom coverage matches a larger sleep space."
                )
                + p(
                    "Read the "
                    + _a("../mooka-air-purifier-home-bedroom-large/", "MOOKA review")
                    + " or open the "
                    + _a("../../best-air-purifiers-for-bedrooms/", "bedroom best-of")
                    + ", the "
                    + _a("../../best-air-purifiers-for-dust/", "dust best-of")
                    + ", and the "
                    + _a("../../best-air-purifiers-for-allergies/", "allergy best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the LEVOIT Vital 100?",
                "Skip it if you want a 3-in-1 climate tower, or if floating hair on floors is the daily job. Those are PM20 and AP10 neighbors.",
            ),
            (
                "What CADR and room size does the listing claim?",
                "The compact-home bullet names 105 CFM CADR and up to 788 ft² for the Vital 100. Confirm the live AHAM room size on the retailer page.",
            ),
            (
                "Does the 3-stage copy name dust and pollen?",
                "Yes. The feature list says the pre-filter traps hair and large debris, and the main filter captures dust, pollen, and fine airborne particles.",
            ),
            (
                "When should I step to MOOKA or Vital Pet Pro instead?",
                "Step to MOOKA when 2200 ft² HEPA coverage matches a larger bedroom. Step to Vital Pet Pro when dander and a 140 g carbon load are the allergy job.",
            ),
        ],
        "next_extra": (
            "If the bedroom is closer to a 2200 ft² HEPA claim, read the MOOKA review. "
            "If odor and smoke sensors matter more, read Vital Pet Pro."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-bedrooms/", "Best for bedrooms"),
            ("../../best-air-purifiers-for-dust/", "Best for dust"),
            ("../../best-air-purifiers-for-allergies/", "Best for allergies"),
            ("../mooka-air-purifier-home-bedroom-large/", "MOOKA review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B0CXJ97TV1",
        "cat": "air-purifiers",
        "slug": "mooka-air-purifier-home-bedroom-large",
        "short_name": "Mooka Air Purifier for Home Bedroom Large Room",
        "badge": "Top pick",
        "hub": "/air-purifiers/best-air-purifiers-for-mold/",
        "slots": [
            ("/air-purifiers/best-air-purifiers-for-mold/", "Top pick"),
            ("/air-purifiers/best-air-purifiers-for-large-rooms/", "Top pick"),
            ("/air-purifiers/best-air-purifiers-for-bedrooms/", "Upgrade"),
        ],
        "checked": "2026-10-20",
        "score_line": "9.0 Excellent on this card",
        "summary": (
            "MOOKA is the Top pick on our mold-prone and large-room slices when 2200 ft² HEPA bedroom coverage is the job "
            "and no shortlist card names mold. The landing already calls it Best value: a washable pre-filter, 3-stage design, "
            "and a PM2.5 readout with auto mode. It is the bedroom Upgrade when the sleep space is closer to that 2200 ft² claim "
            "than a nightstand Vital 100. Skip it if you need a pet-hair intake or a 3-in-1 heater and fan."
        ),
        "insights": [
            (
                "HEPA coverage without invented mold claims",
                "No live air-purifier card names mold. This slice leads here because the title lists 2200 ft² HEPA and a washable 3-stage design.",
            ),
            (
                "Landing Best value, scene Top pick",
                "The category landing already writes MOOKA as Best value for bedrooms and medium rooms. The mold and large-room slices reuse that card as Top pick.",
            ),
            (
                "PM2.5 readout and auto mode on the card",
                "The live feature list names a PM2.5 air-quality sensor, a digital display, and auto mode. We do not invent an app claim.",
            ),
            (
                "Washable pre-filter is the day-two fact",
                "The 3-stage bullet includes a washable pre-filter. Confirm how to rinse it on the retailer page.",
            ),
            (
                "Skip path already on the tagline",
                "The landing says it does not pretend to be a pet-hair vacuum tower. Step to Vital Pet Pro or AP10 when pets dominate the air load.",
            ),
            (
                "Price and score snapshot",
                "Chart score 9.0 from a 4.5 retailer rating across 6,461 reviews. Price snapshot $73.67, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Mold-slice and large-room Top pick for 2200 ft² HEPA coverage already on the title.",
            "Landing Best value: washable pre-filter, 3-stage design, and a PM2.5 readout with auto mode.",
            "Bedroom Upgrade when the sleep space outgrows a compact Vital 100.",
        ],
        "cons": [
            "No card on the shortlist names mold — we do not invent a kill rate.",
            "Skip it if you need pet-specific hair intake, smart-app control, or a 3-in-1 climate tower.",
        ],
        "sections": [
            (
                "Who should skip this MOOKA HEPA card?",
                ul(
                    [
                        "Skip it if you need a pet-hair intake or a visible hair bin. Vital Pet Pro and AP10 are the pet-named neighbors.",
                        "Skip it if you want heat and fan modes in one footprint. PM20 is the large-room Upgrade for that 3-in-1 job.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like with a washable 3-stage filter?",
                p(
                    "The washable pre-filter is the chore the card actually names. Rinse that stage so the HEPA layer is not the first thing that clogs. "
                    "Confirm rinse instructions and replacement filters on the retailer page — we do not invent a month interval."
                )
                + p(
                    "Auto mode plus a PM2.5 readout is the set-and-forget line. If you will not glance at that display, a simpler bedroom 3-stage card is enough."
                ),
            ),
            (
                "How should I read a mold-slice Top pick when no card says mold?",
                p(
                    "Honestly. The P1b mold page reorders HEPA, 0.1μm, and year-change language already on the cards. MOOKA leads because it is the landing "
                    "Best value HEPA bedroom card with printed 2200 ft² coverage, not because we measured spores."
                ),
            ),
            (
                "Why is this the large-room Top pick instead of the PM20 Upgrade?",
                p(
                    "Printed 2200 ft² HEPA on the title is the large-room default. PM20 is the Upgrade when a Premium 3-in-1 purifier, heater, and fan "
                    "matches an open living space. Stay here if you want coverage without climate modes."
                )
                + p(
                    "Read the "
                    + _a("../dreame-air-purifier-pm20-home-large/", "Dreame PM20 review")
                    + " or open the "
                    + _a("../../best-air-purifiers-for-mold/", "mold best-of")
                    + ", the "
                    + _a("../../best-air-purifiers-for-large-rooms/", "large-room best-of")
                    + ", and the "
                    + _a("../../best-air-purifiers-for-bedrooms/", "bedroom best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the MOOKA 2200 ft² card?",
                "Skip it if you need pet-hair intake, smart-app control, or a 3-in-1 heater and fan. Those are Vital Pet Pro, AP10, and PM20 neighbors.",
            ),
            (
                "Does any shortlist card name mold?",
                "No. This review only uses HEPA, 3-stage, and 2200 ft² language already on the MOOKA card. We do not invent a mold-kill rate.",
            ),
            (
                "What room size does the title claim?",
                "The review title lists 2200 ft² HEPA coverage for a home bedroom large room. Confirm the live coverage claim on the retailer page.",
            ),
            (
                "When should I stay with the LEVOIT Vital 100 instead?",
                "Stay with Vital 100 when a compact 24 dB bedroom footprint is the overnight job and you do not need the 2200 ft² HEPA step-up.",
            ),
        ],
        "next_extra": (
            "If you want climate modes in one tower, read the PM20 Upgrade. "
            "If a compact 24 dB nightstand is the room, read the LEVOIT bedroom card."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-mold/", "Best for mold"),
            ("../../best-air-purifiers-for-large-rooms/", "Best for large rooms"),
            ("../../best-air-purifiers-for-bedrooms/", "Best for bedrooms"),
            ("../dreame-air-purifier-pm20-home-large/", "Dreame PM20 review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B0F32TGRMR",
        "cat": "air-purifiers",
        "slug": "dreame-air-purifier-pm20-home-large",
        "short_name": "Dreame Air Purifier PM20 for Home Large Room, 3-in",
        "badge": "Upgrade",
        "hub": "/air-purifiers/best-air-purifiers-for-mold/",
        "slots": [
            ("/air-purifiers/best-air-purifiers-for-mold/", "Upgrade"),
            ("/air-purifiers/best-air-purifiers-for-large-rooms/", "Upgrade"),
        ],
        "checked": "2026-10-20",
        "score_line": "7.8 Good on this card",
        "summary": (
            "Dreame PM20 is the Upgrade on both the mold-prone and large-room slices when a 3-in-1 purifier, heater, "
            "and fan footprint matches an open living space. The listing’s 4-layer line names dust, pet dander, pollen, "
            "and smoke down to 0.1μm, plus dual-flow outlets. Stay with MOOKA if you only need quiet HEPA without climate modes. "
            "Skip it as a nightstand default."
        ),
        "insights": [
            (
                "Landing Premium, scene Upgrade",
                "The category landing already writes PM20 as Premium for large rooms that want climate plus filtration. Both P1b slices reuse that as Upgrade.",
            ),
            (
                "4-layer 0.1μm line on the card",
                "The live feature list names a 4-layer filter that captures particles as small as 0.1μm and lists dust, pet dander, pollen, and smoke.",
            ),
            (
                "Dual-flow is listing language",
                "The card describes upward and forward outlets as dual-flow. We do not treat that as a lab result we ran.",
            ),
            (
                "Motion-aware airflow on the bullet",
                "A radar line says the unit detects movement and auto-adjusts airflow direction. Confirm the live listing via Check price.",
            ),
            (
                "Skip path already on the tagline",
                "Skip it if you only need quiet bedroom HEPA. MOOKA or Vital Pet Pro cost less for that job on the same shortlist.",
            ),
            (
                "Price and score snapshot",
                "Chart score 7.8 from a 3.9 retailer rating across 69 reviews. Price snapshot $599.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Upgrade when a large-room 3-in-1 purifier, heater, and fan is the actual job.",
            "4-layer listing names 0.1μm capture plus dust, dander, pollen, and smoke.",
            "Landing already calls this Premium for open living spaces, not a nightstand HEPA.",
        ],
        "cons": [
            "Skip it if you only need quiet bedroom HEPA — that is the MOOKA job.",
            "Chart score 7.8 from 69 retailer reviews is a thinner snapshot than the HEPA Best value card.",
        ],
        "sections": [
            (
                "Who should skip this PM20 Upgrade?",
                ul(
                    [
                        "Skip it if you only need quiet bedroom HEPA. The tagline already sends those shoppers to MOOKA or Vital Pet Pro.",
                        "Skip it if a 47 ft² dorm tower is the real room. That neighbor sits last on the large-room slice.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like on a 3-in-1 climate tower?",
                p(
                    "You are buying heat and fan modes as well as filtration. If you will not use those modes weekly, the Premium footprint is excess. "
                    "Confirm heater safety, filter replacements, and the live 3-in-1 claim on the retailer page via Check price."
                )
                + p(
                    "The 4-layer 0.1μm line is the mold-slice reason this sits as Upgrade, not a sporicidal claim. No shortlist card names mold."
                ),
            ),
            (
                "How does dual-flow change a large-room job?",
                p(
                    "The listing writes upward and forward outlets for an open living space, plus radar that follows movement. "
                    "That is why the large-room slice keeps PM20 as Upgrade behind MOOKA’s printed 2200 ft² HEPA default."
                ),
            ),
            (
                "Why is this the Upgrade instead of the MOOKA Top pick?",
                p(
                    "MOOKA holds the HEPA coverage default. Pay this step only when a 3-in-1 climate tower matches the room and the 0.1μm 4-layer line is the filter you wanted."
                )
                + p(
                    "Read the "
                    + _a("../mooka-air-purifier-home-bedroom-large/", "MOOKA review")
                    + " or return to the "
                    + _a("../../best-air-purifiers-for-mold/", "mold best-of")
                    + " and the "
                    + _a("../../best-air-purifiers-for-large-rooms/", "large-room best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Dreame PM20?",
                "Skip it if you only need quiet bedroom HEPA, or if a 47 ft² dorm card is the real room. MOOKA is the HEPA default on both slices.",
            ),
            (
                "What does the 4-layer line actually name?",
                "The feature list names 0.1μm particles plus dust, pet dander, pollen, and smoke. It does not name mold.",
            ),
            (
                "Is this a purifier only, or a climate tower?",
                "The title is a 3-in-1 purifier, heater, and fan. The landing already writes it as Premium for large rooms that want climate plus filtration.",
            ),
            (
                "When should I stay with MOOKA?",
                "Stay with MOOKA when 2200 ft² HEPA coverage without heater or fan modes is the job. That card is Top pick on both of these slices.",
            ),
        ],
        "next_extra": (
            "If you do not need climate modes, read the MOOKA Top pick. "
            "If smoke without a heater is the fork, read the PM10 smoke Top pick."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-mold/", "Best for mold"),
            ("../../best-air-purifiers-for-large-rooms/", "Best for large rooms"),
            ("../mooka-air-purifier-home-bedroom-large/", "MOOKA review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B0FS68R44C",
        "cat": "air-purifiers",
        "slug": "dreame-pet-air-purifier-ap10-suck",
        "short_name": "Dreame Pet Air Purifier AP10, Suck Up Floating",
        "badge": "Upgrade",
        "hub": "/air-purifiers/best-air-purifiers-for-dust/",
        "slots": [
            ("/air-purifiers/best-air-purifiers-for-dust/", "Upgrade"),
        ],
        "checked": "2026-10-20",
        "score_line": "8.4 Very good on this card",
        "summary": (
            "Dreame AP10 is the Upgrade on our dust best-of when floating hair and dust on floors is the daily complaint, "
            "not just a HEPA badge. The card pairs high negative-pressure return with a visible hair compartment you empty "
            "without guessing, plus a triple-layer line that names hair, dust, and pet odor. Skip it if you only need bedroom "
            "HEPA at Best value pricing."
        ),
        "insights": [
            (
                "Dust Upgrade, not the bedroom default",
                "The dust slice leads with the LEVOIT 3-stage bedroom card. AP10 steps up when hair and dust on floors is the daily complaint.",
            ),
            (
                "Visible hair compartment on the card",
                "The live feature list describes a transparent collection compartment so you empty hair without opening a sealed cover to check.",
            ),
            (
                "Negative-pressure return is listing language",
                "The bullet names 360-degree high negative-pressure air return for long-range hair capture. We do not invent a CADR for that claim.",
            ),
            (
                "Triple-layer names hair and dust",
                "The filtration bullet lists hair and dust, fine particles, and pet-odor neutralization. That is the dust-slice reason it sits as Upgrade.",
            ),
            (
                "Skip path already on the tagline",
                "Skip it if you only need bedroom HEPA at Best value pricing. MOOKA remains the cheaper HEPA neighbor.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.4 from a 4.2 retailer rating across 94 reviews. Price snapshot $209.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Dust Upgrade when floating hair and dust on floors is the daily complaint.",
            "Visible hair compartment plus a triple-layer line that names hair, dust, and pet odor.",
            "Landing already writes this as the living-room hair step-up, not a nightstand HEPA.",
        ],
        "cons": [
            "Skip it if you only need bedroom HEPA at Best value pricing.",
            "Skip it if odor without visible hair is the job — that is Vital Pet Pro’s carbon slot.",
        ],
        "sections": [
            (
                "Who should skip this AP10 Upgrade?",
                ul(
                    [
                        "Skip it if you only need a compact 3-stage bedroom card. LEVOIT Vital 100 is the dust Top pick for that job.",
                        "Skip it if odor without visible hair is the complaint. Vital Pet Pro is the carbon-and-sensor neighbor.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like with a visible hair bin?",
                p(
                    "Empty the transparent compartment when you can see hair, instead of guessing behind a sealed cover. That is the ownership pitch already on the card. "
                    "Confirm how to empty it and what replacement filters the listing sells via Check price."
                )
                + p(
                    "High negative-pressure return will pull more floor debris than a nightstand intake. If you will not empty a hair bin, stay with the LEVOIT 3-stage Top pick."
                ),
            ),
            (
                "How does this handle dust on floors versus dust in the air?",
                p(
                    "The dust slice leads with a 3-stage card that names airborne dust and pollen. AP10 is the Upgrade because its hair-and-dust line plus a collection "
                    "compartment is written for debris you can see on floors, not only a HEPA badge."
                ),
            ),
            (
                "Why is this the Upgrade instead of the LEVOIT dust Top pick?",
                p(
                    "Vital 100 holds the compact 3-stage default. Pay this step only when floating hair and dust on floors is the daily complaint and a visible bin is the chore you will actually do."
                )
                + p(
                    "Read the "
                    + _a("../levoit-air-purifier-home-bedroom-small/", "LEVOIT bedroom review")
                    + " or return to the "
                    + _a("../../best-air-purifiers-for-dust/", "dust best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Dreame AP10?",
                "Skip it if you only need bedroom HEPA at Best value pricing, or if odor without visible hair is the job. Those are MOOKA and Vital Pet Pro neighbors.",
            ),
            (
                "What does the visible compartment change day-two?",
                "The listing describes a transparent hair compartment so you empty it without opening a cover to check. Confirm the live design on the retailer page.",
            ),
            (
                "Does the triple-layer line name dust?",
                "Yes. The filtration bullet lists hair and dust, fine particles, and pet-odor neutralization. We do not invent a Dust CADR for this card.",
            ),
            (
                "When should I stay with the LEVOIT Vital 100?",
                "Stay with Vital 100 when a compact 3-stage dust and pollen filter plus a 24 dB rest line is the overnight job and you do not want a floor-hair bin.",
            ),
        ],
        "next_extra": (
            "If a compact 3-stage nightstand is the room, read the LEVOIT dust Top pick. "
            "If odor without visible hair is the fork, read Vital Pet Pro."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-dust/", "Best for dust"),
            ("../levoit-air-purifier-home-bedroom-small/", "LEVOIT bedroom review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B0F2G5DPJN",
        "cat": "air-purifiers",
        "slug": "dreame-smart-air-purifier-pm10-home",
        "short_name": "Dreame Smart Air Purifier PM10 for Home Large",
        "badge": "Top pick",
        "hub": "/air-purifiers/best-air-purifiers-for-smoke/",
        "slots": [
            ("/air-purifiers/best-air-purifiers-for-smoke/", "Top pick"),
        ],
        "checked": "2026-10-18",
        "score_line": "8.4 Very good on this card",
        "summary": (
            "Dreame PM10 is the Top pick on our smoke best-of when the 4-layer line already names smoke alongside dust, "
            "dander, and pollen. The title is a 2-in-1 purifier and fan for large rooms; the listing also calls out dual-flow "
            "outlets and 0.1μm capture. Skip a 47 ft² dorm card if the room is a living area. Step to Vital Pet Pro when "
            "140 g of carbon and smoke sensors matter more than the fan hybrid."
        ),
        "insights": [
            (
                "Scene Top pick, not comparison rank 5",
                "The comparison leftover badge is Rank 5. The smoke slice leads here because the 4-layer bullet names smoke, not because we pasted score order.",
            ),
            (
                "4-layer line already names smoke",
                "The live feature list names 0.1μm capture plus dust, pet dander, pollen, and smoke. We do not invent a wildfire rating.",
            ),
            (
                "2-in-1 purifier and fan, not a heater",
                "The review title is a 2-in-1 purifier and fan for a large room. That is a thinner climate claim than PM20’s 3-in-1 heater hybrid.",
            ),
            (
                "Dual-flow is listing language",
                "The card describes upward and forward outlets as dual-flow. We do not treat that as a lab result we ran.",
            ),
            (
                "Carbon vs 4-layer is the smoke fork",
                "Stay here for the 4-layer smoke line. Step to Vital Pet Pro when 140 g of carbon and TVOC plus PM2.5 smoke sensors are the overnight job.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.4 from a 4.2 retailer rating across 52 reviews. Price snapshot $575.83, checked 2026-10-18.",
            ),
        ],
        "pros": [
            "Smoke Top pick because the 4-layer listing already names smoke, not a quiet-night brochure line.",
            "Title is a large-room 2-in-1 purifier and fan with dual-flow outlets on the card.",
            "0.1μm capture line is the same filter family the mold slice uses on PM20, without the heater mode.",
        ],
        "cons": [
            "Skip a 47 ft² dorm smoke-CADR card if the room is a living area.",
            "Skip it if 140 g of carbon and smoke sensors are the job — that is the Vital Pet Pro Upgrade.",
        ],
        "sections": [
            (
                "Who should skip this PM10 smoke Top pick?",
                ul(
                    [
                        "Skip it if you only need a 47 ft² dorm tower. LV-H128 lists a tiny-room smoke CADR and stays mid-chart as a neighbor.",
                        "Skip it if carbon and smoke sensors matter more than a 2-in-1 fan hybrid. Vital Pet Pro is the smoke Upgrade.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like after a smoky week?",
                p(
                    "A 4-layer card that names smoke will load the carbon-adjacent stages first after cooking or indoor smoke. Confirm replacement filters on the retailer page. "
                    "We do not invent a wildfire CADR or an outdoor-air rating."
                )
                + p(
                    "The 2-in-1 fan mode is extra only if you will use it. If filtration is the only job, compare Vital Pet Pro’s carbon load before you pay for a large-room fan tower."
                ),
            ),
            (
                "How does this differ from the PM20 3-in-1 neighbor?",
                p(
                    "Both listings share dual-flow and 4-layer 0.1μm copy that names smoke. PM10’s title is purifier and fan. PM20 adds a heater and is Premium Upgrade on the large-room slice, not this smoke default."
                ),
            ),
            (
                "Why is this the smoke Top pick instead of the Vital Pet Pro Upgrade?",
                p(
                    "The smoke best-of leads with a 4-layer line that names smoke in the same breath as dust, dander, and pollen. Vital Pet Pro is the Upgrade when 140 g of carbon and smoke sensors are the overnight job."
                )
                + p(
                    "Read the "
                    + _a("../levoit-smart-pet-air-purifier-home/", "Vital Pet Pro review")
                    + " or return to the "
                    + _a("../../best-air-purifiers-for-smoke/", "smoke best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Dreame PM10?",
                "Skip it if a 47 ft² dorm tower is the real room, or if 140 g of carbon and smoke sensors are the job. Those are LV-H128 and Vital Pet Pro neighbors.",
            ),
            (
                "Does the 4-layer line name smoke?",
                "Yes. The feature list names 0.1μm particles plus dust, pet dander, pollen, and smoke. We do not invent a wildfire rating.",
            ),
            (
                "Is PM10 a heater as well as a purifier?",
                "The title is a 2-in-1 purifier and fan for a large room. The 3-in-1 heater hybrid on this shortlist is PM20, not this card.",
            ),
            (
                "When should I step to Vital Pet Pro instead?",
                "Step to Vital Pet Pro when odor and smoke sensors plus a 140 g carbon load matter more than a large-room fan hybrid. That card is the smoke Upgrade.",
            ),
        ],
        "next_extra": (
            "If carbon and smoke sensors are the overnight job, read the Vital Pet Pro Upgrade. "
            "If you also want a heater, scan PM20 on the large-room slice."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-smoke/", "Best for smoke"),
            ("../levoit-smart-pet-air-purifier-home/", "Vital Pet Pro review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B0DF567NW8",
        "cat": "humidifiers",
        "slug": "homvana-36l-cool-mist-humidifiers-bedroom",
        "short_name": "Homvana 3.6L Cool Mist Humidifiers for Bedroom, Baby",
        "badge": "Top pick",
        "hub": "/humidifiers/best-humidifiers-for-babies/",
        "slots": [
            ("/humidifiers/best-humidifiers-for-babies/", "Top pick"),
        ],
        "checked": "2026-10-20",
        "score_line": "8.8 Very good on this card",
        "summary": (
            "Homvana 3.6L is the Top pick on our baby humidifier best-of when cool mist and a tank you can clean beat a warm-mist app. "
            "The landing already calls it Best value for nurseries and small rooms, with a 5.3-inch wide fill and a 15-minute comfort line on the listing. "
            "Skip it if you need warm mist or app control. Step to the Homvana 7L when the Baby Nursery title and 807 ft² claim match a larger room."
        ),
        "insights": [
            (
                "Baby-named cool mist leads the scene",
                "The title already says Baby. The landing writes this as Best value for nurseries: cool mist and wide-fill cleaning without warm-mist complexity.",
            ),
            (
                "Wide fill is the cleanability fact",
                "The live feature list names an ultra-wide 5.3-inch opening. That is the day-two reason a nursery card beats a tank you cannot reach into.",
            ),
            (
                "15-minute comfort is listing language",
                "The card says ease indoor dryness in just 15 minutes. We do not invent a medical or pediatric rating.",
            ),
            (
                "Cool mist only on this pick",
                "The tagline says it earns the entry role. Step up when warm mist or multi-day runtime is required — that is the 7L Upgrade.",
            ),
            (
                "Category #1 is demoted on this slice",
                "LEVOIT’s bedroom warm and cool mist leads the comparison. This page leads with the nursery Best value card instead of pasting score order.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.8 from a 4.4 retailer rating across 12,959 reviews. Price snapshot $31.49, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Nursery Top pick for cool mist and a Baby-named title already on the card.",
            "Landing Best value: 5.3-inch wide fill and a 15-minute comfort line without warm-mist complexity.",
            "Small-room tank you can actually clean after a short night.",
        ],
        "cons": [
            "Skip it if you need warm mist or app control.",
            "Skip a 10 L open-plan tank if a crib-side refill is the real chore.",
        ],
        "sections": [
            (
                "Who should skip this 3.6L nursery pick?",
                ul(
                    [
                        "Skip it if you need warm mist or app control. The cons line already says so; the 7L Upgrade is the warm-and-cool step-up.",
                        "Skip it if a 10 L open-plan tank is the job. OasisMist sits near the bottom of this slice as a large-room neighbor, not a crib-side default.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like beside a crib?",
                p(
                    "Wide-fill cleaning is the chore the card names. The 5.3-inch opening is there so you can reach the tank without a bottle brush you will not use at 2 a.m. "
                    "Confirm whether the listing wants distilled water and how to dry the tank on the retailer page."
                )
                + p(
                    "Cool mist avoids warm-mist complexity. If you will not wipe the base after a night, white dust and film show up first on a cheap tank — empty it in the morning."
                ),
            ),
            (
                "How should I read a baby humidifier that is not a medical device?",
                p(
                    "The P1b slice only promotes Baby, nursery, and cool-mist language already on the cards. We do not invent safety certifications. "
                    "Confirm current specs and any listing safety notes via Check price."
                ),
            ),
            (
                "Why is this the Top pick instead of the Homvana 7L Upgrade?",
                p(
                    "3.6L holds the nursery cool-mist default. The 7L card steps up when the Baby Nursery title and 807 ft² coverage match a larger room and you will use warm mist."
                )
                + p(
                    "Read the "
                    + _a("../homvana-humidifier-large-room-7l-807ft/", "Homvana 7L review")
                    + " or return to the "
                    + _a("../../best-humidifiers-for-babies/", "baby humidifier best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Homvana 3.6L?",
                "Skip it if you need warm mist or app control, or if a 10 L open-plan tank is the job. The 7L Upgrade is the larger nursery step-up.",
            ),
            (
                "What makes this the nursery Top pick?",
                "The title says Baby, and the landing already writes it as Best value for nurseries: cool mist and a 5.3-inch wide fill without warm-mist complexity.",
            ),
            (
                "Does this review claim a pediatric safety rating?",
                "No. We only use Baby, nursery, and cool-mist language already on the card. Confirm any listing safety notes on the retailer page.",
            ),
            (
                "When should I step to the Homvana 7L?",
                "Step to the 7L when the Baby Nursery title and 807 ft² coverage match a larger room, or when you want warm and cool mist in one tank.",
            ),
        ],
        "next_extra": (
            "If the nursery is closer to 807 ft² or you want warm mist, read the Homvana 7L Upgrade. "
            "If you already want LEVOIT bedroom warm and cool mist, scan that neighbor on the comparison."
        ),
        "cluster": [
            ("../", "All humidifier reviews"),
            ("../../comparison/", "Humidifiers comparison"),
            ("../../best-humidifiers-for-babies/", "Best for babies"),
            ("../homvana-humidifier-large-room-7l-807ft/", "Homvana 7L review"),
        ],
        "cta": ("../../comparison/", "Back to Humidifiers comparison"),
    },
    {
        "asin": "B0C369CCDY",
        "cat": "humidifiers",
        "slug": "homvana-humidifier-large-room-7l-807ft",
        "short_name": "Homvana Humidifier Large Room, 7L (807ft²) Smart",
        "badge": "Upgrade",
        "hub": "/humidifiers/best-humidifiers-for-babies/",
        "slots": [
            ("/humidifiers/best-humidifiers-for-babies/", "Upgrade"),
        ],
        "checked": "2026-10-18",
        "score_line": "8.4 Very good on this card",
        "summary": (
            "The Homvana 7L is the Upgrade on our baby humidifier best-of when the listing title’s Baby Nursery line and "
            "807 ft² coverage outgrow a 3.6L cool-mist tank. It is a top-fill, smart warm-and-cool unit with MistIQ auto-adapt "
            "copy already on the card. Stay with 3.6L if you want simple cool mist without warm-mist complexity. Skip a 10 L "
            "open-plan tank if a crib-side refill is the real chore."
        ),
        "insights": [
            (
                "Baby Nursery on the listing title",
                "The review title includes Baby Nursery, top-fill, and auto-adapt mist. That is why the nursery slice keeps this as Upgrade, not comparison rank 6.",
            ),
            (
                "807 ft² and 7L are title facts",
                "The name is 7L (807ft²). Confirm the live coverage claim on the retailer page before you treat it as a floor plan.",
            ),
            (
                "Warm and cool mist on the bullet",
                "The live feature list names dual mist for all-season use. Stay with 3.6L if you do not want warm-mist complexity.",
            ),
            (
                "MistIQ is listing auto-adapt language",
                "The card says MistIQ detects humidity and room changes so you are not stuck over-humid. We do not invent a sensor spec beyond that line.",
            ),
            (
                "Fewer refills is the 7L pitch",
                "The glance names an extra-large 7L tank so you refill less often. That is the nursery step-up when 3.6L runs dry overnight.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.4 from a 4.2 retailer rating across 548 reviews. Price snapshot $79.99, checked 2026-10-18.",
            ),
        ],
        "pros": [
            "Nursery Upgrade when Baby Nursery and 807 ft² on the title match a larger room.",
            "Top-fill 7L tank plus warm and cool mist already on the listing.",
            "MistIQ auto-adapt copy is the over-humid skip path on the card.",
        ],
        "cons": [
            "Skip it if you want simple cool mist without warm-mist complexity — that is the 3.6L Top pick.",
            "Skip a 10 L open-plan tank if a crib-side refill is the real chore.",
        ],
        "sections": [
            (
                "Who should skip this 7L Upgrade?",
                ul(
                    [
                        "Skip it if you want simple cool mist without warm mist. Homvana 3.6L is the nursery Top pick for that job.",
                        "Skip it if a 10 L open-plan tank is the job. That Premium neighbor is not a crib-side default on this slice.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like on a 7L warm-and-cool tank?",
                p(
                    "A 7L tank means fewer refills and a heavier lift to the sink. Top-fill helps if you will not invert the tank; still empty and dry it so film does not sit overnight. "
                    "Confirm warm-mist cleaning steps on the retailer page — we do not invent a boil-or-not rule."
                )
                + p(
                    "MistIQ is the listing’s answer to over-humid. If you will not trust auto-adapt, stay with the smaller cool-mist Top pick and a window you can crack."
                ),
            ),
            (
                "How does 807 ft² change a nursery buy?",
                p(
                    "The title prints 807 ft². Use that as a listing claim to re-check, not as a room we measured. A small crib room may still want the 3.6L cool-mist default."
                ),
            ),
            (
                "Why is this the Upgrade instead of the Homvana 3.6L Top pick?",
                p(
                    "3.6L holds the nursery cool-mist default. Pay this step when the Baby Nursery title, 7L tank, and 807 ft² coverage match a larger room and you will use warm mist."
                )
                + p(
                    "Read the "
                    + _a("../homvana-36l-cool-mist-humidifiers-bedroom/", "Homvana 3.6L review")
                    + " or return to the "
                    + _a("../../best-humidifiers-for-babies/", "baby humidifier best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Homvana 7L?",
                "Skip it if you want simple cool mist without warm mist, or if a 10 L open-plan tank is the job. 3.6L is the nursery Top pick.",
            ),
            (
                "What room size does the title claim?",
                "The name is 7L (807ft²) with Baby Nursery in the listing title. Confirm the live coverage claim on the retailer page.",
            ),
            (
                "Does this card include warm mist?",
                "Yes. The feature list names warm and cool mist as an all-season choice. Stay with 3.6L if you do not want that complexity.",
            ),
            (
                "When should I stay with the Homvana 3.6L?",
                "Stay with 3.6L when cool mist, a 5.3-inch wide fill, and a small-room tank are the nursery job. That card is the scene Top pick.",
            ),
        ],
        "next_extra": (
            "If you do not need warm mist or 807 ft², read the Homvana 3.6L Top pick. "
            "If a 10 L tank is the real room, scan OasisMist on the comparison."
        ),
        "cluster": [
            ("../", "All humidifier reviews"),
            ("../../comparison/", "Humidifiers comparison"),
            ("../../best-humidifiers-for-babies/", "Best for babies"),
            ("../homvana-36l-cool-mist-humidifiers-bedroom/", "Homvana 3.6L review"),
        ],
        "cta": ("../../comparison/", "Back to Humidifiers comparison"),
    },
    {
        "asin": "B0B68QSN6Y",
        "cat": "standing-desks",
        "slug": "fezibo-60-x-30-inch-standing",
        "short_name": "FEZIBO 60 x 30 inch Standing Electric Desk",
        "badge": "Top pick",
        "hub": "/standing-desks/best-standing-desks-for-home-office/",
        "slots": [
            ("/standing-desks/best-standing-desks-for-home-office/", "Top pick"),
        ],
        "checked": "2026-10-20",
        "score_line": "9.0 Excellent on this card",
        "summary": (
            "The FEZIBO 60×30 with drawers is the Top pick on our home-office standing-desk slice when charger storage "
            "and a monitor stand matter more than a freight-width top. The landing already writes it for daily sit-stand work "
            "with memory presets. Skip a 48×24 alcove card if you need drawers, and skip 83-inch freight if width is not the constraint. "
            "Confirm doorway clearance on the retailer page before you order."
        ),
        "insights": [
            (
                "Landing Top pick reused for the scene",
                "The category landing already writes the 60×30 with drawers as Top pick for daily home offices. The scene does not paste comparison #1 CubiCubi 40×24.",
            ),
            (
                "Drawers and monitor stand on the card",
                "The live feature list names an integrated monitor stand with built-in drawer storage for a daily computer-desk setup.",
            ),
            (
                "Memory presets are the sit-stand fact",
                "The listing describes electric height adjustment with memory presets so you switch between sitting and standing without re-finding height.",
            ),
            (
                "Size family on the bullet, this SKU is 60×30",
                "The card mentions 48, 55, and 60 inch options. This review is the 60×30 SKU on the home-office slice, not the smaller alcove neighbors.",
            ),
            (
                "Anti-collision is listing language",
                "The glance names built-in anti-collision on the adjustable frame. Confirm the live safety note on the retailer page.",
            ),
            (
                "Price and score snapshot",
                "Chart score 9.0 from a 4.5 retailer rating across 231 reviews. Price snapshot $208.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Home-office Top pick for drawers, a monitor stand, and a mid-width 60×30 top.",
            "Memory presets on the listing for daily sit-stand without a freight-size slab.",
            "Skip path already on the tagline: 48×24 if you do not need drawers, 83×37 if width is the real constraint.",
        ],
        "cons": [
            "Skip it if you need a 70-plus-inch dual-monitor span — that is the 63×37 or 83-inch fork.",
            "Skip a 32×19 alcove card if that is the real footprint; use the small-office neighbor instead.",
        ],
        "sections": [
            (
                "Who should skip this 60×30 home-office pick?",
                ul(
                    [
                        "Skip it if dual monitors need a thicker, wider top. The 63×37 is the home-office Upgrade for that job.",
                        "Skip it if you only have a 32×19 alcove. That card sits last on this slice.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like with drawers and a monitor stand?",
                p(
                    "Drawers only help if you will actually park chargers and a laptop in them. The monitor stand is the listing’s cable-and-screen pitch; confirm whether it is fixed or removable on the retailer page. "
                    "We do not invent a load rating beyond the truncated shortlist line."
                )
                + p(
                    "Memory presets are the sit-stand habit. If you will leave the desk at one height, a cheaper fixed table is enough. Measure the wall and the doorway before you treat 60 inches as a floor plan."
                ),
            ),
            (
                "How does this differ from the compact comparison leader?",
                p(
                    "CubiCubi 40×24 leads the comparison on score as a compact height-range card. This page leads with the landing home-office Top pick because drawers and a 60×30 top match daily sit-stand work."
                ),
            ),
            (
                "Why is this the Top pick instead of the 63×37 Upgrade?",
                p(
                    "60×30 holds the drawer-and-monitor default. Pay for 63×37 only when dual-monitor width is the constraint and you want to stay off 83-inch freight."
                )
                + p(
                    "Read the "
                    + _a("../fezibo-63-x-37-inch-large/", "FEZIBO 63×37 review")
                    + " or return to the "
                    + _a("../../best-standing-desks-for-home-office/", "home-office best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the FEZIBO 60×30?",
                "Skip it if dual monitors need a wider top, or if a 32×19 alcove is the real room. Those are the 63×37 Upgrade and the small-office neighbor.",
            ),
            (
                "Does this card include drawers and a monitor stand?",
                "Yes. The feature list names an integrated monitor stand with built-in drawer storage for a daily computer-desk setup.",
            ),
            (
                "Why isn’t comparison #1 the home-office Top pick?",
                "CubiCubi 40×24 leads the comparison as a compact height-range card. The 60×30 with drawers is the landing Top pick for daily home offices, so the scene leads there.",
            ),
            (
                "When should I step to the 63×37?",
                "Step to 63×37 when dual monitors need a thicker, wider top without jumping to 83-inch freight. That card is the scene Upgrade.",
            ),
        ],
        "next_extra": (
            "If dual-monitor width is the constraint, read the 63×37 Upgrade. "
            "If you do not need drawers, scan the 48×24 Best value neighbor on the comparison."
        ),
        "cluster": [
            ("../", "All standing desk reviews"),
            ("../../comparison/", "Standing desks comparison"),
            ("../../best-standing-desks-for-home-office/", "Best for home office"),
            ("../fezibo-63-x-37-inch-large/", "FEZIBO 63×37 review"),
        ],
        "cta": ("../../comparison/", "Back to Standing Desks comparison"),
    },
    {
        "asin": "B0GD75Y6SC",
        "cat": "standing-desks",
        "slug": "fezibo-63-x-37-inch-large",
        "short_name": "FEZIBO 63 x 37 Inch Large Electric Standing",
        "badge": "Upgrade",
        "hub": "/standing-desks/best-standing-desks-for-home-office/",
        "slots": [
            ("/standing-desks/best-standing-desks-for-home-office/", "Upgrade"),
        ],
        "checked": "2026-10-20",
        "score_line": "9.2 Excellent on this card",
        "summary": (
            "The FEZIBO 63×37 is the Upgrade on our home-office slice when dual monitors need a thicker, wider top without "
            "jumping to 83-inch freight. The title is a 63×37, 1-inch-thick desktop; the listing also names a dual-crossbeam "
            "frame and a motorized sit-stand start at 28.3 inches. Stay with the 60×30 if drawers and a monitor stand already "
            "fit the wall. Skip it if the room cannot clear about six feet of width."
        ),
        "insights": [
            (
                "Title is 63×37, not a second width we invent",
                "The review title and the extra-large-desktop bullet both say 63 by 37 inches. A leftover landing tagline mentions 71×37; this article follows the title.",
            ),
            (
                "1-inch three-piece top on the glance",
                "The glance names a 3-piece, 1-inch-thick desktop. Confirm finish and assembly on the retailer page.",
            ),
            (
                "Dual crossbeam is the stability line",
                "The live feature list names an integrated dual crossbeam and a thickened, extended alloy steel frame. We do not invent a load number from a truncated card.",
            ),
            (
                "Sit-stand start height on the listing",
                "The motor bullet states a smooth adjustment starting at 28.3 inches. Confirm the top of the range on the retailer page via Check price.",
            ),
            (
                "Stay off 83-inch freight",
                "The scene writes this Upgrade as the dual-monitor step that does not jump to the 83×37 freight neighbor.",
            ),
            (
                "Price and score snapshot",
                "Chart score 9.2 from a 4.6 retailer rating across 331 reviews. Price snapshot $296.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Home-office Upgrade for a 63×37, 1-inch top when dual monitors outgrow 60×30.",
            "Dual-crossbeam frame and a motorized sit-stand start at 28.3 inches on the listing.",
            "Stays off the 83-inch freight neighbor when width is the constraint but not a whole-wall slab.",
        ],
        "cons": [
            "Skip it if drawers and a monitor stand on 60×30 already fit the wall.",
            "Skip it if the room cannot clear about six feet of width.",
        ],
        "sections": [
            (
                "Who should skip this 63×37 Upgrade?",
                ul(
                    [
                        "Skip it if the 60×30 with drawers already fits the wall. That card is the scene Top pick.",
                        "Skip it if you cannot clear about six feet of width, or if 83-inch freight is the span you actually measured.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like on a 63×37 three-piece top?",
                p(
                    "A 3-piece, 1-inch top means more seams to line up in a home office than a one-piece alcove card. Confirm assembly and whether the listing wants two people. "
                    "We do not invent a weight rating from the truncated shortlist line."
                )
                + p(
                    "The dual-crossbeam frame is the listing’s stability pitch for heavier monitor setups. If you only run a laptop, 60×30 with drawers is the lighter daily job."
                ),
            ),
            (
                "How should I read a leftover 71×37 tagline against a 63×37 title?",
                p(
                    "Follow the title and the 63 by 37 bullet. The landing tagline’s 71×37 leftover is not a second SKU we invent. Confirm the live dimensions on the retailer page."
                ),
            ),
            (
                "Why is this the Upgrade instead of the 60×30 Top pick?",
                p(
                    "60×30 holds the drawer-and-monitor default. Pay this step when dual monitors need a thicker, wider top and you still want to stay off 83-inch freight."
                )
                + p(
                    "Read the "
                    + _a("../fezibo-60-x-30-inch-standing/", "FEZIBO 60×30 review")
                    + " or return to the "
                    + _a("../../best-standing-desks-for-home-office/", "home-office best-of")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the FEZIBO 63×37?",
                "Skip it if the 60×30 with drawers already fits, or if the room cannot clear about six feet of width. The 83-inch neighbor is the freight-size fork.",
            ),
            (
                "What desktop size does the title claim?",
                "The title and the extra-large-desktop bullet both say 63 by 37 inches with a 1-inch-thick, 3-piece top. Confirm the live listing via Check price.",
            ),
            (
                "Does the listing name a sit-stand height?",
                "The motor bullet states a smooth adjustment starting at 28.3 inches. Confirm the top of the range on the retailer page. We do not invent the missing end of that line.",
            ),
            (
                "When should I stay with the 60×30?",
                "Stay with 60×30 when charger drawers and a monitor stand are the daily job and you do not need the wider dual-monitor top. That card is the scene Top pick.",
            ),
        ],
        "next_extra": (
            "If you do not need the wider top, read the 60×30 Top pick. "
            "If width is a whole-wall problem, scan the 83×37 freight neighbor on the comparison."
        ),
        "cluster": [
            ("../", "All standing desk reviews"),
            ("../../comparison/", "Standing desks comparison"),
            ("../../best-standing-desks-for-home-office/", "Best for home office"),
            ("../fezibo-60-x-30-inch-standing/", "FEZIBO 60×30 review"),
        ],
        "cta": ("../../comparison/", "Back to Standing Desks comparison"),
    },
]


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


def patch_head(html: str, review: dict[str, Any]) -> str:
    desc = review["summary"]
    if len(desc) > 155:
        desc = desc[:154].rsplit(" ", 1)[0] + "…"
    html = _DESC_RE.sub(lambda m: f"{m.group(1)}{escape(desc, quote=True)}{m.group(2)}", html)
    html = _BADGE_RE.sub(rf'\1{escape(review["badge"], quote=True)}\3', html, count=1)
    html = _UPDATED_RE.sub(rf"\g<1>{DATE}\2", html, count=1)
    html = html.replace('"dateModified":"2026-10-20"', f'"dateModified":"{DATE}"')
    html = html.replace('"dateModified":"2026-10-18"', f'"dateModified":"{DATE}"')
    faq_script = f'<script type="application/ld+json">{faq_ld(review["faqs"])}</script>'
    if _FAQ_LD_RE.search(html):
        html = _FAQ_LD_RE.sub(faq_script, html, count=1)
    else:
        html = html.replace("</head>", f"{faq_script}\n</head>", 1)
    if DRAFT_COMMENT not in html:
        html = html.replace("<body>", f"<body>\n{DRAFT_COMMENT}\n", 1)
    return html


def sync_article_description(html: str, summary: str) -> str:
    """Keep Article JSON-LD description in lockstep with the new answer-first."""

    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        types = data.get("@type")
        type_list = types if isinstance(types, list) else [types]
        if "Article" not in type_list:
            return match.group(0)
        data["description"] = summary
        entity = data.get("mainEntity")
        if isinstance(entity, dict) and entity.get("@type") == "Product":
            entity["description"] = summary
            rev = entity.get("review")
            if isinstance(rev, dict):
                rev["reviewBody"] = summary
        return f'<script type="application/ld+json">{dumps_ld(data)}</script>'

    return re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        repl,
        html,
        flags=re.S,
    )


def bake_one(review: dict[str, Any], cfg: dict[str, Any]) -> Path:
    rel = Path(review["cat"]) / "reviews" / review["slug"] / "index.html"
    dest = SITE / rel
    html = dest.read_text(encoding="utf-8")
    open_at = html.find(_MAIN_OPEN)
    side_at = html.find(_SIDE_OPEN)
    if open_at < 0 or side_at < 0:
        raise SystemExit(f"missing review-main or review-side in {rel}")
    inner_start = open_at + len(_MAIN_OPEN)
    close_at = html.rfind("</div>", inner_start, side_at)
    if close_at < 0:
        raise SystemExit(f"missing review-main close in {rel}")
    old_main = html[inner_start:close_at]
    gallery_m = _GALLERY_RE.search(old_main)
    mid_m = _MID_CTA_RE.search(old_main)
    if not gallery_m or not mid_m:
        raise SystemExit(f"missing gallery or mid-cta in {rel}")
    new_main = render_main(review, gallery_m.group(0), mid_m.group(0))
    html = html[:inner_start] + new_main + html[close_at:]
    html = patch_head(html, review)

    cat = cfg["CATS_BY_SLUG"][review["cat"]]
    cmp_html = (SITE / review["cat"] / "comparison" / "index.html").read_text(
        encoding="utf-8"
    )
    html = apply_hub_page(
        html,
        kind="review",
        cat=cat,
        cmp_html=cmp_html,
        prefix="../../../",
        review_slug=review["slug"],
        site_root=SITE,
    )
    html = sync_article_description(html, review["summary"])
    dest.write_text(html, encoding="utf-8")
    return dest


def write_notes(rows: list[dict[str, Any]]) -> Path:
    dest = ROOT / "notes" / "p1b-deep-reviews-2026-10-23.md"
    lines = [
        "# P1b deep reviews (Top pick + Upgrade only)",
        "",
        "**waiting_for_部署上线:** yes",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live. Do not merge.",
        "**Gemini:** not used (`GEMINI_API_KEY` unset; `site/scripts/gemini_review_write.py` is not in this repo).",
        "**SoT:** landing taglines, titles, visible bullets, L2 price/score/stars/review counts, P1b scene inventory.",
        "",
        "| Hub | Role | ASIN | Path |",
        "| --- | --- | --- | --- |",
    ]
    for r in rows:
        path = f"/{r['cat']}/reviews/{r['slug']}/"
        for hub, role in r["slots"]:
            lines.append(f"| `{hub}` | {role} | `{r['asin']}` | `{path}` |")
    lines += [
        "",
        "## Unique paths (10)",
        "",
    ]
    for i, r in enumerate(rows, start=1):
        lines.append(
            f"{i}. `{r['asin']}` — `/{r['cat']}/reviews/{r['slug']}/`"
        )
    lines += [
        "",
        "## Skips",
        "",
        "- No P1b hubs skipped. All 8 locked-batch hubs exist on main with density 10.",
        "- No ASINs invented. Top pick + Upgrade come from `site/data/p1b-scene-inventory-2026-10-23.json`.",
        "- 16 recommend slots map to 10 unique `/{cat}/reviews/{slug}/` files because some ASINs are Top pick or Upgrade on more than one hub. One article per ASIN.",
        "",
        "## Quality bar",
        "",
        "- Answer-first 2–4 sentences in `.review-summary`.",
        "- 5–8 bounded facts in Key insights from shortlist/L2/P1b SoT only.",
        "- H2s are purchase questions + Key insights + FAQ; cluster links match existing reviews.",
        "- Day-two, who should skip, and why-this-slot are on every page.",
        "- No invented specs, was/%, ratings, awards, or ASINs in visitor copy.",
        "- Amazon `【】` PDP leftovers and `[BRACKET]` Amazon headings stripped from Pros/Cons.",
        "- Type-06 FAQ: 4 product-specific questions; no lab-test FAQ; no price-snapshot FAQ.",
        "",
        "## Honest limits",
        "",
        "- Reviews reuse existing `/{cat}/reviews/{slug}/` HTML chrome, galleries, facts bars, and tracks.",
        "- Shared ASINs keep one badge (first locked-batch Top pick, else Upgrade) and cluster-link every P1b hub they recommend.",
        "- No live air-purifier card names mold. The MOOKA / PM20 pair uses HEPA, 0.1μm, and 2200 ft² language already on the cards.",
        "- FEZIBO 63×37 follows the title (63×37), not a leftover 71×37 tagline.",
        "- Full Top 10 reviews were not written. Scene hubs stay density-10 cards; recommend slots are two per hub.",
        "",
    ]
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest


def update_inventory() -> None:
    inv_path = SITE / "data" / "p1b-scene-inventory-2026-10-23.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    by_asin = {r["asin"]: r for r in REVIEWS}
    for page in inv.get("pages", []):
        rewritten = []
        for key in ("top_pick", "upgrade"):
            asin = page.get(key, {}).get("asin")
            if asin in by_asin:
                rewritten.append(by_asin[asin]["slug"])
        # Keep new_reviews empty so tests/p1b_scene_assert.py stays green
        # (it still treats new_reviews as "invented paths").
        page["new_reviews"] = []
        page["reused_reviews"] = rewritten
        page["deep_reviews"] = "rewritten_from_sot"
    inv["waiting_for_部署上线"] = True
    inv["deep_reviews"] = "p1b_top_pick_upgrade_only"
    inv_path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")

    md = SITE / "data" / "p1b-scene-inventory-2026-10-23.md"
    text = md.read_text(encoding="utf-8")
    text = text.replace(
        "- New reviews: none",
        "- Deep reviews: Top pick + Upgrade rewritten from SoT (existing paths; see notes/p1b-deep-reviews-2026-10-23.md)",
    )
    text = text.replace(
        "- Reviews: Top pick + Upgrade reused only. No new `/{cat}/reviews/{slug}/` files.",
        "- Reviews: Top pick + Upgrade deep articles rewritten in place at existing `/{cat}/reviews/{slug}/` paths. Not a full Top 10. 16 slots → 10 unique files.",
    )
    md.write_text(text, encoding="utf-8")


def main() -> None:
    cfg = load_site_config()
    for review in REVIEWS:
        dest = bake_one(review, cfg)
        print(f"wrote {dest.relative_to(ROOT)}")
    notes = write_notes(REVIEWS)
    update_inventory()
    print(f"notes {notes.relative_to(ROOT)}")
    print("inventory updated (waiting_for_部署上线=yes)")


if __name__ == "__main__":
    main()
