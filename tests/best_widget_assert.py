#!/usr/bin/env python3
"""Best / Editors' Picks rails are copy/text only — no product <img>.

Covers `.best-widget`, `.editors-picks-widget`, `.ed-reviews-sidebar`, and
comparison `.sidebar-promo` site-wide. Landing pick cards, comparison product
cards, and Jump-to stay unchanged. Bake ≠ Deploy.
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

from build import best_widget_html, rewrite_best_widget  # noqa: E402

BEST_ASIDE_RE = re.compile(r'<aside class="best-widget">.*?</aside>', re.S)
ED_REV_ASIDE_RE = re.compile(r'<aside class="ed-reviews-sidebar">.*?</aside>', re.S)
ED_PICKS_ASIDE_RE = re.compile(r'<aside class="editors-picks-widget">.*?</aside>', re.S)
PROMO_RE = re.compile(r'<div class="sidebar-promo">.*?</div>\s*</div>', re.S)
IMG_RE = re.compile(r"<img\b|best-widget-img|best-widget-packshot|ed-rev-packshot", re.I)
SAMPLE_CATS = (
    "dehumidifiers",
    "air-fryers",
    "robot-vacuums",
    "dash-cams",
    "hair-dryers",
)


def _emitter_errors() -> list[str]:
    errors: list[str] = []
    html = best_widget_html(
        "Best Dehumidifiers",
        [
            {
                "href": "https://pboost.me/C5piq8k2?uid=fromsll",
                "name": "Waykar 80 Pints 2025 Energy Star Dehumidifier",
            }
        ],
        "../dehumidifiers/comparison/",
    )
    if "<img" in html or "best-widget-img" in html or "best-widget-packshot" in html:
        errors.append("best_widget_html emitted a packshot <img>")
    if 'class="best-widget-name">Waykar 80 Pints 2025 Energy Star Dehumidifier<' not in html:
        errors.append("best_widget_html missing product name")
    if 'class="best-widget-arrow"' not in html or "→" not in html:
        errors.append("best_widget_html missing arrow")
    if "Compare All" not in html:
        errors.append("best_widget_html missing Compare All")
    if 'href="https://pboost.me/C5piq8k2?uid=fromsll"' not in html:
        errors.append("best_widget_html dropped CTA href")
    if 'rel="sponsored noopener noreferrer"' not in html:
        errors.append("best_widget_html dropped sponsored rel")
    return errors


def _rewrite_errors() -> list[str]:
    errors: list[str] = []
    sample = (
        '<aside class="best-widget">'
        '<a class="best-widget-row" href="https://pboost.me/C5piq8k2?uid=fromsll" '
        'rel="sponsored noopener noreferrer" target="_blank">'
        '<img class="best-widget-img best-widget-packshot" '
        'src="https://example.com/pack.jpg" alt="Waykar" width="40" height="40"/>'
        '<span class="best-widget-name">Waykar 80 Pints</span>'
        '<span class="best-widget-arrow" aria-hidden="true">→</span>'
        "</a>"
        '<p class="best-widget-more">'
        '<a class="btn btn-ghost btn-sm best-widget-compare" '
        'href="../dehumidifiers/comparison/">Compare All</a></p>'
        "</aside>"
        '<aside class="ed-reviews-sidebar">'
        '<div class="ed-rev-row">'
        '<img class="ed-rev-img ed-rev-packshot" src="keep-rev.jpg" alt="x"/>'
        '<div class="ed-rev-text"><strong>Waykar 80</strong>'
        '<a href="../reviews/waykar/">Read Review</a></div></div>'
        "</aside>"
        '<aside class="editors-picks-widget"><h3>Editor\'s Picks</h3>'
        '<ul class="ed-picks-list"><li><a href="../how-to/">How to choose</a></li></ul>'
        "</aside>"
        '<div class="sidebar-promo"><div class="sidebar-promo-inner">'
        '<img class="promo-img" src="promo.jpg" alt="promo"/>'
        '<strong class="sidebar-promo-name">Dreame</strong>'
        '<a class="btn" href="https://pboost.me/x" rel="sponsored noopener noreferrer" '
        'target="_blank">Check price</a>'
        "</div></div>"
        '<div class="landing-pick-cta-bar">'
        '<img class="landing-pick-logo landing-packshot" src="keep.jpg" alt="keep"/>'
        "</div>"
        '<article class="product-card">'
        '<img class="pc-logo pc-packshot" src="card.jpg" alt="card"/>'
        "</article>"
        '<nav class="jump-toc"><ul class="toc-items"><li><a href="#pick-1">1. Waykar</a></li></ul></nav>'
    )
    out = rewrite_best_widget(sample)
    best = BEST_ASIDE_RE.search(out)
    if best is None:
        errors.append("rewrite_best_widget dropped the Best aside")
        return errors
    if IMG_RE.search(best.group(0)):
        errors.append("rewrite_best_widget left a packshot in Best aside")
    if "Waykar 80 Pints" not in best.group(0) or "best-widget-arrow" not in best.group(0):
        errors.append("rewrite_best_widget dropped name or arrow")
    if "Compare All" not in best.group(0):
        errors.append("rewrite_best_widget dropped Compare All")
    if 'href="https://pboost.me/C5piq8k2?uid=fromsll"' not in best.group(0):
        errors.append("rewrite_best_widget dropped CTA href")

    ed = ED_REV_ASIDE_RE.search(out)
    if ed is None:
        errors.append("rewrite_best_widget dropped Editorial Reviews aside")
    elif IMG_RE.search(ed.group(0)):
        errors.append("rewrite_best_widget left ed-rev-packshot in Editorial Reviews")
    elif "Read Review" not in ed.group(0) or "Waykar 80" not in ed.group(0):
        errors.append("rewrite_best_widget dropped Editorial Reviews copy")

    picks = ED_PICKS_ASIDE_RE.search(out)
    if picks is None or "How to choose" not in picks.group(0):
        errors.append("rewrite_best_widget dropped Editor's Picks copy")

    promo = PROMO_RE.search(out)
    if promo is None:
        errors.append("rewrite_best_widget dropped comparison sidebar-promo")
    elif "<img" in promo.group(0) or "promo-img" in promo.group(0):
        errors.append("rewrite_best_widget left promo-img on comparison rail")
    elif "Check price" not in promo.group(0) or "pboost.me/x" not in promo.group(0):
        errors.append("rewrite_best_widget dropped sidebar-promo CTA")

    if "landing-pick-logo landing-packshot" not in out:
        errors.append("rewrite_best_widget stripped a landing pick packshot")
    if "pc-logo pc-packshot" not in out:
        errors.append("rewrite_best_widget stripped a comparison card packshot")
    if 'class="jump-toc"' not in out or "1. Waykar" not in out:
        errors.append("rewrite_best_widget touched Jump-to")
    return errors


def _chunk_has_img(chunk: str | None) -> bool:
    return bool(chunk and IMG_RE.search(chunk))


def _baked_errors(site: Path) -> list[str]:
    errors: list[str] = []
    for slug in SAMPLE_CATS:
        landing = site / slug / "index.html"
        if not landing.is_file():
            errors.append(f"missing sample hub site/{slug}/index.html")
            continue
        html = landing.read_text(encoding="utf-8")
        aside = BEST_ASIDE_RE.search(html)
        if aside is None:
            errors.append(f"{slug} landing missing Best aside")
        elif _chunk_has_img(aside.group(0)):
            errors.append(f"{slug} landing Best aside still has product <img>")
        elif "best-widget-name" not in aside.group(0) or "Compare All" not in aside.group(0):
            errors.append(f"{slug} landing Best aside missing name/Compare All")
        if "landing-packshot" not in html and "landing-pick-logo" not in html:
            errors.append(f"{slug} landing pick packshots were stripped")

        hub = site / slug / "reviews" / "index.html"
        if hub.is_file():
            hub_html = hub.read_text(encoding="utf-8")
            hub_aside = BEST_ASIDE_RE.search(hub_html)
            if hub_aside and _chunk_has_img(hub_aside.group(0)):
                errors.append(f"{slug} reviews hub Best aside still has product <img>")

        cmp = site / slug / "comparison" / "index.html"
        if cmp.is_file():
            cmp_html = cmp.read_text(encoding="utf-8")
            promo = PROMO_RE.search(cmp_html)
            if promo and ("<img" in promo.group(0) or "promo-img" in promo.group(0)):
                errors.append(f"{slug} comparison sidebar-promo still has promo-img")
            if "pc-packshot" not in cmp_html and "pc-logo" not in cmp_html:
                errors.append(f"{slug} comparison card packshots were stripped")

    stale_best: list[str] = []
    stale_ed: list[str] = []
    stale_picks: list[str] = []
    stale_promo: list[str] = []
    missing_chrome: list[str] = []
    for path in sorted(site.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(site))
        for regex, bucket, label in (
            (BEST_ASIDE_RE, stale_best, "Best"),
            (ED_REV_ASIDE_RE, stale_ed, "Editorial Reviews"),
            (ED_PICKS_ASIDE_RE, stale_picks, "Editor's Picks"),
        ):
            block = regex.search(text)
            if block and _chunk_has_img(block.group(0)):
                bucket.append(rel)
            if label == "Best" and block and (
                "best-widget-name" not in block.group(0)
                or "best-widget-arrow" not in block.group(0)
                or "Compare All" not in block.group(0)
            ):
                missing_chrome.append(rel)
        promo = PROMO_RE.search(text)
        if promo and ("<img" in promo.group(0) or "promo-img" in promo.group(0)):
            stale_promo.append(rel)

    for label, stale in (
        ("Best widgets", stale_best),
        ("Editorial Reviews rails", stale_ed),
        ("Editor's Picks rails", stale_picks),
        ("comparison sidebar-promo rails", stale_promo),
    ):
        if stale:
            preview = ", ".join(stale[:8])
            extra = f" (+{len(stale) - 8} more)" if len(stale) > 8 else ""
            errors.append(f"{len(stale)} {label} still have product <img>: {preview}{extra}")
    if missing_chrome:
        preview = ", ".join(missing_chrome[:8])
        extra = f" (+{len(missing_chrome) - 8} more)" if len(missing_chrome) > 8 else ""
        errors.append(
            f"{len(missing_chrome)} Best widgets missing name/arrow/Compare All: {preview}{extra}"
        )
    return errors


def sample_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    return _emitter_errors() + _rewrite_errors() + _baked_errors(site)


def main() -> int:
    errors = sample_errors(SITE)
    if errors:
        print("best_widget_assert FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print("best_widget_assert OK")
    print("  emitter: name + arrow + Compare All, no <img>")
    print("  bake: Best / Editors' Picks / Editorial Reviews / comparison promo text-only")
    print("  pick cards / comparison cards / Jump-to unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
