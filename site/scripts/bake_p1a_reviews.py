#!/usr/bin/env python3
"""Bake P1a Top pick + Upgrade deep reviews from in-repo SoT only.

Draft only. No wrangler / no Live deploy. No Lab / RR / OL edits.
No Gemini — GEMINI_API_KEY is not required. Copy is authored from
landing taglines, title fields, visible bullets, L2 price/score/stars,
and P1a scene inventory. Do not invent specs, was/%, ratings, awards, or ASINs.

Usage:
    python3 site/scripts/bake_p1a_reviews.py
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
    "<!-- waiting_for_部署上线: yes. P1a deep reviews draft only. "
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


# --- SoT-bounded review payloads (title / tagline / bullets / L2 / P1a scene) ---

REVIEWS: list[dict[str, Any]] = [
    {
        "asin": "B0C9THG48W",
        "cat": "dehumidifiers",
        "slug": "waykar-80-pints-2025-energy-star",
        "short_name": "Waykar 80 Pints 2025 Energy Star Dehumidifier",
        "badge": "Top pick",
        "hub": "/dehumidifiers/best-dehumidifiers-for-basements/",
        "hub_label": "basement best-of",
        "checked": "2026-10-20",
        "score_line": "8.6 Very good on this card",
        "summary": (
            "The Waykar 80-pint Energy Star dehumidifier is the Top pick on our basement best-of "
            "when a damp lower level needs continuous pull without jumping to a commercial 8,000 sq ft claim. "
            "The listing sizes it for large homes and basements up to 5,000 sq ft, with a drain hose, "
            "auto-defrost, and self-drying on the title. Skip it if a 50-pint apartment job is the real room, "
            "or if one bathroom is the only wet spot."
        ),
        "insights": [
            (
                "Scene slot, not chart paste",
                "This is the Top pick on the basement best-of. The category comparison leads with a higher-pint card sized around a much smaller room, so the scene does not paste score order.",
            ),
            (
                "Coverage the title actually claims",
                "Title language is 80 pints and up to 5,000 sq ft for basement, bathroom, and large-room use—not a whole-house brochure we invented.",
            ),
            (
                "Cool-week safeguards on the listing",
                "2025 Energy Star, auto-defrost, and self-drying sit on the title and feature bullets for seasonal wet weeks.",
            ),
            (
                "Unattended drain path",
                "The title includes a drain hose and portable setup. Confirm hose length and a floor-drain path on the retailer page via Check price.",
            ),
            (
                "Controls already on the card",
                "The live feature list includes a 24-hour timer and an onboard control panel. We do not invent a smart-app claim.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.6 from a 4.3 retailer rating across 3,223 reviews. Price snapshot $189.96, checked 2026-10-20—re-check live totals on the retailer page.",
            ),
        ],
        "pros": [
            "Top pick on the basement best-of for continuous residential pull without a commercial footprint.",
            "Title lists 80 pints, 5,000 sq ft basement coverage, drain hose, auto-defrost, and self-drying.",
            "Energy Star 2025 year label is on the card if the unit will run for months.",
        ],
        "cons": [
            "Skip apartment-sized 50-pint jobs, or a single closet, where an 80-pint machine is excess.",
            "Skip commercial 8,000 sq ft claims if one room is the real problem.",
        ],
        "sections": [
            (
                "Who should skip this 80-pint basement pick?",
                ul(
                    [
                        "Skip it if you only need a closet, laundry nook, or modest apartment room—the shortlist already keeps 30- and 34-pint neighbors for those jobs.",
                        "Skip it if you are shopping the commercial 8,000 sq ft card for a restoration footprint. That is a different slot on the same comparison.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like in a wet basement?",
                p(
                    "Plan the drain first. An 80-pint listing will outrun a bucket you empty by hand after a wet week, "
                    "which is why the title includes a hose. Route it to a floor drain or sump, then use the self-drying "
                    "cycle before you store the unit in a dry season. Confirm reservoir size, weight, and doorway clearance "
                    "on the retailer page—those fields are not on the shortlist card."
                )
                + p(
                    "Auto-defrost is the cool-basement feature already on the title. We do not invent a lowest operating "
                    "temperature. If the space sits near freezing, confirm the listing range via Check price before you leave it running."
                ),
            ),
            (
                "How does this handle a cool, damp basement versus a finished living room?",
                p(
                    "Basements punish units that ice up and units that cannot drain unattended. The Waykar card is written "
                    "for that mix: 80-pint pull, 5,000 sq ft basement language, auto-defrost, and a hose. A finished living "
                    "room that is only slightly damp is not the reason this is the scene Top pick."
                ),
            ),
            (
                "Why is this the Top pick instead of the AEOCKY Upgrade?",
                p(
                    "The basement best-of leads with residential coverage that matches a typical damp lower level. "
                    "AEOCKY 5500 is the Upgrade when Most Efficient 2025 labeling and a higher claimed footprint matter "
                    "through a wet summer. Stay here if 5,000 sq ft plus a hose is the job and you do not want the efficiency-tier step-up."
                )
                + p(
                    "Read the Upgrade review or open the "
                    + _a("../../best-dehumidifiers-for-basements/", "basement best-of")
                    + " and the "
                    + _a("../aeocky-5500-sqft-energy-star-most/", "AEOCKY 5500 review")
                    + " before you pay for the extra coverage claim."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Waykar 80-pint on a basement shortlist?",
                "Skip it for a closet, half-bath, or apartment-sized 50-pint job. Skip the commercial 8,000 sq ft neighbor if one residential basement is the real room.",
            ),
            (
                "Does this unit include a drain hose for unattended wet weeks?",
                "Yes. The title lists a drain hose with the portable basement setup. Confirm hose length and a gravity path to a floor drain or sump on the retailer page.",
            ),
            (
                "How does this Top pick differ from the AEOCKY 5500 Upgrade?",
                "Waykar is the residential 5,000 sq ft basement default. AEOCKY is the Upgrade for Most Efficient 2025 labeling and a higher claimed 5,500 sq ft footprint when summer humidity stays high.",
            ),
            (
                "What should I confirm before leaving it in a cool basement?",
                "Confirm auto-defrost range, hose path, and stock on the retailer page via Check price. We do not invent a lowest operating temperature beyond the auto-defrost label on the card.",
            ),
        ],
        "next_extra": (
            "If 5,000 sq ft still feels short, read the AEOCKY Upgrade. "
            "If the room is smaller, scan the 30- and 34-pint neighbors on the comparison."
        ),
        "cluster": [
            ("../", "All dehumidifier reviews"),
            ("../../comparison/", "Dehumidifiers comparison"),
            ("../../best-dehumidifiers-for-basements/", "Best for basements"),
            ("../aeocky-5500-sqft-energy-star-most/", "AEOCKY 5500 review"),
        ],
        "cta": ("../../comparison/", "Back to Dehumidifiers comparison"),
    },
    {
        "asin": "B0D1C6HWFF",
        "cat": "dehumidifiers",
        "slug": "aeocky-5500-sqft-energy-star-most",
        "short_name": "AEOCKY 5500 Sq.Ft Energy Star Most Efficient",
        "badge": "Upgrade",
        "hub": "/dehumidifiers/best-dehumidifiers-for-basements/",
        "hub_label": "basement best-of",
        "checked": "2026-10-20",
        "score_line": "9.0 Excellent on this card",
        "summary": (
            "Choose the AEOCKY 5500 sq ft Energy Star Most Efficient dehumidifier when Waykar’s 5,000 sq ft "
            "basement sizing still feels short through a wet summer. It is the Upgrade on our basement best-of: "
            "Most Efficient 2025 labeling plus an 80 pint/day mid-summer claim on the card. Skip it if a quiet "
            "50-pint with a drain hose already keeps humidity in range."
        ),
        "insights": [
            (
                "Upgrade slot on the basement slice",
                "Editorial Upgrade when the basement stays wet through summer and Waykar’s 5,000 sq ft sizing still feels short.",
            ),
            (
                "Coverage the title claims",
                "The title is 5,500 sq ft and Energy Star Most Efficient 2025, with a max 80 pint/day line on the review heading.",
            ),
            (
                "Mid-summer pint claim on the bullet",
                "The live feature list states 80 pint/day in humid mid-summer conditions. We do not add a second pint number the truncated card does not show.",
            ),
            (
                "Most Efficient is a listing tier, not our award",
                "The bullet distinguishes Energy Star Most Efficient 2025 from a plain Energy Star year badge. That is manufacturer labeling on the shortlist, not a MoreTop10 prize.",
            ),
            (
                "Skip path already on the tagline",
                "Stay with a quiet 50-pint plus hose if that already holds relative humidity. The 50-pint neighbor remains on the same comparison.",
            ),
            (
                "Price and score snapshot",
                "Chart score 9.0 from a 4.5 retailer rating across 7,225 reviews. Price snapshot $224.97, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Upgrade when summer humidity outruns a residential 5,000 sq ft card.",
            "Title and bullets carry Energy Star Most Efficient 2025 plus 5,500 sq ft.",
            "80 pint/day mid-summer claim is already on the live feature list.",
        ],
        "cons": [
            "Skip if a 50-pint with a drain hose already keeps humidity in range.",
            "Most Efficient is a listing label, not a reason to oversize a single bathroom.",
        ],
        "sections": [
            (
                "Who should skip this Upgrade?",
                ul(
                    [
                        "Skip it if a standard 50-pint with a hose already holds the room—the tagline says so.",
                        "Skip it if you only need the Waykar 80-pint residential default. That is the scene Top pick, not a lesser leftover.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like at this pint claim?",
                p(
                    "An 80 pint/day mid-summer listing will fill a bucket faster than a light room unit. Place it where a hose can reach a floor drain or sump, then empty only as a backup. "
                    "We do not invent tank liters or noise numbers—confirm those on the retailer page via Check price."
                )
                + p(
                    "Efficiency-tier language matters if the compressor will run for months. It does not replace a drain path. Compare running-cost claims on the listing; we do not publish a percent-saved figure."
                ),
            ),
            (
                "What does Energy Star Most Efficient 2025 change on this card?",
                p(
                    "The feature list treats Most Efficient 2025 as a narrower listing tier than a plain Energy Star year badge. "
                    "Use that as a label to re-check on the retailer page, not as a paid award and not as a lab result we ran."
                ),
            ),
            (
                "Why is this the Upgrade instead of the Waykar Top pick?",
                p(
                    "Waykar holds the basement default for 5,000 sq ft continuous pull. This card steps up claimed coverage to 5,500 sq ft and the Most Efficient 2025 label. "
                    "Pay that step only when the lower level still feels wet after a residential 80-pint setup."
                )
                + p(
                    "Read the "
                    + _a("../waykar-80-pints-2025-energy-star/", "Waykar 80-pint review")
                    + " or return to the "
                    + _a("../../best-dehumidifiers-for-basements/", "basement best-of")
                    + " to see both slots on the same slice."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the AEOCKY 5500 Upgrade?",
                "Skip it if a quiet 50-pint with a drain hose already keeps humidity in range, or if the Waykar 80-pint residential default already matches the room.",
            ),
            (
                "What does Energy Star Most Efficient 2025 mean on this card?",
                "It is a listing tier on the title and bullets, written as distinct from a plain Energy Star year badge. It is not a MoreTop10 award and not a lab score we measured.",
            ),
            (
                "When should I stay with the Waykar 80-pint instead?",
                "Stay with Waykar when 5,000 sq ft plus a hose is enough and you do not need the 5,500 sq ft / Most Efficient step-up. That card is the scene Top pick.",
            ),
            (
                "What do I need to plan for day-two water removal?",
                "Plan a hose to a floor drain or sump. The card’s 80 pint/day mid-summer claim is too high to treat bucket emptying as the default chore. Confirm tank size on the retailer page.",
            ),
        ],
        "next_extra": (
            "If you do not need the efficiency-tier step-up, read the Waykar Top pick. "
            "If you need a pump drain, open the LEVOIT basement neighbor on the comparison."
        ),
        "cluster": [
            ("../", "All dehumidifier reviews"),
            ("../../comparison/", "Dehumidifiers comparison"),
            ("../../best-dehumidifiers-for-basements/", "Best for basements"),
            ("../waykar-80-pints-2025-energy-star/", "Waykar 80-pint review"),
        ],
        "cta": ("../../comparison/", "Back to Dehumidifiers comparison"),
    },
    {
        "asin": "B0GXKSC38S",
        "cat": "air-purifiers",
        "slug": "levoit-smart-pet-air-purifier-home",
        "short_name": "LEVOIT Smart Pet Air Purifier for Home Pets",
        "badge": "Top pick",
        "hub": "/air-purifiers/best-air-purifiers-for-pets/",
        "hub_label": "pet air-purifier best-of",
        "checked": "2026-10-20",
        "score_line": "9.2 Excellent on this card",
        "summary": (
            "Vital Pet Pro is the Top pick on our pet air-purifier best-of when odor and dander in the rooms "
            "animals use matter more than a hair-collection show. The card pairs smart controls with 140 g of "
            "activated carbon and TVOC plus PM2.5 sensors. Skip the Dreame AP10 if you do not need a visible "
            "hair bin, and skip 3-in-1 heater/fan hybrids if purification is the only job."
        ),
        "insights": [
            (
                "Pet-named tower leads the scene",
                "This is the Top pick on the pet best-of. Comparison #1 is a filter-longevity card without pet-odor copy, so the scene does not paste score order.",
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
                "Stay here for odor and dander. Move to the AP10 Upgrade when floating hair on floors is the daily complaint.",
            ),
            (
                "Skip climate hybrids",
                "The tagline says this is the pet-first tower when you do not need a heater/fan hybrid. Those 3-in-1 cards sit mid-chart as neighbors.",
            ),
            (
                "Price and score snapshot",
                "Chart score 9.2 from a 4.6 retailer rating across 5,229 reviews. Price snapshot $179.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Top pick on the pet best-of for odor and dander in rooms animals actually use.",
            "140 g activated carbon and TVOC plus PM2.5 sensors are on the live bullets.",
            "Smart-control pet tower without paying for a heater/fan hybrid.",
        ],
        "cons": [
            "Skip if floating hair collection is the job—that is the AP10 Upgrade.",
            "Skip if you need a 3-in-1 climate tower as the main appliance.",
        ],
        "sections": [
            (
                "Who should skip Vital Pet Pro?",
                ul(
                    [
                        "Skip it if you want a visible hair-collection compartment. That is the Dreame AP10 Upgrade on the same slice.",
                        "Skip it if a heater/fan hybrid is the real purchase. Pet dander is only one line on those climate cards.",
                    ]
                ),
            ),
            (
                "What does day-two ownership cost in a pet room?",
                p(
                    "Filter changes are the day-two cost, not a year-change slogan on a neighbor card. The listing mentions an auto-clean pre-filter aimed at captured pet hair; treat that as a listing claim and confirm replacement cartridges on the retailer page via Check price."
                )
                + p(
                    "Support copy on the card points to the retailer order page. Confirm warranty terms there. We do not invent filter-life months."
                ),
            ),
            (
                "How does this handle pet odor versus floating hair?",
                p(
                    "Odor is a gas-and-carbon job. The 140 g carbon load plus a TVOC sensor is why this card leads the pet slice. "
                    "Floating hair that you can see on floors is a different job—the AP10 lists a transparent compartment and high negative-pressure return for that."
                ),
            ),
            (
                "Why is this the Top pick instead of comparison #1?",
                p(
                    "AEOCKY YearChange leads the comparison on score. Its on-page copy is filter longevity, not pet odor or hair, so the pet best-of keeps it as a neighbor. "
                    "Vital Pet Pro is the landing Top pick for pet homes, and this review keeps that slot."
                )
                + p(
                    "Compare both roles on the "
                    + _a("../../best-air-purifiers-for-pets/", "pet air-purifier best-of")
                    + " or read the "
                    + _a("../dreame-pet-air-purifier-ap10-suck/", "Dreame AP10 review")
                    + " if hair, not odor, is the complaint."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the LEVOIT Vital Pet Pro?",
                "Skip it if you want a visible hair bin (AP10) or a 3-in-1 heater/fan hybrid. Stay here when odor and dander in pet rooms are the job.",
            ),
            (
                "How does this Top pick differ from the Dreame AP10 Upgrade?",
                "Vital Pet Pro is odor and dander with 140 g of carbon and dual sensors. AP10 is the hair-collection Upgrade with a transparent compartment and high negative-pressure return.",
            ),
            (
                "What on the card actually targets pet odor?",
                "The feature list states 140 g of activated carbon for dog odor and cat-litter smell, plus a TVOC sensor. Confirm room coverage on the retailer page—we do not invent CADR.",
            ),
            (
                "Why isn’t the comparison #1 the pet default?",
                "Comparison #1 is AEOCKY YearChange, written for filter longevity. The pet best-of reorders to pet-named towers. Roles are editorial labels, not paid awards.",
            ),
        ],
        "next_extra": (
            "If hair on floors is the daily complaint, read the AP10 Upgrade. "
            "If you only need a small bedroom tower, open the comparison neighbors."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-pets/", "Best for pets"),
            ("../dreame-pet-air-purifier-ap10-suck/", "Dreame AP10 review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B0FS68R44C",
        "cat": "air-purifiers",
        "slug": "dreame-pet-air-purifier-ap10-suck",
        "short_name": "Dreame Pet Air Purifier AP10, Suck Up Floating",
        "badge": "Upgrade",
        "hub": "/air-purifiers/best-air-purifiers-for-pets/",
        "hub_label": "pet air-purifier best-of",
        "checked": "2026-10-20",
        "score_line": "8.4 Very good on this card",
        "summary": (
            "The Dreame AP10 is the Upgrade on our pet air-purifier best-of when floating hair on floors is "
            "the daily complaint, not just odor. The listing leans on high negative-pressure return and a "
            "transparent hair compartment you empty without guessing. Stay with Vital Pet Pro if odor and "
            "dander are the job, or skip to a bedroom HEPA if that is all you need."
        ),
        "insights": [
            (
                "Upgrade for hair, not score order",
                "This card sits later on the comparison (not #1) and still earns the pet Upgrade because the title is a pet hair collector.",
            ),
            (
                "Negative-pressure return on the bullet",
                "The feature list states 360° high negative-pressure air return for long-range cat-hair capture and auto collection.",
            ),
            (
                "Visible compartment you empty",
                "A fully transparent hair-collection compartment is on the card so you do not open a hidden bin to guess when it is full.",
            ),
            (
                "Triple-layer claim stays on the listing",
                "The bullet lists triple-layer purification for hair, fine particles, and pet odor. We do not invent CADR or filter-life months.",
            ),
            (
                "Skip path on the tagline",
                "Skip if you only need bedroom HEPA at a Best value price. That is a different job than living-room hair.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.4 from a 4.2 retailer rating across 94 reviews. Price snapshot $209.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Upgrade when floating hair, not just odor, is the daily complaint.",
            "Transparent compartment plus 360° negative-pressure return are on the live bullets.",
            "Pet-named title—one of two cards on the shortlist whose name says pet.",
        ],
        "cons": [
            "Skip if odor and dander are the job—that is Vital Pet Pro.",
            "Skip if a small bedroom HEPA is enough and you do not want a hair-collection tower.",
        ],
        "sections": [
            (
                "Who should skip the AP10?",
                ul(
                    [
                        "Skip it if odor and dander, not visible hair, are the complaint. Vital Pet Pro is the scene Top pick for that.",
                        "Skip it if you only need a bedroom HEPA at Best value pricing. The tagline already sends those shoppers away.",
                    ]
                ),
            ),
            (
                "What do you empty on day two?",
                p(
                    "The transparent compartment is the day-two chore: empty captured hair when you can see it, then keep the triple-layer stack from choking. "
                    "Confirm how the compartment opens and what replacement filters cost on the retailer page via Check price."
                )
                + p(
                    "This is not a heater/fan hybrid. If you expected climate hardware, you are on the wrong card."
                ),
            ),
            (
                "How does hair collection differ from a standard bedroom tower?",
                p(
                    "Most bedroom towers hide hair inside a sealed filter you only notice when airflow drops. AP10 lists a high negative-pressure return and a see-through bin so hair is a visible job, not a surprise. "
                    "That is why the pet best-of uses it as Upgrade instead of a score-sorted bedroom card."
                ),
            ),
            (
                "Why is this the Upgrade instead of the LEVOIT Top pick?",
                p(
                    "Vital Pet Pro leads for odor and dander. AP10 steps up when you want a hair path you can see. "
                    "Pay the Upgrade only if floating hair is the daily mess; do not buy it as a louder odor tower."
                )
                + p(
                    "Read the "
                    + _a("../levoit-smart-pet-air-purifier-home/", "Vital Pet Pro review")
                    + " or the "
                    + _a("../../best-air-purifiers-for-pets/", "pet air-purifier best-of")
                    + " to keep the fork honest."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Dreame AP10?",
                "Skip it if you only need bedroom HEPA, or if odor and dander—not visible hair—are the job. Vital Pet Pro is the scene Top pick for odor.",
            ),
            (
                "When is AP10 the better pet buy than Vital Pet Pro?",
                "Choose AP10 when floating hair on floors is the daily complaint and you want a transparent collection compartment. Stay with Vital Pet Pro when odor and dander matter more.",
            ),
            (
                "What do I empty on day two?",
                "The listing’s transparent hair compartment. Empty it when you can see the load, then confirm replacement-filter cost on the retailer page. We do not invent a bin-liter size.",
            ),
            (
                "Is this the score-sorted #1 on the comparison?",
                "No. It sits later on the comparison and still earns the pet Upgrade because the title and bullets are hair collection, not a score paste.",
            ),
        ],
        "next_extra": (
            "If odor is the job, read Vital Pet Pro. "
            "If you only need a small room, scan the comparison’s bedroom neighbors."
        ),
        "cluster": [
            ("../", "All air purifier reviews"),
            ("../../comparison/", "Air purifiers comparison"),
            ("../../best-air-purifiers-for-pets/", "Best for pets"),
            ("../levoit-smart-pet-air-purifier-home/", "Vital Pet Pro review"),
        ],
        "cta": ("../../comparison/", "Back to Air Purifiers comparison"),
    },
    {
        "asin": "B0FK2HPNCB",
        "cat": "robot-vacuums",
        "slug": "eufy-e25-robot-vacuum-mop-combo",
        "short_name": "eufy E25 Robot Vacuum and Mop Combo, 20,000 Pa",
        "badge": "Top pick",
        "hub": "/robot-vacuums/pet-homes/",
        "hub_label": "pet-homes niche",
        "checked": "2026-10-20",
        "score_line": "8.8 Very good on this card",
        "summary": (
            "The eufy E25 is the Top pick on our pet-homes niche when carpet pet hair and anti-tangle matter "
            "more than the category’s Omni C20 dock default. The card lists 20,000 Pa for embedded pet hair, "
            "DuoSpiral brushes, and a HydroJet roller that rinses with clean water, then dries at 50°C. Skip "
            "it if Omni C20’s empty-plus-wash dock already matches the job, or if you have no pets and only want a thin flagship."
        ),
        "insights": [
            (
                "Pet-homes Top pick, category Upgrade",
                "The pet-homes niche leads with E25. The category landing still treats Omni C20 as #1 and this card as the mopping Upgrade. Both roles are editorial, not paid awards.",
            ),
            (
                "Suction the title claims",
                "The title and a live bullet list 20,000 Pa for dirt and pet hair in carpet fibers. We do not invent a second Pa number.",
            ),
            (
                "DuoSpiral anti-tangle",
                "Tagline and feature copy name DuoSpiral brushes so pet hair does not wrap the roller and kill suction.",
            ),
            (
                "HydroJet plus dock dry",
                "The listing says the roller refreshes with clean water 2 times per second, then the dock applies 50°C hot-air drying.",
            ),
            (
                "Bag the card sizes",
                "The all-in-one station auto-empties into a 3 L bag the bullet rates at about 75 days. Confirm bag stock on the retailer page.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.8 from a 4.4 retailer rating across 54,673 reviews. Price snapshot $629.99, checked 2026-10-20.",
            ),
        ],
        "pros": [
            "Top pick on the pet-homes niche for carpet pet hair plus anti-tangle.",
            "20,000 Pa, DuoSpiral brushes, HydroJet rinse, and 50°C dock drying are on the card.",
            "3 L self-empty bag is listed at about 75 days—useful when hair volume would clog a bin.",
        ],
        "cons": [
            "Skip if Omni C20’s empty-plus-wash dock already matches the job.",
            "Skip if you have no pets and only want a thin flagship clearance robot.",
        ],
        "sections": [
            (
                "Who should skip the E25 on a pet-hair slice?",
                ul(
                    [
                        "Skip it if the Omni C20 empty-plus-wash dock is already enough. That card stays on the niche as a neighbor, not the pet-hair lead.",
                        "Skip it if you have no pets and only want furniture-clearance height. The Saros neighbor’s own skip-if is written for that shopper.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like after a hair-heavy week?",
                p(
                    "Day two is bag and mop care, not a second vacuum pass. The dock empties into the 3 L bag and washes the HydroJet roller, then dries it at 50°C. "
                    "Confirm bag replacements and dock footprint on the retailer page via Check price."
                )
                + p(
                    "Anti-tangle reduces wrap; it does not erase long hair. Check the DuoSpiral rollers when you empty the bag. We do not invent a wrap-free guarantee."
                ),
            ),
            (
                "How does HydroJet change hard floors when paws track?",
                p(
                    "The listing’s HydroJet copy is clean-water rinse on the roller, 2 times per second, instead of dragging one dirty pad. That matters if paws track onto hard floors you will mop weekly. "
                    "If you never mop, you are paying for a dock feature you will not use—stay with a vacuum-first neighbor."
                ),
            ),
            (
                "Why is this the pet-homes Top pick instead of Omni C20?",
                p(
                    "Omni C20 is category #1 and mentions pet hair in Boost IQ, but the card is written as a mid-range empty-plus-wash default. "
                    "E25’s live card calls out 20,000 Pa for carpet pet hair plus DuoSpiral anti-tangle, which is why the niche leads here."
                )
                + p(
                    "Step to the "
                    + _a("../roborock-2026-new-qrevo-s-pro/", "Qrevo S Pro Upgrade")
                    + " when a pet-homes brush system and a multi-week sealed bag are the job. Both sit on the "
                    + _a("../../pet-homes/", "pet-homes niche")
                    + "."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the eufy E25 on a pet-hair slice?",
                "Skip it if Omni C20’s empty-plus-wash dock already matches the job, or if you have no pets and only want a thin flagship. This niche is for hair and anti-tangle.",
            ),
            (
                "Why is E25 the pet-homes Top pick instead of Omni C20?",
                "E25’s card lists 20,000 Pa for carpet pet hair and DuoSpiral anti-tangle. Omni C20 stays on the page as the mid-range dock neighbor, not the pet-hair lead.",
            ),
            (
                "What does the dock handle after a hair-heavy run?",
                "The listing says it auto-empties into a 3 L bag rated about 75 days, washes the HydroJet roller, and dries at 50°C. Confirm bag stock and dock size on the retailer page.",
            ),
            (
                "When is the Qrevo S Pro the better Upgrade?",
                "Choose Qrevo S Pro when the listing’s Anti-Tangle System for Pet Homes and a 7–9 week sealed 2.7 L bag match a heavier shed. Stay with E25 when HydroJet mopping plus 20,000 Pa is the job.",
            ),
        ],
        "next_extra": (
            "If you want the pet-homes brush system and a multi-week bag, read the Qrevo S Pro Upgrade. "
            "If a mid-range empty-plus-wash dock is enough, open Omni C20 on the comparison."
        ),
        "cluster": [
            ("../", "All robot vacuum reviews"),
            ("../../comparison/", "Robot vacuums comparison"),
            ("../../pet-homes/", "Pet-homes niche"),
            ("../roborock-2026-new-qrevo-s-pro/", "Qrevo S Pro review"),
        ],
        "cta": ("../../comparison/", "Back to Robot Vacuums & Mops comparison"),
    },
    {
        "asin": "B0GGRTD2ZY",
        "cat": "robot-vacuums",
        "slug": "roborock-2026-new-qrevo-s-pro",
        "short_name": "Roborock 2026 New Qrevo S Pro Robot Vacuum",
        "badge": "Upgrade",
        "hub": "/robot-vacuums/pet-homes/",
        "hub_label": "pet-homes niche",
        "checked": "2026-10-18",
        "score_line": "8.2 Very good on this card",
        "summary": (
            "The Roborock Qrevo S Pro is the Upgrade on our pet-homes niche when the listing’s "
            "“Anti-Tangle System for Pet Homes” and a multi-week sealed bag match a heavier shed. "
            "The dock empties into a 2.7 L bag the card rates for 7–9 weeks, then washes mops at 167°F "
            "and dries them at 113°F. Skip it if you have no pets and only want a thin flagship, or if "
            "E25’s HydroJet roller is the mopping job you already chose."
        ),
        "insights": [
            (
                "Upgrade on the pet-homes niche",
                "Editorial Upgrade for the named pet-homes brush system plus a sealed bag. Category rank is not the scene order.",
            ),
            (
                "Brush language that earned the slot",
                "The feature list states Anti-Tangle System for Pet Homes: zero-tangle side brush and an all-rubber main brush for pets and long hair.",
            ),
            (
                "Suction the title claims",
                "Title and bullet list 18,500 Pa. We do not invent a higher flagship number.",
            ),
            (
                "Sealed bag weeks on the tagline",
                "The dock empties into a sealed 2.7 L bag the card rates for 7–9 weeks—the hair-volume reason to step up from an open bin.",
            ),
            (
                "Mop wash and dry temperatures on the card",
                "Tagline lists 167°F high-temperature self-cleaning and 113°F warm-air drying. Confirm those on the retailer page; we did not measure them.",
            ),
            (
                "Price and score snapshot",
                "Chart score 8.2 from a 4.1 retailer rating across 6,687 reviews. Price snapshot $699.99, checked 2026-10-18.",
            ),
        ],
        "pros": [
            "Upgrade when the card’s pet-homes anti-tangle system and 7–9 week bag match a heavier shed.",
            "2.7 L sealed bag, 167°F mop wash, and 113°F dry are already on the tagline.",
            "18,500 Pa is on the title—secondary to anti-tangle on this niche.",
        ],
        "cons": [
            "Skip if E25’s HydroJet plus 20,000 Pa already matches the mopping-and-hair job.",
            "Skip if you have no pets and only want a thin flagship.",
        ],
        "sections": [
            (
                "Who should skip the Qrevo S Pro?",
                ul(
                    [
                        "Skip it if you have no pets and only want furniture clearance. This niche is a hair slice, not a flagship height contest.",
                        "Skip it if you already chose E25 for HydroJet mopping. Do not buy both docks for the same floor.",
                    ]
                ),
            ),
            (
                "What does day-two ownership look like with a sealed bag?",
                p(
                    "Day two is bag weeks and mop hygiene, not a daily bin. The card rates the 2.7 L sealed bag at 7–9 weeks and lists 167°F wash plus 113°F dry so pads are not left damp. "
                    "Confirm bag replacements and dock width on the retailer page via Check price."
                )
                + p(
                    "Anti-tangle helps long hair; still check the rubber main brush when you change the bag. We do not invent a zero-maintenance claim."
                ),
            ),
            (
                "Does the all-in-one dock replace a mop you wring by hand?",
                p(
                    "The listing’s dock copy is empty, hot wash, and warm dry after each use. That is the ownership pitch for busy and pet-friendly homes on the tagline. "
                    "If you never mop, the wash temperatures are features you will not use—buy a vacuum-first neighbor instead."
                ),
            ),
            (
                "Why is this the Upgrade instead of the eufy E25 Top pick?",
                p(
                    "E25 leads the niche for 20,000 Pa carpet hair plus DuoSpiral and HydroJet. Qrevo S Pro steps up when the named pet-homes brush system and a 7–9 week sealed bag are the heavier-shed job."
                )
                + p(
                    "Read the "
                    + _a("../eufy-e25-robot-vacuum-mop-combo/", "eufy E25 review")
                    + " or return to the "
                    + _a("../../pet-homes/", "pet-homes niche")
                    + " to see both recommend slots without a full Top 10."
                ),
            ),
        ],
        "faqs": [
            (
                "Who should skip the Qrevo S Pro?",
                "Skip it if you have no pets and only want a thin flagship, or if E25’s HydroJet roller already matches the mopping-and-hair job you chose.",
            ),
            (
                "What makes the brush system a pet-homes Upgrade?",
                "The feature list names an Anti-Tangle System for Pet Homes: zero-tangle side brush and an all-rubber main brush for pets and long hair. That copy, not a score paste, earned the Upgrade slot.",
            ),
            (
                "How long does the card say the sealed bag lasts?",
                "The tagline rates the sealed 2.7 L bag at 7–9 weeks. Confirm the live listing and replacement bags on the retailer page. We do not invent a longer interval.",
            ),
            (
                "When should I stay with the eufy E25?",
                "Stay with E25 when 20,000 Pa carpet pet hair plus HydroJet mopping is the job. Step here when the pet-homes brush system and multi-week sealed bag matter more.",
            ),
        ],
        "next_extra": (
            "If HydroJet mopping is the feature you actually want, read the E25 Top pick. "
            "If you only need a sealed-bag neighbor, scan Q7 M5+ on the comparison."
        ),
        "cluster": [
            ("../", "All robot vacuum reviews"),
            ("../../comparison/", "Robot vacuums comparison"),
            ("../../pet-homes/", "Pet-homes niche"),
            ("../eufy-e25-robot-vacuum-mop-combo/", "eufy E25 review"),
        ],
        "cta": ("../../comparison/", "Back to Robot Vacuums & Mops comparison"),
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
    html = html.replace(f'"dateModified":"2026-10-20"', f'"dateModified":"{DATE}"')
    html = html.replace(f'"dateModified":"2026-10-18"', f'"dateModified":"{DATE}"')
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
    dest = ROOT / "notes" / "p1a-deep-reviews-2026-10-23.md"
    lines = [
        "# P1a deep reviews (Top pick + Upgrade only)",
        "",
        "**waiting_for_部署上线:** yes",
        "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live. Do not merge.",
        "**Gemini:** not used (`GEMINI_API_KEY` unset; `site/scripts/gemini_review_write.py` is not in this repo).",
        "**SoT:** landing taglines, titles, visible bullets, L2 price/score/stars/review counts, P1a scene inventory.",
        "",
        "| Hub | Role | ASIN | Path |",
        "| --- | --- | --- | --- |",
    ]
    for r in rows:
        path = f"/{r['cat']}/reviews/{r['slug']}/"
        lines.append(
            f"| `{r['hub']}` | {r['badge']} | `{r['asin']}` | `{path}` |"
        )
    lines += [
        "",
        "## Six ASINs",
        "",
        "1. `B0C9THG48W` — `/dehumidifiers/reviews/waykar-80-pints-2025-energy-star/`",
        "2. `B0D1C6HWFF` — `/dehumidifiers/reviews/aeocky-5500-sqft-energy-star-most/`",
        "3. `B0GXKSC38S` — `/air-purifiers/reviews/levoit-smart-pet-air-purifier-home/`",
        "4. `B0FS68R44C` — `/air-purifiers/reviews/dreame-pet-air-purifier-ap10-suck/`",
        "5. `B0FK2HPNCB` — `/robot-vacuums/reviews/eufy-e25-robot-vacuum-mop-combo/`",
        "6. `B0GGRTD2ZY` — `/robot-vacuums/reviews/roborock-2026-new-qrevo-s-pro/`",
        "",
        "## Quality bar",
        "",
        "- Answer-first 2–4 sentences in `.review-summary`.",
        "- 5–8 bounded facts in Key insights from shortlist/L2/P1a SoT only.",
        "- H2s are purchase questions + Key insights + FAQ; cluster links match existing reviews.",
        "- Day-two, who should skip, and why-this-slot are on every page.",
        "- No invented specs, was/%, ratings, awards, or ASINs in visitor copy.",
        "- Amazon `【】` PDP leftovers removed from Pros/Cons and glance.",
        "- Type-06 FAQ: 4 product-specific questions; no lab-test FAQ; no price-snapshot FAQ.",
        "",
        "## Honest limits",
        "",
        "- Reviews reuse existing `/{cat}/reviews/{slug}/` HTML chrome, galleries, facts bars, and tracks.",
        "- E25 is Top pick on `/robot-vacuums/pet-homes/` and remains the mopping Upgrade on the category landing.",
        "- Qrevo S Pro badge is Upgrade for the niche (was Rank 7 leftover).",
        "- Full Top 10 reviews were not written. Scene hubs stay density-10 cards; recommend slots are two.",
        "",
    ]
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest


def update_inventory() -> None:
    inv_path = SITE / "data" / "p1a-scene-inventory-2026-10-23.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    by_asin = {r["asin"]: r for r in REVIEWS}
    for page in inv.get("pages", []):
        rewritten = []
        for key in ("top_pick", "upgrade"):
            asin = page.get(key, {}).get("asin")
            if asin in by_asin:
                rewritten.append(by_asin[asin]["slug"])
        page["new_reviews"] = rewritten
        page["reused_reviews"] = []
        page["deep_reviews"] = "rewritten_from_sot"
    inv["waiting_for_部署上线"] = True
    inv["deep_reviews"] = "p1a_top_pick_upgrade_only"
    inv_path.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")

    md = SITE / "data" / "p1a-scene-inventory-2026-10-23.md"
    text = md.read_text(encoding="utf-8")
    text = text.replace("- New reviews: none", "- Deep reviews: Top pick + Upgrade rewritten from SoT (see notes/p1a-deep-reviews-2026-10-23.md)")
    text = text.replace(
        "- Reviews: Top pick + Upgrade reused only. No new `/{cat}/reviews/{slug}/` files.",
        "- Reviews: Top pick + Upgrade deep articles rewritten in place at existing `/{cat}/reviews/{slug}/` paths. Not a full Top 10.",
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
