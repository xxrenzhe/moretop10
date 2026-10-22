#!/usr/bin/env python3
"""Affiliate disclosure chrome: no nav control, honest top-strip copy."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = SITE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chrome import (  # noqa: E402
    MISLEADING_STRIP,
    TOP_STRIP_COPY,
    TOP_STRIP_PANEL,
    rewrite_disclosure,
)

NAV_BLOCK = """<nav class="nav-desktop" aria-label="Primary">
      <a class="nav-link" href="../blog/">Articles</a>
      <div class="ad-disclosure header-disclosure" data-disclosure>
        <button type="button" class="ad-disclosure-btn nav-link-btn" data-disclosure-btn>Advertising Disclosure</button>
        <div class="ad-disclosure-panel" data-disclosure-panel hidden>
          <p>MoreTop10 is an affiliate comparison site. When you click Check price and buy, we may earn a commission at no extra cost to you. We are not the seller.</p>
        </div>
      </div>
    </nav>"""

STRIP_PAGE = f"""<!DOCTYPE html><html><body>
<div class="top-affiliate-bar" data-top-bar>
  <div class="container top-affiliate-inner">
    <p>{MISLEADING_STRIP}
      <button type="button" class="ad-disclosure-btn top-bar-disc-btn" data-top-disc-btn>Advertising Disclosure</button>
    </p>
    <div class="top-affiliate-panel" data-top-disc-panel hidden>
      <p>{TOP_STRIP_PANEL}</p>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="container header-inner">
    {NAV_BLOCK}
    <div class="header-cta"><a class="nav-link nav-cta-soft" href="../hair-dryers/comparison/">Compare picks <span aria-hidden="true">→</span></a></div>
  </div>
  <nav class="mobile-nav" data-mobile-nav aria-label="Mobile">
    <a href="../blog/">Articles</a>
    <p class="mobile-disclosure">Advertising Disclosure: we may earn a commission when you buy via Check price links.</p>
  </nav>
</header>
<main></main>
</body></html>"""

CMP_PAGE = f"""<!DOCTYPE html><html><body>
<header class="site-header">
  <div class="container header-inner">
    {NAV_BLOCK}
  </div>
  <nav class="mobile-nav" data-mobile-nav aria-label="Mobile">
    <p class="mobile-disclosure">Advertising Disclosure: we may earn a commission when you buy via Check price links.</p>
  </nav>
</header>
<main class="comparison-page"></main>
</body></html>"""

SKIP_DIRS = {".cache", "fixtures", "data", "assets"}


def _unit() -> list[str]:
    errors: list[str] = []
    landing = rewrite_disclosure(STRIP_PAGE)
    if "header-disclosure" in landing:
        errors.append("unit landing still has nav Disclosure")
    if ">Articles</a>" not in landing:
        errors.append("unit landing lost Articles")
    if "Compare picks" not in landing:
        errors.append("unit landing lost Compare picks")
    if TOP_STRIP_COPY not in landing:
        errors.append("unit landing missing honest strip")
    if MISLEADING_STRIP in landing:
        errors.append("unit landing kept misleading strip")
    if TOP_STRIP_PANEL not in landing:
        errors.append("unit landing lost panel")
    if "mobile-disclosure" not in landing:
        errors.append("unit landing lost mobile disclosure")
    if landing.count("data-top-disc-btn") != 1:
        errors.append("unit landing should keep exactly one top-strip Disclosure button")

    cmp = rewrite_disclosure(CMP_PAGE)
    if "header-disclosure" in cmp:
        errors.append("unit comparison still has nav Disclosure")
    if 'class="top-affiliate-bar"' not in cmp:
        errors.append("unit comparison missing injected top strip")
    if TOP_STRIP_COPY not in cmp:
        errors.append("unit comparison missing honest strip")
    if TOP_STRIP_PANEL not in cmp:
        errors.append("unit comparison missing panel")
    if "mobile-disclosure" not in cmp:
        errors.append("unit comparison lost mobile disclosure")
    return errors


def _sitewide() -> list[str]:
    errors: list[str] = []
    stale_nav: list[str] = []
    stale_copy: list[str] = []
    missing_strip: list[str] = []
    for path in SITE.rglob("*.html"):
        if set(path.relative_to(SITE).parts) & SKIP_DIRS:
            continue
        text = path.read_text(encoding="utf-8")
        if "site-header" not in text and "top-affiliate-bar" not in text:
            continue
        rel = str(path.relative_to(ROOT))
        if "header-disclosure" in text:
            stale_nav.append(rel)
        if MISLEADING_STRIP in text or "which influences how listings are presented" in text:
            stale_copy.append(rel)
        if 'class="top-affiliate-bar"' not in text:
            missing_strip.append(rel)
        if TOP_STRIP_COPY not in text:
            stale_copy.append(rel)
    if stale_nav:
        preview = ", ".join(stale_nav[:6])
        extra = f" (+{len(stale_nav) - 6} more)" if len(stale_nav) > 6 else ""
        errors.append(f"{len(stale_nav)} pages still have nav Disclosure: {preview}{extra}")
    if stale_copy:
        preview = ", ".join(stale_copy[:6])
        extra = f" (+{len(stale_copy) - 6} more)" if len(stale_copy) > 6 else ""
        errors.append(f"{len(stale_copy)} pages missing honest strip copy: {preview}{extra}")
    if missing_strip:
        preview = ", ".join(missing_strip[:6])
        extra = f" (+{len(missing_strip) - 6} more)" if len(missing_strip) > 6 else ""
        errors.append(f"{len(missing_strip)} pages missing top strip: {preview}{extra}")
    return errors


def collect_errors() -> list[str]:
    return _unit() + _sitewide()


def main() -> int:
    errors = collect_errors()
    if errors:
        print("disclosure_chrome_assert FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print("disclosure_chrome_assert OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
