#!/usr/bin/env python3
"""Local rebake for R8 soft-scrub categories (computer-speakers, tower-fans).

Uses existing apply_hub_page / chrome helpers on local HTML — no Live fetch,
no wrangler, no invented prices. Aligns published now snapshots with shortlist
now and leaves list_price / was / % blank so bake cannot render a strike.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from price_honest import (  # noqa: E402
    apply_now_to_card,
    apply_now_to_glance,
    apply_now_to_review,
    format_display,
    load_shortlist,
    r8_soft_queue_rows,
    scrub_pick_was,
)

AFFECTED = ("computer-speakers", "tower-fans")


def scrub_shortlists() -> None:
    for row in r8_soft_queue_rows():
        path = SITE / "data" / row["src"]
        blob = load_shortlist(path)
        asin = (row.get("asin") or "").upper()
        picks = []
        for pick in blob.get("picks") or []:
            if (pick.get("asin") or "").upper() == asin:
                picks.append(scrub_pick_was(pick))
            else:
                picks.append(pick)
        blob["picks"] = picks
        path.write_text(
            __import__("json").dumps(blob, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


def _patch_comparison(slug: str, asin: str, old: float, new: float, short_title: str) -> None:
    path = SITE / slug / "comparison" / "index.html"
    html = path.read_text(encoding="utf-8")
    html = apply_now_to_card(html, asin, old, new)
    html = apply_now_to_glance(html, short_title, old, new)
    path.write_text(html, encoding="utf-8")


def _patch_review(slug: str, review_slug: str, old: float, new: float) -> None:
    path = SITE / slug / "reviews" / review_slug / "index.html"
    if not path.exists():
        return
    html = path.read_text(encoding="utf-8")
    html = apply_now_to_review(html, old, new)
    if asin_skip_bullet_needed(html, new):
        html = html.replace(
            f"At a {format_display(new)} snapshot price, those seeking sub-$50 basic airflow without app or height options can find simpler alternatives in our category reviews.",
            "Those seeking a basic airflow unit without app or height options can find simpler alternatives in our category reviews.",
            1,
        )
    path.write_text(html, encoding="utf-8")


def asin_skip_bullet_needed(html: str, new: float) -> bool:
    return (
        f"At a {format_display(new)} snapshot price, those seeking sub-$50"
        in html
    )


def patch_affected_html() -> None:
    for row in r8_soft_queue_rows():
        slug = row["category"]
        if slug not in AFFECTED:
            continue
        asin = row["asin"]
        old = row["cleared_was"]
        new = row["now"]
        blob = load_shortlist(SITE / "data" / row["src"])
        pick = next(
            (p for p in blob.get("picks") or [] if (p.get("asin") or "").upper() == asin.upper()),
            {},
        )
        short_title = pick.get("short_title") or ""
        review_slug = pick.get("review_slug") or ""
        _patch_comparison(slug, asin, old, new, short_title)
        if review_slug:
            _patch_review(slug, review_slug, old, new)
        print(f"  patched {slug} {asin} now {format_display(new)} (cleared was {format_display(old)})")


def _schema_paths(slug: str, review_slug: str | None) -> list[tuple[Path, str, str | None]]:
    paths = [
        (SITE / slug / "comparison" / "index.html", "comparison", None),
        (SITE / slug / "index.html", "landing", None),
        (SITE / slug / "reviews" / "index.html", "reviews", None),
    ]
    if review_slug:
        paths.append((SITE / slug / "reviews" / review_slug / "index.html", "review", review_slug))
    return paths


def rebake_schema(slugs: tuple[str, ...] = AFFECTED) -> None:
    """Refresh JSON-LD from local cards. No nav/footer rewrite (avoids unpublished chrome)."""
    from build import apply_hub_page, load_site_config, rel_prefix

    cfg = load_site_config()
    queued = {row["category"]: row for row in r8_soft_queue_rows() if row.get("category") in slugs}
    wrote = 0
    for slug in slugs:
        row = queued.get(slug) or {}
        blob = load_shortlist(SITE / "data" / f"shortlist-{slug}.json")
        asin = (row.get("asin") or "").upper()
        pick = next(
            (p for p in blob.get("picks") or [] if (p.get("asin") or "").upper() == asin),
            {},
        )
        review_slug = pick.get("review_slug")
        cmp_html = (SITE / slug / "comparison" / "index.html").read_text(encoding="utf-8")
        cat = cfg["CATS_BY_SLUG"].get(slug)
        for path, kind, rev in _schema_paths(slug, review_slug):
            if not path.exists():
                continue
            out_rel = path.relative_to(SITE).as_posix()
            text = apply_hub_page(
                path.read_text(encoding="utf-8"),
                kind=kind,
                cat=cat,
                cmp_html=cmp_html if kind != "comparison" else None,
                prefix=rel_prefix(out_rel),
                review_slug=rev,
                site_root=SITE,
            )
            path.write_text(text, encoding="utf-8")
            wrote += 1
            print(f"  schema {out_rel}")
    print(f"rebaked schema on {wrote} pages for {', '.join(slugs)}")


def main() -> None:
    print("R8 soft scrub + local rebake (no Live / no deploy)")
    scrub_shortlists()
    patch_affected_html()
    rebake_schema()


if __name__ == "__main__":
    main()
