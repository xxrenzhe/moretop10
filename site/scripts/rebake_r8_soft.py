#!/usr/bin/env python3
"""Local rebake for R8 soft queue (computer-speakers, tower-fans).

Uses existing apply_hub_page / chrome helpers on local HTML — no Live fetch,
no wrangler, no invented prices. Applies Mac L2 verdicts:

- restore_list_ok: keep/restore honest Amazon list + now
- clear_keep: keep list/was/% blank; align now to L2 buybox
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from price_honest import (  # noqa: E402
    apply_l2_list_strike_to_card,
    apply_now_to_card,
    apply_now_to_glance,
    apply_now_to_review,
    format_display,
    l2_list_amount,
    l2_restore_list,
    load_shortlist,
    parse_money,
    r8_soft_queue_rows,
    scrub_pick_was,
)

AFFECTED = ("computer-speakers", "tower-fans")


def _write_json(path: Path, blob: dict) -> None:
    path.write_text(json.dumps(blob, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def apply_l2_shortlists() -> None:
    """Write L2 now/list onto queued picks. Do not scrub restore_list_ok."""
    for row in r8_soft_queue_rows():
        path = SITE / "data" / row["src"]
        blob = load_shortlist(path)
        asin = (row.get("asin") or "").upper()
        now = parse_money(row.get("now") or row.get("l2_now"))
        picks = []
        for pick in blob.get("picks") or []:
            if (pick.get("asin") or "").upper() != asin:
                picks.append(pick)
                continue
            if l2_restore_list(row):
                out = dict(pick)
                list_amt = l2_list_amount(row)
                if list_amt is not None:
                    out["list_price"] = f"{list_amt:.2f}"
                if now is not None:
                    out["price"] = f"{now:.2f}"
                    out["price_raw"] = format_display(now)
                    out["price_displayed"] = format_display(now)
                picks.append(out)
            else:
                out = scrub_pick_was(pick)
                if now is not None:
                    out["price"] = f"{now:.2f}"
                    out["price_raw"] = format_display(now)
                    out["price_displayed"] = format_display(now)
                picks.append(out)
        blob["picks"] = picks
        _write_json(path, blob)


def _patch_comparison(slug: str, asin: str, old: float | None, new: float, short_title: str) -> str:
    path = SITE / slug / "comparison" / "index.html"
    html = path.read_text(encoding="utf-8")
    if old is not None and abs(old - new) > 0.009:
        html = apply_now_to_card(html, asin, old, new)
        html = apply_now_to_glance(html, short_title, old, new)
    path.write_text(html, encoding="utf-8")
    return html


def _patch_review(slug: str, review_slug: str, old: float | None, new: float) -> None:
    path = SITE / slug / "reviews" / review_slug / "index.html"
    if not path.exists() or old is None or abs(old - new) < 0.009:
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
        new = parse_money(row.get("now") or row.get("l2_now"))
        if new is None:
            raise SystemExit(f"r8_soft_queue {asin} missing L2 now")
        old = parse_money(
            row.get("catalog_now") or row.get("html_now") or row.get("published_now")
        )
        blob = load_shortlist(SITE / "data" / row["src"])
        pick = next(
            (p for p in blob.get("picks") or [] if (p.get("asin") or "").upper() == asin.upper()),
            {},
        )
        if old is None and not l2_restore_list(row):
            old = parse_money(pick.get("price") or pick.get("price_displayed"))
        short_title = pick.get("short_title") or ""
        review_slug = pick.get("review_slug") or ""
        _patch_comparison(slug, asin, old, new, short_title)
        if review_slug:
            _patch_review(slug, review_slug, old, new)
        if l2_restore_list(row):
            list_amt = l2_list_amount(row)
            if list_amt is None:
                raise SystemExit(f"restore_list_ok {asin} missing L2 list")
            path = SITE / slug / "comparison" / "index.html"
            html = apply_l2_list_strike_to_card(path.read_text(encoding="utf-8"), asin, new, list_amt)
            path.write_text(html, encoding="utf-8")
            print(
                f"  patched {slug} {asin} now {format_display(new)} "
                f"list {format_display(list_amt)} (L2 restore_list_ok)"
            )
        else:
            print(
                f"  patched {slug} {asin} now {format_display(new)} "
                f"(clear_keep, no list/strike)"
            )


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
    print("R8 L2 apply + local rebake (no Live / no deploy)")
    apply_l2_shortlists()
    patch_affected_html()
    rebake_schema()


if __name__ == "__main__":
    main()
