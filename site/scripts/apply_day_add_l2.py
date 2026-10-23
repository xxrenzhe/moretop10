#!/usr/bin/env python3
"""Merge Mac CDP L2 + PB fromsll tracks into day-add drafts (PR #33).

Hard rules:
  - No wrangler / no Live / no invented ASINs, prices, or pboost hops.
  - Drop accessory niches, accessory ASINs, and kvm-switches (full niche removal).
  - CTA only when L2 ok AND a verified pboost.me?uid=fromsll track exists.
  - Blocked L2 ASINs stay track_pending (track held, not rendered).
  - Density stays honest (do not pad to 10).

Usage:
    python3 site/scripts/apply_day_add_l2.py
"""

from __future__ import annotations

import json
import re
import shutil
from html import escape
from pathlib import Path

from affiliate_uid import ensure_affiliate_uid, is_allowed_track_host, is_empty_track
from seo_geo import rewrite_visible_jargon
from scaffold_day_add import (
    CONFIRM,
    DATE,
    DATA,
    LEDE,
    SITE,
    chrome_shell,
    write_cover_map,
)

ROOT = SITE.parent
HANDOFF = Path("/tmp/mt10-l2-handoff")
PACKS = HANDOFF / "mt10-day-add-l2-2026-10-23"
SUMMARY_SRC = HANDOFF / "mt10-day-add-l2-summary-2026-10-23.json"
PROBE_SRC = HANDOFF / "mt10-day-add-track-probe-2026-10-23.json"
RULE_SRC = HANDOFF / "day-add-no-accessories-2026-10-23.md"

DROP_NICHES = frozenset({"tv-wall-ceiling-mounts", "monitor-arms", "kvm-switches"})
ACCESSORY_ASINS = frozenset(
    {
        "B075J9RLL6",
        "B079ZRQNMM",
        "B0GTPT3LJV",
        "B0GTPH2Z1W",
        "B0GSVSD8JD",
        "B0H5C3GVDL",
        "B0H5BYJ78P",
        "B0F7QJZWLV",
        "B0DRCXJNMK",
        "B0GK1BT4QZ",
        "B0GK16S6Y9",
        "B0GJS9SCJ6",
        "B0H2TYJ8VG",
    }
)
BLOCKED_L2 = frozenset({"B0HMBF83JS", "B0HLCQQ21L", "B0HKK8PJJR", "B0HJNLKK9R"})
KEEP_SLUGS = (
    "hearing-aids",
    "water-filters",
    "under-sink-countertop-filtration",
    "pitcher-water-filters",
    "doormats",
    "split-system",
    "stage-lights",
    "glass-display-cabinets",
    "document-scanners",
)
CTA_SVG = (
    '<svg class="cta-chevron" width="12" height="12" viewBox="0 0 12 12" '
    'fill="none" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" '
    'd="M4.17 1.17a.75.75 0 0 1 1.06 0l4 4a.75.75 0 0 1 0 1.06l-4 4a.75.75 0 1 1'
    '-1.06-1.06L7.64 6 4.17 2.53a.75.75 0 0 1 0-1.06Z" fill="currentColor"/></svg>'
)


def _esc(text: str) -> str:
    return escape(text, quote=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_sot() -> None:
    for src in (SUMMARY_SRC, PROBE_SRC, RULE_SRC):
        dest = DATA / src.name
        dest.write_bytes(src.read_bytes())


def load_tracks() -> dict[str, dict]:
    probe = load_json(PROBE_SRC)
    out: dict[str, dict] = {}
    for row in probe.get("per_asin") or []:
        asin = row.get("asin")
        if asin:
            out[asin] = row
    return out


def load_pack(asin: str) -> dict | None:
    path = PACKS / f"shortlistlab-detail-{asin}.json"
    if not path.exists():
        return None
    blob = load_json(path)
    if blob.get("blocked"):
        return None
    return blob


def parse_price(raw: str | None) -> tuple[str | None, str | None]:
    if not raw:
        return None, None
    text = raw.strip()
    m = re.search(r"\$([0-9][0-9,]*(?:\.[0-9]{2})?)", text)
    if not m:
        return None, text
    return m.group(1).replace(",", ""), text


def verified_track(row: dict | None) -> str | None:
    if not row or not row.get("has_track"):
        return None
    url = (row.get("track") or "").strip()
    if is_empty_track(url) or not is_allowed_track_host(url):
        return None
    if "pboost.me" not in url:
        return None
    out = ensure_affiliate_uid(url, "pb")
    if "uid=fromsll" not in out:
        return None
    return out


def merge_pick(old: dict, track_row: dict | None) -> dict:
    asin = old["asin"]
    pack = None if asin in BLOCKED_L2 else load_pack(asin)
    track = verified_track(track_row)
    title = (pack or {}).get("title") or (track_row or {}).get("title") or old.get("title") or asin
    brand = (pack or {}).get("brand") or old.get("brand")
    if isinstance(brand, str):
        brand = brand.strip() or None
    price, price_raw = parse_price((pack or {}).get("price_displayed"))
    images = (pack or {}).get("image_urls") or []
    image = images[0] if images else None
    l2_ok = bool(pack) and asin not in BLOCKED_L2
    cta_ok = l2_ok and bool(track)
    pick = {
        "asin": asin,
        "title": title,
        "title_source": "l2_pack" if pack else ("track_probe" if (track_row or {}).get("title") else old.get("title_source")),
        "brand": brand,
        "affiliate_network": "pb",
        "affiliate_link": track if cta_ok else None,
        "track_status": "ok" if cta_ok else "track_pending",
        "l2_status": "ok" if l2_ok else ("l2_blocked" if asin in BLOCKED_L2 else "l2_pending"),
        "price": price,
        "price_raw": price_raw,
        "price_displayed": (pack or {}).get("price_displayed"),
        "list_price": (pack or {}).get("list_price"),
        "image": image,
        "availability": (pack or {}).get("availability") if l2_ok else None,
        "in_stock": (pack or {}).get("in_stock_verified") if l2_ok else None,
        "rating": (pack or {}).get("rating") if l2_ok else None,
        "review_count": (pack or {}).get("review_count") if l2_ok else None,
        "feature_bullets": ((pack or {}).get("feature_bullets") or [])[:3] if l2_ok else [],
        "l2": {
            "ok": l2_ok,
            "method": (pack or {}).get("method_used") or "mac_chrome_cdp",
            "zip": (pack or {}).get("checked_zip") or "10001",
            "fetched_at": (pack or {}).get("verified_at") or (pack or {}).get("scraped_at"),
        }
        if l2_ok
        else {
            "ok": False,
            "method": "mac_chrome_cdp",
            "status": "blocked" if asin in BLOCKED_L2 else "pending",
        },
    }
    if not cta_ok and track:
        pick["held_track"] = track
        pick["held_track_note"] = "PB fromsll track exists; CTA withheld until L2 ok"
    return pick


def shortlist_payload(old: dict, picks: list[dict]) -> dict:
    slug = old["slug"]
    n = len(picks)
    shortfall = n < 10
    ok_asins = [p["asin"] for p in picks if p["l2_status"] == "ok" and p["track_status"] == "ok"]
    blocked = [p["asin"] for p in picks if p["l2_status"] == "l2_blocked"]
    dropped = [a for a in (old.get("l2_pending_asins") or [p["asin"] for p in old.get("picks") or []]) if a in ACCESSORY_ASINS]
    notes = [
        f"Day-add L2 merge {DATE}. waiting_for_部署上线=yes. No Live.",
        "Accessory ASINs and accessory niches removed. No invented pboost hops.",
        "Lifestyle cover remains a gradient placeholder.",
    ]
    if slug == "water-filters":
        notes.append(
            "density_shortfall: leftover SoT ASINs have no L2/track and look like more fridge cartridges — not densified."
        )
    if slug == "pitcher-water-filters":
        notes.append(
            "density_shortfall: leftover SoT ASINs have no L2/verified track — kept 7 honest pitcher systems."
        )
    if blocked:
        notes.append("L2 blocked ASINs stay track_pending; CTA not rendered.")
    return {
        "generated": DATE,
        "slug": slug,
        "name": old.get("name") or slug,
        "amazon_category": old.get("amazon_category") or "",
        "density": n,
        "density_target": 10,
        "density_shortfall": shortfall,
        "status": "unpublished_scaffold",
        "waiting_for_部署上线": "yes",
        "inventory": "l2_ok" if not blocked and not shortfall else ("density_shortfall" if shortfall else "l2_partial"),
        "baked": False,
        "live": False,
        "publishable": not shortfall or slug in {"pitcher-water-filters", "glass-display-cabinets"},
        "cta_label": "Check price",
        "cta_rule": "PB pboost.me keeps uid=fromsll when L2 ok + verified track; otherwise track_pending and no Check price",
        "l2": {
            "status": "ok" if not blocked else "partial",
            "method": "mac_chrome_cdp_9333",
            "ok_count": len(ok_asins),
            "blocked": blocked,
        },
        "notes": notes,
        "dropped_accessory_asins": dropped,
        "picks": picks,
        "l2_ok_asins": ok_asins,
        "l2_pending_asins": blocked,
        "track_pending_asins": [p["asin"] for p in picks if p.get("track_status") == "track_pending"],
    }


def cta_html(pick: dict, *, extra_class: str = "") -> str:
    href = pick.get("affiliate_link")
    cls = f"btn btn-cta-yellow product-cta {extra_class}".strip()
    if href and pick.get("track_status") == "ok":
        return (
            f'<a class="{cls}" href="{_esc(href)}" rel="sponsored noopener noreferrer" target="_blank">'
            f"<span>Check price</span>{CTA_SVG}</a>"
        )
    return '<span class="btn btn-ghost btn-sm">Check price after listing check</span>'


def price_html(pick: dict, *, value_class: str = "pc-price-value") -> str:
    raw = pick.get("price_displayed") or (f"${pick['price']}" if pick.get("price") else None)
    if not raw:
        return '<span class="pc-price-checked">Price pending listing check</span>'
    return (
        f'<span class="{value_class}">{_esc(raw)}</span>'
        f'<span class="pc-price-checked">Checked {DATE}</span>'
    )


def stars(rating: float | None) -> str:
    if rating is None:
        return ""
    filled = min(5, max(0, int(round(float(rating)))))
    return "★" * filled + "☆" * (5 - filled)


def landing_main(slug: str, name: str, picks: list[dict]) -> str:
    confirm = CONFIRM[slug]
    lede = LEDE[slug]
    n = len(picks)
    h1 = f"Top {n} Best {name} for 2026 — Editor Shortlist"
    ok_n = sum(1 for p in picks if p.get("track_status") == "ok")
    items = []
    toc = []
    picks_html = []
    for i, pick in enumerate(picks, start=1):
        title = pick["title"]
        asin = pick["asin"]
        short = title if len(title) <= 42 else title[:41] + "…"
        price_bit = f" {pick['price_displayed']}." if pick.get("price_displayed") else ""
        items.append(
            f"<li><strong>{i}. {_esc(title)}</strong> — {confirm[:-1] if confirm.endswith('.') else confirm}.{price_bit}</li>"
        )
        toc.append(f'<li><a href="#pick-{i}"><span class="toc-num">{i}.</span> {_esc(short)}</a></li>')
        feats = pick.get("feature_bullets") or []
        if feats:
            feat_lis = "".join(f"<li>{_esc(f[:160])}</li>" for f in feats[:3])
            feat_block = f'<ul class="landing-pick-feats">{feat_lis}</ul>'
        else:
            feat_block = ""
        img = ""
        if pick.get("image"):
            img = (
                f'<p class="landing-pick-pack"><img src="{_esc(pick["image"])}" alt="" '
                f'width="240" height="180" loading="lazy" decoding="async" referrerpolicy="no-referrer"/></p>'
            )
        picks_html.append(
            f'<section class="landing-pick" id="pick-{i}">'
            f'<span class="geo-anchor" id="geo-{_esc(asin)}" tabindex="-1"></span>'
            f'<h2><span class="landing-pick-num">{i}</span> {_esc(title)}</h2>'
            f'<p class="landing-pick-tagline">{_esc(confirm)}</p>'
            f"{img}{feat_block}"
            f'<div class="pros-cons landing-pick-pc"><div>'
            f'<div class="pc-col-title pros">Pros</div>'
            f"<ul><li>{_esc(confirm)}</li></ul>"
            f"</div><div>"
            f'<div class="pc-col-title cons">Watch-outs</div>'
            f"<ul><li>Check current stock and returns on the retailer page.</li>"
            f"<li>{_esc(confirm)}</li></ul>"
            f"</div></div>"
            f'<div class="landing-pick-cta-bar"><strong>{_esc(title)}</strong>'
            f"{price_html(pick, value_class='landing-pick-price')}{cta_html(pick)}</div>"
            f'<p class="landing-pick-links"><a href="comparison/">See in comparison →</a></p>'
            f"</section>"
        )
    widget_rows = "".join(
        f'<a class="best-widget-row" href="#pick-{i}">'
        f'<span class="best-widget-name">{_esc(p["title"])}</span>'
        f'<span class="best-widget-arrow" aria-hidden="true">→</span></a>'
        for i, p in enumerate(picks[:5], start=1)
    )
    lead = (
        f"As of {DATE}, we list {n} {_esc(name.lower())} "
        f"({ok_n} with a verified price and Check price link). "
        "Chart prices are a listing check (ZIP 10001)—not a live cart. "
        "Confirm shipping, tax, and returns on the retailer page before you buy."
    )
    if n < 10:
        lead += f" Density is honest at {n}, not padded to 10."
    faqs = [
        ("What should I confirm before I buy?", f"{lede} {confirm}"),
        ("Are prices on this page live?", "Prices are a publish-time snapshot. Confirm tax, shipping, and stock on the retailer page."),
        ("Where is the comparison chart?", "Use Jump to comparison for the side-by-side chart."),
    ]
    faq_html = "\n        ".join(
        f'<details class="landing-faq"{" open" if i == 0 else ""}><summary>{_esc(q)}</summary> '
        f"<p>{_esc(a)}</p></details>"
        for i, (q, a) in enumerate(faqs)
    )
    return f"""<main class="landing-page">
  <div class="container">
    <nav class="breadcrumb"><a href="../">Home</a> <span class="sep">/</span> <span>{_esc(name)}</span></nav>
    <header class="landing-hero">
      <div class="landing-hero-copy">
        <h1>{_esc(h1)}</h1>
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
        <p class="geo-answer-first">{lead}</p>
        <p>{_esc(lede)}</p>
        <section class="our-top-list"><h2>Our top {n} {_esc(name.lower())} for 2026</h2><ol>{"".join(items)}</ol></section>
        <p><a class="btn btn-primary" href="comparison/">Jump to comparison</a></p>
        <p class="landing-related-cluster"><strong>Also explore:</strong> <a href="comparison/">Full comparison chart</a> · <a href="reviews/">Reviews hub</a></p>
        {"".join(picks_html)}
        <h2>How to use this {_esc(name)} guide</h2>
        <p>Scan Jump to, skim Our top list, then open a pick section for the snapshot and Check price.</p>
        <h2>What we look for</h2>
        <p>A usable title, a listing we can check, and a retailer track we can verify. We skip accessories and incomplete listings rather than pad the page.</p>
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
    n = len(picks)
    cards = []
    for i, pick in enumerate(picks, start=1):
        title = pick["title"]
        asin = pick["asin"]
        href = pick.get("affiliate_link") if pick.get("track_status") == "ok" else ""
        img = pick.get("image") or ""
        hit = ""
        if href:
            hit = (
                f'<a class="card-hit" href="{_esc(href)}" rel="sponsored noopener noreferrer" '
                f'target="_blank" tabindex="-1" aria-hidden="true"></a>'
            )
        pack = ""
        if img:
            pack = (
                f'<div class="pc-left"><img class="pc-logo pc-packshot" src="{_esc(img)}" '
                f'alt="{_esc(title)}" width="200" height="180" loading="lazy" decoding="async" '
                f'referrerpolicy="no-referrer"/></div>'
            )
        else:
            pack = '<div class="pc-left"></div>'
        score = ""
        if pick.get("rating") is not None:
            mapped = f"{float(pick['rating']) * 2:.1f}"
            score = (
                f'<div class="pc-right"><div class="pc-score-block"><div class="pc-score-row">'
                f'<div class="avg-score">{mapped}</div>'
                f'<div class="stars-and-label"><span class="stars" aria-label="{pick["rating"]} out of 5">'
                f"{stars(pick['rating'])}</span></div></div></div></div>"
            )
        else:
            score = '<div class="pc-right"></div>'
        cards.append(
            f"""<div class="product-card-wrap">
<article class="product-card" data-asin="{_esc(asin)}" data-role="" data-position="{i}"
  data-sticky="product-card" data-product-name="{_esc(title)}" data-cta="{_esc(href)}" data-img="{_esc(img)}" id="geo-{_esc(asin)}">
  {hit}
  <div class="pc-rank-only"><span class="pc-pos">{i}</span></div>
  <div class="pc-main">
    {pack}
    <div class="pc-mid">
      <div class="pc-name" title="{_esc(title)}">{_esc(title)}</div>
      <p class="pc-tagline">{_esc(confirm)}</p>
    </div>
    {score}
    <div class="pc-price-decision">{price_html(pick)}</div>
    <div class="pc-footer">
      {cta_html(pick)}
    </div>
  </div>
</article>
</div>
"""
        )
    lead = (
        f"As of {DATE}, this chart lists {n} {_esc(name.lower())} "
        "after we dropped accessories. Prices and Check price come from a checked "
        "retailer listing. Confirm shipping, tax, and returns on the retailer page before you buy."
    )
    if n < 10:
        lead += f" Density is honest at {n}."
    faqs = [
        ("What should I confirm before I buy?", f"{LEDE[slug]} {confirm}"),
        ("Are these prices a live cart?", "No. Prices are a ZIP 10001 listing snapshot. Confirm tax, shipping, and stock on the retailer page."),
        ("Why is a Check price missing?", "We only show Check price when we have a verified retailer listing and a working checkout link."),
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
        <p>{lead}</p>
      </section>
      <section class="key-insights prose-block" aria-label="Key insights">
        <h2>Key insights</h2>
        <ul class="card-bullets">
          <li>{n} products remain after we dropped accessories.</li>
          <li>Check price opens a verified retailer listing only.</li>
          <li>{_esc(confirm)}</li>
          <li>Last updated {DATE}.</li>
        </ul>
      </section>
    </div>
    <div class="prose-block"><ol class="cmp-howto"><li>Scan the shortlist</li><li>Open a card</li><li>Confirm the retailer listing</li></ol></div>
    <div class="cmp-layout">
      <div class="cmp-main">
        <aside class="score-disclosure" aria-label="How scores work"><p><strong>How scores work.</strong> Scores map from the retailer star rating (stars × 2) when the listing included a star rating. Prices are from the day we checked—not a live cart. Last Updated: {DATE}.</p></aside>
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
        extra = f" {pick['price_displayed']}." if pick.get("price_displayed") else ""
        cards.append(
            f'<article class="rev-hub-card" id="geo-{_esc(asin)}">'
            f'<div class="rev-hub-copy">'
            f'<h2 class="rev-hub-title">{_esc(title)}</h2>'
            f'<p class="rev-hub-date">{DATE}</p>'
            f'<p class="rev-hub-excerpt">{_esc(CONFIRM[slug])}{extra} '
            f"A deeper review will follow.</p>"
            f"</div></article>"
        )
    return f"""<main class="reviews-hub-page">
  <div class="container layout-sidebar">
    <div>
      <nav class="breadcrumb"><a href="../../">Home</a> <span class="sep">/</span> <a href="../">{_esc(name)}</a> <span class="sep">/</span> <span>Reviews</span></nav>
      <header class="page-head">
        <h1>Unbiased {_esc(name)} Reviews by Our Experts</h1>
        <p class="page-lede">This reviews hub lists the current shortlist after we dropped accessories. Last Updated: {DATE}.</p>
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
        dest.write_text(rewrite_visible_jargon(html_out), encoding="utf-8")


def drop_excluded_niches() -> None:
    yaml_path = SITE / "instances" / "moretop10.site.yaml"
    text = yaml_path.read_text(encoding="utf-8")
    for slug in DROP_NICHES:
        text = re.sub(rf"\n    - \{{slug: {slug},[^\n]*", "", text)
        shortlist = DATA / f"shortlist-{slug}.json"
        if shortlist.exists():
            shortlist.unlink()
        hub = SITE / slug
        if hub.exists():
            shutil.rmtree(hub)
        cover = SITE / "assets" / "img" / "lifestyle" / f"cmp-hero-{slug}.jpg"
        if cover.exists():
            cover.unlink()
    yaml_path.write_text(text, encoding="utf-8")

    restore = SITE / "scripts" / "restore_home_assets.py"
    rtxt = restore.read_text(encoding="utf-8")
    for slug, label in (
        ("tv-wall-ceiling-mounts", "TV Mounts"),
        ("monitor-arms", "Monitor Arms"),
        ("kvm-switches", "KVM Switches"),
    ):
        rtxt = rtxt.replace(f'        ("{label}", "{slug}"),\n', "")
    restore.write_text(rtxt, encoding="utf-8")

    cover_path = DATA / "day-add-cover-map-2026-10-23.json"
    if cover_path.exists():
        cover = json.loads(cover_path.read_text(encoding="utf-8"))
        covers = cover.get("covers") or {}
        for slug in DROP_NICHES:
            covers.pop(slug, None)
        cover["covers"] = covers
        cover_path.write_text(json.dumps(cover, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    sitemap = SITE / "sitemap.xml"
    xml = sitemap.read_text(encoding="utf-8")
    for slug in DROP_NICHES:
        xml = re.sub(
            rf"\s*<url>\s*<loc>https://moretop10.com/{slug}[^<]*</loc>.*?</url>",
            "",
            xml,
            flags=re.S,
        )
    sitemap.write_text(xml, encoding="utf-8")

    html_map = SITE / "sitemap" / "index.html"
    h = html_map.read_text(encoding="utf-8")
    for slug in DROP_NICHES:
        h = re.sub(rf"<li><a href=\"[^\"]*{slug}/[^\"]*\"[^>]*>.*?</li>\n?", "", h)
    html_map.write_text(h, encoding="utf-8")


def rebake_chrome_and_hubs() -> None:
    from build import (
        apply_hub_page,
        inject_nav_css,
        load_site_config,
        rel_prefix,
        rewrite_best_widget,
        rewrite_compare_cta,
        rewrite_disclosure,
        rewrite_footer,
        rewrite_non_home_nav,
        verify,
    )
    from seo_geo import (
        build_llms_txt,
        extract_authors_from_home,
        extract_comparison_products,
        extract_landing_picks,
        merge_hub_products,
        rebake_author_feed_thumbs,
    )

    cfg = load_site_config()
    cats = cfg["ALL_CATS"]
    skip = {".cache", "fixtures", "data", "assets"}
    for path in sorted(SITE.rglob("*.html")):
        if set(path.relative_to(SITE).parts) & skip:
            continue
        text = path.read_text(encoding="utf-8")
        if "site-header" not in text and "top-affiliate-bar" not in text:
            continue
        out_rel = str(path.relative_to(SITE))
        prefix = rel_prefix(out_rel)
        kind = "page"
        slug = None
        parts = path.relative_to(SITE).parts
        if parts[0] in {c["slug"] for c in cats}:
            slug = parts[0]
            if len(parts) >= 2 and parts[1] == "comparison":
                kind = "comparison"
            elif len(parts) >= 2 and parts[1] == "reviews":
                kind = "reviews" if parts[-2] == "reviews" else "review"
            else:
                kind = "landing"
        if out_rel == "index.html":
            kind = "home"
        if kind != "home":
            text = inject_nav_css(text)
        text = rewrite_non_home_nav(text, cats, prefix)
        text = rewrite_footer(text, cats, prefix)
        text = rewrite_compare_cta(text, prefix, slug, kind)
        text = rewrite_disclosure(text)
        if slug in KEEP_SLUGS and kind in {"landing", "comparison", "reviews"}:
            cat = cfg["CATS_BY_SLUG"].get(slug)
            cmp_html = None
            if kind in {"landing", "reviews"}:
                cmp_path = SITE / slug / "comparison" / "index.html"
                if cmp_path.exists():
                    cmp_html = cmp_path.read_text(encoding="utf-8")
            text = apply_hub_page(
                text,
                kind=kind,
                cat=cat,
                cmp_html=cmp_html,
                prefix=prefix,
                review_slug=None,
                site_root=SITE,
            )
        text = rewrite_best_widget(text)
        path.write_text(text, encoding="utf-8")

    home_html = (SITE / "index.html").read_text(encoding="utf-8")
    authors = extract_authors_from_home(home_html)
    products_by_slug: dict[str, list] = {}
    for cat in cats:
        slug = cat["slug"]
        landing_path = SITE / slug / "index.html"
        cmp_path = SITE / slug / "comparison" / "index.html"
        landing = landing_path.read_text(encoding="utf-8") if landing_path.exists() else ""
        cmp = cmp_path.read_text(encoding="utf-8") if cmp_path.exists() else ""
        products_by_slug[slug] = merge_hub_products(
            extract_landing_picks(landing),
            extract_comparison_products(cmp, slug),
        )
    llms = build_llms_txt(
        cats=cats,
        products_by_slug=products_by_slug,
        live_llms="",
        authors=authors,
    )
    (SITE / "llms.txt").write_text(llms, encoding="utf-8")
    well = SITE / ".well-known" / "llms.txt"
    well.parent.mkdir(parents=True, exist_ok=True)
    well.write_text(llms, encoding="utf-8")
    rebake_author_feed_thumbs(SITE)
    verify(cfg)


def main() -> None:
    if not PROBE_SRC.exists() or not PACKS.exists():
        raise SystemExit("handoff missing — unpack mt10-day-add-l2-handoff first")
    copy_sot()
    tracks = load_tracks()
    drop_excluded_niches()
    table = []
    for slug in KEEP_SLUGS:
        path = DATA / f"shortlist-{slug}.json"
        old = load_json(path)
        kept = []
        for row in old.get("picks") or []:
            asin = row["asin"]
            if asin in ACCESSORY_ASINS:
                continue
            kept.append(merge_pick(row, tracks.get(asin)))
        payload = shortlist_payload(old, kept)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_pages(slug, payload["name"], kept)
        table.append(payload)
        print(
            f"{slug}: density={payload['density']} shortfall={payload['density_shortfall']} "
            f"cta={len(payload['l2_ok_asins'])} blocked={payload['l2_pending_asins']}"
        )
    write_cover_map(list(KEEP_SLUGS))
    for slug in KEEP_SLUGS:
        dest = DATA / f"shortlist-{slug}.json"
        blob = load_json(dest)
        blob["baked"] = True
        dest.write_text(json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rebake_chrome_and_hubs()
    print("apply_day_add_l2 done")


if __name__ == "__main__":
    main()
