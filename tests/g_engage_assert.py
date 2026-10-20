#!/usr/bin/env python3
"""Light G-ENGAGE bake assert — structural engagement, not bounce %.

Sample only: air-fryers money hub + comparison. Requires:

  1. Answer-first lead (or equivalent first meaningful prose/table)
  2. Primary Check-price CTA with price near that CTA (existing layout rules)

Does not measure bounce, dwell, or OpenSEO. Bake ≠ Deploy.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCRIPTS = ROOT / "site" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from seo_geo import has_html_class  # noqa: E402

PRICE_RE = re.compile(r"\$\d")


def _strip_scripts(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.S | re.I)
    return html


def _text(chunk: str) -> str:
    return re.sub(r"<[^>]+>", " ", chunk)


def _first_card(html: str) -> str | None:
    m = re.search(r'<article\s+class="product-card"[\s\S]*?</article>', html)
    return m.group(0) if m else None


def _first_pick(html: str) -> str | None:
    m = re.search(r'<section class="landing-pick"[^>]*>[\s\S]*?</section>', html)
    return m.group(0) if m else None


def sample_errors(site: Path | None = None) -> list[str]:
    site = site or SITE
    errors: list[str] = []
    hub = site / "air-fryers" / "index.html"
    cmp = site / "air-fryers" / "comparison" / "index.html"
    if not hub.exists():
        errors.append("missing sample hub air-fryers/")
    else:
        errors.extend(_check_hub(hub.read_text(encoding="utf-8")))
    if not cmp.exists():
        errors.append("missing sample comparison air-fryers/comparison/")
    else:
        errors.extend(_check_comparison(cmp.read_text(encoding="utf-8")))
    return errors


def _check_hub(html: str) -> list[str]:
    errors: list[str] = []
    body = _strip_scripts(html)
    if not has_html_class(body, "geo-answer-first"):
        errors.append("air-fryers hub missing HTML Answer-first lead (.geo-answer-first)")
        return errors

    art = re.search(r'<article class="landing-article">([\s\S]*?)</article>', body)
    if not art:
        errors.append("air-fryers hub missing landing-article")
        return errors
    first_p = re.search(r"<p\b[^>]*>[\s\S]*?</p>", art.group(1))
    if not first_p:
        errors.append("air-fryers hub landing-article has no lead paragraph")
        return errors
    lead = first_p.group(0)
    if not has_html_class(lead, "geo-answer-first"):
        errors.append("air-fryers hub first landing-article <p> is not Answer-first")
    lead_text = _text(lead)
    if len(re.sub(r"\s+", " ", lead_text).strip()) < 80:
        errors.append("air-fryers hub Answer-first lead is too short")
    if not PRICE_RE.search(lead_text):
        errors.append("air-fryers hub Answer-first lead has no $ price snapshot")

    pick = _first_pick(body)
    if not pick:
        errors.append("air-fryers hub missing first landing-pick")
        return errors
    cta_bar = re.search(r'<div class="landing-pick-cta-bar">[\s\S]*?</div>', pick)
    if not cta_bar or "Check price" not in cta_bar.group(0):
        errors.append("air-fryers hub first pick missing primary Check price CTA")
    # Hub layout: $ lives in the Answer-first lead; CTA is the first pick bar.
    if art.start() > body.find('class="landing-pick"'):
        errors.append("air-fryers hub Answer-first must precede the first pick CTA")
    return errors


def _check_comparison(html: str) -> list[str]:
    errors: list[str] = []
    body = _strip_scripts(html)
    if not has_html_class(body, "cmp-answer-first") and not has_html_class(
        body, "geo-answer-first"
    ):
        errors.append(
            "air-fryers comparison missing Answer-first lead "
            "(.cmp-answer-first / .geo-answer-first) or equivalent first prose"
        )
        return errors
    if not has_html_class(body, "geo-answer-first"):
        errors.append(
            "air-fryers comparison Answer-first is JSON-LD only "
            "(HTML class geo-answer-first missing)"
        )

    lead = re.search(
        r'<section class="[^"]*cmp-answer-first[^"]*"[^>]*>[\s\S]*?</section>',
        body,
    )
    if not lead:
        errors.append("air-fryers comparison missing cmp-answer-first section")
        return errors
    lead_text = _text(lead.group(0))
    if len(re.sub(r"\s+", " ", lead_text).strip()) < 80:
        errors.append("air-fryers comparison Answer-first lead is too short")
    if not PRICE_RE.search(lead_text):
        errors.append("air-fryers comparison Answer-first lead has no $ price snapshot")

    stack_at = body.find('class="product-stack"')
    if stack_at != -1 and lead.start() > stack_at:
        errors.append("air-fryers comparison Answer-first must precede the product stack")

    card = _first_card(body)
    if not card:
        errors.append("air-fryers comparison missing first product-card")
        return errors
    price_pos = card.find('class="pc-price-decision"')
    footer_pos = card.find('class="pc-footer"')
    if price_pos < 0:
        errors.append("air-fryers comparison first card missing .pc-price-decision")
    elif footer_pos < 0 or price_pos > footer_pos:
        errors.append(
            "air-fryers comparison first card: price must sit above .pc-footer "
            "(existing layout: price near Check price, not under the divider)"
        )
    if not re.search(r'class="pc-price-value">\$\d', card):
        errors.append("air-fryers comparison first card missing $ in .pc-price-value")
    if "Check price" not in card or "product-cta" not in card:
        errors.append("air-fryers comparison first card missing primary Check price CTA")
    footer_chunk = card[footer_pos:] if footer_pos >= 0 else ""
    if "pc-price-decision" in footer_chunk or "pc-price-value" in footer_chunk:
        errors.append("air-fryers comparison first card nested price inside .pc-footer")
    if "pc-footer-buy" in card:
        errors.append("air-fryers comparison first card used .pc-footer-buy (price under divider)")
    return errors


def main() -> None:
    errors = sample_errors(SITE)
    if errors:
        raise SystemExit("g_engage_assert failed:\n- " + "\n- ".join(errors))
    print("g_engage_assert ok")
    print("  sample: air-fryers hub + comparison")
    print("  gate: Answer-first lead + Check-price with price near CTA (not bounce %)")


if __name__ == "__main__":
    main()
