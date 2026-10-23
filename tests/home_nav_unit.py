#!/usr/bin/env python3
"""Home header uses the shared hub mega nav (Categories / Compare / Reviews / Articles)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from chrome import (  # noqa: E402
    inject_nav_css,
    published_nav_cats,
    rewrite_compare_cta,
    rewrite_nav,
)
from site_config import ALL_CATS  # noqa: E402

HOME_SIMPLE = """<!DOCTYPE html><html><head></head><body>
<header class="site-header site-header-home">
  <div class="container header-inner">
    <a class="logo-link" href="/" aria-label="MoreTop10 home">
      <img class="logo-mark" src="assets/img/symbol-color.svg" width="32" height="32" alt=""/>
    </a>
    <nav class="nav-desktop nav-home-simple" aria-label="Primary">
      <a class="nav-link" href="about-us/">About us</a>
      <a class="nav-link" href="partner-with-us/">Partner With Us</a>
    </nav>
    <button class="burger" type="button" data-burger aria-expanded="false" aria-label="Open menu"><span></span><span></span><span></span></button>
  </div>
  <nav class="mobile-nav" data-mobile-nav aria-label="Mobile">
    <a href="about-us/">About us</a>
    <a href="partner-with-us/">Partner With Us</a>
    <a href="robot-vacuums/comparison/">Compare robot vacuums</a>
    <p class="mobile-disclosure">Advertising Disclosure: we may earn a commission when you buy via Check price links.</p>
  </nav>
</header>
<main class="home-page"></main>
<footer><a href="partner-with-us/">Partner With Us</a></footer>
</body></html>"""

HUB = """<!DOCTYPE html><html><head></head><body>
<header class="site-header">
  <div class="container header-inner">
    <nav class="nav-desktop" aria-label="Primary">
      <div class="nav-item"><button type="button" class="nav-trigger">Categories</button><div class="mega" role="menu"><a href="../robot-vacuums/">Robot Vacuums &amp; Mops</a></div></div>
      <div class="nav-item"><button type="button" class="nav-trigger">Compare</button><div class="mega" role="menu"><a href="../robot-vacuums/comparison/">old</a></div></div>
      <div class="nav-item"><button type="button" class="nav-trigger">Reviews</button><div class="mega" role="menu"><a href="../robot-vacuums/reviews/">old</a></div></div>
      <a class="nav-link" href="../blog/">Articles</a>
      </nav>
    <div class="header-cta"><a class="nav-link nav-cta-soft" href="../robot-vacuums/comparison/">Compare picks <span aria-hidden="true">→</span></a></div>
  </div>
  <nav class="mobile-nav" data-mobile-nav aria-label="Mobile">
    <details open><summary>Categories</summary><a href="../robot-vacuums/">Robot Vacuums &amp; Mops</a></details>
    <details open><summary>Compare</summary><a href="../robot-vacuums/comparison/">old</a></details>
    <details><summary>Reviews</summary><a href="../robot-vacuums/reviews/">old</a></details>
    <a href="../blog/">Articles</a>
  </nav>
</header>
<main></main>
</body></html>"""


def _header(page: str) -> str:
    return page.split("<main", 1)[0]


def main() -> None:
    errors: list[str] = []
    cats = ALL_CATS
    pub = published_nav_cats(cats)
    pub_slugs = {c["slug"] for c in pub}
    draft_slugs = {c["slug"] for c in cats if c["slug"] not in pub_slugs}

    home = rewrite_compare_cta(rewrite_nav(inject_nav_css(HOME_SIMPLE), cats, ""), "", None, "home")
    head = _header(home)
    if "nav-home-simple" in head or "site-header-home" in head:
        errors.append("home still has simple-header chrome")
    if 'id="landing-hub-nav"' not in home:
        errors.append("home missing shared landing-hub-nav CSS")
    for label in ("Categories", "Compare", "Reviews"):
        if f'class="nav-trigger">{label}</button>' not in head:
            errors.append(f"home missing {label} trigger")
    if 'href="blog/">Articles</a>' not in head:
        errors.append("home missing Articles → blog/")
    if 'class="nav-link" href="about-us/"' in head:
        errors.append("home header still has About us")
    if 'class="nav-link" href="partner-with-us/"' in head:
        errors.append("home header still has Partner With Us")
    if ">Partner With Us<" not in home.split("<footer", 1)[-1]:
        errors.append("footer lost Partner With Us")
    if 'href="kids-bikes/"' not in head:
        errors.append("home Categories missing kids-bikes")
    if 'href="kids-bikes/comparison/"' not in head:
        errors.append("home Compare missing kids-bikes comparison")
    if 'href="/" aria-label="MoreTop10 home"' not in home:
        errors.append("home logo href was rewritten away from /")
    if 'href="robot-vacuums/comparison/"' not in head or "Compare picks" not in head:
        errors.append("home missing Compare picks CTA")

    # Categories mega stays on the published subset (Live hub pattern).
    cat_mega_start = head.find('class="nav-trigger">Categories</button>')
    cat_mega = head[cat_mega_start : head.find('class="nav-trigger">Compare</button>')]
    for slug in draft_slugs:
        if f'href="{slug}/"' in cat_mega:
            errors.append(f"home Categories mega leaked draft slug {slug}")
            break

    # Hub pages keep the same generators (no home-only structure).
    hub = rewrite_nav(HUB, cats, "../")
    hub_head = _header(hub)
    if 'href="../kids-bikes/"' not in hub_head:
        errors.append("hub Categories rewrite missing kids-bikes")
    if 'href="../kids-bikes/comparison/"' not in hub_head:
        errors.append("hub Compare rewrite missing kids-bikes comparison")
    if 'href="../blog/">Articles</a>' not in hub_head:
        errors.append("hub lost Articles")

    if errors:
        print("home_nav_unit FAIL")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)
    print("home_nav_unit OK")


if __name__ == "__main__":
    main()
