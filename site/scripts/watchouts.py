#!/usr/bin/env python3
"""Scrub category-wrong Watch-outs leftover from the shared landing-pick template.

Live snapshots baked a robot-vac generic into every category card:

    Confirm mop pads, bags, and dock footprint on the retailer page.

That line is correct on robot-vacuums. Everywhere else it is a template leak.
This module swaps it for a category-fitting "Confirm … on the retailer page"
line already used as a watch-out shape in that niche (tank / drain / sq ft,
basket / counter, runtime / bin, etc.). Unknown slugs drop the leftover.

No new product claims. Bake-only — not a Live deploy.
"""

from __future__ import annotations

import re
from pathlib import Path

LEFTOVER = "Confirm mop pads, bags, and dock footprint on the retailer page."

# Robot-vac phrasing that must not appear in Watch-outs/Cons on other cats.
ROBOT_VAC_PHRASES = (
    "mop pads",
    "mop pad",
    "dock footprint",
    "hydrojet",
    "auto mop wash",
)

KEEP_ROBOT_VAC_SLUGS = frozenset({"robot-vacuums"})

# Vacuum money URLs (success grep is "non-vacuum categories → zero").
VACUUM_SLUGS = frozenset(
    {
        "robot-vacuums",
        "robot-vacuums-match",
        "cordless-vacuums",
        "wet-dry-vacuums",
    }
)

# Generic confirm lines grounded in each niche's existing skip / review copy.
# Same sentence shape as the leftover; specs are checklists, not claims.
CATEGORY_CONFIRM = {
    "air-fryers": "Confirm basket capacity, counter depth, and footprint on the retailer page.",
    "air-purifiers": "Confirm room coverage, filter type, and noise rating on the retailer page.",
    "bluetooth-speakers": "Confirm output, battery life, and outdoor rating on the retailer page.",
    "computer-speakers": "Confirm wattage, inputs, and desk size on the retailer page.",
    "cordless-vacuums": "Confirm runtime, bin emptying, and dock space on the retailer page.",
    "dash-cams": "Confirm channel count, cabin coverage, and card support on the retailer page.",
    "dehumidifiers": "Confirm tank size, drain hose, and coverage sq ft on the retailer page.",
    "espresso-machines": "Confirm tank size, counter footprint, and grinder setup on the retailer page.",
    "hair-dryers": "Confirm attachments, dual-voltage, and heat settings on the retailer page.",
    "humidifiers": "Confirm tank size, mist type, and room coverage on the retailer page.",
    "kids-bikes": "Confirm wheel size, age range, and training-wheel setup on the retailer page.",
    "hearing-aids": "Confirm fit, battery type, and return window on the retailer page.",
    "water-filters": "Confirm install type, flow rate, and filter life on the retailer page.",
    "under-sink-countertop-filtration": "Confirm install type, GPD rating, and faucet finish on the retailer page.",
    "pitcher-water-filters": "Confirm pitcher model, filter life, and pack count on the retailer page.",
    "doormats": "Confirm size, indoor vs outdoor use, and wash method on the retailer page.",
    "split-system": "Confirm BTU, voltage, and install requirements on the retailer page.",
    "tv-wall-ceiling-mounts": "Confirm TV size range, VESA pattern, and weight rating on the retailer page.",
    "monitor-arms": "Confirm screen size, weight per arm, and VESA pattern on the retailer page.",
    "stage-lights": "Confirm pack count, control mode, and indoor vs outdoor rating on the retailer page.",
    "glass-display-cabinets": "Confirm dimensions, lighting type, and shelf rating on the retailer page.",
    "document-scanners": "Confirm camera MP, cover contents, and OS support on the retailer page.",
    "ceramic-space-heaters": "Confirm wattage, oscillation, noise, and tip-over protection on the retailer page.",
    "pillows": "Confirm loft, fill, and firmness on the retailer page.",
    "mattresses": "Confirm size, firmness, and trial window on the retailer page.",
    "office-chairs": "Confirm lumbar support, weight rating, and seat depth on the retailer page.",
    "water-flossers": "Confirm tank size, pressure settings, and tip count on the retailer page.",
    "litter-boxes": "Confirm entry type, waste-bag setup, and size fit on the retailer page.",
    "massage-guns": "Confirm heads, heat/cold options, and noise on the retailer page.",
    "noise-cancelling-headphones": "Confirm ANC type, fit, and battery life on the retailer page.",
    "projectors": "Confirm brightness, resolution, and throw distance on the retailer page.",
    "security-cameras": "Confirm power type, resolution, and storage plan on the retailer page.",
    "standing-desks": "Confirm width, height range, and weight rating on the retailer page.",
    "tower-fans": "Confirm height, oscillation, and noise on the retailer page.",
    "video-doorbells": "Confirm power type, field of view, and kit contents on the retailer page.",
    "wet-dry-vacuums": "Confirm steam option, hard-floor fit, and tank emptying on the retailer page.",
}

WATCHOUTS_BLOCK = re.compile(
    r'(<div class="pc-col-title cons">(Watch-outs|Cons)</div><ul>)(.*?)(</ul>)',
    re.S,
)
LI_LEFTOVER = re.compile(
    r"<li>\s*" + re.escape(LEFTOVER) + r"\s*</li>",
    re.I,
)


def replacement_for(slug: str | None) -> str | None:
    """Category confirm line, or None to drop the leftover."""
    if not slug:
        return None
    if slug in KEEP_ROBOT_VAC_SLUGS:
        return LEFTOVER
    return CATEGORY_CONFIRM.get(slug)


def _scrub_list(inner: str, slug: str | None, *, heading: str) -> str:
    repl = replacement_for(slug)
    if slug in KEEP_ROBOT_VAC_SLUGS:
        return inner
    if repl:
        inner = inner.replace(LEFTOVER, repl)
        # Landing cards use "Watch-outs". Review articles use "Cons" and
        # already carry product skip lines — do not invent extra review cons.
        if heading == "Watch-outs" and repl not in inner:
            inner = inner.rstrip() + f"<li>{repl}</li>"
        return inner
    return LI_LEFTOVER.sub("", inner)


def scrub_watchouts(html: str, slug: str | None) -> str:
    """Replace leftover or ensure a category-fitting confirm in Watch-outs / Cons."""
    if slug in KEEP_ROBOT_VAC_SLUGS:
        return html

    def _block(m: re.Match[str]) -> str:
        return m.group(1) + _scrub_list(m.group(3), slug, heading=m.group(2)) + m.group(4)

    html = WATCHOUTS_BLOCK.sub(_block, html)
    # Safety: leftover outside a recognized list (same template string).
    repl = replacement_for(slug)
    if LEFTOVER in html:
        if repl:
            html = html.replace(LEFTOVER, repl)
        else:
            html = LI_LEFTOVER.sub("", html)
            html = html.replace(LEFTOVER, "")
    return html


def watchouts_list_text(html: str) -> list[str]:
    items: list[str] = []
    for block in WATCHOUTS_BLOCK.findall(html):
        inner = block[2] if isinstance(block, tuple) else block
        for li in re.findall(r"<li>(.*?)</li>", inner, re.S):
            text = re.sub(r"<[^>]+>", "", li)
            text = text.replace("&amp;", "&").strip()
            if text:
                items.append(text)
    return items


def leftover_in_watchouts(html: str) -> bool:
    blob = " ".join(watchouts_list_text(html)).lower()
    return any(p in blob for p in ROBOT_VAC_PHRASES)


def scrub_site(site: Path) -> dict[str, int]:
    """Rewrite baked HTML under site/. Returns {rel_path: replacement_count}."""
    from site_config import ALL_CATS  # local import — stdlib script

    changed: dict[str, int] = {}
    slugs = {c["slug"] for c in ALL_CATS if c.get("slug")}
    for slug in slugs:
        if slug in KEEP_ROBOT_VAC_SLUGS:
            continue
        root = site / slug
        if not root.is_dir():
            continue
        for path in root.rglob("*.html"):
            html = path.read_text(encoding="utf-8")
            out = scrub_watchouts(html, slug)
            if out != html:
                path.write_text(out, encoding="utf-8")
                changed[str(path.relative_to(site))] = html.count(LEFTOVER) - out.count(
                    LEFTOVER
                )
    return changed


def site_errors(site: Path) -> list[str]:
    """Assert leftover robot-vac Watch-outs are gone from non-robot pages."""
    from site_config import ALL_CATS  # local import

    errors: list[str] = []
    for cat in ALL_CATS:
        slug = cat["slug"]
        landing = site / slug / "index.html"
        if not landing.is_file():
            errors.append(f"missing landing {slug}/")
            continue
        html = landing.read_text(encoding="utf-8")
        items = watchouts_list_text(html)
        if slug in KEEP_ROBOT_VAC_SLUGS:
            if LEFTOVER not in items:
                errors.append(f"{slug} lost native robot-vac Watch-outs confirm line")
            continue
        if leftover_in_watchouts(html) or LEFTOVER in html:
            errors.append(f"{slug} still has robot-vac leftover Watch-outs")
        expected = CATEGORY_CONFIRM.get(slug)
        if expected and expected not in items:
            errors.append(f"{slug} missing category confirm Watch-outs line")
        if slug not in VACUUM_SLUGS:
            body = html.lower()
            if "mop pads" in body or "dock footprint" in body:
                errors.append(f"{slug} non-vac landing still mentions mop pads / dock footprint")
    return errors


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    site = root / "site"
    changed = scrub_site(site)
    errors = site_errors(site)
    print(f"scrubbed {len(changed)} pages")
    for rel, n in sorted(changed.items()):
        print(f"  {rel}: {n}")
    if errors:
        raise SystemExit("watchouts verify failed:\n- " + "\n- ".join(errors))
    print("watchouts ok")


if __name__ == "__main__":
    main()
