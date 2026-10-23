#!/usr/bin/env python3
"""Bake helper: landing-hero shells must receive pages-landing.css."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from chrome import (  # noqa: E402
    apply_editorial_page_class,
    ensure_pages_landing_css,
    rel_prefix,
)


SHELL = """<!DOCTYPE html>
<html><head>
<link rel="stylesheet" href="../../assets/css/tokens.css"/>
<link rel="stylesheet" href="../../assets/css/site.css"/>
</head>
<body>
<main class="editorial-page">
  <header class="landing-hero">
    <div class="lifestyle-block has-photo">
      <img class="lifestyle-photo" src="cover.jpg" alt=""/>
    </div>
  </header>
</main>
</body></html>
"""


def main() -> int:
    errors: list[str] = []

    prefix = rel_prefix("kids-bikes/royalbaby-ez-vs-dual-handbrake/index.html")
    if prefix != "../../":
        errors.append(f"rel_prefix vs page got {prefix!r}")

    injected = ensure_pages_landing_css(SHELL, prefix)
    href = f'{prefix}assets/css/pages-landing.css'
    if href not in injected:
        errors.append("ensure_pages_landing_css did not inject pages-landing.css")
    if injected.find("site.css") > injected.find("pages-landing.css"):
        errors.append("pages-landing.css must follow site.css")

    already = injected.replace(href, "../assets/css/pages-landing.css", 1)
    fixed = ensure_pages_landing_css(already, prefix)
    if href not in fixed:
        errors.append("ensure_pages_landing_css did not rewrite a wrong-depth href")

    no_hero = SHELL.replace("landing-hero", "page-head").replace(
        "lifestyle-photo", "other-photo"
    )
    skipped = ensure_pages_landing_css(no_hero, prefix)
    if "pages-landing.css" in skipped:
        errors.append("ensure_pages_landing_css injected CSS without a hero")

    vs = apply_editorial_page_class(SHELL, "kids-bikes/royalbaby-ez-vs-dual-handbrake/index.html")
    if 'class="editorial-page vs-page"' not in vs:
        errors.append(f"vs-page class missing: {vs[vs.find('<main'):vs.find('>')+1]}")

    alts = apply_editorial_page_class(
        SHELL, "espresso-machines/premium-espresso-machine-alternatives/index.html"
    )
    if 'class="editorial-page alts-page"' not in alts:
        errors.append("alts-page class missing")

    best = apply_editorial_page_class(
        SHELL, "humidifiers/best-humidifiers-for-bedrooms/index.html"
    )
    if 'class="editorial-page bestof-page"' not in best:
        errors.append("bestof-page class missing")

    howto = apply_editorial_page_class(
        SHELL, "kids-bikes/how-to-choose-a-kids-bike/index.html"
    )
    if 'class="editorial-page"' not in howto or "vs-page" in howto or "alts-page" in howto:
        errors.append("howto should keep editorial-page only")

    hub = apply_editorial_page_class(
        '<main class="landing-page">', "kids-bikes/index.html"
    )
    if hub != '<main class="landing-page">':
        errors.append("category hub landing-page class must stay")

    if errors:
        print("landing_css_unit FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print("landing_css_unit OK inject+rewrite+page-class")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
