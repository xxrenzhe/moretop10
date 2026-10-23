#!/usr/bin/env python3
"""MoreTop10 SEO/GEO transforms (local bake only).

P0 (already on main): hub CollectionPage/ItemList, /authors/ hub, dual llms.txt,
Content-Signal, match noindex.

P1: sitewide robots preview, How-to-Cite strips, #geo-{ASIN} on comparison +
reviews (hubs and articles). Hubs already had cite + pick anchors.
Light G-ENGAGE: HTML Answer-first class (not JSON-LD-only) on money pages.
Author feeds: post thumbs use each target page's cover SoT (og/product/hero),
not a shared category cmp-hero.

Honest rules:
  - Product / Offer / ASIN / price come from Live HTML (comparison cards, hub picks,
    or the review page Price snapshot). Never invent amounts.
  - Review Article JSON-LD: emit Offer.price only when a real snapshot/catalog
    amount exists; otherwise drop a price-less Offer (GSC offers.price warning).
  - AggregateRating / Review / description only from retailer stars+counts and
    review-summary already on the page. Never invent awards, SKUs, or quotes.
  - Offer.availability only from a real catalog stock token — never fake InStock.
  - Merchant return/shipping stay omitted unless a published policy SoT exists.
  - Visitor FAQ / visible copy: no publishable, inventory-blocked, completeness gate,
    card checklist, PartnerBoost, Mac L2/CDP, PB∪YP, healthy track, L5 inventory,
    Snapshot $ price prefix, or other internal jargon.
  - Bake ≠ Deploy.
"""

from __future__ import annotations

import html
import json
import re
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from landing_faq import scrub_faqs  # noqa: E402
from watchouts import scrub_watchouts  # noqa: E402

LIVE = "https://moretop10.com"
ORG_LOGO = f"{LIVE}/icon-512.png"
ROBOTS_INDEX = "index,follow,max-image-preview:large"
ROBOTS_NOINDEX = "noindex,follow"
ASIN_RE = re.compile(r"\b(B0[0-9A-Z]{8,10})\b")

# Visitor-facing copy only. Do not strip affiliate track query params (uid=fromsll).
RETAILER_CONFIRM = (
    "Confirm current specs, stock, and returns on the retailer page."
)
PUBLISH_RULE = (
    "We only publish products with a title, gallery, and price snapshot."
)
UNPUBLISHED_UNTIL_TEN = (
    "We keep the category unpublished until we can fill ten honest cards."
)

JARGON_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Kids-bikes / feed draft leaks (full sentences first).
    (re.compile(
        r"Draft card from PartnerBoost L1\s*[—–-]\s*Mac L2 required before publish\.?",
        re.I,
    ), RETAILER_CONFIRM),
    (re.compile(r"Draft card from PartnerBoost L1[^.<]*\.?", re.I), RETAILER_CONFIRM),
    (re.compile(
        r"[^.<>]*Mac CDP blocked[^.<>]*?(?:\.|&hellip;|…)",
        re.I,
    ), RETAILER_CONFIRM),
    (re.compile(r"[^.<>]*Mac CDP blocked[^.<>]*", re.I), RETAILER_CONFIRM),
    (re.compile(
        r"Value-lane dual-handbrake kids bike;\s*replaces Chipmunk variant that L2[^.<>]*\.?",
        re.I,
    ), RETAILER_CONFIRM),
    (re.compile(r"replaces Chipmunk variant that L2[^.<>…]*[.…]?", re.I), ""),
    (re.compile(r";?\s*L2 In Stock ZIP \d+\.?", re.I), ""),
    (re.compile(r"\bMac CDP\b", re.I), ""),
    (re.compile(r"\bMac L2\b", re.I), ""),
    (re.compile(r"\bL2 In Stock\b", re.I), "In stock"),
    (re.compile(r"\bL2 showed Currently unavailable\b", re.I), "the prior listing was unavailable"),
    # Chrome methodology — visitor English, not “completeness gate” / “card checklist”.
    (re.compile(
        r"We only publish products that clear our (?:completeness gate|card checklist):\s*"
        r"title, gallery, price snapshot, and a healthy affiliate CTA\.?",
        re.I,
    ), PUBLISH_RULE),
    (re.compile(
        r"We publish products that clear our (?:completeness gate|card checklist) "
        r"\(title, gallery, price snapshot, and a healthy Check price CTA\)",
        re.I,
    ), PUBLISH_RULE.rstrip(".")),
    (re.compile(
        r"Every pick on this page (?:clears|meets) our "
        r"(?:completeness gate|card checklist|title, gallery, and price snapshot):\s*"
        r"a usable title, product imagery, a current price snapshot, and a Check price CTA"
        r" that opens the retailer\.?",
        re.I,
    ), PUBLISH_RULE),
    (re.compile(
        r"Editorial work is the shortlist and (?:completeness gate|card checklist) "
        r"\(title, gallery, price snapshot, Check price CTA\)\.?",
        re.I,
    ), "Editorial work is the shortlist: a title, gallery, price snapshot, and Check price link."),
    (re.compile(
        r"Every card must clear the (?:completeness gate|card checklist):\s*"
        r"title, gallery, price snapshot, and a[^.]*\.?",
        re.I,
    ), "Every card needs a title, gallery, and price snapshot."),
    (re.compile(
        r"Every ranked card clears the same gate:\s*clear title, usable gallery, "
        r"price snapshot, and a healthy Check price CTA\.?",
        re.I,
    ), PUBLISH_RULE),
    (re.compile(
        r"when the shortlist clears our (?:completeness gate|card checklist)",
        re.I,
    ), "when each pick has a title, gallery, and price snapshot"),
    (re.compile(
        r"Thin imagery or stock fails the (?:completeness gate|card checklist)\.?",
        re.I,
    ), "We skip listings that are missing a title, gallery, or price snapshot."),
    (re.compile(
        r"(\d+) products clear the (?:completeness gate|card checklist)",
        re.I,
    ), r"\1 products include a title, gallery, and price snapshot"),
    (re.compile(
        r"using our (?:completeness gate|card checklist) and role labels",
        re.I,
    ), "using a title, gallery, and price snapshot"),
    (re.compile(
        r"when a product fails the (?:completeness gate|card checklist)",
        re.I,
    ), "when a product is missing a title, gallery, or price snapshot"),
    (re.compile(
        r"clears our (?:completeness gate|card checklist)",
        re.I,
    ), "has a title, gallery, and price snapshot"),
    (re.compile(r"\bcompleteness-gated\b", re.I), "complete"),
    (re.compile(r"Completeness-gated picks", re.I), "Complete shortlist picks"),
    (re.compile(r"completeness gate", re.I), "title, gallery, and price snapshot"),
    (re.compile(r"card checklist", re.I), "title, gallery, and price snapshot"),
    # Inventory hold — visitor English, not “inventory-blocked”.
    (re.compile(
        r"A category that cannot fill ten stays (?:inventory-blocked|held)"
        r"(?: until listings are complete)?—we do not ship a short chart\.?",
        re.I,
    ), UNPUBLISHED_UNTIL_TEN),
    (re.compile(
        r"If we cannot fill ten(?: solid cards)?, we hold the category rather than "
        r"(?:pad the chart|ship a short chart)\.?",
        re.I,
    ), UNPUBLISHED_UNTIL_TEN),
    (re.compile(
        r"Incomplete inventory keeps the category (?:inventory-blocked|held) "
        r"rather than shipping a short list\.?",
        re.I,
    ), UNPUBLISHED_UNTIL_TEN),
    (re.compile(r"inventory[_-]blocked", re.I), "unpublished"),
    (re.compile(r"\bpublishable\b", re.I), "live"),
    # Network / lab names that must never reach visitors.
    (re.compile(r"(?<![A-Za-z0-9.-])PartnerBoost(?![A-Za-z0-9.-])", re.I), "our retail partner"),
    (re.compile(r"(?<![A-Za-z0-9.-])YeahPromos(?![A-Za-z0-9.-])", re.I), "our retail partner"),
    (re.compile(r"(?<![A-Za-z0-9.-])PartnerWhiz(?![A-Za-z0-9.-])", re.I), "our retail partner"),
    (re.compile(r"\bSeaker\b", re.I), "our product research"),
    (re.compile(r"\bG-HD\b|\bG-IL\b|\bG-SE\b|\bG-NM\b", re.I), ""),
    (re.compile(r"\bL1/L2\b|\bL2\b evidence|\bL1\b feed", re.I), "listing"),
    (re.compile(r"\(listing\)", re.I), ""),
    (re.compile(r"\(fromsll\)", re.I), ""),
    (re.compile(r"aff_pb_autoads", re.I), ""),
    # American English (visitor-facing; do not touch <time datetime>).
    (re.compile(r"\bwhilst\b"), "while"),
    (re.compile(r"\bWhilst\b"), "While"),
    (re.compile(r"\btowards\b"), "toward"),
    (re.compile(r"\bTowards\b"), "Toward"),
    (re.compile(r"\bUtilize\b"), "Use"),
    # TV / day-add ops copy — visitor English, keep the real price.
    (re.compile(
        r"No healthy track in current PB∪YP feed\. Decision-tree slot stays empty\.",
        re.I,
    ), "No retailer link yet."),
    (re.compile(
        r"No healthy track\. Do not invent a Walmart or Amazon hop\.",
        re.I,
    ), "No retailer link yet."),
    (re.compile(r"L5 inventory still empty\. Content-only\.", re.I), "No retailer link yet."),
    (re.compile(
        r"These decision-tree slots stay visible and empty\.",
        re.I,
    ), "These options stay listed even when we don't have a checkout link yet."),
    (re.compile(r"Content-only follow-ups:", re.I), "Related guides:"),
    (re.compile(r"(?i)\bsnapshot (\$[0-9][0-9,]*(?:\.[0-9]{2})?)"), r"\1"),
    (re.compile(r"\bSnapshot [Pp]rice\b"), "Price"),
    (re.compile(r"\bSnapshot pricing\b"), "Price"),
    (re.compile(r"\bSnapshot value\b"), "Price"),
    (re.compile(r"\bPrice snapshot:"), "Price:"),
    (re.compile(
        r"What does the (\$[0-9][0-9,]*(?:\.[0-9]{2})?) price snapshot mean\?",
        re.I,
    ), r"What does the \1 price mean?"),
    (re.compile(
        r"(\$[0-9][0-9,]*(?:\.[0-9]{2})?) figure is a publish-time snapshot",
        re.I,
    ), r"\1 figure is the price we last checked"),
    (re.compile(
        r"price snapshot of (\$[0-9][0-9,]*(?:\.[0-9]{2})?)",
        re.I,
    ), r"current price about \1 — confirm on the retailer page"),
    (re.compile(
        r"(?:a )?snapshot price of (\$[0-9][0-9,]*(?:\.[0-9]{2})?)",
        re.I,
    ), r"current price about \1 — confirm on the retailer page"),
    (re.compile(
        r"(?:a |an )?(\$[0-9][0-9,]*(?:\.[0-9]{2})?) price snapshot",
        re.I,
    ), r"about \1"),
    # Visible ASIN prose — keep data-asin / JSON-LD sku.
    (re.compile(r" or ASIN B0[0-9A-Z]{8,} on Amazon", re.I), " on the retailer page"),
    (re.compile(r"search for ASIN B0[0-9A-Z]{8,} on Amazon", re.I), "search on the retailer page"),
    (re.compile(r"referenced under ASIN B0[0-9A-Z]{8,}", re.I), "listed on the retailer page"),
    (re.compile(r"\s*\(ASIN:\s*B0[0-9A-Z]{8,}\)", re.I), ""),
    (re.compile(r"\s*\(ASIN\s+B0[0-9A-Z]{8,}\)", re.I), ""),
    (re.compile(r"\s+under ASIN\s+B0[0-9A-Z]{8,}", re.I), ""),
    (re.compile(r"those ASINs", re.I), "those products"),
    (re.compile(r"invent an ASIN", re.I), "invent a product"),
    (re.compile(r"invented ASIN", re.I), "invented product"),
    (re.compile(r"no Check price button and no ASIN", re.I), "no Check price button and no product listing"),
    (re.compile(r"no Check price button, no ASIN,", re.I), "no Check price button, no product listing,"),
    (re.compile(r"or an ASIN", re.I), "or a product"),
    (re.compile(r"and no ASIN\.", re.I), "and no product listing."),
    (re.compile(r"No invented ASIN", re.I), "No invented product"),
    (re.compile(
        r"we did not have an ASIN in the baked HTML",
        re.I,
    ), "we did not have a product identifier in the baked HTML"),
    # Day-add leftovers (raw ops + #35 word-swap remnants).
    (re.compile(
        r"Chart prices are a(?: Mac CDP)?\s+listing check \(ZIP 10001\)—not a live cart\.",
        re.I,
    ), "Chart prices are a listing check (ZIP 10001)—not a live cart."),
    (re.compile(
        r"Prices and Check price come from(?: Mac CDP)?\s*L2 plus a verified "
        r"(?:PartnerBoost|our retail partner) fromsll track\.",
        re.I,
    ), "Prices and Check price come from a checked retailer listing."),
    (re.compile(
        r"from the day-add inventory after accessory exclusions\.",
        re.I,
    ), "after we dropped accessories."),
    (re.compile(
        r"This reviews hub lists the day-add shortlist after accessory exclusions\.",
        re.I,
    ), "This reviews hub lists the current shortlist after we dropped accessories."),
    (re.compile(
        r"(\d+) ASINs remain after accessory exclusions\.",
        re.I,
    ), r"\1 products remain after we dropped accessories."),
    (re.compile(
        r"Check price uses verified (?:PartnerBoost|our retail partner) fromsll tracks only\.",
        re.I,
    ), "Check price opens a verified retailer listing only."),
    (re.compile(
        r"We only render Check price when L2 is ok and a pboost\.me\?uid=fromsll track is verified\.",
        re.I,
    ), "We only show Check price when we have a verified retailer listing and a working checkout link."),
    (re.compile(r"when L2 returned one", re.I), "when the listing included a star rating"),
    (re.compile(r"Prices are a Checked-day snapshot", re.I), "Prices are from the day we checked"),
    (re.compile(r"A deep review lands after deploy\.", re.I), "A deeper review will follow."),
]

FAQ_VISITOR_OK = re.compile(
    r"publishable|inventory[_-]blocked|completeness gate|completeness-gated|"
    r"card checklist|PartnerBoost|YeahPromos|PartnerWhiz|\bSeaker\b|"
    r"\bG-HD\b|\bG-IL\b|\bMac CDP\b|\bMac L2\b",
    re.I,
)

VISITOR_LEAK_RE = re.compile(
    r"(?i:completeness gate|card checklist|inventory-blocked|inventory_blocked|"
    r"(?<![A-Za-z0-9.-])PartnerBoost(?![A-Za-z0-9.-])|"
    r"(?<![A-Za-z0-9.-])YeahPromos(?![A-Za-z0-9.-])|"
    r"Mac CDP|Mac L2|\bwhilst\b|\btowards\b|"
    r"PB∪YP|healthy track|L5 inventory|Content-only\.|"
    r"fromsll track|day-add inventory|ASINs remain|when L2 returned|L2 plus|"
    r"lands after deploy)"
    r"|\bUtilize\b"
    r"|(?i:snapshot \$)"
    r"|Snapshot [Pp]rice"
    r"|Snapshot pricing|Snapshot value"
    r"|price snapshot of \$|snapshot price of \$"
    r"|\$[0-9][0-9,]*(?:\.[0-9]{2})? price snapshot"
    r"|Price snapshot:"
    r"|\(ASIN:|under ASIN|\bASIN B0"
    r"|invent an ASIN|invented ASIN|those ASINs"
    r"|no ASIN|\ban ASIN\b"
)


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


MERCHANT_NAME_LIMIT = 150  # Google Merchant listings `name` max
_STOCK_TOKENS = frozenset(
    {
        "InStock",
        "OutOfStock",
        "PreOrder",
        "LimitedAvailability",
        "OnlineOnly",
        "SoldOut",
    }
)


def truncate_name(name: str, limit: int = 70) -> str:
    name = re.sub(r"\s+", " ", (name or "").strip())
    if len(name) <= limit:
        return name
    cut = name[: limit - 1].rsplit(" ", 1)[0]
    return (cut or name[: limit - 1]).rstrip(" ,;:/") + "…"


def _plain_text(html_fragment: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", " ", html_fragment or ""))
    return re.sub(r"\s+", " ", text).strip()


def normalize_star_rating(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip()
    if not re.fullmatch(r"[1-5](?:\.[0-9])?", text):
        return None
    amount = float(text)
    if amount < 1 or amount > 5:
        return None
    return text


def normalize_review_count(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    text = str(value).replace(",", "").strip()
    if not text.isdigit():
        return None
    count = int(text)
    return count if count > 0 else None


def normalize_availability(value: Any) -> str | None:
    if not value or isinstance(value, bool):
        return None
    token = str(value).strip().replace("https://schema.org/", "")
    if token not in _STOCK_TOKENS:
        return None
    return f"https://schema.org/{token}"


def honest_aggregate_rating_node(
    rating_value: Any, rating_count: Any
) -> dict[str, Any] | None:
    stars = normalize_star_rating(rating_value)
    count = normalize_review_count(rating_count)
    if not stars or not count:
        return None
    return {
        "@type": "AggregateRating",
        "ratingValue": stars,
        "bestRating": "5",
        "worstRating": "1",
        "ratingCount": count,
    }


def brand_from_name(name: str) -> str | None:
    token = re.split(r"[\s,|/]+", (name or "").strip())
    if not token:
        return None
    brand = token[0].strip("™®")
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9.&'-]{1,32}", brand):
        return brand
    return None


def slug_from_href(href: str) -> str | None:
    if not href:
        return None
    path = href.split("?")[0].split("#")[0].rstrip("/")
    if "/reviews/" in path:
        return path.rsplit("/", 1)[-1] or None
    parts = [p for p in path.split("/") if p and p != "." and p != ".."]
    if parts and parts[-1] not in {"comparison", "reviews", "index.html"}:
        return parts[-1]
    return None


def cat_slug_from_path(out_rel: str) -> str | None:
    parts = out_rel.strip("/").split("/")
    if parts and parts[0] not in {
        "about-us", "authors", "blog", "index.html", "robot-vacuums-match",
        "llms.txt", "sitemap.xml", "robots.txt",
    }:
        return parts[0]
    return None


def page_kind(out_rel: str) -> str:
    p = out_rel.strip("/")
    if p in {"index.html", ""}:
        return "home"
    if p.startswith("authors/") and p.endswith("index.html"):
        rest = p[len("authors/"):]
        return "authors_hub" if rest == "index.html" else "author"
    if p == "robot-vacuums-match/index.html":
        return "match"
    if "/comparison/" in p:
        return "comparison"
    if p.endswith("/reviews/index.html"):
        return "reviews"
    if "/reviews/" in p and p.endswith("/index.html"):
        return "review"
    if "/search/" in p:
        return "search"
    if p.count("/") == 1 and p.endswith("/index.html"):
        return "landing"
    return "page"


LD_JSON_RE = re.compile(
    r"<script\b[^>]*\btype=[\"']application/ld\+json[\"'][^>]*>.*?</script>",
    re.I | re.S,
)


def html_without_ld_json(html_text: str) -> str:
    """Visitor-visible HTML only — JSON-LD Offer / Review blocks stay out of leak scans."""
    return LD_JSON_RE.sub("", html_text)


def rewrite_outside_ld_json(html_text: str, rewriter) -> str:
    """Rewrite chrome/body only. Leave application/ld+json scripts byte-for-byte."""
    parts: list[str] = []
    last = 0
    for match in LD_JSON_RE.finditer(html_text):
        parts.append(rewriter(html_text[last:match.start()]))
        parts.append(match.group(0))
        last = match.end()
    parts.append(rewriter(html_text[last:]))
    return "".join(parts)


def apply_jargon_patterns(text: str, *, collapse_ws: bool = False) -> str:
    out = text
    for pat, repl in JARGON_PATTERNS:
        out = pat.sub(repl, out)
    if collapse_ws:
        out = re.sub(r"[ \t]{2,}", " ", out)
        out = re.sub(r" \.", ".", out)
        return out.strip()
    return out


def scrub_jargon(text: str) -> str:
    return apply_jargon_patterns(text, collapse_ws=True)


def set_robots_meta(html_text: str, content: str) -> str:
    if re.search(r'<meta name="robots"', html_text, re.I):
        return re.sub(
            r'<meta name="robots" content="[^"]*"\s*/?>',
            f'<meta name="robots" content="{content}"/>',
            html_text,
            count=1,
            flags=re.I,
        )
    return html_text.replace("</head>", f'<meta name="robots" content="{content}"/>\n</head>', 1)


def set_canonical(html_text: str, url: str) -> str:
    if re.search(r'rel="canonical"', html_text, re.I):
        return re.sub(
            r'<link rel="canonical" href="[^"]*"\s*/?>',
            f'<link rel="canonical" href="{url}"/>',
            html_text,
            count=1,
            flags=re.I,
        )
    return html_text.replace("</head>", f'<link rel="canonical" href="{url}"/>\n</head>', 1)


def dumps_ld(obj: dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def upsert_jsonld(html_text: str, objs: list[dict[str, Any]], replace_types: set[str]) -> str:
    """Drop existing ld+json blobs whose @type is in replace_types, then insert objs before </head>."""

    def keep(script: str) -> bool:
        m = re.search(r"<script type=\"application/ld\+json\">(.*?)</script>", script, re.S)
        if not m:
            return True
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            return True
        t = data.get("@type")
        types = t if isinstance(t, list) else [t]
        return not (set(types) & replace_types)

    html_text = re.sub(
        r'<script type="application/ld\+json">.*?</script>\n?',
        lambda m: m.group(0) if keep(m.group(0)) else "",
        html_text,
        flags=re.S,
    )
    block = "".join(
        f'<script type="application/ld+json">{dumps_ld(obj)}</script>\n' for obj in objs
    )
    if "</head>" in html_text:
        return html_text.replace("</head>", block + "</head>", 1)
    return block + html_text


# --- extraction -------------------------------------------------------------

_CARD_RE = re.compile(
    r'<article class="product-card"[^>]*>.*?</article>',
    re.S,
)
_PICK_RE = re.compile(
    r'<section class="landing-pick" id="(pick-\d+)">(.*?)</section>',
    re.S,
)
_ATTR_RE = re.compile(r'\b(data-asin|data-position|data-product-name|data-img|data-cta)="([^"]*)"')


def extract_comparison_products(html_text: str, cat_slug: str) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    seen: set[str] = set()
    for i, card in enumerate(_CARD_RE.findall(html_text), start=1):
        attrs = {k: unescape(v) for k, v in _ATTR_RE.findall(card)}
        asin = (attrs.get("data-asin") or "").strip()
        name = (attrs.get("data-product-name") or "").strip()
        if not name:
            nm = re.search(r'class="pc-name"[^>]*>([^<]+)', card)
            name = unescape(nm.group(1)).strip() if nm else ""
        if not name:
            continue
        price_m = re.search(r'class="pc-price-value">\$([0-9][0-9,]*(?:\.[0-9]{2})?)<', card)
        price = price_m.group(1).replace(",", "") if price_m else None
        img = attrs.get("data-img") or ""
        if not img:
            im = re.search(r'<img[^>]+src="([^"]+)"', card)
            img = im.group(1) if im else ""
        hrefs = re.findall(r'href="([^"]+)"', card)
        review_slug = None
        for href in hrefs:
            if "/reviews/" in href and not href.rstrip("/").endswith("/reviews"):
                review_slug = slug_from_href(href)
                if review_slug:
                    break
        star_m = re.search(r'aria-label="([1-5](?:\.[0-9])?)\s+out of 5"', card, re.I)
        count_m = re.search(
            r'class="pc-reviews-link"[^>]*>\s*([0-9][0-9,]*)\s+reviews',
            card,
            re.I,
        )
        tag_m = re.search(r"class=['\"]pc-tagline['\"]>(.*?)</p>", card, re.S)
        stock_m = re.search(r'data-(?:stock|availability)="([^"]+)"', card)
        key = asin or f"{review_slug}:{name}:{i}"
        if key in seen:
            continue
        seen.add(key)
        products.append(
            {
                "asin": asin or None,
                "name": name,
                "price": price,
                "image": img or None,
                "review_slug": review_slug,
                "position": int(attrs.get("data-position") or i),
                "brand": brand_from_name(name),
                "rating_value": normalize_star_rating(star_m.group(1)) if star_m else None,
                "rating_count": normalize_review_count(
                    count_m.group(1) if count_m else None
                ),
                "description": _plain_text(tag_m.group(1)) if tag_m else None,
                "availability": normalize_availability(
                    stock_m.group(1) if stock_m else None
                ),
            }
        )
    products.sort(key=lambda p: p["position"])
    for i, p in enumerate(products, start=1):
        p["position"] = i
    return products


def extract_landing_picks(html_text: str) -> list[dict[str, Any]]:
    picks: list[dict[str, Any]] = []
    for pick_id, body in _PICK_RE.findall(html_text):
        hm = re.search(r"<h2>(?:<span class=\"landing-pick-num\">\d+</span>\s*)?(.*?)</h2>", body, re.S)
        name = unescape(re.sub(r"<[^>]+>", "", hm.group(1))).strip() if hm else ""
        review_slug = None
        for href in re.findall(r'href="([^"]+)"', body):
            if "reviews/" in href:
                review_slug = slug_from_href(href)
                if review_slug:
                    break
        im = re.search(r'<img[^>]+src="([^"]+)"', body)
        img = im.group(1) if im else None
        picks.append(
            {
                "pick_id": pick_id,
                "name": name,
                "review_slug": review_slug,
                "image": img,
            }
        )
    return picks


_NAV_FAQ_TITLES = {"compare", "reviews", "categories", "compare picks"}


def extract_visible_faqs(html_text: str) -> list[tuple[str, str]]:
    faqs: list[tuple[str, str]] = []
    # Visitor FAQ widgets only — never header/mobile <details> megas.
    blocks = re.findall(
        r"<details[^>]*>\s*<summary>(.*?)</summary>\s*(.*?)</details>",
        html_text,
        re.S,
    )
    for q_html, a_html in blocks:
        if "mega-cat" in a_html or "mega-overview" in a_html:
            continue
        q = unescape(re.sub(r"<[^>]+>", " ", q_html))
        q = re.sub(r"\s+", " ", q).strip()
        a = unescape(re.sub(r"<[^>]+>", " ", a_html))
        a = re.sub(r"\s+", " ", a).strip()
        if q.lower() in _NAV_FAQ_TITLES:
            continue
        if not q or not a or len(q) > 200 or len(a) < 24:
            continue
        faqs.append((scrub_jargon(q), scrub_jargon(a)))
    # Dedupe by question, keep first 8.
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for q, a in faqs:
        k = q.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append((q, a))
        if len(out) >= 8:
            break
    return out


def extract_authors_from_home(html_text: str) -> list[dict[str, str]]:
    authors: list[dict[str, str]] = []
    for card in re.findall(r"<article class=\"expert-card\">(.*?)</article>", html_text, re.S):
        href_m = re.search(r'href="(?:\.\./)*authors/([^"/]+)/"', card)
        if not href_m:
            continue
        slug = href_m.group(1)
        name_m = re.search(r"<strong>(.*?)</strong>", card)
        role_m = re.search(r'class="expert-role">(.*?)</span>', card)
        img_m = re.search(r'<img[^>]+src="([^"]+)"', card)
        alt_m = re.search(r'<img[^>]+alt="([^"]*)"', card)
        name = unescape(re.sub(r"<[^>]+>", "", name_m.group(1))).strip() if name_m else slug
        if alt_m and alt_m.group(1).strip():
            name = unescape(alt_m.group(1)).strip()
        role = unescape(role_m.group(1)).strip() if role_m else "Editor"
        img = img_m.group(1) if img_m else ""
        authors.append({"slug": slug, "name": name, "role": role, "img": img})
    # Editorial team page is in the sitemap / footer but not the expert grid.
    if not any(a["slug"] == "moretop10-editors" for a in authors):
        authors.append(
            {
                "slug": "moretop10-editors",
                "name": "MoreTop10 Editors",
                "role": "Editorial team",
                "img": "",
            }
        )
    return authors


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", unescape(name).lower())[:48]


def merge_hub_products(
    picks: list[dict[str, Any]],
    cmp_products: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    unused = list(cmp_products)
    merged: list[dict[str, Any]] = []
    for i, pick in enumerate(picks, start=1):
        found = None
        if pick.get("review_slug"):
            for j, c in enumerate(unused):
                if c.get("review_slug") == pick["review_slug"]:
                    found = unused.pop(j)
                    break
        if found is None and pick.get("name"):
            target = _norm(pick["name"])
            for j, c in enumerate(unused):
                if _norm(c.get("name") or "") == target:
                    found = unused.pop(j)
                    break
        row = {
            "position": i,
            "pick_id": pick.get("pick_id") or f"pick-{i}",
            "name": pick.get("name") or (found or {}).get("name") or "",
            "image": pick.get("image") or (found or {}).get("image"),
            "review_slug": pick.get("review_slug") or (found or {}).get("review_slug"),
            "asin": (found or {}).get("asin"),
            "price": (found or {}).get("price"),
            "brand": (found or {}).get("brand") or brand_from_name(pick.get("name") or ""),
            "rating_value": (found or {}).get("rating_value"),
            "rating_count": (found or {}).get("rating_count"),
            "description": (found or {}).get("description"),
            "availability": (found or {}).get("availability"),
        }
        if not row["name"]:
            continue
        merged.append(row)
    if not merged and cmp_products:
        # Hub HTML without landing-pick sections: still list comparison products.
        for i, c in enumerate(cmp_products, start=1):
            merged.append({**c, "position": i, "pick_id": f"pick-{i}"})
    return merged


_PRICE_AMOUNT_RE = re.compile(r"^[0-9]+(?:\.[0-9]{1,2})?$")
_REVIEW_SNAPSHOT_PRICE_RE = re.compile(
    r"<strong>Price snapshot</strong>\s*<span>\$([0-9][0-9,]*(?:\.[0-9]{2})?)",
    re.I,
)


def normalize_offer_price(value: Any) -> str | None:
    """Return a Google-safe Offer.price string, or None if this is not a real amount."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value) if value > 0 else None
    if isinstance(value, float):
        if value != value or value <= 0:  # NaN or non-positive
            return None
        return f"{value:.2f}"
    text = unescape(str(value)).strip().replace(",", "").replace("$", "").strip()
    if not text or not _PRICE_AMOUNT_RE.fullmatch(text):
        return None
    try:
        amount = float(text)
    except ValueError:
        return None
    if amount <= 0:
        return None
    return text


def review_snapshot_price(html_text: str) -> str | None:
    """Visible review-fact Price snapshot (the amount the page already shows)."""
    match = _REVIEW_SNAPSHOT_PRICE_RE.search(html_text)
    return normalize_offer_price(match.group(1)) if match else None


def catalog_price_for_review(
    products: list[dict[str, Any]], review_slug: str | None
) -> str | None:
    if not review_slug:
        return None
    for prod in products:
        if prod.get("review_slug") == review_slug:
            return normalize_offer_price(prod.get("price"))
    return None


def honest_review_price(
    html_text: str,
    products: list[dict[str, Any]],
    review_slug: str | None,
) -> str | None:
    return review_snapshot_price(html_text) or catalog_price_for_review(
        products, review_slug
    )


def offer_has_gsc_price(offer: dict[str, Any]) -> bool:
    if normalize_offer_price(offer.get("price")):
        return True
    spec = offer.get("priceSpecification")
    specs = spec if isinstance(spec, list) else [spec] if isinstance(spec, dict) else []
    return any(normalize_offer_price(item.get("price")) for item in specs)


def _iter_product_nodes(data: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            types = node.get("@type")
            type_list = types if isinstance(types, list) else [types]
            if "Product" in type_list:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return found


def apply_honest_availability(offer: dict[str, Any], availability: str | None) -> None:
    if availability:
        offer["availability"] = availability
    else:
        offer.pop("availability", None)
    offer.pop("hasMerchantReturnPolicy", None)
    offer.pop("shippingDetails", None)


def apply_honest_product_offer(
    product: dict[str, Any],
    price: str | None,
    availability: str | None = None,
) -> None:
    """Attach Offer.price from SoT, or drop a price-less Offer. Never invent amounts."""
    if price:
        offer = product.get("offers")
        if isinstance(offer, list) and offer and isinstance(offer[0], dict):
            first = dict(offer[0])
            first.setdefault("@type", "Offer")
            first["price"] = price
            first.setdefault("priceCurrency", "USD")
            apply_honest_availability(first, availability)
            product["offers"] = [first, *offer[1:]] if len(offer) > 1 else first
            return
        if isinstance(offer, dict):
            offer = dict(offer)
            offer.setdefault("@type", "Offer")
            offer["price"] = price
            offer.setdefault("priceCurrency", "USD")
            apply_honest_availability(offer, availability)
            product["offers"] = offer
            return
        offer = {
            "@type": "Offer",
            "price": price,
            "priceCurrency": "USD",
        }
        apply_honest_availability(offer, availability)
        product["offers"] = offer
        return

    offer = product.get("offers")
    if isinstance(offer, dict) and not offer_has_gsc_price(offer):
        product.pop("offers", None)
        return
    if isinstance(offer, dict):
        offer = dict(offer)
        apply_honest_availability(offer, availability)
        product["offers"] = offer
        return
    if isinstance(offer, list):
        kept = [item for item in offer if isinstance(item, dict) and offer_has_gsc_price(item)]
        if not kept:
            product.pop("offers", None)
            return
        for item in kept:
            apply_honest_availability(item, availability)
        product["offers"] = kept[0] if len(kept) == 1 else kept


def apply_honest_review_product(
    product: dict[str, Any],
    *,
    price: str | None,
    availability: str | None = None,
    description: str | None = None,
    rating: dict[str, Any] | None = None,
    review: dict[str, Any] | None = None,
) -> None:
    apply_honest_product_offer(product, price, availability)
    name = product.get("name")
    if isinstance(name, str) and name.strip():
        product["name"] = truncate_name(name, MERCHANT_NAME_LIMIT)
    if description:
        product["description"] = description
    if rating:
        product["aggregateRating"] = rating
    else:
        product.pop("aggregateRating", None)
    if review:
        product["review"] = review
    else:
        product.pop("review", None)


_STARS_ARIA_RE = re.compile(r'aria-label="([1-5](?:\.[0-9])?)\s+out of 5"', re.I)
_RETAILER_COUNT_RE = re.compile(
    r"<strong>Retailer reviews</strong>\s*<span>([0-9][0-9,]*)\s+reviews</span>",
    re.I,
)
_REVIEW_SUMMARY_RE = re.compile(r'<p class="review-summary">(.*?)</p>', re.S)


def review_retailer_aggregate(html_text: str) -> dict[str, Any] | None:
    star_m = _STARS_ARIA_RE.search(html_text)
    count_m = _RETAILER_COUNT_RE.search(html_text)
    return honest_aggregate_rating_node(
        star_m.group(1) if star_m else None,
        count_m.group(1) if count_m else None,
    )


def catalog_rating_for_review(
    products: list[dict[str, Any]], review_slug: str | None
) -> dict[str, Any] | None:
    if not review_slug:
        return None
    for prod in products:
        if prod.get("review_slug") == review_slug:
            return honest_aggregate_rating_node(
                prod.get("rating_value"), prod.get("rating_count")
            )
    return None


def catalog_availability_for_review(
    products: list[dict[str, Any]], review_slug: str | None
) -> str | None:
    if not review_slug:
        return None
    for prod in products:
        if prod.get("review_slug") == review_slug:
            return normalize_availability(prod.get("availability"))
    return None


def review_product_description(html_text: str) -> str | None:
    match = _REVIEW_SUMMARY_RE.search(html_text)
    if not match:
        return None
    text = _plain_text(match.group(1))
    return text[:5000] if text else None


def editorial_review_from_page(html_text: str) -> dict[str, Any] | None:
    """Editorial Review from the page's own review-summary. No invented stars."""
    body = review_product_description(html_text)
    if not body:
        return None
    node: dict[str, Any] = {
        "@type": "Review",
        "author": {"@type": "Organization", "name": "MoreTop10", "url": f"{LIVE}/"},
        "reviewBody": body,
    }
    checked = last_checked(html_text)
    if checked:
        node["datePublished"] = checked
    headline = h1_text(html_text)
    if headline:
        node["name"] = headline
    return node


def patch_review_article_jsonld(
    html_text: str,
    *,
    price: str | None,
    availability: str | None = None,
    description: str | None = None,
    rating: dict[str, Any] | None = None,
    review: dict[str, Any] | None = None,
) -> str:
    """Rewrite review Article/Product JSON-LD; leave FAQ/Org blobs alone."""

    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        types = data.get("@type")
        type_list = types if isinstance(types, list) else [types]
        if not ({"Article", "Product"} & {t for t in type_list if t}):
            return match.group(0)
        products = _iter_product_nodes(data)
        if not products:
            return match.group(0)
        for product in products:
            apply_honest_review_product(
                product,
                price=price,
                availability=availability,
                description=description,
                rating=rating,
                review=review,
            )
        return f'<script type="application/ld+json">{dumps_ld(data)}</script>'

    return re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        repl,
        html_text,
        flags=re.S,
    )


def patch_review_article_offers(html_text: str, price: str | None) -> str:
    return patch_review_article_jsonld(html_text, price=price)


def product_node(prod: dict[str, Any], cat_slug: str, page_url: str) -> dict[str, Any]:
    name = truncate_name(prod["name"])
    node: dict[str, Any] = {"@type": "Product", "name": name}
    asin = prod.get("asin")
    if asin:
        node["sku"] = asin
        node["url"] = f"{LIVE}/{cat_slug}/#geo-{asin}"
    elif prod.get("review_slug"):
        node["url"] = f"{LIVE}/{cat_slug}/reviews/{prod['review_slug']}/"
    else:
        node["url"] = page_url
    if prod.get("image"):
        node["image"] = prod["image"]
    if prod.get("brand"):
        node["brand"] = {"@type": "Brand", "name": prod["brand"]}
    description = (prod.get("description") or "").strip()
    if description:
        node["description"] = description[:5000]
    rating = honest_aggregate_rating_node(
        prod.get("rating_value"), prod.get("rating_count")
    )
    if rating:
        node["aggregateRating"] = rating
    price = normalize_offer_price(prod.get("price"))
    if price:
        offer: dict[str, Any] = {
            "@type": "Offer",
            "price": price,
            "priceCurrency": "USD",
            "url": node["url"],
        }
        apply_honest_availability(offer, normalize_availability(prod.get("availability")))
        node["offers"] = offer
    return node


def item_list_element(products: list[dict[str, Any]], cat_slug: str, page_url: str) -> list[dict[str, Any]]:
    els = []
    for prod in products:
        els.append(
            {
                "@type": "ListItem",
                "position": prod["position"],
                "item": product_node(prod, cat_slug, page_url),
            }
        )
    return els


def org_node() -> dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "MoreTop10",
        "url": f"{LIVE}/",
        "logo": ORG_LOGO,
        "description": "Ranked comparisons and practical reviews for everyday home products.",
        "publishingPrinciples": f"{LIVE}/about-us/",
    }


def faq_node(faqs: list[tuple[str, str]]) -> dict[str, Any] | None:
    if not faqs:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
            if not FAQ_VISITOR_OK.search(q + " " + a)
        ],
    }


def speakable_node(selectors: list[str]) -> dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "SpeakableSpecification",
        "cssSelector": selectors,
    }


def breadcrumb_node(items: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": url}
            for i, (name, url) in enumerate(items, start=1)
        ],
    }


# --- HTML transforms --------------------------------------------------------

def inject_geo_anchors(html_text: str, products: list[dict[str, Any]]) -> str:
    for prod in products:
        asin = prod.get("asin")
        if not asin:
            continue
        pick_id = prod.get("pick_id")
        if pick_id:
            # Keep #pick-N for jump TOC; add a dedicated #geo-ASIN child.
            html_text = re.sub(
                rf'(<section class="landing-pick" id="{re.escape(pick_id)}">)(?!\s*<span class="geo-anchor")',
                rf'\1<span class="geo-anchor" id="geo-{_esc(asin)}" tabindex="-1"></span>',
                html_text,
                count=1,
            )
        # Comparison cards (opening tag is often split across two lines).
        html_text = re.sub(
            rf'(<article class="product-card"[^>]*data-asin="{re.escape(asin)}"[^>]*)(>)',
            lambda m, a=asin: (
                m.group(0)
                if f'id="geo-{a}"' in m.group(1)
                else m.group(1) + f' id="geo-{a}"' + m.group(2)
            ),
            html_text,
            count=1,
            flags=re.S,
        )
    return html_text


def inject_rev_hub_geo(html_text: str, products: list[dict[str, Any]]) -> str:
    """Stamp #geo-{ASIN} on reviews-hub cards when the Live card maps to a known ASIN."""
    by_slug = {p.get("review_slug"): p for p in products if p.get("review_slug") and p.get("asin")}
    by_asin = {p["asin"]: p for p in products if p.get("asin")}

    def stamp(card: str) -> str:
        if re.search(r'\sid="geo-[^"]+"', card):
            return card
        asin = None
        hrefs = re.findall(r'href="([^"]+)"', card)
        for href in hrefs:
            slug = slug_from_href(href)
            if slug and slug in by_slug:
                asin = by_slug[slug]["asin"]
                break
        if not asin:
            for img in re.findall(r'src="([^"]+)"', card):
                m = ASIN_RE.search(img)
                if m and m.group(1) in by_asin:
                    asin = m.group(1)
                    break
        if not asin:
            return card
        return re.sub(
            r'(<article class="rev-hub-card")',
            rf'\1 id="geo-{_esc(asin)}"',
            card,
            count=1,
        )

    return re.sub(
        r'<article class="rev-hub-card">.*?</article>',
        lambda m: stamp(m.group(0)),
        html_text,
        flags=re.S,
    )


def inject_review_geo(html_text: str, asin: str | None) -> str:
    if not asin or f'id="geo-{asin}"' in html_text:
        return html_text
    span = f'<span class="geo-anchor" id="geo-{_esc(asin)}" tabindex="-1"></span>'
    if '<main class="product-review-page">' in html_text:
        return html_text.replace(
            '<main class="product-review-page">',
            f'<main class="product-review-page">{span}',
            1,
        )
    if "<main" in html_text:
        return re.sub(r"(<main[^>]*>)", rf"\1{span}", html_text, count=1)
    return html_text


def asin_for_review(
    html_text: str,
    review_slug: str | None,
    products: list[dict[str, Any]],
) -> str | None:
    if review_slug:
        for p in products:
            if p.get("review_slug") == review_slug and p.get("asin"):
                return p["asin"]
    # First product packshot on the review (not sidebar alternatives).
    hero = re.search(
        r'class="review-hero-img"[^>]*src="([^"]+)"|src="([^"]+)"[^>]*class="review-hero-img"',
        html_text,
    )
    if hero:
        m = ASIN_RE.search(hero.group(1) or hero.group(2) or "")
        if m:
            return m.group(1)
    m = ASIN_RE.search(html_text)
    return m.group(1) if m else None


def has_html_class(html_text: str, class_name: str) -> bool:
    """True when class_name is on an HTML class= attribute (JSON-LD cssSelector does not count)."""
    return bool(re.search(rf'\bclass="[^"]*\b{re.escape(class_name)}\b', html_text))


def mark_answer_first(html_text: str, kind: str) -> str:
    if kind == "landing":
        if has_html_class(html_text, "geo-answer-first"):
            return html_text
        html_text = re.sub(
            r'(<article class="landing-article">\s*)<p>',
            r'\1<p class="geo-answer-first">',
            html_text,
            count=1,
        )
    elif kind == "comparison":
        if has_html_class(html_text, "cmp-answer-first") and not has_html_class(
            html_text, "geo-answer-first"
        ):
            html_text = html_text.replace(
                'class="cmp-answer-first',
                'class="cmp-answer-first geo-answer-first',
                1,
            )
    return html_text


def inject_cite_strip(html_text: str, title: str, canonical: str, checked: str) -> str:
    """Visible How to Cite strip. Relocate if a prior bake parked it inside the first card."""
    html_text = re.sub(
        r'\s*<aside class="geo-cite-strip"[^>]*>.*?</aside>',
        "",
        html_text,
        flags=re.S,
    )
    cite = (
        f'<aside class="geo-cite-strip" id="how-to-cite">'
        f"<strong>How to cite:</strong> MoreTop10 Editorial Team, "
        f"“{_esc(title)},” "
        f'<a href="{_esc(canonical)}">{_esc(canonical)}</a> '
        f"(last checked {_esc(checked)}).</aside>"
    )
    if 'class="landing-article"' in html_text:
        return re.sub(
            r'(<article class="landing-article">)(.*?)(</article>)',
            lambda m: m.group(1) + m.group(2) + cite + "\n      " + m.group(3),
            html_text,
            count=1,
            flags=re.S,
        )
    if "</main>" in html_text:
        return html_text.replace("</main>", cite + "\n</main>", 1)
    if "<footer" in html_text:
        return html_text.replace("<footer", cite + "\n<footer", 1)
    return html_text + cite


def last_checked(html_text: str) -> str:
    m = re.search(r"Last Updated[:\s]*([0-9]{4}-[0-9]{2}-[0-9]{2})", html_text)
    if m:
        return m.group(1)
    m = re.search(r"Checked\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", html_text)
    if m:
        return m.group(1)
    m = re.search(r"Updated\s+([0-9]{4}-[0-9]{2}-[0-9]{2})", html_text)
    if m:
        return m.group(1)
    return "2026-10-20"


def page_title_text(html_text: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html_text, re.S)
    return unescape(m.group(1)).strip() if m else "MoreTop10"


def h1_text(html_text: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.S)
    if not m:
        return page_title_text(html_text)
    return unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip()


def rewrite_visible_jargon(html_text: str) -> str:
    """Scrub jargon in visible copy and meta. JSON-LD scripts are not rewritten.

    Affiliate track URLs (pboost.me?uid=fromsll) and <time datetime> stay intact.
    Patterns are phrase-level and do not rewrite class names or hrefs.
    """
    return rewrite_outside_ld_json(
        html_text, lambda chunk: apply_jargon_patterns(chunk, collapse_ws=False)
    )


def rewrite_footer_editors(html_text: str, prefix: str) -> str:
    return re.sub(
        r'(<li><a href=")(?:(?:\.\./)*)authors/moretop10-editors/(">)Editors</a></li>',
        rf'\1{prefix}authors/\2Editors</a></li>',
        html_text,
    )


def rewrite_author_breadcrumb(html_text: str) -> str:
    html_text = html_text.replace(
        '"name":"Authors","item":"https://moretop10.com/authors/moretop10-editors/"',
        '"name":"Authors","item":"https://moretop10.com/authors/"',
    )
    html_text = re.sub(
        r'(<nav class="breadcrumb">.*?<a href=")[^"]*authors/moretop10-editors/(">[^<]*Authors</a>)',
        rf'\1../"\2',
        html_text,
        count=1,
        flags=re.S,
    )
    return html_text


# Author feed thumbs: per-article cover SoT (never invent art).
# Candidates per target page, then unique allocation across all author posts
# (same logical article may repeat on two profiles; distinct articles may not
# share a thumb URL).
# 1. og:image / twitter:image when it is a product packshot
# 2. In-page review-hero + every product packshot already on that page
# 3. og:image / twitter:image when it is any non-icon image
# 4. Existing page hero (cmp-hero-bg / lifestyle-photo) as last-resort fallback
# Site icon (icon-512) is never a post thumb.
# Individual reviews claim their product og first; hubs/comparison/reviews-hub
# take the next unused candidate from their own page.

_AUTHOR_POST_RE = re.compile(
    r'<article class="author-post-row[^"]*"[^>]*>.*?</article>',
    re.S,
)
_OG_IMAGE_RE = re.compile(
    r'<meta\s[^>]*(?:property|name)="(og:image|twitter:image)"[^>]*content="([^"]+)"',
    re.I,
)
_OG_IMAGE_RE_SWAP = re.compile(
    r'<meta\s[^>]*content="([^"]+)"[^>]*(?:property|name)="(og:image|twitter:image)"',
    re.I,
)
_REVIEW_HERO_RE = re.compile(
    r'class="review-hero-img"[^>]*src="([^"]+)"|src="([^"]+)"[^>]*class="review-hero-img"',
)
_PACKSHOT_SRC_RE = re.compile(
    r'<img\b[^>]*\bsrc="([^"]+)"',
    re.I,
)
_CMP_HERO_BG_RE = re.compile(
    r"--cmp-hero-bg:\s*url\(['\"]?([^'\")]+)['\"]?\)",
)
_LIFESTYLE_PHOTO_RE = re.compile(
    r'<img[^>]*class="[^"]*\blifestyle-photo\b[^"]*"[^>]*src="([^"]+)"|'
    r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*\blifestyle-photo\b[^"]*"',
    re.I,
)
_SITE_ICON_RE = re.compile(
    r"icon-512|favicon|apple-touch-icon",
    re.I,
)
_PRODUCT_COVER_RE = re.compile(
    r"/assets/img/products/|media-amazon\.com/images/",
    re.I,
)


def _prefix_from_out(out_path: str) -> str:
    p = out_path.strip("/").replace("\\", "/")
    if p.endswith("index.html"):
        p = p[: -len("index.html")].rstrip("/")
    if not p:
        return ""
    return "../" * (p.count("/") + 1)


def _join_rel(base: str, rel: str) -> str:
    parts = [bit for bit in base.replace("\\", "/").split("/") if bit and bit != "."]
    for bit in rel.replace("\\", "/").split("/"):
        if bit in ("", "."):
            continue
        if bit == "..":
            if parts:
                parts.pop()
            continue
        parts.append(bit)
    return "/".join(parts)


def canonical_cover_url(src: str, page_rel: str = "") -> str:
    """Normalize a cover src to /assets/... or an absolute external URL."""
    src = (src or "").strip()
    if not src:
        return ""
    src = src.split("?", 1)[0]
    if src.startswith(LIVE + "/"):
        return "/" + src[len(LIVE) + 1 :]
    if src.startswith("http://") or src.startswith("https://"):
        return src
    if src.startswith("/"):
        return src
    if page_rel:
        base = str(Path(page_rel).parent).replace("\\", "/")
        if base in (".", ""):
            base = ""
        return "/" + _join_rel(base, src)
    return "/" + src.lstrip("./")


def is_site_icon_cover(url: str) -> bool:
    return bool(url) and bool(_SITE_ICON_RE.search(url))


def is_product_cover(url: str) -> bool:
    return bool(url) and bool(_PRODUCT_COVER_RE.search(url))


def extract_meta_image(html_text: str) -> str:
    og = ""
    twitter = ""
    for m in _OG_IMAGE_RE.finditer(html_text):
        kind, val = m.group(1).lower(), m.group(2).strip()
        if kind == "og:image" and not og:
            og = val
        elif kind == "twitter:image" and not twitter:
            twitter = val
    if not og and not twitter:
        for m in _OG_IMAGE_RE_SWAP.finditer(html_text):
            val, kind = m.group(1).strip(), m.group(2).lower()
            if kind == "og:image" and not og:
                og = val
            elif kind == "twitter:image" and not twitter:
                twitter = val
    return og or twitter


def extract_review_hero_src(html_text: str) -> str:
    m = _REVIEW_HERO_RE.search(html_text)
    if not m:
        return ""
    return (m.group(1) or m.group(2) or "").strip()


def extract_first_packshot_src(html_text: str) -> str:
    """First product packshot already on the page (not must-read lifestyle thumbs)."""
    main = html_text
    m_main = re.search(r"<main\b[^>]*>(.*?)</main>", html_text, re.S | re.I)
    if m_main:
        main = m_main.group(1)
    for skip in (
        "must-reads-widget",
        "must-read-thumb",
        "author-post-thumb",
        "ed-rev-list",
        "best-widget-list",
    ):
        main = re.sub(rf'<[^>]*class="[^"]*\b{skip}\b[^"]*"[^>]*>.*?</\w+>', "", main, flags=re.S)
    for m in _PACKSHOT_SRC_RE.finditer(main):
        src = m.group(1).strip()
        if is_product_cover(src):
            return src
    return ""


def extract_page_hero_src(html_text: str) -> str:
    m = _CMP_HERO_BG_RE.search(html_text)
    if m:
        return m.group(1).strip()
    m = _LIFESTYLE_PHOTO_RE.search(html_text)
    if m:
        return (m.group(1) or m.group(2) or "").strip()
    return ""


def _packshot_quality(url: str) -> int:
    """Prefer local product JPGs and large Amazon frames over UL thumbs."""
    u = url.lower()
    if "/assets/img/products/" in u:
        return 0
    if "_sl1500" in u or "_ac_sl" in u:
        return 1
    if "_ul" in u:
        return 3
    return 2


def page_cover_candidates(html_text: str, page_rel: str = "") -> list[str]:
    """Ordered unique covers already referenced by this page (no new art)."""
    preferred: list[str] = []
    packs: list[str] = []
    fallback: list[str] = []

    def add(dest: list[str], src: str, *, product_only: bool = False) -> None:
        url = canonical_cover_url(src, page_rel)
        if not url or is_site_icon_cover(url) or url in preferred or url in packs or url in fallback:
            return
        if product_only and not is_product_cover(url):
            return
        dest.append(url)

    og = extract_meta_image(html_text)
    add(preferred, og, product_only=True)
    add(preferred, extract_review_hero_src(html_text), product_only=True)
    for m in _PACKSHOT_SRC_RE.finditer(html_text):
        add(packs, m.group(1), product_only=True)
    packs.sort(key=_packshot_quality)
    add(fallback, og)
    add(fallback, extract_page_hero_src(html_text))
    return preferred + packs + fallback


def resolve_page_cover(html_text: str, page_rel: str = "") -> str:
    """Preferred cover for a page (first candidate). Allocation may pick a later one."""
    cands = page_cover_candidates(html_text, page_rel)
    return cands[0] if cands else ""


def article_alloc_rank(site_rel: str) -> tuple[int, str]:
    """Reviews keep their product og; hubs take leftover packshots."""
    parts = [p for p in site_rel.replace("\\", "/").strip("/").split("/") if p]
    if len(parts) >= 4 and parts[1] == "reviews":
        return (0, site_rel)
    if len(parts) >= 2 and parts[-2] == "comparison":
        return (1, site_rel)
    if len(parts) == 2 and parts[1] == "index.html":
        return (2, site_rel)
    if len(parts) >= 3 and parts[1] == "reviews" and parts[2] == "index.html":
        return (3, site_rel)
    return (4, site_rel)


def allocate_unique_covers(
    site_root: Path, site_rels: list[str]
) -> tuple[dict[str, str], list[str]]:
    """One unique cover URL per distinct article. Missing = no unused candidate."""
    assigned: dict[str, str] = {}
    missing: list[str] = []
    used: set[str] = set()
    for rel in sorted(set(site_rels), key=article_alloc_rank):
        if not rel:
            continue
        path = site_root / rel
        if not path.is_file():
            missing.append(rel)
            continue
        pick = ""
        for cand in page_cover_candidates(path.read_text(encoding="utf-8"), rel):
            if cand not in used:
                pick = cand
                break
        if not pick:
            missing.append(rel)
            continue
        assigned[rel] = pick
        used.add(pick)
    return assigned, missing


def collect_author_article_rels(site_root: Path) -> list[str]:
    rels: list[str] = []
    authors_dir = site_root / "authors"
    if not authors_dir.is_dir():
        return rels
    for path in sorted(authors_dir.glob("*/index.html")):
        html_text = path.read_text(encoding="utf-8")
        if "data-author-posts" not in html_text:
            continue
        for post in iter_author_posts(html_text):
            rel = author_href_to_site_rel(post["href"])
            if rel:
                rels.append(rel)
    return rels


def cover_to_thumb_src(cover: str, prefix: str) -> str:
    if not cover:
        return ""
    if cover.startswith(LIVE + "/"):
        return prefix + cover[len(LIVE) + 1 :]
    if cover.startswith("http://") or cover.startswith("https://"):
        return cover
    return prefix + cover.lstrip("/")


def author_href_to_site_rel(href: str) -> str:
    href = (href or "").strip()
    if href.startswith(LIVE):
        href = href[len(LIVE) :]
    if href.startswith("http://") or href.startswith("https://"):
        return ""
    while href.startswith("../"):
        href = href[3:]
    href = href.lstrip("/")
    if not href:
        return "index.html"
    if href.endswith(".html"):
        return href
    return href.rstrip("/") + "/index.html"


def iter_author_posts(html_text: str) -> list[dict[str, str]]:
    posts: list[dict[str, str]] = []
    for m in _AUTHOR_POST_RE.finditer(html_text):
        block = m.group(0)
        href_m = re.search(r'<h3 class="feed-title"><a href="([^"]+)"', block)
        if not href_m:
            href_m = re.search(r'<a class="author-post-thumb-link" href="([^"]+)"', block)
        img_m = re.search(
            r'<img\b[^>]*\bclass="[^"]*\bauthor-post-thumb\b[^"]*"[^>]*\bsrc="([^"]+)"|'
            r'<img\b[^>]*\bsrc="([^"]+)"[^>]*\bclass="[^"]*\bauthor-post-thumb\b[^"]*"',
            block,
        )
        href = href_m.group(1) if href_m else ""
        thumb = ""
        if img_m:
            thumb = (img_m.group(1) or img_m.group(2) or "").strip()
        posts.append({"href": href, "thumb": thumb, "html": block})
    return posts


def _replace_author_thumb_src(block: str, new_src: str) -> str:
    def repl_img(m: re.Match[str]) -> str:
        tag = m.group(0)
        if "author-post-thumb" not in tag:
            return tag
        tag = re.sub(r'\bsrc="[^"]+"', f'src="{new_src}"', tag, count=1)
        tag = re.sub(r'\s*srcset="[^"]+"', "", tag)
        return tag

    return re.sub(r"<img\b[^>]*>", repl_img, block)


def rewrite_author_feed_thumbs(
    html_text: str,
    *,
    site_root: Path,
    prefix: str,
    covers: dict[str, str] | None = None,
) -> str:
    """Point each author-post thumb at that post's allocated unique cover."""
    if covers is None:
        rels = [
            author_href_to_site_rel(p["href"])
            for p in iter_author_posts(html_text)
            if p.get("href")
        ]
        covers, _missing = allocate_unique_covers(site_root, rels)

    def repl(m: re.Match[str]) -> str:
        block = m.group(0)
        href_m = re.search(r'<h3 class="feed-title"><a href="([^"]+)"', block)
        if not href_m:
            href_m = re.search(r'<a class="author-post-thumb-link" href="([^"]+)"', block)
        if not href_m:
            return block
        site_rel = author_href_to_site_rel(href_m.group(1))
        if not site_rel:
            return block
        cover = covers.get(site_rel, "")
        if not cover:
            target = site_root / site_rel
            if target.is_file():
                cover = resolve_page_cover(target.read_text(encoding="utf-8"), site_rel)
        thumb = cover_to_thumb_src(cover, prefix)
        if not thumb:
            return block
        return _replace_author_thumb_src(block, thumb)

    return _AUTHOR_POST_RE.sub(repl, html_text)


def rebake_author_feed_thumbs(site_root: Path) -> int:
    """Rewrite thumbs on every author profile page. Returns pages written."""
    authors_dir = site_root / "authors"
    if not authors_dir.is_dir():
        return 0
    covers, _missing = allocate_unique_covers(
        site_root, collect_author_article_rels(site_root)
    )
    wrote = 0
    for path in sorted(authors_dir.glob("*/index.html")):
        html_text = path.read_text(encoding="utf-8")
        if "data-author-posts" not in html_text:
            continue
        rel = str(path.relative_to(site_root)).replace("\\", "/")
        new = rewrite_author_feed_thumbs(
            html_text,
            site_root=site_root,
            prefix=_prefix_from_out(rel),
            covers=covers,
        )
        if new != html_text:
            path.write_text(new, encoding="utf-8")
            wrote += 1
    return wrote


def author_feed_cover_errors(site_root: Path) -> list[str]:
    """Assert distinct author-feed articles never share a thumb URL."""
    errors: list[str] = []
    authors_dir = site_root / "authors"
    if not authors_dir.is_dir():
        return ["missing authors/"]
    covers, missing = allocate_unique_covers(
        site_root, collect_author_article_rels(site_root)
    )
    for rel in missing:
        errors.append(f"no unique unused cover for {rel}")
    by_thumb: dict[str, set[str]] = {}
    for path in sorted(authors_dir.glob("*/index.html")):
        html_text = path.read_text(encoding="utf-8")
        if "data-author-posts" not in html_text:
            continue
        page_rel = str(path.relative_to(site_root)).replace("\\", "/")
        slug = path.parent.name
        for post in iter_author_posts(html_text):
            href = post["href"]
            if not href:
                errors.append(f"{slug}: author post missing href")
                continue
            site_rel = author_href_to_site_rel(href)
            if not site_rel:
                errors.append(f"{slug}: bad href {href}")
                continue
            if site_rel not in covers:
                continue
            want = covers[site_rel]
            got = canonical_cover_url(post["thumb"], page_rel)
            if got != want:
                errors.append(
                    f"{slug}: thumb {got or '(empty)'} != allocated {want} for {href}"
                )
            if "cmp-hero-" in got:
                errors.append(f"{slug}: {href} still uses category cmp-hero {got}")
            by_thumb.setdefault(got, set()).add(site_rel)
    for thumb, arts in sorted(by_thumb.items()):
        if len(arts) > 1:
            errors.append(
                f"distinct articles share thumb {thumb}: {', '.join(sorted(arts))}"
            )
    return errors


def rewrite_home_robot_tile(html_text: str) -> str:
    """G-IL: robot-vacuums hub must be reachable from the home tile, not only the match quiz."""
    html_text = html_text.replace(
        'href="robot-vacuums-match/" class="home-tile-link">Find Your Match',
        'href="robot-vacuums/" class="home-tile-link">Browse category',
    )
    return html_text


def cluster_match_link(html_text: str, cat_slug: str) -> str:
    if cat_slug != "robot-vacuums":
        return html_text
    if "Floor matching quiz" in html_text:
        return html_text

    def add_link(m: re.Match[str]) -> str:
        inner = m.group(2)
        if "robot-vacuums-match" in inner:
            return m.group(0)
        return (
            m.group(1)
            + inner
            + ' · <a href="../robot-vacuums-match/">Floor matching quiz (demo)</a>'
            + m.group(3)
        )

    if 'class="landing-related-cluster"' in html_text:
        return re.sub(
            r'(<p class="landing-related-cluster"[^>]*>)(.*?)(</p>)',
            add_link,
            html_text,
            count=1,
            flags=re.S,
        )
    note = (
        '<p class="landing-related-cluster match-cluster">'
        "<strong>Also:</strong> "
        '<a href="../robot-vacuums-match/">Floor matching quiz</a> '
        "(demo — hands off to this shortlist; not a separate category)."
        "</p>"
    )
    return html_text.replace("</article>", note + "\n        </article>", 1)


def apply_match_page(html_text: str) -> str:
    """Demo quiz: keep in the robot-vacuums cluster, noindex, canonical to hub, drop from sitemap."""
    html_text = set_robots_meta(html_text, ROBOTS_NOINDEX)
    html_text = set_canonical(html_text, f"{LIVE}/robot-vacuums/")
    html_text = rewrite_visible_jargon(html_text)
    if 'id="match-cluster-links"' not in html_text:
        block = (
            '<p id="match-cluster-links" class="landing-related-cluster">'
            "<strong>Robot vacuums shortlist:</strong> "
            f'<a href="{LIVE}/robot-vacuums/">Category overview</a> · '
            f'<a href="{LIVE}/robot-vacuums/comparison/">Comparison chart</a> · '
            f'<a href="{LIVE}/robot-vacuums/reviews/">Reviews</a>'
            "</p>"
        )
        if "<main" in html_text:
            html_text = re.sub(r"(<main[^>]*>)", r"\1\n" + block, html_text, count=1)
        else:
            html_text += block
    return html_text


def apply_landing_schema(
    html_text: str,
    cat: dict[str, Any],
    products: list[dict[str, Any]],
) -> str:
    slug = cat["slug"]
    name = cat["name"]
    canonical = f"{LIVE}/{slug}/"
    checked = last_checked(html_text)
    title = h1_text(html_text) or f"{name} — Top Picks & Buying Guide | MoreTop10"
    faqs = extract_visible_faqs(html_text)
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', html_text)
    desc = unescape(desc_m.group(1)) if desc_m else f"Top picks and buying guide for {name}."

    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": f"{canonical}#page",
        "name": title,
        "url": canonical,
        "description": desc,
        "isPartOf": {"@type": "WebSite", "name": "MoreTop10", "url": f"{LIVE}/"},
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": [".geo-answer-first", ".landing-faq"],
        },
        "mainEntity": {
            "@type": "ItemList",
            "name": f"{name} top picks",
            "url": canonical,
            "numberOfItems": len(products),
            "itemListElement": item_list_element(products, slug, canonical),
        },
    }
    objs: list[dict[str, Any]] = [
        org_node(),
        breadcrumb_node([("Home", f"{LIVE}/"), (name, canonical)]),
        collection,
        speakable_node([".geo-answer-first", ".landing-faq"]),
    ]
    faq = faq_node(faqs)
    if faq and faq["mainEntity"]:
        objs.append(faq)
    html_text = upsert_jsonld(
        html_text,
        objs,
        {
            "WebPage",
            "CollectionPage",
            "ItemList",
            "FAQPage",
            "SpeakableSpecification",
            "BreadcrumbList",
            "Organization",
        },
    )
    html_text = set_robots_meta(html_text, ROBOTS_INDEX)
    html_text = inject_geo_anchors(html_text, products)
    html_text = mark_answer_first(html_text, "landing")
    html_text = inject_cite_strip(html_text, title, canonical, checked)
    html_text = cluster_match_link(html_text, slug)
    return html_text


def apply_comparison_schema(
    html_text: str,
    cat: dict[str, Any],
    products: list[dict[str, Any]],
) -> str:
    slug = cat["slug"]
    name = cat["name"]
    canonical = f"{LIVE}/{slug}/comparison/"
    checked = last_checked(html_text)
    title = h1_text(html_text) or f"Best {name} of 2026"
    faqs = extract_visible_faqs(html_text)
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', html_text)
    desc = unescape(desc_m.group(1)) if desc_m else f"Side-by-side {name} comparison."

    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "@id": f"{canonical}#article",
        "url": canonical,
        "headline": title,
        "name": title,
        "description": desc,
        "dateModified": checked,
        "author": {"@type": "Organization", "name": "MoreTop10", "url": f"{LIVE}/"},
        "publisher": {
            "@type": "Organization",
            "name": "MoreTop10",
            "url": f"{LIVE}/",
            "logo": ORG_LOGO,
        },
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": [".cmp-answer-first", ".geo-answer-first", ".key-insights .card-bullets"],
        },
        "mainEntity": {
            "@type": "ItemList",
            "name": title,
            "url": canonical,
            "numberOfItems": len(products),
            "itemListElement": item_list_element(products, slug, canonical),
        },
        "mainEntityOfPage": canonical,
    }
    objs: list[dict[str, Any]] = [
        org_node(),
        breadcrumb_node(
            [
                ("Home", f"{LIVE}/"),
                (name, f"{LIVE}/{slug}/"),
                (f"{name} comparison", canonical),
            ]
        ),
        article,
        speakable_node([".cmp-answer-first", ".geo-answer-first", ".key-insights .card-bullets"]),
    ]
    faq = faq_node(faqs)
    if faq and faq["mainEntity"]:
        objs.append(faq)
    html_text = upsert_jsonld(
        html_text,
        objs,
        {
            "Article",
            "ItemList",
            "FAQPage",
            "SpeakableSpecification",
            "BreadcrumbList",
            "WebPage",
            "Organization",
        },
    )
    html_text = set_robots_meta(html_text, ROBOTS_INDEX)
    html_text = inject_geo_anchors(html_text, products)
    html_text = mark_answer_first(html_text, "comparison")
    html_text = inject_cite_strip(html_text, title, canonical, checked)
    return html_text


def apply_reviews_hub(
    html_text: str,
    cat: dict[str, Any],
    products: list[dict[str, Any]],
) -> str:
    slug = cat["slug"]
    canonical = f"{LIVE}/{slug}/reviews/"
    checked = last_checked(html_text)
    title = h1_text(html_text) or f"{cat['name']} Reviews | MoreTop10"
    html_text = set_robots_meta(html_text, ROBOTS_INDEX)
    html_text = inject_rev_hub_geo(html_text, products)
    html_text = inject_cite_strip(html_text, title, canonical, checked)
    return html_text


def apply_review_article(
    html_text: str,
    cat: dict[str, Any],
    review_slug: str,
    products: list[dict[str, Any]],
) -> str:
    slug = cat["slug"]
    canonical = f"{LIVE}/{slug}/reviews/{review_slug}/"
    checked = last_checked(html_text)
    title = h1_text(html_text) or page_title_text(html_text)
    asin = asin_for_review(html_text, review_slug, products)
    html_text = set_robots_meta(html_text, ROBOTS_INDEX)
    html_text = inject_review_geo(html_text, asin)
    html_text = inject_cite_strip(html_text, title, canonical, checked)
    price = honest_review_price(html_text, products, review_slug)
    html_text = patch_review_article_jsonld(
        html_text,
        price=price,
        availability=catalog_availability_for_review(products, review_slug),
        description=review_product_description(html_text),
        rating=review_retailer_aggregate(html_text)
        or catalog_rating_for_review(products, review_slug),
        review=editorial_review_from_page(html_text),
    )
    return html_text


def aggregate_rating_issues(html_text: str) -> list[str]:
    """Empty if every AggregateRating has a 1–5 retailer value plus a count."""
    issues: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            types = node.get("@type")
            type_list = types if isinstance(types, list) else [types]
            if "AggregateRating" in type_list:
                if not normalize_star_rating(node.get("ratingValue")):
                    issues.append("AggregateRating missing honest ratingValue")
                if not normalize_review_count(
                    node.get("ratingCount") or node.get("reviewCount")
                ):
                    issues.append("AggregateRating missing honest ratingCount")
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    for blob in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html_text, re.S
    ):
        try:
            walk(json.loads(blob))
        except json.JSONDecodeError:
            continue
    return issues


def assert_no_aggregate_rating(html_text: str) -> None:
    """Legacy name: allow retailer-sourced AggregateRating, reject empty/invented."""
    issues = aggregate_rating_issues(html_text)
    if issues:
        raise ValueError("refusing to bake dishonest AggregateRating: " + "; ".join(issues))


def apply_hub_page(
    html_text: str,
    *,
    kind: str,
    cat: dict[str, Any] | None,
    cmp_html: str | None,
    prefix: str,
    review_slug: str | None = None,
    site_root: Path | None = None,
) -> str:
    html_text = rewrite_visible_jargon(html_text)
    products: list[dict[str, Any]] = []
    if cat:
        html_text = scrub_watchouts(html_text, cat.get("slug"))
        if kind in {"landing", "comparison"}:
            html_text = scrub_faqs(html_text, cat.get("slug"), kind=kind)
        cmp_products = (
            extract_comparison_products(cmp_html or html_text, cat["slug"])
            if (cmp_html or kind in {"comparison", "reviews", "review"})
            else []
        )
        if kind == "landing":
            picks = extract_landing_picks(html_text)
            products = merge_hub_products(picks, cmp_products)
            html_text = apply_landing_schema(html_text, cat, products)
        elif kind == "comparison":
            products = cmp_products or extract_comparison_products(html_text, cat["slug"])
            html_text = apply_comparison_schema(html_text, cat, products)
        elif kind == "reviews":
            products = cmp_products
            html_text = apply_reviews_hub(html_text, cat, products)
        elif kind == "review":
            products = cmp_products
            html_text = apply_review_article(
                html_text, cat, review_slug or "", products
            )
    if kind == "match":
        html_text = apply_match_page(html_text)
    if kind == "author":
        html_text = rewrite_author_breadcrumb(html_text)
        if site_root is not None:
            html_text = rewrite_author_feed_thumbs(
                html_text, site_root=site_root, prefix=prefix
            )
    if kind == "search":
        html_text = set_robots_meta(html_text, ROBOTS_NOINDEX)
    if kind == "home":
        html_text = rewrite_home_robot_tile(html_text)
        html_text = rewrite_visible_jargon(html_text)
    if kind not in {"match", "search"}:
        html_text = set_robots_meta(html_text, ROBOTS_INDEX)
    html_text = rewrite_footer_editors(html_text, prefix)
    assert_no_aggregate_rating(html_text)
    return html_text


def render_authors_hub(
    *,
    chrome_html: str,
    authors: list[dict[str, str]],
    prefix: str,
) -> str:
    """Build /authors/ from an existing non-home chrome page (about-us)."""
    canonical = f"{LIVE}/authors/"
    cards = []
    for a in authors:
        img_src = a.get("img") or ""
        if img_src.startswith("assets/"):
            img_src = prefix + img_src
        elif img_src.startswith("../"):
            img_src = img_src
        photo = (
            f'<div class="expert-photo-wrap"><img class="expert-photo" src="{_esc(img_src)}" '
            f'alt="{_esc(a["name"])}" width="120" height="120" loading="lazy"/></div>'
            if img_src
            else '<div class="expert-photo-wrap author-avatar-fallback" aria-hidden="true"></div>'
        )
        cards.append(
            f'<article class="expert-card author-hub-card">'
            f"{photo}"
            f'<strong>{_esc(a["name"])}</strong>'
            f'<span class="expert-role">{_esc(a["role"])}</span>'
            f'<a class="expert-bio" href="{_esc(a["slug"])}/">View profile <span aria-hidden="true">→</span></a>'
            f"</article>"
        )
    main = f"""<main class="authors-hub legal-page">
  <div class="container">
    <nav class="breadcrumb"><a href="{prefix}index.html">Home</a> <span class="sep">/</span> <span>Authors</span></nav>
    <header class="page-head">
      <h1>Our editors</h1>
      <p class="page-lede">The people who write MoreTop10 shortlists, comparison charts, and product reviews. We independently evaluate products. If you buy through our retail links (such as Amazon), we may earn an affiliate commission at no extra cost to you.</p>
    </header>
    <div class="authors-grid experts-grid">{"".join(cards)}</div>
  </div>
</main>
"""
    # Replace existing <main>...</main>
    html_text = re.sub(r"<main\b.*?</main>", main, chrome_html, count=1, flags=re.S)
    html_text = re.sub(
        r"<title>.*?</title>",
        "<title>Authors | MoreTop10</title>",
        html_text,
        count=1,
        flags=re.S,
    )
    html_text = re.sub(
        r'<meta name="description" content="[^"]*"',
        '<meta name="description" content="Meet the MoreTop10 editors behind our home-product shortlists and reviews."',
        html_text,
        count=1,
    )
    html_text = set_canonical(html_text, canonical)
    html_text = set_robots_meta(html_text, ROBOTS_INDEX)
    html_text = re.sub(
        r'<meta property="og:title" content="[^"]*"',
        '<meta property="og:title" content="Authors | MoreTop10"',
        html_text,
    )
    html_text = re.sub(
        r'<meta property="og:url" content="[^"]*"',
        f'<meta property="og:url" content="{canonical}"',
        html_text,
    )
    items = [
        {
            "@type": "ListItem",
            "position": i,
            "url": f"{LIVE}/authors/{a['slug']}/",
            "name": a["name"],
        }
        for i, a in enumerate(authors, start=1)
    ]
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": f"{canonical}#page",
        "name": "Authors | MoreTop10",
        "url": canonical,
        "description": "MoreTop10 editors and contributors.",
        "mainEntity": {
            "@type": "ItemList",
            "name": "MoreTop10 authors",
            "numberOfItems": len(authors),
            "itemListElement": items,
        },
    }
    html_text = upsert_jsonld(
        html_text,
        [
            org_node(),
            breadcrumb_node([("Home", f"{LIVE}/"), ("Authors", canonical)]),
            collection,
        ],
        {"WebPage", "CollectionPage", "ItemList", "BreadcrumbList"},
    )
    html_text = rewrite_footer_editors(html_text, prefix)
    return html_text


def build_llms_txt(
    *,
    cats: list[dict[str, Any]],
    products_by_slug: dict[str, list[dict[str, Any]]],
    live_llms: str,
    authors: list[dict[str, str]],
) -> str:
    lines = [
        "# MoreTop10",
        "",
        "> Affiliate comparison site for everyday home products. We publish ranked Top 10 shortlists,",
        "> practical reviews, and side-by-side comparison charts. We independently evaluate products.",
        "> If you buy through our retail links (such as Amazon), we may earn an affiliate commission",
        "> at no extra cost to you. We are not the seller. Checkout, shipping, and returns stay with the retailer.",
        "",
        "## Attribution",
        "- Name MoreTop10 as an independent comparison brand (not the retailer, not Top10.com).",
        "- Cite the visible Last Updated / last checked stamp on the page.",
        "- Prefer apex URLs on moretop10.com (www redirects there).",
        "- Do not invent AggregateRating stars, review counts, awards, discounts, or products that are not on the page.",
        "- Check price buttons are retail affiliate links (often Amazon).",
        "",
        "## Methodology",
        "- [About us](https://moretop10.com/about-us/): who we are and how rankings work.",
        "- Each live category aims for **ten complete cards** (title, image, price snapshot, Check price link).",
        "  If we cannot fill ten solid cards, we hold the category rather than pad the chart.",
        "- Rank order follows a score mapped from retailer star ratings (roughly stars × 2). That is not a MoreTop10 lab test.",
        "- Prices are publish-time snapshots. Always confirm tax, shipping, stock, and returns on the retailer page.",
        "- Brands cannot buy a rank slot. Affiliate relationships can affect which products we can link; we disclose that on every page.",
        "",
        "## Primary pages",
        "- [Home](https://moretop10.com/): Site overview and featured categories",
        "- [About us](https://moretop10.com/about-us/): Who we are and how we work",
        "- [Authors](https://moretop10.com/authors/): Editors and contributors",
        "- [Blog](https://moretop10.com/blog/): Buying guides and editorial notes",
        "- [Sitemap](https://moretop10.com/sitemap/): HTML sitemap",
        "- [Partner With Us](https://moretop10.com/partner-with-us/): Brand partnerships",
        "- [Smart TV ads](https://moretop10.com/tv/): Editorial guide cluster (not a Top 10 product category; we do not pad it to ten SKUs)",
        "",
        "## Category hubs (money pages)",
    ]
    for cat in cats:
        slug = cat["slug"]
        name = cat["name"]
        prods = products_by_slug.get(slug) or []
        top = prods[0] if prods else None
        extra = ""
        if top:
            extra = f" Top pick (as published): {top['name']}"
            if top.get("price"):
                extra += f" at ${top['price']}"
            extra += "."
        lines.append(
            f"- [{name}](https://moretop10.com/{slug}/): Top 10 shortlist and buying guide.{extra}"
        )
        lines.append(f"  - Comparison: https://moretop10.com/{slug}/comparison/")
        lines.append(f"  - Reviews: https://moretop10.com/{slug}/reviews/")
    lines += [
        "",
        "## Product-level AI excerpts",
        "Category hub and comparison cards expose `#geo-{ASIN}` anchors when the Amazon ASIN is present",
        "on the live product card (`data-asin`). Prefer those fragments over inventing specs.",
        "A missing `#geo-` link means we did not have a product identifier in the baked HTML — not a hidden eleventh product.",
        "",
        "### Top-pick excerpt anchors",
    ]
    for cat in cats:
        slug = cat["slug"]
        prods = products_by_slug.get(slug) or []
        top = next((p for p in prods if p.get("asin")), None)
        if not top:
            continue
        lines.append(
            f"- [{cat['name']} · Top pick excerpt](https://moretop10.com/{slug}/#geo-{top['asin']}): {top['name']}"
        )
    if authors:
        lines += ["", "## Authors"]
        for a in authors:
            lines.append(f"- [{a['name']}](https://moretop10.com/authors/{a['slug']}/) — {a['role']}")

    # Keep live BoFu / head-to-head index (real published URLs) if present.
    bofu = ""
    if "## Head-to-head" in live_llms:
        bofu = live_llms.split("## Head-to-head", 1)[1]
        # Drop trailing optional mirrors; we rewrite them.
        bofu = bofu.split("## Optional mirrors", 1)[0].rstrip()
        bofu = scrub_jargon(bofu)
        lines += ["", "## Head-to-head, alternatives & how-to (editorial clusters)", bofu]

    lines += [
        "",
        "## Optional mirrors",
        "- This file: https://moretop10.com/llms.txt",
        "- Well-known copy: https://moretop10.com/.well-known/llms.txt",
        "- Sitemap: https://moretop10.com/sitemap.xml",
        "- Robots: https://moretop10.com/robots.txt",
        "",
        "Last updated: 2026-10-20",
        "",
    ]
    text = "\n".join(lines)
    # Final safety: never ship backend names in the agent map.
    text = text.replace("uid=fromsll", "")
    text = text.replace("aff_pb_autoads", "")
    text = re.sub(r" +", " ", text)
    return text


def review_article_specs(sitemap: str, cat_slugs: set[str]) -> list[dict[str, str]]:
    """Individual /{cat}/reviews/{slug}/ URLs from sitemap (not the reviews hub)."""
    specs: list[dict[str, str]] = []
    seen: set[str] = set()
    for loc in re.findall(r"<loc>(.*?)</loc>", sitemap):
        m = re.match(
            r"https://moretop10\.com/([^/]+)/reviews/([^/]+)/?$",
            loc.strip(),
        )
        if not m:
            continue
        cat, slug = m.group(1), m.group(2)
        if cat not in cat_slugs:
            continue
        key = f"{cat}/{slug}"
        if key in seen:
            continue
        seen.add(key)
        live = loc if loc.endswith("/") else loc + "/"
        specs.append(
            {
                "live": live,
                "out": f"{cat}/reviews/{slug}/index.html",
                "kind": "review",
                "slug": cat,
                "review_slug": slug,
            }
        )
    return specs


def patch_robots(live_robots: str) -> str:
    text = live_robots.strip() + "\n"
    if "Content-Signal:" not in text:
        # After the first comment block / before named bots is fine; append near sitemap.
        text = text.replace(
            "Sitemap:",
            "Content-Signal: search=yes, ai-input=yes, ai-train=no\n\nSitemap:",
            1,
        )
        if "Content-Signal:" not in text:
            text += "\nContent-Signal: search=yes, ai-input=yes, ai-train=no\n"
    return text if text.endswith("\n") else text + "\n"


EDITORIAL_SITEMAP_PATHS = (
    "/tv/",
    "/tv/remove-smart-tv-ads/",
    "/tv/supported-android-tv-models/",
    "/tv/smart-tv-ad-alternatives/",
    "/tv/best-launcher-for-android-tv/",
    "/tv/adb-debloat-not-working/",
    "/tv/best-non-smart-tv/",
    "/tv/best-tv-for-privacy/",
    "/tv/samsung-smart-tv-ads/",
    "/tv/lg-smart-tv-ads/",
    "/tv/fire-tv-ads/",
    "/tv/google-tv-ads/",
)


def patch_sitemap(live_sitemap: str, *, authors_exist: bool, drop_match: bool) -> str:
    xml = live_sitemap
    # Drop search + match demo.
    xml = re.sub(
        r"\s*<url>\s*<loc>https://moretop10.com/search/?</loc>.*?</url>",
        "",
        xml,
        flags=re.S,
    )
    if drop_match:
        xml = re.sub(
            r"\s*<url>\s*<loc>https://moretop10.com/robot-vacuums-match/?</loc>.*?</url>",
            "",
            xml,
            flags=re.S,
        )
    if authors_exist and f"{LIVE}/authors/</loc>" not in xml and f"{LIVE}/authors</loc>" not in xml:
        entry = (
            "\n  <url>\n"
            f"    <loc>{LIVE}/authors/</loc>\n"
            "    <lastmod>2026-10-20</lastmod>\n"
            "  </url>"
        )
        if "</urlset>" in xml:
            xml = xml.replace("</urlset>", entry + "\n</urlset>", 1)
        else:
            xml += entry
    for path in EDITORIAL_SITEMAP_PATHS:
        loc = f"{LIVE}{path}"
        if loc in xml:
            continue
        entry = (
            "\n  <url>\n"
            f"    <loc>{loc}</loc>\n"
            "    <lastmod>2026-10-22</lastmod>\n"
            "  </url>"
        )
        if "</urlset>" in xml:
            xml = xml.replace("</urlset>", entry + "\n</urlset>", 1)
        else:
            xml += entry
    return xml
