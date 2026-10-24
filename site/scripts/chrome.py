"""Header mega, mobile nav, disclosure chrome, footer, home-tile WWNN pack, hub reciprocity."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

NAV_CSS = """
<style id="landing-hub-nav">
.mega-with-overview{min-width:300px;max-height:70vh;overflow:auto}
.mega-cat{display:grid;grid-template-columns:1fr auto;gap:0 0.25rem;align-items:center;border-bottom:1px solid var(--mt-border, #eee)}
.mega-cat:last-child{border-bottom:0}
.mega-cat a.mega-overview{font-weight:600}
.mega-cat a.mega-compare-sm{color:var(--mt-ink-muted, #5b6573);white-space:nowrap}
.mobile-nav .mega-cat{display:grid;grid-template-columns:1fr auto;gap:0 0.75rem;padding:0.15rem 0}
.hub-reciprocity{margin:0.75rem 0 1.25rem;font-size:0.95rem}
.footer-col-cats ul,.footer-col-categories ul{columns:1}
@media (min-width:720px){.footer-col-cats ul,.footer-col-categories ul{columns:3}.footer-grid{grid-template-columns:1.4fr 2.2fr 0.85fr 0.85fr}}
</style>
"""


def rel_prefix(out_path: str) -> str:
    """Prefix from a baked file back to the site root.

    index.html → ''
    about-us/index.html → '../'
    kids-bikes/comparison/index.html → '../../'
    """
    p = out_path.strip("/")
    if p.endswith("index.html"):
        p = p[: -len("index.html")].rstrip("/")
    if not p:
        return ""
    return "../" * (p.count("/") + 1)


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def overview_href(prefix: str, slug: str) -> str:
    return f"{prefix}{slug}/"


def comparison_href(prefix: str, slug: str) -> str:
    return f"{prefix}{slug}/comparison/"


def reviews_href(prefix: str, slug: str) -> str:
    return f"{prefix}{slug}/reviews/"


def render_compare_mega(cats: list[dict[str, Any]], prefix: str) -> str:
    rows = []
    for cat in cats:
        slug = cat["slug"]
        name = _esc(cat["name"])
        rows.append(
            f'<div class="mega-cat">'
            f'<a class="mega-overview" href="{overview_href(prefix, slug)}">{name} overview</a>'
            f'<a class="mega-compare-sm" href="{comparison_href(prefix, slug)}">Compare</a>'
            f"</div>"
        )
    return f'<div class="mega mega-with-overview" role="menu">{"".join(rows)}</div>'


def render_reviews_mega(cats: list[dict[str, Any]], prefix: str) -> str:
    links = "".join(
        f'<a href="{reviews_href(prefix, cat["slug"])}">{_esc(cat["name"])}</a>' for cat in cats
    )
    return f'<div class="mega" role="menu">{links}</div>'


def render_compare_mobile(cats: list[dict[str, Any]], prefix: str, open_first: bool = True) -> str:
    rows = []
    for cat in cats:
        slug = cat["slug"]
        name = _esc(cat["name"])
        rows.append(
            f'<div class="mega-cat">'
            f'<a class="mega-overview" href="{overview_href(prefix, slug)}">{name} overview</a>'
            f'<a href="{comparison_href(prefix, slug)}">Compare</a>'
            f"</div>"
        )
    open_attr = " open" if open_first else ""
    return f"<details{open_attr}><summary>Compare</summary>{''.join(rows)}</details>"


def render_reviews_mobile(cats: list[dict[str, Any]], prefix: str) -> str:
    links = "".join(
        f'<a href="{reviews_href(prefix, cat["slug"])}">{_esc(cat["name"])}</a>' for cat in cats
    )
    return f"<details><summary>Reviews</summary>{links}</details>"


def published_nav_cats(cats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Categories mega matches Live hubs: omit status:draft slugs."""
    return [c for c in cats if str(c.get("status") or "") != "draft"]


def render_categories_mega(cats: list[dict[str, Any]], prefix: str) -> str:
    links = "".join(
        f'<a href="{overview_href(prefix, cat["slug"])}">{_esc(cat["name"])}</a>' for cat in cats
    )
    return f'<div class="mega" role="menu">{links}</div>'


def render_categories_mobile(cats: list[dict[str, Any]], prefix: str, open_first: bool = True) -> str:
    links = "".join(
        f'<a href="{overview_href(prefix, cat["slug"])}">{_esc(cat["name"])}</a>' for cat in cats
    )
    open_attr = " open" if open_first else ""
    return f"<details{open_attr}><summary>Categories</summary>{links}</details>"


def render_nav_item(trigger: str, mega: str) -> str:
    return (
        f'<div class="nav-item">'
        f'<button type="button" class="nav-trigger">{trigger}</button>'
        f"{mega}"
        f"</div>"
    )


def render_header_cta(prefix: str, slug: str | None = None) -> str:
    href = comparison_href(prefix, slug or "robot-vacuums")
    return (
        f'<a class="nav-link nav-cta-soft" href="{href}">Compare picks '
        f'<span aria-hidden="true">→</span></a>'
    )


def render_desktop_nav(cats: list[dict[str, Any]], prefix: str) -> str:
    """Shared primary nav: Categories / Compare / Reviews / Articles."""
    pub = published_nav_cats(cats)
    return (
        '<nav class="nav-desktop" aria-label="Primary">\n'
        f"      {render_nav_item('Categories', render_categories_mega(pub, prefix))}\n"
        f"      {render_nav_item('Compare', render_compare_mega(cats, prefix))}\n"
        f"      {render_nav_item('Reviews', render_reviews_mega(cats, prefix))}\n"
        f'      <a class="nav-link" href="{prefix}blog/">Articles</a>\n'
        "      </nav>"
    )


def render_footer_cats(
    cats: list[dict[str, Any]],
    prefix: str,
    editorial: list[dict[str, Any]] | None = None,
) -> str:
    home = prefix if prefix else "/"
    items = [f'<li><a href="{home}">Home</a></li>']
    for cat in cats:
        slug = cat["slug"]
        label = _esc(cat.get("short_name") or cat["name"])
        items.append(f'<li><a href="{overview_href(prefix, slug)}">{label}</a></li>')
    for cluster in editorial or []:
        slug = cluster["slug"]
        label = _esc(cluster.get("short_name") or cluster["name"])
        items.append(f'<li><a href="{overview_href(prefix, slug)}">{label}</a></li>')
    return (
        '<div class="footer-col footer-col-cats">\n'
        "      <h2>Categories</h2>\n"
        "      <ul>\n        "
        + "\n        ".join(items)
        + "\n      </ul>\n    </div>"
    )


def render_footer_company(prefix: str) -> str:
    """Company column: existing About/Editors/Partner/Contact, then Blog + Sitemap."""
    items = [
        f'<li><a href="{prefix}about-us/">About Us</a></li>',
        f'<li><a href="{prefix}authors/">Editors</a></li>',
        f'<li><a href="{prefix}partner-with-us/">Partner With Us</a></li>',
        f'<li><a href="{prefix}contact/">Contact</a></li>',
        f'<li><a href="{prefix}blog/">Blog</a></li>',
        f'<li><a href="{prefix}sitemap/">Sitemap</a></li>',
    ]
    return (
        '<div class="footer-col">\n'
        "      <h2>Company</h2>\n"
        "      <ul>\n        "
        + "\n        ".join(items)
        + "\n      </ul>\n    </div>"
    )


_NAV_STYLE_RE = re.compile(r'<style id="landing-hub-nav">.*?</style>\n?', re.S)


def inject_nav_css(page: str) -> str:
    """Upsert the hub chrome stylesheet so rebakes pick up NAV_CSS edits."""
    block = NAV_CSS.strip() + "\n"
    if 'id="landing-hub-nav"' in page:
        return _NAV_STYLE_RE.sub(block, page, count=1)
    if "</head>" in page:
        return page.replace("</head>", block + "</head>", 1)
    return block + page


_LANDING_CSS_LINK_RE = re.compile(
    r'<link\s+rel="stylesheet"\s+href="[^"]*pages-landing\.css"/>'
)
_SITE_CSS_LINK_RE = re.compile(
    r'(<link\s+rel="stylesheet"\s+href="[^"]*site\.css"/>)'
)
_MAIN_CLASS_RE = re.compile(r'<main class="([^"]*)"')


def needs_pages_landing_css(html: str) -> bool:
    """True when the page uses the landing hero / lifestyle cover layout."""
    return "landing-hero" in html or "lifestyle-photo" in html


def ensure_pages_landing_css(html: str, prefix: str) -> str:
    """Guarantee pages-landing.css is linked next to site.css at `prefix` depth.

    Editorial VS / alts / howto / best-of shells historically shipped with
    tokens.css + site.css only. Without the landing grid, `.lifestyle-photo`
    goes full container width at 16/10.
    """
    if not needs_pages_landing_css(html):
        return html
    href = f"{prefix}assets/css/pages-landing.css"
    link = f'<link rel="stylesheet" href="{href}"/>'
    if _LANDING_CSS_LINK_RE.search(html):
        return _LANDING_CSS_LINK_RE.sub(link, html, count=1)
    if _SITE_CSS_LINK_RE.search(html):
        return _SITE_CSS_LINK_RE.sub(rf"\1\n{link}", html, count=1)
    if "</head>" in html:
        return html.replace("</head>", f"{link}\n</head>", 1)
    return html


def editorial_page_kind(out_rel: str) -> str | None:
    """Map a cluster URL to an existing pages-landing.css page class."""
    parts = Path(out_rel).as_posix().strip("/").split("/")
    if len(parts) != 3 or parts[-1] != "index.html":
        return None
    leaf = parts[1]
    if "-vs-" in leaf:
        return "vs-page"
    if "alternatives" in leaf:
        return "alts-page"
    if leaf.startswith("best-"):
        return "bestof-page"
    return None


def apply_editorial_page_class(html: str, out_rel: str) -> str:
    """Add vs-page / alts-page / bestof-page next to editorial-page when obvious.

    Does not invent new classes or restyle category hubs (`landing-page`).
    """
    kind = editorial_page_kind(out_rel)
    if not kind:
        return html
    match = _MAIN_CLASS_RE.search(html)
    if not match:
        return html
    classes = match.group(1).split()
    if "landing-page" in classes or kind in classes:
        return html
    classes.append(kind)
    return (
        html[: match.start()]
        + f'<main class="{" ".join(classes)}"'
        + html[match.end() :]
    )


_CATEGORIES_MOBILE_RE = re.compile(
    r"<details[^>]*>\s*<summary>Categories</summary>.*?</details>", re.S
)
_COMPARE_MOBILE_RE = re.compile(r"<details[^>]*>\s*<summary>Compare</summary>.*?</details>", re.S)
_REVIEWS_MOBILE_RE = re.compile(r"<details[^>]*>\s*<summary>Reviews</summary>.*?</details>", re.S)
_DESKTOP_NAV_RE = re.compile(
    r'<nav class="nav-desktop[^"]*" aria-label="Primary">.*?</nav>',
    re.S,
)
_MOBILE_NAV_RE = re.compile(
    r'<nav class="mobile-nav"[^>]*>.*?</nav>',
    re.S,
)
_HEADER_CLASS_RE = re.compile(r'<header class="site-header(?: site-header-home)?"')
_EXPLORE_COL_RE = re.compile(
    r'<div class="footer-col(?: footer-col-cats| footer-col-categories)?">\s*<h2>(?:Explore|Categories)</h2>\s*<ul>.*?</ul>\s*</div>',
    re.S,
)
_COMPANY_COL_RE = re.compile(
    r'<div class="footer-col(?: footer-col-company)?">\s*<h2>Company</h2>\s*<ul>.*?</ul>\s*</div>',
    re.S,
)
_COMPARE_CTA_RE = re.compile(
    r'<a class="nav-link nav-cta-soft" href="[^"]*">Compare picks <span aria-hidden="true">→</span></a>',
)


def _replace_nav_item_mega(page: str, trigger: str, new_mega: str) -> str:
    needle = f'<div class="nav-item"><button type="button" class="nav-trigger">{trigger}</button>'
    start = page.find(needle)
    if start < 0:
        return page
    mega_at = page.find('<div class="mega', start)
    if mega_at < 0:
        return page
    mega, end = _consume_element(page, mega_at)
    # drop the closing </div> of nav-item that follows the mega
    rest = page[end:]
    close_nav = rest.find("</div>")
    if close_nav < 0:
        return page
    return page[:mega_at] + new_mega + rest[close_nav:]


# Affiliate disclosure chrome — one source for every baked page.
# Rank order is retailer stars mapped to score, not commission size.
TOP_STRIP_COPY = (
    "We may earn a commission when you buy via our links—at no extra cost to you."
)
TOP_STRIP_PANEL = (
    "MoreTop10 is an affiliate comparison site. When you click Check price and buy, "
    "we may earn a commission at no extra cost to you. We are not the seller."
)
MOBILE_DISCLOSURE = (
    "Advertising Disclosure: we may earn a commission when you buy via Check price links."
)
MISLEADING_STRIP = (
    "We earn commissions from brands listed on this site, which influences how listings are presented."
)


def render_top_affiliate_bar() -> str:
    """Top strip + expandable panel. Existing site.css / site.js already style this."""
    return (
        '<div class="top-affiliate-bar" data-top-bar>\n'
        '  <div class="container top-affiliate-inner">\n'
        f"    <p>{TOP_STRIP_COPY}\n"
        '      <button type="button" class="ad-disclosure-btn top-bar-disc-btn" '
        "data-top-disc-btn>Advertising Disclosure</button>\n"
        "    </p>\n"
        '    <div class="top-affiliate-panel" data-top-disc-panel hidden>\n'
        f"      <p>{TOP_STRIP_PANEL}</p>\n"
        "    </div>\n"
        "  </div>\n"
        "</div>\n\n"
    )


def _remove_nav_disclosure(page: str) -> str:
    """Drop the desktop primary-nav Advertising Disclosure control."""
    marker = 'class="ad-disclosure header-disclosure"'
    while True:
        at = page.find(marker)
        if at < 0:
            return page
        div_at = page.rfind("<div", 0, at)
        if div_at < 0:
            return page
        _block, end = _consume_element(page, div_at)
        left = page[:div_at].rstrip()
        right = page[end:].lstrip()
        page = left + "\n      " + right


def _rewrite_top_strip_copy(page: str) -> str:
    if 'class="top-affiliate-bar"' not in page:
        return page

    def repl(m: re.Match[str]) -> str:
        return f"{m.group(1)}{TOP_STRIP_COPY}"

    page = re.sub(
        r'(<div class="top-affiliate-bar"[^>]*>\s*<div class="container top-affiliate-inner">\s*<p>)\s*.*?(?=\s*<button type="button" class="ad-disclosure-btn top-bar-disc-btn")',
        repl,
        page,
        count=1,
        flags=re.S,
    )
    if MISLEADING_STRIP in page:
        page = page.replace(MISLEADING_STRIP, TOP_STRIP_COPY)
    return page


def _ensure_top_affiliate_bar(page: str) -> str:
    if 'class="top-affiliate-bar"' in page:
        return page
    if 'class="site-header' not in page:
        return page
    return re.sub(
        r'(<header class="site-header)',
        render_top_affiliate_bar() + r"\1",
        page,
        count=1,
    )


def rewrite_disclosure(page: str) -> str:
    """Remove nav Disclosure; keep top strip + panel + mobile with honest copy."""
    page = _remove_nav_disclosure(page)
    page = _ensure_top_affiliate_bar(page)
    page = _rewrite_top_strip_copy(page)
    return page


def rewrite_compare_cta(page: str, prefix: str, slug: str | None, kind: str) -> str:
    """Header/mobile Compare picks CTA. Comparison pages never self-link."""
    if kind == "comparison" and slug:
        href = overview_href(prefix, slug)
        label = "Category overview"
    elif slug:
        href = comparison_href(prefix, slug)
        label = "Compare picks"
    else:
        href = comparison_href(prefix, "robot-vacuums")
        label = "Compare picks"
    replacement = (
        f'<a class="nav-link nav-cta-soft" href="{href}">{label} '
        f'<span aria-hidden="true">→</span></a>'
    )
    return _COMPARE_CTA_RE.sub(replacement, page)


def render_mobile_nav(cats: list[dict[str, Any]], prefix: str) -> str:
    """Shared mobile nav: Categories / Compare / Reviews / Articles + CTA."""
    pub = published_nav_cats(cats)
    return (
        '<nav class="mobile-nav" data-mobile-nav aria-label="Mobile">\n'
        f"    {render_categories_mobile(pub, prefix)}\n"
        f"    {render_compare_mobile(cats, prefix)}\n"
        f"    {render_reviews_mobile(cats, prefix)}\n"
        f'    <a href="{prefix}blog/">Articles</a>\n'
        f'    <p class="mobile-disclosure">{MOBILE_DISCLOSURE}</p>\n'
        f'    <p style="margin-top:1rem">{render_header_cta(prefix)}</p>\n'
        "  </nav>"
    )


def install_hub_nav(page: str, cats: list[dict[str, Any]], prefix: str) -> str:
    """Replace a simple/home header with the shared hub mega nav."""
    page = _HEADER_CLASS_RE.sub('<header class="site-header"', page, count=1)
    desktop = render_desktop_nav(cats, prefix)
    if _DESKTOP_NAV_RE.search(page):
        page = _DESKTOP_NAV_RE.sub(desktop, page, count=1)
    if 'class="header-cta"' not in page.split("</header>", 1)[0]:
        page = re.sub(
            r'(<button class="burger")',
            f'<div class="header-cta">{render_header_cta(prefix)}</div>\n    \\1',
            page,
            count=1,
        )
    mobile = render_mobile_nav(cats, prefix)
    if _MOBILE_NAV_RE.search(page):
        page = _MOBILE_NAV_RE.sub(mobile, page, count=1)
    return page


def rewrite_nav(page: str, cats: list[dict[str, Any]], prefix: str) -> str:
    """Shared header mega + mobile lists for home and hubs.

    Home used to ship `nav-home-simple` (About / Partner). Inner pages already
    have Categories / Compare / Reviews / Articles; this installs that same
    chrome on home, then fills Compare/Reviews from ALL_CATS and Categories
    from the published subset (Live hub Categories mega).
    """
    if "nav-home-simple" in page or "site-header-home" in page:
        page = install_hub_nav(page, cats, prefix)

    pub = published_nav_cats(cats)
    page = _replace_nav_item_mega(page, "Categories", render_categories_mega(pub, prefix))
    page = _replace_nav_item_mega(page, "Compare", render_compare_mega(cats, prefix))
    page = _replace_nav_item_mega(page, "Reviews", render_reviews_mega(cats, prefix))
    page = _CATEGORIES_MOBILE_RE.sub(render_categories_mobile(pub, prefix), page, count=1)
    page = _COMPARE_MOBILE_RE.sub(render_compare_mobile(cats, prefix), page, count=1)
    page = _REVIEWS_MOBILE_RE.sub(render_reviews_mobile(cats, prefix), page, count=1)
    return page


def rewrite_non_home_nav(page: str, cats: list[dict[str, Any]], prefix: str) -> str:
    """Alias kept for existing bake callers — home is no longer skipped."""
    return rewrite_nav(page, cats, prefix)


# Visitor footer copyright — independent brand facts only. Never name
# Top10.com / Natural Intelligence (including in a denial).
FOOTER_COPYRIGHT = "© 2026 MoreTop10. Independent comparison brand."
_OLD_FOOTER_COPYRIGHT = (
    "© 2026 MoreTop10. Independent brand — not affiliated with "
    "Top10.com or Natural Intelligence Ltd."
)
_FOOTER_COPYRIGHT_RE = re.compile(
    r"(<div class=\"container footer-legal\">\s*(?:<p>.*?</p>\s*)*<p>)"
    r"©\s*20\d{2}\s*MoreTop10\.[^<]*(</p>)",
    re.S,
)


def rewrite_footer_copyright(page: str) -> str:
    """Replace association-denial copyright with the chrome SoT line."""
    if _OLD_FOOTER_COPYRIGHT in page:
        page = page.replace(_OLD_FOOTER_COPYRIGHT, FOOTER_COPYRIGHT)
    if "footer-legal" in page and FOOTER_COPYRIGHT not in page:

        def _repl(match: re.Match[str]) -> str:
            return f"{match.group(1)}{FOOTER_COPYRIGHT}{match.group(2)}"

        page = _FOOTER_COPYRIGHT_RE.sub(_repl, page, count=1)
    return page


def rewrite_footer(page: str, cats: list[dict[str, Any]], prefix: str) -> str:
    from site_config import EDITORIAL_CLUSTERS

    cats_col = render_footer_cats(cats, prefix, editorial=EDITORIAL_CLUSTERS)
    if _EXPLORE_COL_RE.search(page):
        page = _EXPLORE_COL_RE.sub(cats_col, page, count=1)
    company_col = render_footer_company(prefix)
    if _COMPANY_COL_RE.search(page):
        page = _COMPANY_COL_RE.sub(company_col, page, count=1)
    return rewrite_footer_copyright(page)


TV_HOME_TILE = (
    '<a class="home-tile home-tile--compact home-tile--narrow" data-home-tile '
    'data-editorial-cluster="tv" href="tv/">'
    '<div class="home-tile-icon" aria-hidden="true">'
    '<svg class="cat-icon" viewBox="0 0 48 48" width="52" height="52" aria-hidden="true" '
    'fill="none" stroke="currentColor" stroke-width="2.25" stroke-linecap="round" '
    'stroke-linejoin="round">'
    '<rect x="8" y="12" width="32" height="20" rx="2"/>'
    '<path d="M16 38h16"/>'
    '<path d="M24 32v6"/>'
    '<path d="M14 18h8"/>'
    "</svg></div>"
    '<strong class="home-tile-title">Smart TV ads</strong></a>'
)

# pages-home.css ≥960px: grid-template-columns: 2.15fr 2.15fr 1fr 1fr
# Tracks (0-index %4): 0=W, 1=W, 2=N, 3=N. Complete rows are 4k tiles.
# Leftover after 4k — any extra N must stay on a narrow column, not a 2.15fr W:
#   count 4k+1, leftover N at %4==0 → pin col 3
#   count 4k+2, leftover WN (N at %4==1) → pin N col 3
#   leftover NN → col 3 then col 4
# Live home today: 22 = 5*4 + WN (Hair Dryers + Dash Cams). Not Dash-Cams-only.
HOME_TILE_TRACKS = ("W", "W", "N", "N")
HOME_TILE_GRID_RE = re.compile(
    r'(<div class="home-tile-grid"[^>]*>)(.*?)(</div>\s*<button type="button" class="home-show-more")',
    re.S,
)


def tile_is_wide(tile: str) -> bool:
    return "home-tile--wide" in tile[:220]


def tile_is_tv(tile: str) -> bool:
    return 'data-editorial-cluster="tv"' in tile


def tile_width_code(tile: str) -> str:
    return "W" if tile_is_wide(tile) else "N"


def home_tile_width_codes(tiles: list[str], n: int | None = None) -> list[str]:
    subset = tiles if n is None else tiles[:n]
    return [tile_width_code(t) for t in subset]


def expected_wwnn_codes(n: int) -> list[str]:
    return [HOME_TILE_TRACKS[i % 4] for i in range(n)]


_HOME_TILE_COL_CLASS_RE = re.compile(r"\s*home-tile--col-[34]")


def set_tile_grid_column(tile: str, col: int | None) -> str:
    """Pin a leftover tile to a 1-indexed WWNN column, or strip a prior pin."""

    def repl(m: re.Match[str]) -> str:
        classes = _HOME_TILE_COL_CLASS_RE.sub("", m.group(1))
        parts = [p for p in classes.split() if p]
        if col in (3, 4):
            parts.append(f"home-tile--col-{col}")
        return f'class="{" ".join(parts)}"'

    return re.sub(r'class="(home-tile[^"]*)"', repl, tile, count=1)


def place_leftover_narrows(tiles: list[str]) -> list[str]:
    """Pin every leftover N after complete WWNN rows onto a narrow track.

    Applies to any leftover N (today Dash Cams at 22=4k+2 / %4==1; tomorrow a
    single N at 4k+1 / %4==0), not a named tile. Complete 4k rows are untouched.
    """
    if not tiles:
        return tiles
    complete = (len(tiles) // 4) * 4
    out = [set_tile_grid_column(t, None) for t in tiles[:complete]]
    leftover = tiles[complete:]
    if not leftover:
        return out
    auto = 0
    used_n: set[int] = set()
    for tile in leftover:
        tile = set_tile_grid_column(tile, None)
        if tile_is_wide(tile):
            auto += 1
            out.append(tile)
            continue
        if auto in (0, 1):
            target = 2 if 2 not in used_n else 3
            used_n.add(target)
            out.append(set_tile_grid_column(tile, target + 1))
            continue
        out.append(tile)
        auto += 1
    return out


def arrange_tiles_wwnn(
    tiles: list[str],
    cats_by_slug: dict[str, dict[str, Any]] | None = None,
) -> list[str]:
    """Stable-partition tiles into CSS-track order: W W N N repeating.

    Extended / kids-bikes stay first among wides. Editorial TV stays first
    among narrows so it lands in a row-1 Narrow slot (index 2). Any leftover
    N after complete 4k rows (WN at %4==1, or a single N at 4k+1) pins to
    an N column so it does not fill a W track.
    """
    slugs = set(cats_by_slug or ())
    wide: list[tuple[tuple[int, int], str]] = []
    narrow: list[tuple[tuple[int, int], str]] = []
    for idx, tile in enumerate(tiles):
        if tile_is_tv(tile):
            pin = (0, -1)
        else:
            cat = (cats_by_slug or {}).get(tile_slug(tile, slugs) or "")
            pin = (0 if _is_extended(cat) else 1, idx)
        bucket = wide if tile_is_wide(tile) else narrow
        bucket.append((pin, tile))
    wide.sort(key=lambda row: row[0])
    narrow.sort(key=lambda row: row[0])
    wides = [t for _, t in wide]
    narrows = [t for _, t in narrow]
    out: list[str] = []
    wi = ni = 0
    while wi < len(wides) or ni < len(narrows):
        for _ in range(2):
            if wi < len(wides):
                out.append(wides[wi])
                wi += 1
        for _ in range(2):
            if ni < len(narrows):
                out.append(narrows[ni])
                ni += 1
    return place_leftover_narrows(out)


def apply_home_tile_visibility(tiles: list[str], visible: int) -> list[str]:
    return [set_tile_is_more(tile, i >= visible) for i, tile in enumerate(tiles)]


def _rebuild_home_grid(page: str, match: re.Match[str], tiles: list[str]) -> str:
    rebuilt = match.group(1) + "\n        " + "".join(tiles) + "\n      " + match.group(3)
    return page[: match.start()] + rebuilt + page[match.end() :]


def ensure_tv_home_tile(
    page: str,
    cats_by_slug: dict[str, dict[str, Any]] | None = None,
    visible: int = 8,
) -> str:
    """Keep editorial /tv/ in the visible home grid and restore WWNN track order.

    Not an ALL_CATS slug. Always re-packs the grid so a prior insert-at-1
    (W N W W…) cannot leave a narrow tile in a wide track.
    """
    m = HOME_TILE_GRID_RE.search(page)
    if not m:
        return page
    tiles = split_home_tiles(m.group(2))
    if not tiles:
        return page
    if not any(tile_is_tv(t) for t in tiles):
        tiles.append(TV_HOME_TILE)
    tiles = arrange_tiles_wwnn(tiles, cats_by_slug)
    tiles = apply_home_tile_visibility(tiles, visible)
    return _rebuild_home_grid(page, m, tiles)


def _consume_element(src: str, start: int) -> tuple[str, int]:
    m = re.match(r"<([a-zA-Z0-9]+)", src[start:])
    if not m:
        return src[start : start + 1], start + 1
    tag = m.group(1)
    gt = src.find(">", start)
    if gt < 0:
        return src[start:], len(src)
    if src[gt - 1] == "/":
        return src[start : gt + 1], gt + 1
    close = f"</{tag}>"
    depth = 1
    j = gt + 1
    open_pat = re.compile(rf"<{tag}(?=[\s>/])")
    while j < len(src) and depth:
        nxt_open = open_pat.search(src, j)
        nxt_close = src.find(close, j)
        if nxt_close < 0:
            return src[start:], len(src)
        if nxt_open and nxt_open.start() < nxt_close:
            end_open = src.find(">", nxt_open.start())
            if end_open < 0:
                return src[start:], len(src)
            if src[end_open - 1] != "/":
                depth += 1
            j = end_open + 1
        else:
            depth -= 1
            j = nxt_close + len(close)
            if depth == 0:
                return src[start:j], j
    return src[start:j], j


def split_home_tiles(inner: str) -> list[str]:
    tiles: list[str] = []
    i = 0
    while i < len(inner):
        while i < len(inner) and inner[i].isspace():
            i += 1
        if i >= len(inner):
            break
        if inner.startswith("<div", i) or inner.startswith("<a", i):
            tile, i = _consume_element(inner, i)
            if "home-tile" in tile[:120]:
                tiles.append(tile)
        else:
            i += 1
    return tiles


def tile_slug(tile: str, slugs: set[str]) -> str | None:
    hrefs = re.findall(r'href="([^"]+)"', tile)
    for href in hrefs:
        for part in href.strip("/").split("/"):
            if part in slugs:
                return part
    return None


def _is_extended(cat: dict[str, Any] | None) -> bool:
    if not cat:
        return False
    if str(cat.get("tier") or "") == "extended":
        return True
    return bool(cat.get("published"))


def set_tile_is_more(tile: str, more: bool) -> str:
    def repl(m: re.Match[str]) -> str:
        classes = m.group(1)
        parts = [p for p in classes.split() if p != "is-more"]
        if more:
            parts.append("is-more")
        return f'class="{" ".join(parts)}"'

    return re.sub(r'class="(home-tile[^"]*)"', repl, tile, count=1)


def reorder_home_tiles(
    page: str,
    cats_by_slug: dict[str, dict[str, Any]],
    visible: int,
) -> str:
    m = HOME_TILE_GRID_RE.search(page)
    if not m:
        return page
    tiles = split_home_tiles(m.group(2))
    if not tiles:
        return page
    tiles = arrange_tiles_wwnn(tiles, cats_by_slug)
    tiles = apply_home_tile_visibility(tiles, visible)
    return _rebuild_home_grid(page, m, tiles)


_HUB_CLUSTER_RE = re.compile(
    r'<p class="landing-related-cluster hub-reciprocity">.*?</p>',
    re.S,
)


def render_hub_block(kind: str) -> str:
    """Related strip. Omit the current page so links are not self / duplicate."""
    parts = ['<a href="../">Category overview</a>']
    if kind == "comparison":
        parts.append('<a href="../reviews/">Full guide</a>')
    else:
        parts.append('<a href="../comparison/">Comparison chart</a>')
    return (
        '<p class="landing-related-cluster hub-reciprocity">'
        "<strong>Related:</strong> "
        + " · ".join(parts)
        + "</p>"
    )


_HERO_STEPS_RE = re.compile(r"\s*<ol class=\"cmp-hero-steps\">.*?</ol>", re.S)


def strip_cmp_hero_steps(page: str) -> str:
    """Drop the decorative Compare / Shortlist / Check price icon row.

    Per-card Check price CTAs (``.product-cta`` / ``.top3-cta``) stay.
    Live snapshots still ship the ``<ol>``; strip on every comparison bake.
    """
    return _HERO_STEPS_RE.sub("", page)


_RV_MOP_PADS_LEFTOVER = (
    "<li>Confirm mop pads, bags, and dock footprint on the retailer page.</li>"
)


def strip_rv_mop_pads_leftover(page: str, slug: str | None, kind: str) -> str:
    """Drop the robot-vacuum template cons line on non-RV landings."""
    if kind != "landing" or slug == "robot-vacuums":
        return page
    return page.replace(_RV_MOP_PADS_LEFTOVER, "")


def ensure_hub_reciprocity(page: str, kind: str) -> str:
    """Inbound path from comparison/ and reviews/ hubs back to /{slug}/."""
    block = render_hub_block(kind)

    if _HUB_CLUSTER_RE.search(page):
        page = _HUB_CLUSTER_RE.sub(block, page, count=1)
    elif 'class="landing-related-cluster hub-reciprocity"' not in page:
        if kind == "reviews":
            page = re.sub(
                r'(<header class="page-head">.*?</header>)',
                r"\1\n      " + block,
                page,
                count=1,
                flags=re.S,
            )
        else:
            # comparison: jump links near the top of the article column
            page = re.sub(
                r'(<nav class="breadcrumb">.*?</nav>)',
                r"\1\n        " + block,
                page,
                count=1,
                flags=re.S,
            )

    # Always keep a landing href in the related / foot clusters.
    if kind == "reviews":
        foot = re.search(r'<p class="rev-hub-foot">.*?</p>', page, re.S)
        if foot and 'href="../"' not in foot.group(0):
            page = re.sub(
                r'(<p class="rev-hub-foot">)(.*?)(</p>)',
                r'\1<a class="btn btn-ghost btn-sm" href="../">Category overview</a> \2\3',
                page,
                count=1,
                flags=re.S,
            )
        # Breadcrumb "Kids Bikes" (or any cat) should hit the landing, not comparison.
        page = re.sub(
            r'(<nav class="breadcrumb"><a href="[^"]+">Home</a> <span class="sep">/</span> )<a href="[^"]+/comparison/">',
            r'\1<a href="../">',
            page,
            count=1,
        )
    else:
        if 'href="../"' not in page and "Category overview" not in page:
            page = page.replace(
                "</header>",
                "</header>\n        " + block,
                1,
            )
    return page
