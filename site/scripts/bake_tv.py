#!/usr/bin/env python3
"""Bake the editorial /tv/ content cluster (local HTML only).

Intent-only routes — paths must never contain `cleanyourtv`.
Density exception: do not force 10 SKUs; empty slots stay empty.
YP `affiliate_link` is used as stored (no uid). Bake ≠ Live deploy.
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from affiliate_uid import prepare_affiliate_link  # noqa: E402
from chrome import (  # noqa: E402
    ensure_tv_home_tile,
    inject_nav_css,
    rel_prefix,
    rewrite_footer,
    rewrite_non_home_nav,
)
from site_config import ALL_CATS, EDITORIAL_CLUSTERS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SHORTLIST = SITE / "data" / "shortlist-tv.json"
UPDATED = "2026-10-22"
LIVE = "https://moretop10.com"
CTA_LABEL = "Check price"

# Forbidden branded paths — bake must never write these.
FORBIDDEN_PATHS = (
    "tv/cleanyourtv",
    "tv/cleanyourtv-alternatives",
)

CLUSTER_NAV = [
    ("/tv/", "Smart TV ads hub"),
    ("/tv/remove-smart-tv-ads/", "Turn off ads"),
    ("/tv/supported-android-tv-models/", "Supported models"),
    ("/tv/smart-tv-ad-alternatives/", "When software will not install"),
    ("/tv/best-launcher-for-android-tv/", "Launchers"),
    ("/tv/adb-debloat-not-working/", "ADB troubleshooting"),
]

DISCLOSURE = (
    "<aside class=\"tv-disclosure\" data-tv-disclosure>"
    "<strong>Unofficial guide.</strong> This cluster discusses a third-party "
    "open-source project called CleanYourTV. MoreTop10 is not affiliated with "
    "that project, its authors, any TV brand, or any domain that uses that "
    "name. We do not host the software. Checkout and returns stay with the retailer."
    "</aside>"
)


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def load_shortlist() -> dict:
    return json.loads(SHORTLIST.read_text(encoding="utf-8"))


def cta_anchor(item: dict) -> str:
    href = prepare_affiliate_link(item.get("affiliate_link"), item.get("affiliate_network"))
    if not href:
        return ""
    return (
        f'<a class="btn btn-cta-yellow" href="{_esc(href)}" '
        f'rel="sponsored noopener noreferrer" target="_blank">'
        f"<span>{_esc(CTA_LABEL)}</span></a>"
    )


def product_card(item: dict, *, heading: str = "h3") -> str:
    name = item.get("short_title") or item.get("title") or item["asin"]
    price = item.get("price")
    price_html = f'<p class="tv-meta">Snapshot ${ _esc(price) } · confirm on the retailer page</p>' if price else ""
    img = item.get("image") or ""
    img_html = (
        f'<img src="{_esc(img)}" alt="{_esc(name)}" width="88" height="66" '
        f'loading="lazy" decoding="async" referrerpolicy="no-referrer"/>'
        if img
        else "<span></span>"
    )
    cta = cta_anchor(item)
    os_label = "Google TV" if item.get("kind") == "google_tv" else "Fire TV"
    return (
        f'<article class="tv-product" id="geo-{_esc(item["asin"])}" data-asin="{_esc(item["asin"])}" '
        f'data-affiliate-network="{_esc(item.get("affiliate_network") or "")}">'
        f"{img_html}"
        f"<div><{heading}>{_esc(name)}</{heading}>"
        f'<p class="tv-meta">{_esc(os_label)} · whole TV</p>{price_html}</div>'
        f"{cta or '<span class=\"tv-empty\">No retailer link yet</span>'}"
        "</article>"
    )


def compact_row(item: dict) -> str:
    name = item.get("short_title") or item.get("title") or item["asin"]
    price = f"${item['price']}" if item.get("price") else "—"
    cta = cta_anchor(item)
    return (
        f'<tr id="geo-{_esc(item["asin"])}">'
        f"<td>{_esc(name)}</td>"
        f"<td>{_esc(item.get('kind') or '').replace('_', ' ')}</td>"
        f"<td>{_esc(price)}</td>"
        f"<td>{cta or '—'}</td>"
        "</tr>"
    )


def cluster_nav_html(current: str, prefix: str) -> str:
    items = []
    for path, label in CLUSTER_NAV:
        href = prefix + path.lstrip("/")
        if not href.endswith("/"):
            href += "/"
        cls = ' class="is-current"' if path.rstrip("/") == current.rstrip("/") else ""
        items.append(f'<li{cls}><a href="{_esc(href)}">{_esc(label)}</a></li>')
    return f'<ul class="tv-cluster-nav" aria-label="Smart TV ads guides">{"".join(items)}</ul>'


def related_html(prefix: str) -> str:
    return (
        '<p class="landing-related-cluster tv-related"><strong>In this guide:</strong> '
        f'<a href="{prefix}tv/">Smart TV ads hub</a> · '
        f'<a href="{prefix}tv/remove-smart-tv-ads/">Turn off ads</a> · '
        f'<a href="{prefix}tv/supported-android-tv-models/">Supported models</a> · '
        f'<a href="{prefix}tv/smart-tv-ad-alternatives/">When software will not install</a> · '
        f'<a href="{prefix}projectors/">Projectors shortlist</a></p>'
    )


def page_ld(title: str, url: str, description: str, crumbs: list[tuple[str, str]], products: list[dict] | None = None) -> str:
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": loc}
            for i, (name, loc) in enumerate(crumbs)
        ],
    }
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "url": url,
        "description": description,
        "dateModified": UPDATED,
        "isPartOf": {"@type": "WebSite", "name": "MoreTop10", "url": f"{LIVE}/"},
        "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".geo-answer-first"]},
    }
    blobs = [webpage, breadcrumb]
    if products:
        webpage["mainEntity"] = {
            "@type": "ItemList",
            "name": "Google TV whole-TV recommendations",
            "numberOfItems": len(products),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": {
                        "@type": "Product",
                        "name": p.get("short_title") or p.get("title"),
                        "sku": p["asin"],
                        "url": f"{url}#geo-{p['asin']}",
                        "image": p.get("image"),
                        "brand": {"@type": "Brand", "name": (p.get("short_title") or "TV").split()[0]},
                        "offers": {
                            "@type": "Offer",
                            "priceCurrency": "USD",
                            "price": p.get("price") or None,
                            "url": f"{url}#geo-{p['asin']}",
                        },
                    },
                }
                for i, p in enumerate(products)
            ],
        }
    return "".join(
        f'<script type="application/ld+json">{json.dumps(blob, ensure_ascii=False)}</script>\n'
        for blob in blobs
    )


def wrap_page(
    *,
    out_rel: str,
    title: str,
    description: str,
    canonical: str,
    body: str,
    crumbs: list[tuple[str, str]],
    products: list[dict] | None = None,
) -> str:
    prefix = rel_prefix(out_rel)
    chrome_src = (SITE / "about-us" / "index.html").read_text(encoding="utf-8")
    # Normalize about-us `../` prefixes to the target depth.
    about_prefix = "../"
    if prefix != about_prefix:
        chrome_src = chrome_src.replace('href="../', f'href="{prefix}')
        chrome_src = chrome_src.replace('src="../', f'src="{prefix}')

    head_end = chrome_src.find("</head>")
    body_start = chrome_src.find("<body")
    main_start = chrome_src.find("<main")
    main_end = chrome_src.find("</main>")
    if min(head_end, body_start, main_start, main_end) < 0:
        raise RuntimeError("about-us chrome missing main/head")

    pre_main = chrome_src[body_start:main_start]
    post_main = chrome_src[main_end + len("</main>") :]

    # Rebuild <head> from about-us, swapping title / canonical / CSS.
    head = chrome_src[:head_end]
    head = re.sub(r"<title>.*?</title>", f"<title>{_esc(title)}</title>", head, count=1, flags=re.S)
    head = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{_esc(description)}"',
        head,
        count=1,
    )
    head = re.sub(
        r'<link rel="canonical" href="[^"]*"',
        f'<link rel="canonical" href="{_esc(canonical)}"',
        head,
        count=1,
    )
    for prop in ("og:title", "twitter:title"):
        head = re.sub(
            rf'<meta property="{prop}" content="[^"]*"',
            f'<meta property="{prop}" content="{_esc(title)}"',
            head,
        )
        head = re.sub(
            rf'<meta name="{prop}" content="[^"]*"',
            f'<meta name="{prop}" content="{_esc(title)}"',
            head,
        )
    for prop in ("og:description", "twitter:description"):
        head = re.sub(
            rf'<meta property="{prop}" content="[^"]*"',
            f'<meta property="{prop}" content="{_esc(description)}"',
            head,
        )
        head = re.sub(
            rf'<meta name="{prop}" content="[^"]*"',
            f'<meta name="{prop}" content="{_esc(description)}"',
            head,
        )
    head = re.sub(
        r'<meta property="og:url" content="[^"]*"',
        f'<meta property="og:url" content="{_esc(canonical)}"',
        head,
    )
    head = re.sub(
        r'<meta name="twitter:url" content="[^"]*"',
        f'<meta name="twitter:url" content="{_esc(canonical)}"',
        head,
    )
    # Drop about-us JSON-LD; we inject cluster JSON-LD.
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", head, flags=re.S)
    if "pages-tv.css" not in head:
        head = head.replace(
            'href="../assets/css/site.css"/>',
            f'href="{prefix}assets/css/site.css"/>\n<link rel="stylesheet" href="{prefix}assets/css/pages-tv.css"/>',
            1,
        )
        if "pages-tv.css" not in head:
            head = head.replace(
                f'href="{prefix}assets/css/site.css"/>',
                f'href="{prefix}assets/css/site.css"/>\n<link rel="stylesheet" href="{prefix}assets/css/pages-tv.css"/>',
                1,
            )
    head += page_ld(title, canonical, description, crumbs, products)

    page = head + "</head>\n" + pre_main + body + post_main
    if not page.lstrip().lower().startswith("<!doctype"):
        page = "<!DOCTYPE html>\n" + page
    page = inject_nav_css(page)
    page = rewrite_non_home_nav(page, ALL_CATS, prefix)
    page = rewrite_footer(page, ALL_CATS, prefix)
    return page


def hub_body(prefix: str, current: str) -> str:
    return f"""<main class="legal-page tv-page">
  <div class="container legal-layout">
    <nav class="breadcrumb"><a href="{prefix}index.html">Home</a> <span class="sep">/</span> <span>Smart TV ads</span></nav>
    <header class="page-head">
      <h1>Can you turn off ads on a smart TV?</h1>
      <p class="page-lede tv-lede">Last updated {UPDATED}. A platform-by-platform guide to home-screen ads — and what to do when the software path is blocked.</p>
    </header>
    {cluster_nav_html(current, prefix)}
    {DISCLOSURE}
    <div class="legal-body">
      <p class="geo-answer-first">As of {UPDATED}, some Android TV / Google TV sets can reduce <em>launcher</em> ads (boot screens, home-row recommendations, and some promoted rows) with a software path. Samsung Tizen and LG webOS generally cannot — there is no supported ADB / sideload route. Fire TV software can help on some panels; buying a Fire TV is not a way to “escape ads.” Streaming-app ads inside Netflix or YouTube are out of scope. If install fails or the platform has no ADB, see <a href="{prefix}tv/smart-tv-ad-alternatives/">when software will not install</a>.</p>
      <h2>What this hub covers</h2>
      <p>Use this cluster when a new TV’s home screen is louder than the shows. Start with the software path on Android / Google TV. Only consider another <strong>whole TV</strong> after that path fails, or when the platform never offered it.</p>
      <h2>Ads you can and cannot remove</h2>
      <div class="tv-table-wrap">
        <table class="tv-table">
          <thead><tr><th>Ad type</th><th>Android / Google TV</th><th>Fire TV</th><th>Samsung Tizen</th><th>LG webOS</th><th>Apple TV</th></tr></thead>
          <tbody>
            <tr><td>Boot / splash promo</td><td>Often reducible with a custom launcher</td><td>Sometimes, software-first</td><td>No supported ADB path</td><td>No supported ADB path</td><td>No ADB path</td></tr>
            <tr><td>Home-row recommendations</td><td>Often reducible</td><td>Partial</td><td>No</td><td>No</td><td>No</td></tr>
            <tr><td>Screen-mirroring / ACR prompts</td><td>Settings + software</td><td>Settings + software</td><td>Settings only</td><td>Settings only</td><td>Settings only</td></tr>
            <tr><td>Ads inside Netflix / YouTube</td><td colspan="5">Not removable here. Those are app subscriptions, not launcher ads.</td></tr>
          </tbody>
        </table>
      </div>
      <h2>Pick a starting point</h2>
      <ul>
        <li><a href="{prefix}tv/remove-smart-tv-ads/"><strong>Turn off smart-TV ads</strong></a> — install order, then models, then troubleshooting.</li>
        <li><a href="{prefix}tv/supported-android-tv-models/"><strong>Supported Android / Google TV models</strong></a> — a living table. Counts follow upstream examples, not a frozen “54 / 23.”</li>
        <li><a href="{prefix}tv/smart-tv-ad-alternatives/"><strong>When software will not install</strong></a> — decision tree. Primary recommendations are whole TVs with Google TV. Fire TV panels sit in a separate honest section. Apple TV, onn streamers, and non-smart sets stay empty until we have a real retailer link.</li>
        <li><a href="{prefix}tv/best-launcher-for-android-tv/"><strong>Launchers</strong></a> — ranking notes, no product checkout.</li>
        <li><a href="{prefix}tv/adb-debloat-not-working/"><strong>ADB not working</strong></a> — common failures before you replace the set.</li>
      </ul>
      <h2>What we will not do</h2>
      <ul>
        <li>We will not recommend a Fire Stick.</li>
        <li>We will not put a projector, soundbar, HDMI hub, or mount in the hero “buy a TV” list.</li>
        <li>We will not invent a product or a checkout link to fill a slot.</li>
      </ul>
      {related_html(prefix)}
    </div>
  </div>
</main>"""


def remove_ads_body(prefix: str, current: str) -> str:
    return f"""<main class="legal-page tv-page">
  <div class="container legal-layout">
    <nav class="breadcrumb"><a href="{prefix}index.html">Home</a> <span class="sep">/</span> <a href="{prefix}tv/">Smart TV ads</a> <span class="sep">/</span> <span>Turn off ads</span></nav>
    <header class="page-head">
      <h1>How to remove smart TV ads (software first)</h1>
      <p class="page-lede tv-lede">Last updated {UPDATED}. Install, confirm the model, then troubleshoot. Buy another TV only after this path fails.</p>
    </header>
    {cluster_nav_html(current, prefix)}
    {DISCLOSURE}
    <div class="legal-body">
      <p class="geo-answer-first">As of {UPDATED}, the honest order is: (1) confirm the set is Android TV or Google TV with USB debugging, (2) sideload a community launcher from the unofficial CleanYourTV project, (3) check the <a href="{prefix}tv/supported-android-tv-models/">supported models table</a>, (4) if ADB fails or the platform is Samsung / LG / Apple, open <a href="{prefix}tv/smart-tv-ad-alternatives/">when software will not install</a>. Do not skip to a new TV to “escape ads” if the current set still has a software path.</p>
      <h2>1. Install — software first</h2>
      <ol class="tv-tree">
        <li>Enable Developer options and USB debugging on the TV (Android / Google TV only).</li>
        <li>Use ADB from a computer on the same network. The unofficial project’s README is the install source of truth — we do not mirror those commands here.</li>
        <li>Install the community launcher, then disable or hide the stock launcher ads row if the project documents that step for your build.</li>
        <li>Reboot and confirm boot ads and home-row promos. App-inside ads (Netflix, YouTube) will still be there.</li>
      </ol>
      <h2>2. Confirm the model</h2>
      <p>Codename and retail name often disagree. Use the <a href="{prefix}tv/supported-android-tv-models/">supported Android TV models</a> table. If the set is not listed, treat that as “unknown,” not “impossible,” and read the project’s current examples rather than a screenshot from last year.</p>
      <h2>3. Troubleshoot before you replace the set</h2>
      <p>If ADB cannot see the TV, debugging resets after reboot, or the launcher crashes on a vendor overlay, start with <a href="{prefix}tv/adb-debloat-not-working/">ADB not working</a>. Many “it does not work” threads are a debugging-toggle or network issue, not a dead platform.</p>
      <h2>When to leave this page</h2>
      <p>Go to <a href="{prefix}tv/smart-tv-ad-alternatives/">when software will not install</a> if any of these are true:</p>
      <ul>
        <li>The TV is Samsung Tizen or LG webOS — there is no supported ADB sideload path.</li>
        <li>Developer options are locked, grayed out, or wiped on every reboot.</li>
        <li>You already followed the unofficial install notes and the launcher will not stay default.</li>
        <li>You are shopping for a <em>replacement</em> set and want Google TV called out honestly versus Fire TV.</li>
      </ul>
      <p>That alternatives page recommends <strong>whole TVs</strong> when a retailer link exists. HDMI switches, mounts, soundbars, and projectors are secondary or excluded from the hero list.</p>
      {related_html(prefix)}
    </div>
  </div>
</main>"""


def models_body(prefix: str, current: str) -> str:
    return f"""<main class="legal-page tv-page">
  <div class="container legal-layout">
    <nav class="breadcrumb"><a href="{prefix}index.html">Home</a> <span class="sep">/</span> <a href="{prefix}tv/">Smart TV ads</a> <span class="sep">/</span> <span>Supported models</span></nav>
    <header class="page-head">
      <h1>Supported Android TV / Google TV models</h1>
      <p class="page-lede tv-lede">Last updated {UPDATED}. A scaffold that should follow the unofficial project’s <code>examples/</code> list — not a frozen headcount.</p>
    </header>
    {cluster_nav_html(current, prefix)}
    {DISCLOSURE}
    <div class="legal-body">
      <p class="geo-answer-first">As of {UPDATED}, this table is a scaffold. The unofficial CleanYourTV repository documents supported builds under <code>examples/</code>; that list moves. We will not hard-code “54,” “23,” or “66” models as if they were a permanent count. If your set is missing, go to <a href="{prefix}tv/smart-tv-ad-alternatives/">when software will not install</a> rather than assuming a checkout link.</p>
      <h2>How to read this table</h2>
      <p>Retail stickers say “Hisense U8” or “Toshiba Fire TV.” The software path cares about the Android / Google TV build and whether USB debugging stays on. Fire TV panels are listed only so you do not confuse them with Google TV. Samsung and LG do not belong here.</p>
      <div class="tv-table-wrap">
        <table class="tv-table">
          <thead><tr><th>Retail name (examples)</th><th>OS</th><th>Software path?</th><th>Notes</th></tr></thead>
          <tbody>
            <tr><td>Hisense U8 / U7 Google TV (current US 4K panels)</td><td>Google TV</td><td>Try software first</td><td>Confirm the exact build in upstream examples before you assume support.</td></tr>
            <tr><td>Other Android TV / Google TV (Sony, TCL, and similar)</td><td>Android TV / Google TV</td><td>Maybe</td><td>Look up the codename. Absence from this scaffold is not a “no.”</td></tr>
            <tr><td>Hisense / Toshiba Fire TV panels</td><td>Fire TV</td><td>Software-first on Fire, not a Google TV twin</td><td>Do not buy Fire hardware to escape ads. See the honest Fire section on the alternatives page.</td></tr>
            <tr><td>Samsung Crystal / Frame / QLED (Tizen)</td><td>Tizen</td><td>No ADB path</td><td><a href="{prefix}tv/smart-tv-ad-alternatives/">Decision tree</a> — whole-TV alternatives if you are replacing the set.</td></tr>
            <tr><td>LG OLED / NanoCell (webOS)</td><td>webOS</td><td>No ADB path</td><td>Same as Samsung: software will not sideload a third-party launcher.</td></tr>
            <tr><td>Apple TV 4K (box)</td><td>tvOS</td><td>No ADB path</td><td>No retailer link on this site yet. Slot stays empty.</td></tr>
          </tbody>
        </table>
      </div>
      <p>Dynamic row count from upstream <code>examples/</code> will replace this scaffold in a later bake. Until then, thin is honest.</p>
      <h2>Not on the list</h2>
      <p>If the unofficial examples folder does not mention your build, use <a href="{prefix}tv/adb-debloat-not-working/">ADB troubleshooting</a> first. If the platform has no debugging surface, use <a href="{prefix}tv/smart-tv-ad-alternatives/">when software will not install</a>.</p>
      {related_html(prefix)}
    </div>
  </div>
</main>"""


def alternatives_body(prefix: str, current: str, shortlist: dict) -> str:
    hero = shortlist.get("hero_google_tv") or []
    fire = shortlist.get("honest_fire_tv") or []
    empties = shortlist.get("empty_slots") or []
    do_not = set(shortlist.get("do_not_hero_asins") or [])
    hero = [p for p in hero if p.get("asin") not in do_not]
    fire = [p for p in fire if p.get("asin") not in do_not]

    hero_html = "\n".join(product_card(p) for p in hero) or '<p class="tv-empty">No Google TV whole-TV links in this bake.</p>'
    fire_rows = "\n".join(compact_row(p) for p in fire)
    empty_html = []
    for slot in empties:
        empty_html.append(
            f'<div class="tv-empty" data-slot="{_esc(slot.get("slot") or "")}">'
            f"<strong>{_esc(slot.get('label') or slot.get('slot') or 'Slot')}</strong> — "
            f"{_esc(slot.get('note') or 'No retailer link yet. We will not invent one.')}"
            "</div>"
        )

    return f"""<main class="legal-page tv-page">
  <div class="container legal-layout">
    <nav class="breadcrumb"><a href="{prefix}index.html">Home</a> <span class="sep">/</span> <a href="{prefix}tv/">Smart TV ads</a> <span class="sep">/</span> <span>Alternatives</span></nav>
    <header class="page-head">
      <h1>Smart TV ad alternatives — when software will not install</h1>
      <p class="page-lede tv-lede">Last updated {UPDATED}. Replace the set only after the software path fails or the platform has no ADB. Hero picks are Google TV whole TVs.</p>
    </header>
    {cluster_nav_html(current, prefix)}
    {DISCLOSURE}
    <div class="legal-body">
      <p class="geo-answer-first">As of {UPDATED}, start on <a href="{prefix}tv/remove-smart-tv-ads/">the software guide</a> if the TV is Android or Google TV. Come here when install failed, ADB is missing, or you are replacing a Samsung / LG set. Primary recommendations below are <strong>Hisense Google TV whole TVs</strong> — not projectors, not Fire sticks, not HDMI hubs. Fire TV panels are listed separately so nobody treats them as an “ad-free” upgrade. Apple TV, onn streamers, and non-smart sets have no retailer link on this bake; those slots stay empty.</p>

      <h2>Decision tree</h2>
      <ol class="tv-tree">
        <li><strong>Android TV / Google TV, ADB works</strong> — stay on the software path. Do not buy another TV to solve a launcher problem.</li>
        <li><strong>Android TV / Google TV, ADB broken</strong> — read <a href="{prefix}tv/adb-debloat-not-working/">ADB not working</a>. If it stays broken, a Google TV replacement is a last resort, not a first click.</li>
        <li><strong>Samsung Tizen or LG webOS</strong> — there is no unofficial sideload path. A Google TV whole set is the honest hardware alternative we can link today.</li>
        <li><strong>Fire TV panel you already own</strong> — try Fire software first. Do not buy a second Fire TV to escape ads. The Fire list below is for people who already want that OS, with the limitation stated.</li>
        <li><strong>Want a box or a non-smart panel</strong> — Apple TV, onn, and privacy / non-smart sets are listed as empty slots until a real track exists.</li>
      </ol>

      <h2>Primary recommendations — Google TV whole TVs</h2>
      <p>These are living-room TVs running Google TV. Prices are a {UPDATED} snapshot. Confirm tax, shipping, and returns on the retailer page. We are not padding this list to ten.</p>
      <div class="tv-product-list">
        {hero_html}
      </div>

      <h2>Fire TV panels — honest section</h2>
      <p>Fire TV is a different software stack. Some launcher ads can be reduced on Fire; many cannot. This is <strong>not</strong> a list of TVs to buy so you can skip ads. It exists so Hisense / Toshiba Fire panels are not mixed into the Google TV hero row.</p>
      <div class="tv-table-wrap">
        <table class="tv-table">
          <thead><tr><th>Set</th><th>OS</th><th>Snapshot</th><th>Retailer</th></tr></thead>
          <tbody>
            {fire_rows}
          </tbody>
        </table>
      </div>

      <h2>Boxes, streamers, and non-smart TVs</h2>
      <p>These decision-tree slots stay visible and empty. A missing button is better than a made-up link.</p>
      {''.join(empty_html)}

      <h2>Secondary only — not the hero list</h2>
      <p>HDMI switches, wall mounts, soundbars, and projectors are not whole-TV replacements. If you want a projection setup, use the existing <a href="{prefix}projectors/">projectors shortlist</a> and do not treat an ultra-short-throw as a Google TV panel. We will not put those ASINs in the hero row.</p>
      {related_html(prefix)}
    </div>
  </div>
</main>"""


def launcher_body(prefix: str, current: str) -> str:
    return f"""<main class="legal-page tv-page">
  <div class="container legal-layout">
    <nav class="breadcrumb"><a href="{prefix}index.html">Home</a> <span class="sep">/</span> <a href="{prefix}tv/">Smart TV ads</a> <span class="sep">/</span> <span>Launchers</span></nav>
    <header class="page-head">
      <h1>Best launcher for Android TV (no checkout list)</h1>
      <p class="page-lede tv-lede">Last updated {UPDATED}. A ranking note, not a product shortlist. There are no affiliate SKUs on this page.</p>
    </header>
    {cluster_nav_html(current, prefix)}
    {DISCLOSURE}
    <div class="legal-body">
      <p class="geo-answer-first">As of {UPDATED}, the unofficial CleanYourTV launcher is the project this cluster documents for Android TV / Google TV ad rows. We are not selling a launcher. There is no Check price button here. Compare it against stock Google TV, Projectivy, and vendor overlays on fit — then return to <a href="{prefix}tv/remove-smart-tv-ads/">the install guide</a>.</p>
      <h2>How we would rank (when we publish scores)</h2>
      <ol>
        <li>Does it stay default after reboot?</li>
        <li>Does it hide boot and home-row promos without breaking HDMI-CEC or inputs?</li>
        <li>Is the install path documented for your build?</li>
      </ol>
      <p>Vendor “kids” or “hotel” modes are not substitutes. Paid APK stores are out of scope.</p>
      {related_html(prefix)}
    </div>
  </div>
</main>"""


def adb_body(prefix: str, current: str) -> str:
    return f"""<main class="legal-page tv-page">
  <div class="container legal-layout">
    <nav class="breadcrumb"><a href="{prefix}index.html">Home</a> <span class="sep">/</span> <a href="{prefix}tv/">Smart TV ads</a> <span class="sep">/</span> <span>ADB troubleshooting</span></nav>
    <header class="page-head">
      <h1>ADB debloat not working</h1>
      <p class="page-lede tv-lede">Last updated {UPDATED}. Common failures before you replace the television.</p>
    </header>
    {cluster_nav_html(current, prefix)}
    {DISCLOSURE}
    <div class="legal-body">
      <p class="geo-answer-first">As of {UPDATED}, most “ADB not working” cases on Android TV / Google TV are a debugging toggle, a network mismatch, or a vendor overlay that resets Developer options — not proof that you need a new TV. Walk the list below, then open <a href="{prefix}tv/smart-tv-ad-alternatives/">when software will not install</a> only if the platform has no ADB surface (Samsung, LG, Apple) or the unofficial install still fails after a clean retry.</p>
      <h2>Check these first</h2>
      <ul>
        <li>TV and computer on the same subnet. Guest Wi-Fi and client isolation break ADB over network.</li>
        <li>USB debugging still on after a reboot. Some builds wipe Developer options.</li>
        <li>The TV’s IP changed after a DHCP lease. Re-authorize the computer.</li>
        <li>A second launcher already holds the default home role.</li>
      </ul>
      <h2>When to stop</h2>
      <p>If the set is Tizen, webOS, or tvOS, this page does not apply — go to the alternatives decision tree. If you are shopping for a replacement, prefer a <strong>Google TV whole TV</strong> over a Fire panel sold as an ad workaround.</p>
      {related_html(prefix)}
    </div>
  </div>
</main>"""


PAGES = [
    {
        "out": "tv/index.html",
        "path": "/tv/",
        "title": "Can you turn off ads on a smart TV? | MoreTop10",
        "description": "Platform-by-platform guide to smart-TV ads. Software first on Android and Google TV. Unofficial project discussed with no brand affiliation.",
        "crumbs": [("Home", f"{LIVE}/"), ("Smart TV ads", f"{LIVE}/tv/")],
        "body": hub_body,
        "products": False,
    },
    {
        "out": "tv/remove-smart-tv-ads/index.html",
        "path": "/tv/remove-smart-tv-ads/",
        "title": "How to remove smart TV ads | MoreTop10",
        "description": "Install, confirm the model, then troubleshoot. Replace the TV only after the software path fails or the platform has no ADB.",
        "crumbs": [
            ("Home", f"{LIVE}/"),
            ("Smart TV ads", f"{LIVE}/tv/"),
            ("Turn off ads", f"{LIVE}/tv/remove-smart-tv-ads/"),
        ],
        "body": remove_ads_body,
        "products": False,
    },
    {
        "out": "tv/supported-android-tv-models/index.html",
        "path": "/tv/supported-android-tv-models/",
        "title": "Supported Android TV and Google TV models | MoreTop10",
        "description": "Scaffold for Android TV and Google TV models. Counts follow upstream examples, not a frozen headcount.",
        "crumbs": [
            ("Home", f"{LIVE}/"),
            ("Smart TV ads", f"{LIVE}/tv/"),
            ("Supported models", f"{LIVE}/tv/supported-android-tv-models/"),
        ],
        "body": models_body,
        "products": False,
    },
    {
        "out": "tv/smart-tv-ad-alternatives/index.html",
        "path": "/tv/smart-tv-ad-alternatives/",
        "title": "Smart TV ad alternatives | MoreTop10",
        "description": "When software will not install: decision tree plus Google TV whole-TV recommendations. Fire TV listed separately. No invented products.",
        "crumbs": [
            ("Home", f"{LIVE}/"),
            ("Smart TV ads", f"{LIVE}/tv/"),
            ("Alternatives", f"{LIVE}/tv/smart-tv-ad-alternatives/"),
        ],
        "body": alternatives_body,
        "products": True,
    },
    {
        "out": "tv/best-launcher-for-android-tv/index.html",
        "path": "/tv/best-launcher-for-android-tv/",
        "title": "Best launcher for Android TV | MoreTop10",
        "description": "Launcher ranking notes for Android TV. No affiliate product list on this page.",
        "crumbs": [
            ("Home", f"{LIVE}/"),
            ("Smart TV ads", f"{LIVE}/tv/"),
            ("Launchers", f"{LIVE}/tv/best-launcher-for-android-tv/"),
        ],
        "body": launcher_body,
        "products": False,
    },
    {
        "out": "tv/adb-debloat-not-working/index.html",
        "path": "/tv/adb-debloat-not-working/",
        "title": "ADB debloat not working | MoreTop10",
        "description": "Troubleshooting when USB debugging or a community launcher will not stick. Replace the set only after this list.",
        "crumbs": [
            ("Home", f"{LIVE}/"),
            ("Smart TV ads", f"{LIVE}/tv/"),
            ("ADB troubleshooting", f"{LIVE}/tv/adb-debloat-not-working/"),
        ],
        "body": adb_body,
        "products": False,
    },
]


def assert_no_forbidden(path: Path) -> None:
    rel = path.as_posix()
    for bad in FORBIDDEN_PATHS:
        if bad in rel:
            raise SystemExit(f"refusing forbidden path {rel}")


def bake_pages(shortlist: dict) -> list[Path]:
    wrote: list[Path] = []
    hero = shortlist.get("hero_google_tv") or []
    for spec in PAGES:
        prefix = rel_prefix(spec["out"])
        current = spec["path"]
        if spec["body"] is alternatives_body:
            body = spec["body"](prefix, current, shortlist)
            products = hero
        else:
            body = spec["body"](prefix, current)
            products = None
        html_out = wrap_page(
            out_rel=spec["out"],
            title=spec["title"],
            description=spec["description"],
            canonical=f"{LIVE}{spec['path']}",
            body=body,
            crumbs=spec["crumbs"],
            products=products if spec["products"] else None,
        )
        dest = SITE / spec["out"]
        assert_no_forbidden(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")
        wrote.append(dest)
        print(f"  wrote {dest.relative_to(ROOT)}")
    return wrote


def patch_existing_chrome() -> int:
    """Keep /tv/ reachable from home + every footer without registering ALL_CATS."""
    n = 0
    for path in SITE.rglob("index.html"):
        rel = path.relative_to(SITE).as_posix()
        if "/.cache/" in f"/{rel}" or rel.startswith(".cache/"):
            continue
        prefix = rel_prefix(rel)
        text = path.read_text(encoding="utf-8")
        updated = rewrite_footer(text, ALL_CATS, prefix)
        if rel == "index.html":
            updated = ensure_tv_home_tile(updated)
        if rel == "projectors/index.html":
            cluster = re.search(r'<p class="landing-related-cluster">.*?</p>', updated, re.S)
            if cluster and f"{prefix}tv/" not in cluster.group(0):
                updated = updated.replace(
                    cluster.group(0),
                    cluster.group(0).replace(
                        "</p>",
                        f' · <a href="{prefix}tv/">Smart TV ads guide</a></p>',
                        1,
                    ),
                    1,
                )
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            n += 1
    return n


def patch_sitemap() -> None:
    sitemap_path = SITE / "sitemap.xml"
    if not sitemap_path.exists():
        return
    xml = sitemap_path.read_text(encoding="utf-8")
    for spec in PAGES:
        loc = f"{LIVE}{spec['path']}"
        if loc in xml:
            continue
        entry = (
            "\n  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{UPDATED}</lastmod>\n"
            "  </url>"
        )
        if "</urlset>" in xml:
            xml = xml.replace("</urlset>", entry + "\n</urlset>", 1)
    sitemap_path.write_text(xml, encoding="utf-8")
    print("  patched site/sitemap.xml")


def patch_llms() -> None:
    for rel in ("llms.txt", ".well-known/llms.txt"):
        path = SITE / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "/tv/" in text:
            continue
        block = (
            "\n## Editorial guides\n"
            "- [Smart TV ads](https://moretop10.com/tv/): Can you turn off ads, "
            "then what to do when the software path fails. Not a Top 10 product category — "
            "we do not pad this cluster to ten SKUs.\n"
            "  - Remove ads: https://moretop10.com/tv/remove-smart-tv-ads/\n"
            "  - Supported models: https://moretop10.com/tv/supported-android-tv-models/\n"
            "  - Alternatives (Google TV whole TVs): https://moretop10.com/tv/smart-tv-ad-alternatives/\n"
        )
        text = text.rstrip() + "\n" + block
        path.write_text(text, encoding="utf-8")
        print(f"  patched site/{rel}")


def verify_tv(shortlist: dict) -> None:
    errors: list[str] = []
    slugs = {c["slug"] for c in ALL_CATS}
    if "tv" in slugs:
        errors.append("tv must not be in ALL_CATS")
    if not any(c["slug"] == "tv" for c in EDITORIAL_CLUSTERS):
        errors.append("EDITORIAL_CLUSTERS missing tv")

    for spec in PAGES:
        path = SITE / spec["out"]
        if not path.exists():
            errors.append(f"missing {spec['out']}")
            continue
        html_out = path.read_text(encoding="utf-8")
        if "cleanyourtv" in spec["out"]:
            errors.append(f"forbidden path baked {spec['out']}")
        if "geo-answer-first" not in html_out:
            errors.append(f"{spec['out']} missing answer-first")
        if "data-tv-disclosure" not in html_out:
            errors.append(f"{spec['out']} missing unofficial disclosure")
        if "uid=" in html_out:
            errors.append(f"{spec['out']} leaked uid= on a CTA")
        if "PartnerBoost" in html_out or "YeahPromos" in html_out or "fromsll" in html_out:
            errors.append(f"{spec['out']} visitor jargon")

    alt = (SITE / "tv/smart-tv-ad-alternatives/index.html").read_text(encoding="utf-8")
    alt_hrefs = html.unescape(alt)
    for item in shortlist.get("hero_google_tv") or []:
        href = item.get("affiliate_link") or ""
        if href and href not in alt_hrefs:
            errors.append(f"hero missing track for {item.get('asin')}")
        if "uid=" in href:
            errors.append(f"shortlist hero {item.get('asin')} has uid")
    if "B0DGHZ1C8V" in alt or "B0FHGNWZXT" in alt:
        errors.append("do_not_hero projector ASIN appeared on L2")
    if "Fire Stick" in alt and "never" not in alt.lower():
        pass  # mention in a prohibition is ok
    home = (SITE / "index.html").read_text(encoding="utf-8")
    if 'data-editorial-cluster="tv"' not in home:
        errors.append("home missing /tv/ tile")
    if "tv/" not in home:
        errors.append("home missing tv/ href")
    about = (SITE / "about-us" / "index.html").read_text(encoding="utf-8")
    if "tv/" not in about.split("<footer", 1)[-1]:
        errors.append("about footer missing /tv/")
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    if f"{LIVE}/tv/" not in sitemap:
        errors.append("sitemap missing /tv/")
    if f"{LIVE}/tv/smart-tv-ad-alternatives/" not in sitemap:
        errors.append("sitemap missing L2")
    if errors:
        raise SystemExit("bake_tv verify failed:\n- " + "\n- ".join(errors))
    print("bake_tv verify ok")


def main() -> None:
    shortlist = load_shortlist()
    print(f"bake /tv/ cluster ({len(PAGES)} pages, hero={len(shortlist.get('hero_google_tv') or [])})")
    bake_pages(shortlist)
    n = patch_existing_chrome()
    print(f"  patched chrome on {n} existing pages")
    patch_sitemap()
    patch_llms()
    verify_tv(shortlist)


if __name__ == "__main__":
    main()
