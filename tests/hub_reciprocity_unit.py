#!/usr/bin/env python3
"""Unit tests for comparison/reviews Related strip (no self-links)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from chrome import ensure_hub_reciprocity, render_hub_block, strip_cmp_hero_steps  # noqa: E402


def main() -> None:
    errors: list[str] = []

    cmp_block = render_hub_block("comparison")
    if 'href="../"' not in cmp_block or "Category overview" not in cmp_block:
        errors.append("comparison block missing Category overview → ../")
    if 'href="../reviews/"' not in cmp_block or "Full guide" not in cmp_block:
        errors.append("comparison block missing Full guide → ../reviews/")
    if "Comparison chart" in cmp_block or 'href="./"' in cmp_block:
        errors.append("comparison block still self-links Comparison chart")

    rev_block = render_hub_block("reviews")
    if 'href="../"' not in rev_block or "Category overview" not in rev_block:
        errors.append("reviews block missing Category overview → ../")
    if 'href="../comparison/"' not in rev_block or "Comparison chart" not in rev_block:
        errors.append("reviews block missing Comparison chart → ../comparison/")
    if "Full guide" in rev_block or 'href="../reviews/"' in rev_block:
        errors.append("reviews block still self-links Full guide")

    stale = (
        '<nav class="breadcrumb"><a href="../../">Home</a></nav>\n'
        '<p class="landing-related-cluster hub-reciprocity">'
        "<strong>Related:</strong> "
        '<a href="../">Category overview</a> · '
        '<a href="../">Full guide</a> · '
        '<a href="./">Comparison chart</a></p>'
    )
    rewritten = ensure_hub_reciprocity(stale, "comparison")
    if 'href="./"' in rewritten:
        errors.append("ensure_hub_reciprocity left comparison self-link")
    if rewritten.count("landing-related-cluster hub-reciprocity") != 1:
        errors.append("ensure_hub_reciprocity duplicated the Related cluster")
    if 'href="../reviews/"' not in rewritten:
        errors.append("ensure_hub_reciprocity did not retarget Full guide")

    with_steps = (
        '<p class="cmp-hero-sub">lede</p>\n'
        '        <ol class="cmp-hero-steps">\n'
        '          <li><span>Compare</span></li>\n'
        '          <li><span>Shortlist</span></li>\n'
        '          <li><span>Check price</span></li>\n'
        "        </ol>\n"
        '        <div class="meta-row">updated</div>'
        '<a class="product-cta" href="https://example.test/buy">Check price</a>'
        '<a class="top3-cta" href="https://example.test/buy">Check price</a>'
    )
    stripped = strip_cmp_hero_steps(with_steps)
    if "cmp-hero-steps" in stripped:
        errors.append("strip_cmp_hero_steps left the decorative ol")
    if "product-cta" not in stripped or "top3-cta" not in stripped:
        errors.append("strip_cmp_hero_steps removed a real Check price CTA")

    if errors:
        print("hub_reciprocity_unit FAIL")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)
    print("hub_reciprocity_unit OK")


if __name__ == "__main__":
    main()
