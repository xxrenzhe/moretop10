#!/usr/bin/env python3
"""Build /blog/ as a real editorial article index (local only).

Scans baked HTML under site/ and lists decision/guides/comparison editorial
pages — not category landings, comparison charts, reviews hubs, or SKU reviews.
Methodology (/blog/how-we-pick-products/) stays in the sidebar.

Ordering: newest first (page date, else sitemap lastmod). Ties break by
editorial kind, then title. See notes/blog-hub-article-index-2026-10-23.md.

Usage:
    python3 site/scripts/build_blog.py
"""

from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from seo_geo import (  # noqa: E402
    LIVE,
    ROBOTS_INDEX,
    _esc,
    allocate_unique_covers,
    breadcrumb_node,
    cover_to_thumb_src,
    org_node,
    resolve_page_cover,
    set_canonical,
    set_robots_meta,
    upsert_jsonld,
)
from site_config import CATS_BY_SLUG, EDITORIAL_CLUSTERS, load_site_config  # noqa: E402

BLOG_TITLE = "Articles"
BLOG_DESC = (
    "Editor guides, versus notes, alternatives, and how-to articles. "
    "Ranked Top 10 shortlists live on each category hub."
)
BLOG_CANONICAL = f"{LIVE}/blog/"
PREFIX = "../"

# Company / legal / infra roots — never article rows.
SKIP_TOP = frozenset(
    {
        "about-us",
        "authors",
        "contact",
        "partner-with-us",
        "privacy-policy",
        "terms-of-use",
        "cookie",
        "cookie-policy",
        "sitemap",
        "search",
        "assets",
        "data",
        "scripts",
        "instances",
        ".well-known",
        ".cache",
        "fixtures",
    }
)

KIND_LABELS = {
    "how-to": "How-to",
    "guide": "Guide",
    "versus": "Versus",
    "alternatives": "Alternatives",
    "best-of": "Best-of",
    "top-reads": "Top reads",
    "article": "Article",
}

# When dates tie, prefer decision surfaces over indexes.
KIND_RANK = {
    "how-to": 0,
    "guide": 1,
    "versus": 2,
    "alternatives": 3,
    "best-of": 4,
    "top-reads": 5,
    "article": 6,
}

METHODOLOGY_REL = "blog/how-we-pick-products/index.html"

_H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)
_META_DESC_RE = re.compile(
    r'<meta\s+name="description"\s+content="([^"]*)"', re.I
)
_TAG_RE = re.compile(r"<[^>]+>")
_DATE_RES = (
    re.compile(r"Last Updated:\s*(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"Last updated\s+(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r'<time\b[^>]*\bdatetime="(\d{4}-\d{2}-\d{2})', re.I),
    re.compile(r'class="author-post-date"[^>]*>(\d{4}-\d{2}-\d{2})', re.I),
    re.compile(
        r'<meta\s+(?:property|name)="article:(?:modified|published)_time"\s+content="(\d{4}-\d{2}-\d{2})',
        re.I,
    ),
)
_SITEMAP_URL_RE = re.compile(
    r"<url>\s*<loc>([^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?",
    re.I | re.S,
)


def classify_editorial(site_rel: str) -> tuple[str, str] | None:
    """Return (kind, category_slug) for an editorial article, else None.

    Include: /tv/* cluster; category how-to / VS / alternatives / best-of /
    top-reads; /blog/{slug}/ essays. Exclude: home, landings, comparison
    charts, reviews hubs, SKU reviews, methodology, company/legal, match
    demo, and unpatterned niche/scene pages (those land on other PRs).
    """
    rel = site_rel.replace("\\", "/").strip("/")
    if not rel.endswith("index.html"):
        return None
    parts = [p for p in rel.split("/") if p]
    if not parts or parts == ["index.html"]:
        return None
    top = parts[0]
    if top in SKIP_TOP or top == "robot-vacuums-match":
        return None
    if "reviews" in parts or "comparison" in parts:
        return None
    if top == "blog":
        if parts == ["blog", "index.html"]:
            return None
        if rel == METHODOLOGY_REL:
            return None
        if len(parts) == 3 and parts[2] == "index.html":
            return ("article", "blog")
        return None
    if top == "tv":
        if parts == ["tv", "index.html"]:
            return ("guide", "tv")
        if len(parts) == 3 and parts[2] == "index.html":
            kind = kind_from_slug(parts[1]) or _tv_kind_fallback(parts[1])
            return (kind, "tv")
        return None
    if parts == [top, "index.html"]:
        return None
    if len(parts) == 3 and parts[2] == "index.html":
        kind = kind_from_slug(parts[1])
        if kind is None:
            return None
        return (kind, top)
    return None


def kind_from_slug(slug: str) -> str | None:
    s = (slug or "").lower()
    if not s:
        return None
    if s == "top-reads":
        return "top-reads"
    if "-vs-" in s or s.endswith("-vs") or s.startswith("vs-"):
        return "versus"
    if s.endswith("-alternatives") or "alternatives" in s:
        return "alternatives"
    if s.startswith("best-"):
        return "best-of"
    if s.startswith("how-to"):
        return "how-to"
    return None


def _tv_kind_fallback(slug: str) -> str:
    s = slug.lower()
    if s.startswith("adb-") or s.startswith("remove-") or "how-to" in s:
        return "how-to"
    return "guide"


def category_label(slug: str, cats_by_slug: dict[str, dict] | None = None) -> str:
    if slug == "tv":
        for cluster in EDITORIAL_CLUSTERS:
            if cluster.get("slug") == "tv":
                return cluster.get("short_name") or cluster.get("name") or "Smart TV ads"
        return "Smart TV ads"
    if slug == "blog":
        return "Articles"
    cats = cats_by_slug if cats_by_slug is not None else CATS_BY_SLUG
    cat = cats.get(slug) or {}
    return cat.get("short_name") or cat.get("name") or slug.replace("-", " ").title()


def site_rel_to_href(site_rel: str, prefix: str = PREFIX) -> str:
    p = site_rel.replace("\\", "/").strip("/")
    if p.endswith("index.html"):
        p = p[: -len("index.html")]
    p = p.strip("/")
    if not p:
        return prefix
    return f"{prefix}{p}/"


def _plain(text: str) -> str:
    return unescape(_TAG_RE.sub("", text or "")).strip()


def extract_title(html_text: str) -> str:
    m = _H1_RE.search(html_text)
    if m:
        title = _plain(m.group(1))
        if title:
            return title
    m = _TITLE_RE.search(html_text)
    if m:
        title = _plain(m.group(1))
        title = re.sub(r"\s*\|\s*MoreTop10\s*$", "", title).strip()
        if title:
            return title
    return ""


def extract_excerpt(html_text: str) -> str:
    m = _META_DESC_RE.search(html_text)
    if not m:
        return ""
    excerpt = unescape(m.group(1)).strip()
    excerpt = re.sub(r"\s+", " ", excerpt)
    if len(excerpt) > 220:
        cut = excerpt[:217].rsplit(" ", 1)[0]
        excerpt = (cut or excerpt[:217]).rstrip(" ,;:") + "…"
    return excerpt


def extract_page_date(html_text: str) -> str:
    for pat in _DATE_RES:
        m = pat.search(html_text)
        if m:
            return m.group(1)
    return ""


def sitemap_lastmods(site_root: Path) -> dict[str, str]:
    """Read-only lastmod map keyed by site_rel. Does not write sitemap.xml."""
    path = site_root / "sitemap.xml"
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    text = path.read_text(encoding="utf-8")
    prefix = LIVE.rstrip("/") + "/"
    for loc, lastmod in _SITEMAP_URL_RE.findall(text):
        loc = loc.strip()
        if not loc.startswith(prefix):
            continue
        rel = loc[len(prefix) :].strip("/")
        if not rel:
            continue
        site_rel = rel if rel.endswith(".html") else rel + "/index.html"
        date = (lastmod or "").strip()[:10]
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            out[site_rel] = date
    return out


def iter_index_html(site_root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in site_root.rglob("index.html"):
        try:
            rel = path.relative_to(site_root)
        except ValueError:
            continue
        if rel.parts and rel.parts[0] in SKIP_TOP:
            continue
        paths.append(path)
    return paths


def collect_blog_articles(
    site_root: Path,
    *,
    cats_by_slug: dict[str, dict] | None = None,
    lastmods: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Inventory editorial pages that exist as local HTML."""
    lastmods = lastmods if lastmods is not None else sitemap_lastmods(site_root)
    cats = cats_by_slug if cats_by_slug is not None else CATS_BY_SLUG
    articles: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in iter_index_html(site_root):
        site_rel = str(path.relative_to(site_root)).replace("\\", "/")
        classified = classify_editorial(site_rel)
        if classified is None or site_rel in seen:
            continue
        seen.add(site_rel)
        html_text = path.read_text(encoding="utf-8")
        title = extract_title(html_text)
        if not title:
            continue
        kind, cat_slug = classified
        date = extract_page_date(html_text) or lastmods.get(site_rel, "")
        articles.append(
            {
                "rel": site_rel,
                "href": site_rel_to_href(site_rel, PREFIX),
                "title": title,
                "excerpt": extract_excerpt(html_text),
                "date": date,
                "kind": kind,
                "kind_label": KIND_LABELS.get(kind, kind.replace("-", " ").title()),
                "category": cat_slug,
                "category_label": category_label(cat_slug, cats),
            }
        )
    return sort_articles(articles)


def sort_articles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Newest first; missing dates sink; then kind rank, then title."""
    return sorted(
        articles,
        key=lambda a: (
            0 if a.get("date") else 1,
            -(int((a.get("date") or "0000-00-00").replace("-", "") or 0)),
            KIND_RANK.get(a.get("kind") or "", 9),
            (a.get("title") or "").lower(),
        ),
    )


def render_feed_row(article: dict[str, Any], thumb_src: str = "") -> str:
    href = _esc(article["href"])
    title = _esc(article["title"])
    kicker = f"{article['kind_label']} · {article['category_label']}"
    excerpt = article.get("excerpt") or ""
    excerpt_html = (
        f'<p class="feed-excerpt">{_esc(excerpt)}</p>' if excerpt else ""
    )
    date = article.get("date") or ""
    date_html = f'<time class="feed-date" datetime="{_esc(date)}">{_esc(date)}</time>' if date else ""
    thumb = ""
    if thumb_src:
        thumb = (
            f'<a class="feed-thumb" href="{href}" tabindex="-1" aria-hidden="true">'
            f'<img src="{_esc(thumb_src)}" alt="" width="231" height="130" '
            f'loading="lazy" decoding="async"/>'
            f"</a>"
        )
    return (
        f'<article class="feed-row" data-blog-article data-kind="{_esc(article["kind"])}" '
        f'data-category="{_esc(article["category"])}">'
        f'<div class="feed-copy">'
        f'<p class="feed-kicker">{_esc(kicker)}</p>'
        f'<h2 class="feed-title"><a href="{href}">{title}</a></h2>'
        f"{excerpt_html}"
        f'<div class="author-post-meta">'
        f'<a class="author-read-more" href="{href}">Read More</a>'
        f"{date_html}"
        f"</div></div>{thumb}</article>"
    )


def render_blog_main(articles: list[dict[str, Any]], thumbs: dict[str, str]) -> str:
    rows = [render_feed_row(a, thumbs.get(a["rel"], "")) for a in articles]
    feed = "\n".join(rows)
    count = len(articles)
    return f"""<main class="legal-page blog-hub-page">
  <div class="container legal-layout blog-hub-layout">
    <header class="page-head about-head">
      <h1>Articles</h1>
      <p class="page-lede">{_esc(BLOG_DESC)}</p>
    </header>
    <div class="blog-hub-grid">
      <div class="blog-hub-feed">
        <p class="blog-hub-count">{count} editor articles</p>
        <div class="feed-list" data-blog-feed>
{feed}
        </div>
      </div>
      <aside class="blog-hub-side" aria-label="Methodology">
        <div class="must-reads-widget">
          <h3>How we work</h3>
          <ul>
            <li><a href="how-we-pick-products/">How we pick products</a></li>
            <li><a href="../about-us/">About Us</a></li>
            <li><a href="../authors/">Editors</a></li>
          </ul>
        </div>
        <p class="blog-hub-reviews-note">Individual product reviews stay on each category <a href="../robot-vacuums/reviews/">Reviews</a> hub.</p>
      </aside>
    </div>
  </div>
</main>
"""


def _chrome_html(site_root: Path) -> str:
    about = site_root / "about-us" / "index.html"
    if about.is_file():
        return about.read_text(encoding="utf-8")
    existing = site_root / "blog" / "index.html"
    if existing.is_file():
        return existing.read_text(encoding="utf-8")
    raise FileNotFoundError("build_blog needs about-us/ or blog/ chrome")


def render_blog_hub(
    site_root: Path,
    *,
    articles: list[dict[str, Any]] | None = None,
) -> str:
    articles = list(articles if articles is not None else collect_blog_articles(site_root))
    covers, _missing = allocate_unique_covers(site_root, [a["rel"] for a in articles])
    thumbs: dict[str, str] = {}
    for a in articles:
        cover = covers.get(a["rel"], "")
        if not cover:
            target = site_root / a["rel"]
            if target.is_file():
                cover = resolve_page_cover(target.read_text(encoding="utf-8"), a["rel"])
        thumb = cover_to_thumb_src(cover, PREFIX)
        if thumb:
            thumbs[a["rel"]] = thumb
    main = render_blog_main(articles, thumbs)
    html_text = _chrome_html(site_root)
    html_text = re.sub(r"<main\b.*?</main>", main, html_text, count=1, flags=re.S)
    html_text = re.sub(
        r"<title>.*?</title>",
        f"<title>{BLOG_TITLE} | MoreTop10</title>",
        html_text,
        count=1,
        flags=re.S,
    )
    html_text = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{_esc(BLOG_DESC)}"',
        html_text,
        count=1,
    )
    html_text = re.sub(
        r'<meta property="og:title" content="[^"]*"',
        f'<meta property="og:title" content="{BLOG_TITLE} | MoreTop10"',
        html_text,
    )
    html_text = re.sub(
        r'<meta property="og:description" content="[^"]*"',
        f'<meta property="og:description" content="{_esc(BLOG_DESC)}"',
        html_text,
    )
    html_text = re.sub(
        r'<meta property="og:url" content="[^"]*"',
        f'<meta property="og:url" content="{BLOG_CANONICAL}"',
        html_text,
    )
    html_text = re.sub(
        r'<meta name="twitter:title" content="[^"]*"',
        f'<meta name="twitter:title" content="{BLOG_TITLE} | MoreTop10"',
        html_text,
    )
    html_text = re.sub(
        r'<meta name="twitter:description" content="[^"]*"',
        f'<meta name="twitter:description" content="{_esc(BLOG_DESC)}"',
        html_text,
    )
    html_text = re.sub(
        r'<meta name="twitter:url" content="[^"]*"',
        f'<meta name="twitter:url" content="{BLOG_CANONICAL}"',
        html_text,
    )
    html_text = set_canonical(html_text, BLOG_CANONICAL)
    html_text = set_robots_meta(html_text, ROBOTS_INDEX)
    items = [
        {
            "@type": "ListItem",
            "position": i,
            "url": f"{LIVE}/{a['rel'][: -len('index.html')]}"
            if a["rel"].endswith("index.html")
            else f"{LIVE}/{a['rel']}",
            "name": a["title"],
        }
        for i, a in enumerate(articles, start=1)
    ]
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "@id": f"{BLOG_CANONICAL}#page",
        "name": f"{BLOG_TITLE} | MoreTop10",
        "url": BLOG_CANONICAL,
        "description": BLOG_DESC,
        "mainEntity": {
            "@type": "ItemList",
            "name": "MoreTop10 articles",
            "numberOfItems": len(articles),
            "itemListElement": items,
        },
    }
    html_text = upsert_jsonld(
        html_text,
        [
            org_node(),
            breadcrumb_node([("Home", f"{LIVE}/"), ("Articles", BLOG_CANONICAL)]),
            collection,
        ],
        {"WebPage", "CollectionPage", "ItemList", "BreadcrumbList"},
    )
    return html_text


def write_blog_hub(site_root: Path | None = None) -> int:
    """Write site/blog/index.html. Returns the article count."""
    site_root = site_root or SITE
    articles = collect_blog_articles(site_root)
    html_text = render_blog_hub(site_root, articles=articles)
    dest = site_root / "blog" / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html_text, encoding="utf-8")
    return len(articles)


def main() -> None:
    load_site_config()
    n = write_blog_hub(SITE)
    print(f"wrote site/blog/index.html ({n} articles)")


if __name__ == "__main__":
    main()
