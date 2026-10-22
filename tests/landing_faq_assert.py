#!/usr/bin/env python3
"""Buyer-intent landing/comparison FAQ rewrite — unit + baked site."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "site" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from landing_faq import (  # noqa: E402
    CATEGORY_FAQS,
    DOCK_A,
    DOCK_Q,
    META_FAQ_PHRASES,
    faqs_for,
    jsonld_faq_pairs,
    scrub_faqs,
    site_errors,
    visible_faq_pairs,
)

LANDING_SHELL = """<!DOCTYPE html><html><head></head><body>
<article class="landing-article">
<h2>FAQ: buying sample</h2>
<details class="landing-faq" open><summary>How many products do you rank?</summary>
<p>We publish ten complete, in-stock picks per category when the shortlist clears our card checklist.</p></details>
<details class="landing-faq"><summary>Do I need the most automated dock?</summary>
<p>Only if you mop often or hate emptying a bin. Many homes are happier with a mid-chart pick that self-empties dry debris and keeps mopping optional.</p></details>
<details class="landing-faq"><summary>Do you earn a commission?</summary>
<p>Yes—when you tap Check price and buy, we may earn an affiliate commission at no extra cost to you.</p></details>
<aside class="geo-cite-strip">cite</aside>
</article></body></html>"""

CMP_SHELL = """<!DOCTYPE html><html><head></head><body>
<div class="prose-block"><ol class="cmp-howto"><li>Scan</li></ol></div>
<div class="faq">
          <h2>FAQ</h2>
          <details open><summary>Are these prices live?</summary><p>Prices are publish-time snapshots, not a live cart.</p></details>
<details><summary>How do you rank products on this chart?</summary><p>Cards are ordered by score mapped from retailer star ratings.</p></details>
<details><summary>Do you earn a commission?</summary><p>Yes—when you tap Check price and buy, we may earn an affiliate commission.</p></details>
        </div>
</body></html>"""


def _blob(pairs: list[tuple[str, str]]) -> str:
    return " ".join(f"{q} {a}" for q, a in pairs).lower()


def main() -> int:
    errors: list[str] = []

    wet = scrub_faqs(LANDING_SHELL, "wet-dry-vacuums", kind="landing")
    wet_vis = visible_faq_pairs(wet)
    if DOCK_Q in wet or "most automated dock" in wet.lower() or "mopping optional" in wet.lower():
        errors.append("wet-dry landing unit still has robot-vac dock leftover")
    expected = faqs_for("wet-dry-vacuums")
    if [q for q, _ in wet_vis] != [q for q, _ in expected]:
        errors.append("wet-dry landing unit questions mismatch")
    if not any("dirty-water tank" in a.lower() for _, a in wet_vis):
        errors.append("wet-dry landing unit missing dirty-water tank answer")
    if any(m in _blob(wet_vis) for m in META_FAQ_PHRASES):
        errors.append("wet-dry landing unit still has meta FAQ")
    if jsonld_faq_pairs(wet) != wet_vis:
        errors.append("wet-dry landing unit JSON-LD mismatch")

    desk = scrub_faqs(CMP_SHELL, "standing-desks", kind="comparison")
    desk_vis = visible_faq_pairs(desk)
    if "are these prices live" in _blob(desk_vis) or "commission" in _blob(desk_vis):
        errors.append("standing-desks comparison unit still has chart/meta FAQ")
    if not any("height range" in q.lower() for q, _ in desk_vis):
        errors.append("standing-desks comparison unit missing height-range question")
    if not (3 <= len(desk_vis) <= 5):
        errors.append(f"standing-desks comparison unit count={len(desk_vis)}")

    robot = scrub_faqs(LANDING_SHELL, "robot-vacuums", kind="landing")
    robot_vis = visible_faq_pairs(robot)
    if DOCK_Q not in [q for q, _ in robot_vis] or DOCK_A not in [a for _, a in robot_vis]:
        errors.append("robot-vacuums unit must keep dock FAQ")
    if any(m in _blob(robot_vis) for m in META_FAQ_PHRASES):
        errors.append("robot-vacuums unit still has meta FAQ")

    unknown = scrub_faqs(LANDING_SHELL, "not-a-cat", kind="landing")
    if DOCK_Q in unknown or "most automated dock" in unknown.lower():
        errors.append("unknown slug must drop dock leftover")

    missing = [s for s in CATEGORY_FAQS if not (3 <= len(CATEGORY_FAQS[s]) <= 5)]
    if missing:
        errors.append("FAQ sets outside 3–5: " + ", ".join(missing))

    errors.extend(site_errors(ROOT / "site"))

    if errors:
        print("landing_faq_assert failed:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("landing_faq_assert: ok")
    print("  unit: wet-dry / standing-desks replace; robot-vacuums keep dock")
    print("  baked landings + comparison: buyer FAQ, no dock leftover, JSON-LD matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
