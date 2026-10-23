#!/usr/bin/env python3
"""Open unpublished local drafts for a day-add ASIN batch.

Reads site/data/day-add-open-batch-*.json (MT10 niches only). Writes:

  - site/data/shortlist-<slug>.json          (density=10, l2_pending, track_pending)
  - site/data/day-add-cover-map-YYYY-MM-DD.json
  - site/assets/img/lifestyle/cmp-hero-<slug>.jpg  (gradient slot, not a product photo)
  - site/<slug>/{index,comparison,reviews}/index.html

Rules (hard):
  - Use only provided ASINs. Prefer first 10 distinct. Never invent ASINs/prices/tracks.
  - Skip ASINs already used as role picks in shortlist-*.json when avoidable.
  - PartnerBoost CTA stays empty unless a verified track URL is already in-repo.
  - No wrangler / no Live fetch. Bake ≠ deploy.

Usage:
    python3 site/scripts/scaffold_day_add.py
    python3 site/scripts/scaffold_day_add.py --batch site/data/day-add-open-batch-2026-10-23.json
"""

from __future__ import annotations

import argparse
import html
import json
import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
DATA = SITE / "data"
DEFAULT_BATCH = DATA / "day-add-open-batch-2026-10-23.json"
DENSITY = 10
DATE = "2026-10-23"

# Visitor-safe confirm lines (also in watchouts.CATEGORY_CONFIRM).
CONFIRM = {
    "hearing-aids": "Confirm fit, battery type, and return window on the retailer page.",
    "water-filters": "Confirm install type, flow rate, and filter life on the retailer page.",
    "under-sink-countertop-filtration": "Confirm install type, GPD rating, and faucet finish on the retailer page.",
    "pitcher-water-filters": "Confirm pitcher model, filter life, and pack count on the retailer page.",
    "doormats": "Confirm size, indoor vs outdoor use, and wash method on the retailer page.",
    "split-system": "Confirm BTU, voltage, and install requirements on the retailer page.",
    "tv-wall-ceiling-mounts": "Confirm TV size range, VESA pattern, and weight rating on the retailer page.",
    "monitor-arms": "Confirm screen size, weight per arm, and VESA pattern on the retailer page.",
    "stage-lights": "Confirm pack count, control mode, and indoor vs outdoor rating on the retailer page.",
    "glass-display-cabinets": "Confirm dimensions, lighting type, and shelf rating on the retailer page.",
    "document-scanners": "Confirm camera MP, cover contents, and OS support on the retailer page.",
    "ceramic-space-heaters": "Confirm wattage, oscillation, noise, and tip-over protection on the retailer page.",
}

LEDE = {
    "hearing-aids": "OTC rechargeable hearing aids for everyday speech clarity.",
    "water-filters": "Countertop, under-sink, and whole-house water filter systems—not replacement cartridges.",
    "under-sink-countertop-filtration": "Under-sink and countertop filtration systems, including reverse osmosis.",
    "pitcher-water-filters": "Electric pitchers and replacement filters for Brita-style pitchers.",
    "doormats": "Washable dirt-trapper and welcome doormats for entryways.",
    "split-system": "Mini-split heating and cooling systems by BTU and voltage.",
    "tv-wall-ceiling-mounts": "Full-motion, tilting, and slim TV wall and ceiling mounts.",
    "monitor-arms": "Desk and wall monitor arms for single, dual, and ultrawide screens.",
    "stage-lights": "Par-can wash and moving stage lights for DJ and venue setups.",
    "glass-display-cabinets": "Glass display cabinets and curios for collectibles.",
    "document-scanners": "Overhead book and document scanners with flattening covers.",
    "ceramic-space-heaters": "Portable PTC ceramic space heaters for bedrooms, offices, large rooms, and garages.",
}

COVER_COLORS = {
    "hearing-aids": ((90, 120, 150), (40, 60, 80)),
    "water-filters": ((70, 140, 170), (30, 70, 90)),
    "under-sink-countertop-filtration": ((60, 110, 140), (25, 55, 75)),
    "pitcher-water-filters": ((100, 160, 180), (40, 80, 100)),
    "doormats": ((120, 100, 80), (60, 45, 35)),
    "split-system": ((150, 170, 190), (70, 85, 100)),
    "tv-wall-ceiling-mounts": ((50, 50, 60), (20, 20, 28)),
    "monitor-arms": ((70, 75, 85), (30, 32, 40)),
    "stage-lights": ((80, 40, 90), (30, 15, 40)),
    "glass-display-cabinets": ((180, 170, 150), (90, 80, 70)),
    "document-scanners": ((140, 140, 145), (70, 70, 75)),
    "ceramic-space-heaters": ((180, 90, 50), (90, 40, 25)),
}

ASIN_RE = re.compile(r"\b(B0[0-9A-Z]{8,10})\b")


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def write_png_bytes(width: int, height: int, rgba_rows: list[bytes]) -> bytes:
    raw = b"".join(b"\x00" + row for row in rgba_rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )


def gradient_jpg(dest: Path, top: tuple[int, int, int], bot: tuple[int, int, int]) -> None:
    """Gradient cover slot (PNG bytes, .jpg name — same as restore_home_assets)."""
    w, h = 640, 400
    rows = []
    for y in range(h):
        t = y / max(h - 1, 1)
        rgb = tuple(int(a + (b - a) * t) for a, b in zip(top, bot))
        rows.append(bytes(rgb + (255,)) * w)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(write_png_bytes(w, h, rows))


def occupied_asins() -> set[str]:
    """ASINs already used as role picks in existing shortlist-*.json."""
    used: set[str] = set()
    for path in DATA.glob("shortlist-*.json"):
        if path.name.startswith("shortlist-") and DATE in path.read_text(encoding="utf-8"):
            # Re-running this scaffold should not treat its own files as occupied.
            continue
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        stack = [blob]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                asin = cur.get("asin")
                if isinstance(asin, str) and ASIN_RE.fullmatch(asin):
                    used.add(asin)
                stack.extend(cur.values())
            elif isinstance(cur, list):
                stack.extend(cur)
    return used


def pick_asins(niche: dict, occupied: set[str]) -> list[dict]:
    samples = {row["asin"]: row for row in (niche.get("sample_asins") or []) if row.get("asin")}
    chosen: list[str] = []
    skipped: list[str] = []
    for asin in niche.get("asins") or []:
        if asin in chosen:
            continue
        if asin in occupied:
            skipped.append(asin)
            continue
        chosen.append(asin)
        if len(chosen) >= DENSITY:
            break
    if len(chosen) < DENSITY:
        for asin in niche.get("asins") or []:
            if asin in chosen:
                continue
            chosen.append(asin)
            if len(chosen) >= DENSITY:
                break
    rows = []
    for asin in chosen:
        sample = samples.get(asin) or {}
        title = (sample.get("title") or "").strip()
        brand = (sample.get("brand") or "").strip()
        rows.append(
            {
                "asin": asin,
                "title": title or asin,
                "title_source": "sample_asins" if title else "asin_only",
                "brand": brand or None,
                "affiliate_network": "pb",
                "affiliate_link": None,
                "track_status": "track_pending",
                "l2_status": "l2_pending",
                "price": None,
                "image": None,
            }
        )
    return rows


def write_shortlist(niche: dict, picks: list[dict]) -> Path:
    slug = niche["slug"]
    payload = {
        "generated": DATE,
        "slug": slug,
        "name": niche.get("niche_label") or slug,
        "amazon_category": niche.get("category") or "",
        "density": DENSITY,
        "status": "unpublished_scaffold",
        "waiting_for_部署上线": "yes",
        "inventory": "l2_pending",
        "baked": False,
        "live": False,
        "cta_label": "Check price",
        "cta_rule": "PB pboost.me keeps uid=fromsll when a verified track exists; otherwise track_pending and no Check price",
        "l2": {
            "status": "pending",
            "method": "mac_chrome_cdp_9333",
            "notes": "Skip Mac Chrome CDP L2 in this pass. Every wired ASIN needs G-L2 next.",
        },
        "notes": [
            f"Day-add local scaffold {DATE}. ASINs from day-add-open-batch sites.mt10 only.",
            "No invented prices, tracks, or product photos.",
            "Lifestyle cover is a gradient placeholder until a real cover exists.",
        ],
        "picks": picks,
        "l2_pending_asins": [p["asin"] for p in picks],
        "track_pending_asins": [p["asin"] for p in picks if p.get("track_status") == "track_pending"],
    }
    dest = DATA / f"shortlist-{slug}.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dest


def chrome_shell(kind: str, slug: str, name: str) -> tuple[str, str]:
    """Reuse kids-bikes chrome (head+header / footer) so bake can rewrite nav."""
    if kind == "landing":
        src = (SITE / "kids-bikes" / "index.html").read_text(encoding="utf-8")
        prefix = "../"
        css = "pages-landing.css"
        title = f"{name} | MoreTop10"
        canon = f"https://moretop10.com/{slug}/"
        desc = LEDE[slug]
        cover = f"{prefix}assets/img/lifestyle/cmp-hero-{slug}.jpg"
    elif kind == "comparison":
        src = (SITE / "kids-bikes" / "comparison" / "index.html").read_text(encoding="utf-8")
        prefix = "../../"
        css = "pages-comparison.css"
        title = f"Best {name} of 2026 | MoreTop10"
        canon = f"https://moretop10.com/{slug}/comparison/"
        desc = LEDE[slug]
        cover = f"{prefix}assets/img/lifestyle/cmp-hero-{slug}.jpg"
    else:
        src = (SITE / "kids-bikes" / "reviews" / "index.html").read_text(encoding="utf-8")
        prefix = "../../"
        css = "pages-landing.css"
        title = f"{name} Reviews | MoreTop10"
        canon = f"https://moretop10.com/{slug}/reviews/"
        desc = f"Unbiased {name.lower()} reviews by MoreTop10 editors. Updated {DATE}."
        cover = f"{prefix}assets/img/lifestyle/cmp-hero-{slug}.jpg"

    head = src.split("<main", 1)[0]
    foot = "<footer" + src.split("<footer", 1)[1]
    head = head.replace("Kids Bikes", name)
    head = head.replace("kids-bikes", slug)
    head = re.sub(r"<title>.*?</title>", f"<title>{_esc(title)}</title>", head, count=1, flags=re.S)
    head = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{_esc(desc)}"',
        head,
        count=1,
    )
    head = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{canon}"', head, count=1)
    for prop in ("og:title", "og:description", "og:url", "og:image", "twitter:title", "twitter:description", "twitter:url", "twitter:image"):
        if prop.endswith("title"):
            val = title
        elif prop.endswith("description"):
            val = desc
        elif prop.endswith("url"):
            val = canon
        else:
            val = cover if cover.startswith("http") else f"https://moretop10.com/{cover.lstrip('./')}"
            val = f"https://moretop10.com/assets/img/lifestyle/cmp-hero-{slug}.jpg"
        attr = "name" if prop.startswith("twitter:") else "property"
        head = re.sub(
            rf'<meta {attr}="{prop}" content="[^"]*"',
            f'<meta {attr}="{prop}" content="{_esc(val)}"',
            head,
        )
    if css not in head:
        head = head.replace("pages-landing.css", css).replace("pages-comparison.css", css)
    return head, foot


def landing_main(slug: str, name: str, picks: list[dict]) -> str:
    confirm = CONFIRM[slug]
    lede = LEDE[slug]
    items = []
    toc = []
    picks_html = []
    for i, pick in enumerate(picks, start=1):
        title = pick["title"]
        asin = pick["asin"]
        short = title if len(title) <= 42 else title[:41] + "…"
        items.append(
            f"<li><strong>{i}. {_esc(title)}</strong> — Confirm current specs, stock, and "
            f"returns on the retailer page.</li>"
        )
        toc.append(
            f'<li><a href="#pick-{i}"><span class="toc-num">{i}.</span> {_esc(short)}</a></li>'
        )
        picks_html.append(
            f'<section class="landing-pick" id="pick-{i}">'
            f'<h2><span class="landing-pick-num">{i}</span> {_esc(title)}</h2>'
            f'<p class="landing-pick-tagline">Confirm current specs, stock, and returns on the retailer page.</p>'
            f'<div class="pros-cons landing-pick-pc"><div>'
            f'<div class="pc-col-title pros">Pros</div>'
            f"<ul><li>Confirm current specs, stock, and returns on the retailer page.</li></ul>"
            f"</div><div>"
            f'<div class="pc-col-title cons">Watch-outs</div>'
            f"<ul><li>Check current stock and returns on the retailer page.</li>"
            f"<li>{_esc(confirm)}</li></ul>"
            f"</div></div>"
            f'<div class="landing-pick-cta-bar"><strong>{_esc(title)}</strong>'
            f'<span class="btn btn-ghost btn-sm">Check price after the retailer track is verified</span>'
            f"</div>"
            f'<p class="landing-pick-links"><a href="comparison/">See in comparison →</a></p>'
            f"</section>"
        )
    faqs = [
        # Placeholder details; bake/scrub_faqs replaces from CATEGORY_FAQS.
        ("What should I confirm before I buy?", f"{lede} {confirm}"),
        ("Are prices on this page live?", "Prices are not listed yet. Confirm tax, shipping, and stock on the retailer page."),
        ("Where is the comparison chart?", "Use Jump to comparison for the side-by-side chart. Individual reviews land after listing checks."),
    ]
    faq_html = "\n        ".join(
        f'<details class="landing-faq"{" open" if i == 0 else ""}><summary>{_esc(q)}</summary> '
        f"<p>{_esc(a)}</p></details>"
        for i, (q, a) in enumerate(faqs)
    )
    widget_rows = "".join(
        f'<a class="best-widget-row" href="#pick-{i}">'
        f'<span class="best-widget-name">{_esc(p["title"])}</span>'
        f'<span class="best-widget-arrow" aria-hidden="true">→</span></a>'
        for i, p in enumerate(picks[:5], start=1)
    )
    return f"""<main class="landing-page">
  <div class="container">
    <nav class="breadcrumb"><a href="../">Home</a> <span class="sep">/</span> <span>{_esc(name)}</span></nav>
    <header class="landing-hero">
      <div class="landing-hero-copy">
        <h1>Top 10 Best {_esc(name)} for 2026 — Editor Shortlist</h1>
        <div class="author-byline">
          <div class="author-avatar" aria-hidden="true">PN</div>
          <div class="author-meta">
            <span class="author-name">Written by <a class="author-name-link" href="../authors/priya-nair/">Priya Nair</a></span>
            <span class="author-updated">Last Updated: {DATE}</span>
          </div>
        </div>
      </div>
      <div class="lifestyle-block lifestyle-category has-photo"><img class="lifestyle-photo" src="../assets/img/lifestyle/cmp-hero-{slug}.jpg" alt="" width="640" height="400" loading="lazy" decoding="async"/><span class="lifestyle-label">{_esc(name)}</span></div>
    </header>
    <div class="landing-layout">
      <nav class="jump-toc" aria-label="Jump to picks">
        <span class="toc-title">Jump to:</span>
        <ul class="toc-items">{"".join(toc)}</ul>
      </nav>
      <article class="landing-article">
        <p class="geo-answer-first">As of {DATE}, this {_esc(name.lower())} shortlist is a local draft of {len(picks)} products. Titles come from the inventory batch when present. Prices and Check price links wait on a listing check. Confirm shipping, tax, and returns on the retailer page before you buy.</p>
        <p>{_esc(lede)}</p>
        <p>Every pick on this page is a product from the current shortlist. We do not invent prices, retailer tracks, or product photos. Use Jump to for the ranked products, or open the comparison chart.</p>
        <section class="our-top-list"><h2>Our top {len(picks)} {_esc(name.lower())} for 2026</h2><ol>{"".join(items)}</ol></section>
        <p><a class="btn btn-primary" href="comparison/">Jump to comparison</a></p>
        <p class="landing-related-cluster"><strong>Also explore:</strong> <a href="comparison/">Full comparison chart</a> · <a href="reviews/">Reviews hub</a></p>
        {"".join(picks_html)}
        <h2>How to use this {_esc(name)} guide</h2>
        <p>Scan Jump to, skim Our top list, then open a pick section. Use the comparison when you want products side by side.</p>
        <h2>What we look for</h2>
        <p>A usable title, a listing we can check, and a retailer track we can verify. We skip incomplete listings rather than pad the page.</p>
        <h2>FAQ: buying {_esc(name.lower())}</h2>
        {faq_html}
      </article>
      <aside class="best-widget">
        <h3>Best {_esc(name)}</h3>
        <div class="best-widget-list">{widget_rows}</div>
        <p class="best-widget-more"><a class="btn btn-ghost btn-sm best-widget-compare" href="comparison/">Compare All</a></p>
      </aside>
    </div>
  </div>
</main>
"""


def comparison_main(slug: str, name: str, picks: list[dict]) -> str:
    confirm = CONFIRM[slug]
    cards = []
    for i, pick in enumerate(picks, start=1):
        title = pick["title"]
        asin = pick["asin"]
        cards.append(
            f"""<div class="product-card-wrap">
<article class="product-card" data-asin="{_esc(asin)}" data-role="" data-position="{i}"
  data-sticky="product-card" data-product-name="{_esc(title)}" data-cta="" data-img="">
  <div class="pc-rank-only"><span class="pc-pos">{i}</span></div>
  <div class="pc-main">
    <div class="pc-left"></div>
    <div class="pc-mid">
      <div class="pc-name" title="{_esc(title)}">{_esc(title)}</div>
      <p class="pc-tagline">Confirm current specs, stock, and returns on the retailer page.</p>
    </div>
    <div class="pc-right"></div>
    <div class="pc-price-decision"><span class="pc-price-checked">Price pending listing check</span></div>
    <div class="pc-footer">
      <span class="btn btn-ghost">Check price after the retailer track is verified</span>
    </div>
  </div>
</article>
</div>
"""
        )
    faqs = [
        ("What should I confirm before I buy?", f"{LEDE[slug]} {confirm}"),
        ("Are these prices a live cart?", "No price snapshot is on this draft chart yet. Confirm tax, shipping, and stock on the retailer page."),
        ("Why is Check price missing?", "Retailer tracks are not verified for this draft. We will not invent a hop."),
    ]
    faq_html = "\n          ".join(
        f"<details{' open' if i == 0 else ''}><summary>{_esc(q)}</summary><p>{_esc(a)}</p></details>"
        for i, (q, a) in enumerate(faqs)
    )
    return f"""<main class="comparison-page">
  <div class="container">
    <nav class="breadcrumb"><a href="../../">Home</a> <span class="sep">/</span> <a href="../">{_esc(name)}</a> <span class="sep">/</span> <span>Comparison</span></nav>
    <header class="page-head">
      <h1>Best {_esc(name)} of 2026</h1>
      <p class="page-lede">{_esc(LEDE[slug])}</p>
    </header>
    <div class="cmp-geo-strip">
      <section class="cmp-answer-first geo-answer-first prose-block" aria-label="Quick answer">
        <h2>Quick answer</h2>
        <p>As of {DATE}, this chart lists {len(picks)} {_esc(name.lower())} from the current shortlist. Prices and Check price wait on a listing check. Confirm shipping, tax, and returns on the retailer page before you buy.</p>
      </section>
      <section class="key-insights prose-block" aria-label="Key insights">
        <h2>Key insights</h2>
        <ul class="card-bullets">
          <li>{len(picks)} products are listed on this draft chart.</li>
          <li>No invented prices or retailer tracks.</li>
          <li>{_esc(confirm)}</li>
          <li>Last updated {DATE}.</li>
        </ul>
      </section>
    </div>
    <div class="prose-block"><ol class="cmp-howto"><li>Scan the shortlist</li><li>Open a card</li><li>Confirm the retailer listing</li></ol></div>
    <div class="cmp-layout">
      <div class="cmp-main">
        <aside class="score-disclosure" aria-label="How scores work"><p><strong>How scores work.</strong> Scores and prices land after a listing check. This draft keeps product titles only. Last Updated: {DATE}.</p></aside>
        <div class="product-stack" role="list">
{"".join(cards)}
        </div>
        <div class="faq">
          <h2>FAQ</h2>
          {faq_html}
        </div>
      </div>
    </div>
  </div>
</main>
"""


def reviews_main(slug: str, name: str, picks: list[dict]) -> str:
    cards = []
    for pick in picks:
        title = pick["title"]
        asin = pick["asin"]
        cards.append(
            f'<article class="rev-hub-card" id="geo-{_esc(asin)}">'
            f'<div class="rev-hub-copy">'
            f'<h2 class="rev-hub-title">{_esc(title)}</h2>'
            f'<p class="rev-hub-date">{DATE}</p>'
            f'<p class="rev-hub-excerpt">Confirm current specs, stock, and returns on the retailer page. '
            f"A deep review lands after the listing check.</p>"
            f"</div></article>"
        )
    return f"""<main class="reviews-hub-page">
  <div class="container layout-sidebar">
    <div>
      <nav class="breadcrumb"><a href="../../">Home</a> <span class="sep">/</span> <a href="../">{_esc(name)}</a> <span class="sep">/</span> <span>Reviews</span></nav>
      <header class="page-head">
        <h1>Unbiased {_esc(name)} Reviews by Our Experts</h1>
        <p class="page-lede">This reviews hub lists the draft shortlist ASINs. Individual review articles land after listing checks. Last Updated: {DATE}.</p>
      </header>
      <p class="landing-related-cluster hub-reciprocity"><strong>Related:</strong> <a href="../">Category overview</a> · <a href="../comparison/">Comparison chart</a></p>
      <div class="rev-hub-list">{"".join(cards)}</div>
      <p class="rev-hub-foot"><a class="btn btn-ghost btn-sm" href="../">Category overview</a> · <a class="btn btn-ghost btn-sm" href="../comparison/">Compare all</a></p>
    </div>
  </div>
</main>
"""


def write_pages(slug: str, name: str, picks: list[dict]) -> None:
    for kind, body in (
        ("landing", landing_main(slug, name, picks)),
        ("comparison", comparison_main(slug, name, picks)),
        ("reviews", reviews_main(slug, name, picks)),
    ):
        head, foot = chrome_shell(kind, slug, name)
        html_out = head + body + foot
        if kind == "landing":
            dest = SITE / slug / "index.html"
        elif kind == "comparison":
            dest = SITE / slug / "comparison" / "index.html"
        else:
            dest = SITE / slug / "reviews" / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")


def write_cover_map(slugs: list[str]) -> Path:
    mapping = {}
    for slug in slugs:
        rel = f"assets/img/lifestyle/cmp-hero-{slug}.jpg"
        mapping[slug] = {
            "status": "placeholder",
            "lifestyle": rel,
            "product_photos": "none — do not invent packshots",
            "todo": "Replace gradient placeholder with a real lifestyle cover after G-L2. Do not invent product photos.",
        }
    dest = DATA / f"day-add-cover-map-{DATE}.json"
    dest.write_text(
        json.dumps(
            {
                "generated": DATE,
                "notes": [
                    "Cover slots only. Gradient placeholders, not product photos.",
                    "waiting_for_部署上线=yes. No Live.",
                ],
                "covers": mapping,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return dest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", default=str(DEFAULT_BATCH))
    parser.add_argument("--site", default="mt10")
    args = parser.parse_args()
    batch = json.loads(Path(args.batch).read_text(encoding="utf-8"))
    niches = (batch.get("sites") or {}).get(args.site, {}).get("niches") or []
    if not niches:
        raise SystemExit(f"no niches in {args.batch} sites.{args.site}")

    occupied = occupied_asins()
    cover_slugs: list[str] = []
    summary = []
    for niche in niches:
        slug = niche["slug"]
        if (SITE / slug / "index.html").exists() and slug in {
            "robot-vacuums",
            "kids-bikes",
        }:
            print(f"skip live/published {slug}")
            continue
        name = niche.get("niche_label") or slug
        picks = pick_asins(niche, occupied)
        write_shortlist(niche, picks)
        top, bot = COVER_COLORS.get(slug, ((90, 90, 100), (40, 40, 50)))
        cover = SITE / "assets" / "img" / "lifestyle" / f"cmp-hero-{slug}.jpg"
        gradient_jpg(cover, top, bot)
        write_pages(slug, name, picks)
        cover_slugs.append(slug)
        occupied.update(p["asin"] for p in picks)
        summary.append((slug, len(picks), [p["asin"] for p in picks]))
        print(f"scaffolded {slug} ({len(picks)} ASINs)")

    write_cover_map(cover_slugs)
    print(f"cover map: {len(cover_slugs)} placeholder slots")
    print("done")
    for slug, n, asins in summary:
        print(f"  {slug}: {n} {','.join(asins)}")


if __name__ == "__main__":
    main()
