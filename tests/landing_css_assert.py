#!/usr/bin/env python3
"""Landing CSS presence + SoT hero layout (no network, no deploy).

Live 2026-10-23: site/assets/css/pages-landing.css was missing from git tip,
so ~261 landing/review pages 404'd that stylesheet. .landing-hero then fell
through to site.css .lifestyle-block.has-photo{aspect-ratio:16/10} full-width
(huge cover, tight gap). Fail closed if the file is missing or lacks the
desktop copy|photo grid.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
LANDING_CSS = SITE / "assets" / "css" / "pages-landing.css"
SAMPLE_PAGES = (
    "security-cameras/index.html",
    "robot-vacuums/index.html",
    "air-fryers/index.html",
    "security-cameras/reviews/eufy-security-solocam-s220-solar-security/index.html",
)

# SoT bake copy is 22296 bytes. A stub / empty file must fail.
MIN_BYTES = 20000


def collect_errors(site: Path = SITE) -> list[str]:
    errors: list[str] = []
    css_path = site / "assets" / "css" / "pages-landing.css"
    if not css_path.is_file() or css_path.stat().st_size < MIN_BYTES:
        errors.append("missing or empty assets/css/pages-landing.css")
        return errors

    css = css_path.read_text(encoding="utf-8")
    if ".landing-hero{display:grid" not in css:
        errors.append("pages-landing.css missing .landing-hero display:grid")
    if "grid-template-columns:1.15fr 0.85fr" not in css:
        errors.append("pages-landing.css missing desktop 1.15fr 0.85fr hero grid")
    if "margin:0.75rem 0 1.75rem" not in css:
        errors.append("pages-landing.css missing .landing-hero SoT margins")
    if ".landing-pick-cta-bar{display:flex" not in css:
        errors.append("pages-landing.css missing .landing-pick-cta-bar flex row")
    # Later img.landing-packshot{width:140px;height:100px} must not win in the bar.
    if ".landing-pick-cta-bar .landing-pick-logo.landing-packshot" not in css:
        errors.append(
            "pages-landing.css missing CTA-bar packshot override "
            "(.landing-pick-cta-bar .landing-pick-logo.landing-packshot)"
        )
    bar_pack = css.split(".landing-pick-cta-bar .landing-pick-logo.landing-packshot", 1)
    if len(bar_pack) > 1 and "max-height:36px" not in bar_pack[1][:220]:
        errors.append("CTA-bar packshot override missing max-height:36px")

    leftover = "Confirm mop pads, bags, and dock footprint"
    keep_rv = {"robot-vacuums"}
    for hub in site.iterdir():
        if not hub.is_dir():
            continue
        landing = hub / "index.html"
        if not landing.is_file():
            continue
        html = landing.read_text(encoding="utf-8")
        if leftover not in html:
            continue
        if hub.name not in keep_rv:
            errors.append(
                f"{hub.name}/ landing still has RV mop-pads leftover cons"
            )

    for rel in SAMPLE_PAGES:
        path = site / rel
        if not path.is_file():
            errors.append(f"missing sample page {rel}")
            continue
        if "pages-landing.css" not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel} does not link pages-landing.css")

    linked = 0
    for path in site.rglob("*.html"):
        if "pages-landing.css" in path.read_text(encoding="utf-8"):
            linked += 1
    if linked < 200:
        errors.append(
            f"only {linked} HTML pages link pages-landing.css (expected ~261)"
        )
    return errors


def main() -> int:
    errors = collect_errors()
    if errors:
        print("landing_css_assert FAILED")
        for err in errors:
            print(" -", err)
        return 1
    css_path = LANDING_CSS
    print(
        f"landing_css_assert OK bytes={css_path.stat().st_size} "
        f"hero=grid+1.15fr/0.85fr cta-bar=36px"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
