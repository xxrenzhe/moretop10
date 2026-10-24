#!/usr/bin/env python3
"""Footer Categories: 3 CSS columns + widened 4-track grid on desktop.

Bake-time only (no network, no deploy). Desktop = min-width 720px.

Tracks are Brand | Categories | Company | Legal. Categories must be the
widest track so the 3-column cats list is not squeezed into 1fr.

Blog and Sitemap belong under Company (after Contact), not Categories.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = SITE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chrome import NAV_CSS, render_footer_cats, render_footer_company, rewrite_footer  # noqa: E402
from site_config import ALL_CATS, EDITORIAL_CLUSTERS  # noqa: E402

# Brand | wide Categories | Company | Legal — same recipe in site.css + NAV_CSS.
WIDENED_4TRACK = "1.4fr 2.2fr 0.85fr 0.85fr"
STALE_5TRACK = "1.4fr 1fr 1.1fr 0.9fr 0.8fr"

DESKTOP_3COL = re.compile(
    r"@media\s*\(\s*min-width:\s*720px\s*\)\s*\{.*?"
    r"\.footer-col-cats(?:\s*,\s*\.footer-col-categories)?\s+ul.*?columns\s*:\s*3",
    re.S,
)
DESKTOP_GRID = re.compile(
    r"@media\s*\(\s*min-width:\s*720px\s*\)\s*\{.*?"
    r"\.footer-grid\s*\{\s*grid-template-columns\s*:\s*([^;}]+)",
    re.S,
)
NAV_BLOCK = re.compile(r'<style id="landing-hub-nav">.*?</style>', re.S)
FR_TRACK = re.compile(r"([\d.]+)fr")
FOOTER_CHUNK = re.compile(r"<footer\b.*?</footer>", re.S)
CATS_COL = re.compile(
    r'<div class="footer-col(?: footer-col-cats| footer-col-categories)?">\s*'
    r"<h2>(?:Explore|Categories)</h2>\s*<ul>(.*?)</ul>",
    re.S,
)
COMPANY_COL = re.compile(
    r'<div class="footer-col(?: footer-col-company)?">\s*'
    r"<h2>Company</h2>\s*<ul>(.*?)</ul>",
    re.S,
)
BLOG_LI = re.compile(r'<li><a href="[^"]*blog/">Blog</a></li>')
SITEMAP_LI = re.compile(r'<li><a href="[^"]*sitemap/">Sitemap</a></li>')
CONTACT_THEN_BLOG_SITEMAP = re.compile(
    r'<li><a href="[^"]*contact/">Contact</a></li>\s*'
    r'<li><a href="[^"]*blog/">Blog</a></li>\s*'
    r'<li><a href="[^"]*sitemap/">Sitemap</a></li>',
    re.S,
)


def _has_3col(css: str) -> bool:
    return bool(DESKTOP_3COL.search(css))


def _desktop_tracks(css: str) -> list[float] | None:
    m = DESKTOP_GRID.search(css)
    if not m:
        return None
    raw = m.group(1).strip()
    tracks = [float(x) for x in FR_TRACK.findall(raw)]
    return tracks or None


def _has_widened_4track(css: str) -> bool:
    if STALE_5TRACK in css:
        return False
    if WIDENED_4TRACK in css:
        return True
    tracks = _desktop_tracks(css)
    if not tracks or len(tracks) != 4:
        return False
    brand, cats, company, legal = tracks
    return cats > brand and cats > company and cats > legal


def _footer(html: str) -> str:
    match = FOOTER_CHUNK.search(html)
    return match.group(0) if match else ""


def _placement_errors(label: str, html: str) -> list[str]:
    footer = _footer(html)
    if not footer:
        return [f"{label} missing <footer>"]
    cats = CATS_COL.search(footer)
    company = COMPANY_COL.search(footer)
    errors: list[str] = []
    if not cats:
        errors.append(f"{label} missing footer Categories column")
    else:
        inner = cats.group(1)
        if BLOG_LI.search(inner):
            errors.append(f"{label} Categories still lists Blog")
        if SITEMAP_LI.search(inner):
            errors.append(f"{label} Categories still lists Sitemap")
    if not company:
        errors.append(f"{label} missing footer Company column")
    else:
        inner = company.group(1)
        if not BLOG_LI.search(inner):
            errors.append(f"{label} Company missing Blog")
        if not SITEMAP_LI.search(inner):
            errors.append(f"{label} Company missing Sitemap")
        if not CONTACT_THEN_BLOG_SITEMAP.search(inner):
            errors.append(f"{label} Company order must be Contact, then Blog, then Sitemap")
    return errors


def _generator_errors() -> list[str]:
    errors: list[str] = []
    cats_html = render_footer_cats(ALL_CATS, "", editorial=EDITORIAL_CLUSTERS)
    if BLOG_LI.search(cats_html) or SITEMAP_LI.search(cats_html):
        errors.append("render_footer_cats still appends Blog/Sitemap")
    company_html = render_footer_company("")
    if not CONTACT_THEN_BLOG_SITEMAP.search(company_html):
        errors.append("render_footer_company missing Contact → Blog → Sitemap")
    sample = (
        '<footer class="site-footer">'
        '<div class="footer-col footer-col-cats"><h2>Categories</h2>'
        "<ul>"
        '<li><a href="blog/">Blog</a></li>'
        '<li><a href="sitemap/">Sitemap</a></li>'
        "</ul></div>"
        '<div class="footer-col"><h2>Company</h2><ul>'
        '<li><a href="about-us/">About Us</a></li>'
        '<li><a href="authors/">Editors</a></li>'
        '<li><a href="partner-with-us/">Partner With Us</a></li>'
        '<li><a href="contact/">Contact</a></li>'
        "</ul></div></footer>"
    )
    errors.extend(_placement_errors("rewrite_footer unit", rewrite_footer(sample, ALL_CATS, "")))
    return errors


def sample_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    errors: list[str] = []
    errors.extend(_generator_errors())

    if not _has_3col(NAV_CSS):
        errors.append("chrome.py NAV_CSS missing desktop columns:3 for Categories")
    if not _has_widened_4track(NAV_CSS):
        errors.append(
            "chrome.py NAV_CSS missing desktop 4-track widened-cats "
            f"({WIDENED_4TRACK}); stale 5-track is not allowed"
        )
    if STALE_5TRACK in NAV_CSS:
        errors.append("chrome.py NAV_CSS still has mismatched 5-track footer-grid")

    site_css = (site / "assets/css/site.css").read_text(encoding="utf-8")
    if not _has_3col(site_css):
        errors.append("site.css missing desktop columns:3 for Categories")
    if not _has_widened_4track(site_css):
        errors.append(
            f"site.css missing desktop 4-track widened-cats ({WIDENED_4TRACK})"
        )

    home = (site / "index.html").read_text(encoding="utf-8")
    if 'id="landing-hub-nav"' in home:
        if not _has_3col(home):
            errors.append("homepage inlines landing-hub-nav without desktop columns:3")
        if not _has_widened_4track(home):
            errors.append("homepage inlines landing-hub-nav without widened 4-track")
    if "footer-col-cats" not in home and "footer-col-categories" not in home:
        errors.append("homepage missing Categories footer column")
    errors.extend(_placement_errors("homepage", home))

    hub = site / "robot-vacuums" / "index.html"
    if not hub.is_file():
        errors.append("missing hub site/robot-vacuums/index.html")
    else:
        text = hub.read_text(encoding="utf-8")
        block = NAV_BLOCK.search(text)
        if not block:
            errors.append("robot-vacuums missing landing-hub-nav")
        else:
            if not _has_3col(block.group(0)):
                errors.append("robot-vacuums landing-hub-nav missing desktop columns:3")
            if not _has_widened_4track(block.group(0)):
                errors.append(
                    "robot-vacuums landing-hub-nav missing desktop 4-track widened-cats"
                )
        errors.extend(_placement_errors("robot-vacuums", text))

    legal = site / "privacy-policy" / "index.html"
    if not legal.is_file():
        errors.append("missing Legal page site/privacy-policy/index.html")
    else:
        errors.extend(_placement_errors("privacy-policy", legal.read_text(encoding="utf-8")))

    stale_3col: list[str] = []
    stale_grid: list[str] = []
    stale_place: list[str] = []
    for path in site.rglob("*.html"):
        rel_parts = set(path.relative_to(site).parts)
        if rel_parts & {".cache", "fixtures", "data", "assets"}:
            continue
        text = path.read_text(encoding="utf-8")
        try:
            rel = str(path.relative_to(ROOT))
        except ValueError:
            rel = str(path)
        if "<footer" in text:
            place = _placement_errors(rel, text)
            if place:
                stale_place.append(rel)
        if 'id="landing-hub-nav"' not in text:
            continue
        block = NAV_BLOCK.search(text)
        if not block or not _has_3col(block.group(0)):
            stale_3col.append(rel)
        if not block or not _has_widened_4track(block.group(0)):
            stale_grid.append(rel)
    if stale_3col:
        preview = ", ".join(stale_3col[:8])
        extra = f" (+{len(stale_3col) - 8} more)" if len(stale_3col) > 8 else ""
        errors.append(
            f"{len(stale_3col)} pages still lack desktop 3-col cats: {preview}{extra}"
        )
    if stale_grid:
        preview = ", ".join(stale_grid[:8])
        extra = f" (+{len(stale_grid) - 8} more)" if len(stale_grid) > 8 else ""
        errors.append(
            f"{len(stale_grid)} pages still lack desktop 4-track widened-cats: "
            f"{preview}{extra}"
        )
    if stale_place:
        preview = ", ".join(stale_place[:8])
        extra = f" (+{len(stale_place) - 8} more)" if len(stale_place) > 8 else ""
        errors.append(
            f"{len(stale_place)} pages still have Blog/Sitemap under Categories "
            f"(or missing under Company): {preview}{extra}"
        )

    return errors


def main() -> int:
    errors = sample_errors()
    if errors:
        print("footer_cats_columns_assert FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print("footer_cats_columns_assert OK")
    print(f"  desktop grid: {WIDENED_4TRACK} (Brand | wide Categories | Company | Legal)")
    print("  Categories ul: columns:1 mobile / columns:3 ≥720px")
    print("  Company links: About Us, Editors, Partner With Us, Contact, Blog, Sitemap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
