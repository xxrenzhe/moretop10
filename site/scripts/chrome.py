"""Header mega, mobile nav, footer, home-tile pin, hub reciprocity."""

from __future__ import annotations

import html
import re
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
.footer-col-cats ul{columns:1}
@media (min-width:720px){.footer-grid{grid-template-columns:1.4fr 1fr 1.1fr 0.9fr 0.8fr}}
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


def render_footer_cats(cats: list[dict[str, Any]], prefix: str) -> str:
    home = f"{prefix}index.html" if prefix else "index.html"
    items = [f'<li><a href="{home}">Home</a></li>']
    for cat in cats:
        slug = cat["slug"]
        label = _esc(cat.get("short_name") or cat["name"])
        items.append(f'<li><a href="{overview_href(prefix, slug)}">{label}</a></li>')
    items.append(f'<li><a href="{prefix}blog/">Blog</a></li>')
    items.append(f'<li><a href="{prefix}sitemap/">Sitemap</a></li>')
    return (
        '<div class="footer-col footer-col-cats">\n'
        "      <h2>Categories</h2>\n"
        "      <ul>\n        "
        + "\n        ".join(items)
        + "\n      </ul>\n    </div>"
    )


def inject_nav_css(page: str) -> str:
    if 'id="landing-hub-nav"' in page:
        return page
    if "</head>" in page:
        return page.replace("</head>", NAV_CSS + "</head>", 1)
    return NAV_CSS + page


_COMPARE_MOBILE_RE = re.compile(r"<details[^>]*>\s*<summary>Compare</summary>.*?</details>", re.S)
_REVIEWS_MOBILE_RE = re.compile(r"<details[^>]*>\s*<summary>Reviews</summary>.*?</details>", re.S)
_EXPLORE_COL_RE = re.compile(
    r'<div class="footer-col(?: footer-col-cats)?">\s*<h2>(?:Explore|Categories)</h2>\s*<ul>.*?</ul>\s*</div>',
    re.S,
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


def rewrite_non_home_nav(page: str, cats: list[dict[str, Any]], prefix: str) -> str:
    """Replace Compare/Reviews megas + mobile lists. Leave home simple nav alone."""
    if "nav-home-simple" in page or "site-header-home" in page:
        return page

    page = _replace_nav_item_mega(page, "Compare", render_compare_mega(cats, prefix))
    page = _replace_nav_item_mega(page, "Reviews", render_reviews_mega(cats, prefix))
    page = _COMPARE_MOBILE_RE.sub(render_compare_mobile(cats, prefix), page, count=1)
    page = _REVIEWS_MOBILE_RE.sub(render_reviews_mobile(cats, prefix), page, count=1)
    return page


def rewrite_footer(page: str, cats: list[dict[str, Any]], prefix: str) -> str:
    col = render_footer_cats(cats, prefix)
    if _EXPLORE_COL_RE.search(page):
        return _EXPLORE_COL_RE.sub(col, page, count=1)
    return page


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
    m = re.search(r'(<div class="home-tile-grid"[^>]*>)(.*?)(</div>\s*<button type="button" class="home-show-more")', page, re.S)
    if not m:
        return page
    slugs = set(cats_by_slug)
    tiles = split_home_tiles(m.group(2))
    if not tiles:
        return page

    decorated = []
    for idx, tile in enumerate(tiles):
        slug = tile_slug(tile, slugs)
        cat = cats_by_slug.get(slug or "")
        pin = 0 if _is_extended(cat) else 1
        decorated.append((pin, idx, slug, tile))
    decorated.sort(key=lambda row: (row[0], row[1]))

    out_tiles = []
    for i, (_pin, _idx, _slug, tile) in enumerate(decorated):
        out_tiles.append(set_tile_is_more(tile, i >= visible))
    rebuilt = m.group(1) + "\n        " + "".join(out_tiles) + "\n      " + m.group(3)
    return page[: m.start()] + rebuilt + page[m.end() :]


HUB_BLOCK = (
    '<p class="landing-related-cluster hub-reciprocity">'
    "<strong>Related:</strong> "
    '<a href="../">Category overview</a>'
    " · "
    '<a href="../">Full guide</a>'
    " · "
    '<a href="{compare}">Comparison chart</a>'
    "</p>"
)


def ensure_hub_reciprocity(page: str, kind: str) -> str:
    """Inbound path from comparison/ and reviews/ hubs back to /{slug}/."""
    compare = "../comparison/" if kind == "reviews" else "./"
    block = HUB_BLOCK.format(compare=compare)

    if 'class="landing-related-cluster hub-reciprocity"' not in page:
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
