#!/usr/bin/env python3
"""Best sidebar is copy/text only — no packshot <img> in the aside.

Scope is the Best widget only. Landing pick cards, comparison tables, and
Jump-to stay unchanged. Bake ≠ Deploy.
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

ASIDE_RE = re.compile(r'<aside class="best-widget">.*?</aside>', re.S)
IMG_IN_ASIDE = re.compile(r"<img\b|best-widget-img", re.I)


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
    if "<img" in html or "best-widget-img" in html:
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
        '<div class="landing-pick-cta-bar">'
        '<img class="landing-pick-logo landing-packshot" src="keep.jpg" alt="keep"/>'
        "</div>"
        '<nav class="jump-toc"><ul class="toc-items"><li><a href="#pick-1">1. Waykar</a></li></ul></nav>'
    )
    out = rewrite_best_widget(sample)
    aside = ASIDE_RE.search(out)
    if aside is None:
        errors.append("rewrite_best_widget dropped the Best aside")
        return errors
    chunk = aside.group(0)
    if IMG_IN_ASIDE.search(chunk):
        errors.append("rewrite_best_widget left a packshot in the aside")
    if "Waykar 80 Pints" not in chunk or "best-widget-arrow" not in chunk:
        errors.append("rewrite_best_widget dropped name or arrow")
    if "Compare All" not in chunk:
        errors.append("rewrite_best_widget dropped Compare All")
    if 'href="https://pboost.me/C5piq8k2?uid=fromsll"' not in chunk:
        errors.append("rewrite_best_widget dropped CTA href")
    if 'rel="sponsored noopener noreferrer"' not in chunk:
        errors.append("rewrite_best_widget dropped sponsored rel")
    if "landing-pick-logo landing-packshot" not in out:
        errors.append("rewrite_best_widget stripped a landing pick packshot")
    if 'class="jump-toc"' not in out or "1. Waykar" not in out:
        errors.append("rewrite_best_widget touched Jump-to")
    return errors


def _baked_errors(site: Path) -> list[str]:
    errors: list[str] = []
    dehum = site / "dehumidifiers" / "index.html"
    if not dehum.is_file():
        errors.append("missing sample hub site/dehumidifiers/index.html")
        return errors

    dehum_html = dehum.read_text(encoding="utf-8")
    aside = ASIDE_RE.search(dehum_html)
    if aside is None:
        errors.append("dehumidifiers landing missing Best aside")
    else:
        chunk = aside.group(0)
        if IMG_IN_ASIDE.search(chunk):
            errors.append("dehumidifiers Best aside still has packshot <img>")
        if "best-widget-name" not in chunk:
            errors.append("dehumidifiers Best aside missing names")
        if "best-widget-arrow" not in chunk:
            errors.append("dehumidifiers Best aside missing arrows")
        if "Compare All" not in chunk:
            errors.append("dehumidifiers Best aside missing Compare All")
        if "pboost.me" not in chunk or "sponsored" not in chunk:
            errors.append("dehumidifiers Best aside lost CTA href/sponsored attrs")

    if "landing-pick-logo" not in dehum_html and "landing-packshot" not in dehum_html:
        errors.append("dehumidifiers landing pick packshots were stripped")
    if 'class="jump-toc"' not in dehum_html:
        errors.append("dehumidifiers Jump-to was stripped")

    stale: list[str] = []
    missing_chrome: list[str] = []
    for path in sorted(site.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        if 'class="best-widget"' not in text:
            continue
        block = ASIDE_RE.search(text)
        if block is None:
            continue
        chunk = block.group(0)
        rel = str(path.relative_to(site))
        if IMG_IN_ASIDE.search(chunk):
            stale.append(rel)
        if (
            "best-widget-name" not in chunk
            or "best-widget-arrow" not in chunk
            or "Compare All" not in chunk
        ):
            missing_chrome.append(rel)
    if stale:
        preview = ", ".join(stale[:8])
        extra = f" (+{len(stale) - 8} more)" if len(stale) > 8 else ""
        errors.append(f"{len(stale)} Best widgets still have packshot <img>: {preview}{extra}")
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
    print("  bake: Best aside text-only; pick cards / Jump-to unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
