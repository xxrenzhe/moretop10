#!/usr/bin/env python3
"""MT10 day-add 9 niches — unpublished hubs + type-07, honest counts, brand_gate skips."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_mt10_day_add import (  # noqa: E402
    DATE,
    DRAFT_COMMENT,
    NICHES,
    OCCUPIED_INREPO,
    PACK_INREPO,
    SKIP_BRAND_GATE,
    TEMPLATE_LEFTOVER,
    healthy_track,
)
from seo_geo import ROBOTS_INDEX, ROBOTS_NOINDEX, VISITOR_LEAK_RE, html_without_ld_json  # noqa: E402

INV_JSON = SITE / "data" / f"mt10-day-add-inventory-{DATE}.json"
INV_MD = SITE / "data" / f"mt10-day-add-inventory-{DATE}.md"
NOTES = ROOT / "notes" / f"mt10-day-add-draft-{DATE}.md"
ASIN_RE = re.compile(r"\bB0[A-Z0-9]{8}\b")


def jsonld_blocks(html: str) -> list[dict]:
    out: list[dict] = []
    for raw in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, flags=re.S
    ):
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return out


def faq_ld_pairs(html: str) -> list[tuple[str, str]]:
    for blob in jsonld_blocks(html):
        if blob.get("@type") != "FAQPage":
            continue
        pairs: list[tuple[str, str]] = []
        for ent in blob.get("mainEntity") or []:
            name = unescape(str(ent.get("name") or "")).strip()
            ans = unescape(str((ent.get("acceptedAnswer") or {}).get("text") or "")).strip()
            if name and ans:
                pairs.append((name, ans))
        return pairs
    return []


def main() -> int:
    errors: list[str] = []

    if not NOTES.exists():
        errors.append(f"missing {NOTES.relative_to(ROOT)}")
    if not OCCUPIED_INREPO.exists():
        errors.append("missing occupied ASIN list")
        print("mt10_day_add_assert failed:\n- " + "\n- ".join(errors))
        return 1
    occupied = {
        str(a).strip().upper()
        for a in (json.loads(OCCUPIED_INREPO.read_text(encoding="utf-8")).get("flat") or [])
        if a
    }
    if len(occupied) < 700:
        errors.append(f"occupied flat expected ~772, got {len(occupied)}")

    if not INV_JSON.exists():
        errors.append("missing inventory json")
        print("mt10_day_add_assert failed:\n- " + "\n- ".join(errors))
        return 1
    if not INV_MD.exists():
        errors.append("missing inventory markdown")
    if not PACK_INREPO.exists():
        errors.append("missing L1 fill pack")

    inv = json.loads(INV_JSON.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")
    if inv.get("published") is not False:
        errors.append("inventory published must be false")
    if inv.get("live") is True or inv.get("merged") is True:
        errors.append("inventory must stay draft (not live/merged)")
    if inv.get("independent_of_shortlist_lab") is not True:
        errors.append("inventory must stay independent of Lab")
    skipped_paths = {row.get("path") for row in inv.get("skipped") or []}
    for slug in SKIP_BRAND_GATE:
        if f"/{slug}/" not in skipped_paths:
            errors.append(f"inventory missing skip {slug}")

    pack = json.loads(PACK_INREPO.read_text(encoding="utf-8"))
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    html_map = (SITE / "sitemap" / "index.html").read_text(encoding="utf-8")

    expected_total = 0
    for cat in NICHES:
        slug = cat["slug"]
        expected = cat["expected"]
        expected_total += expected
        scene = (pack.get("scenes") or {}).get(slug) or {}
        pack_asins = [p["asin"] for p in scene.get("products") or []]
        if len(pack_asins) != expected:
            errors.append(f"{slug} pack count {len(pack_asins)} != expected {expected}")

        shortlist = json.loads((SITE / "data" / f"shortlist-{slug}.json").read_text(encoding="utf-8"))
        if shortlist.get("density") != expected:
            errors.append(f"{slug} shortlist density {shortlist.get('density')} != {expected}")
        if expected < 10 and not shortlist.get("density_shortfall"):
            errors.append(f"{slug} shortlist must keep density_shortfall")
        if shortlist.get("waiting_for_部署上线") != "yes":
            errors.append(f"{slug} shortlist missing waiting_for_部署上线")
        if shortlist.get("published") is not False:
            errors.append(f"{slug} shortlist published must be false")
        got_asins = [p["asin"] for p in shortlist.get("picks") or []]
        if got_asins != pack_asins:
            errors.append(f"{slug} shortlist ASINs drifted from pack")
        hits = [a for a in got_asins if a.upper() in occupied]
        if hits:
            errors.append(f"{slug} collision {hits}")
        for pick in shortlist.get("picks") or []:
            track = healthy_track(pick.get("affiliate_link"))
            if not track:
                errors.append(f"{slug} {pick.get('asin')} missing healthy fromsll track")
            if pick.get("image"):
                errors.append(f"{slug} {pick.get('asin')} invented gallery")
            if pick.get("list_price"):
                errors.append(f"{slug} {pick.get('asin')} invented list_price")

        for rel in (
            f"{slug}/index.html",
            f"{slug}/comparison/index.html",
            f"{slug}/reviews/index.html",
        ):
            path = SITE / rel
            if not path.exists():
                errors.append(f"missing {rel}")
                continue
            html = path.read_text(encoding="utf-8")
            if DRAFT_COMMENT not in html:
                errors.append(f"{rel} missing draft comment")
            if ROBOTS_INDEX not in html:
                errors.append(f"{rel} missing {ROBOTS_INDEX}")
            if "10%" in html or "12%" in html:
                errors.append(f"{rel} leaked was/%")
            if "m.media-amazon.com" in html or "amazon.com/dp/" in html:
                errors.append(f"{rel} invented Amazon gallery or hop")
            if "yeahpromos.com" in html:
                errors.append(f"{rel} YP rebind")
            visible = html_without_ld_json(html)
            hit = VISITOR_LEAK_RE.search(visible)
            if hit:
                errors.append(f"{rel} visitor leak {hit.group(0)!r}")

        landing = SITE / slug / "index.html"
        if landing.exists():
            html = landing.read_text(encoding="utf-8")
            if f"Top {expected} Best {cat['name']}" not in html:
                errors.append(f"{slug} landing H1 must stay honest Top {expected}")
            for needed in (f"{cat['scene_path']}/", "comparison/", "reviews/"):
                if needed not in html:
                    errors.append(f"{slug} landing related-cluster missing {needed}")
            for asin in pack_asins:
                if f'id="geo-{asin}"' not in html:
                    errors.append(f"{slug} landing missing #geo-{asin}")

        cmp = SITE / slug / "comparison" / "index.html"
        if cmp.exists():
            html = cmp.read_text(encoding="utf-8")
            cards = html.count('class="product-card"')
            if cards != expected:
                errors.append(f"{slug} comparison cards={cards} (need {expected})")

        review_articles = list((SITE / slug / "reviews").glob("*/index.html"))
        if review_articles:
            errors.append(f"{slug} new review articles exist: {[p.parent.name for p in review_articles]}")

        rel = f"{slug}/{cat['scene_path']}/index.html"
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
        else:
            html = path.read_text(encoding="utf-8")
            if DRAFT_COMMENT not in html:
                errors.append(f"{rel} missing draft comment")
            if f'name="robots" content="{ROBOTS_NOINDEX}"' not in html:
                errors.append(f"{rel} robots is not noindex,follow")
            if cat["scene_h1"] not in html:
                errors.append(f"{rel} missing h1")
            visits = html.count('class="bestof-visit-card"')
            if visits != expected:
                errors.append(f"{rel} visit cards={visits} (need {expected})")
            if html.count('class="inline-pick-card"') != min(3, expected):
                errors.append(f"{rel} inline picks mismatch")
            for leak in TEMPLATE_LEFTOVER:
                if leak in html:
                    errors.append(f"{rel} leftover {leak!r}")
            if "10%" in html or "12%" in html:
                errors.append(f"{rel} leaked was/%")
            if "amazon.com/dp/" in html or "m.media-amazon.com" in html:
                errors.append(f"{rel} invented Amazon gallery")
            if "yeahpromos.com" in html:
                errors.append(f"{rel} YP rebind")
            if html.count("pboost.me") < expected or "uid=fromsll" not in html:
                errors.append(f"{rel} missing PB fromsll tracks")
            if 'class="landing-related-cluster"' in html:
                errors.append(f"{rel} must not ship landing-related-cluster")
            visible = html_without_ld_json(html)
            hit = VISITOR_LEAK_RE.search(visible)
            if hit:
                errors.append(f"{rel} visitor leak {hit.group(0)!r}")
            for asin in pack_asins:
                if asin not in html:
                    errors.append(f"{rel} missing packed ASIN {asin}")

        for loc in (
            f"/{slug}/",
            f"/{slug}/comparison/",
            f"/{slug}/reviews/",
            f"/{slug}/{cat['scene_path']}/",
        ):
            if f"https://moretop10.com{loc}" not in sitemap:
                errors.append(f"sitemap missing {loc}")
        if f'href="../{slug}/"' not in html_map:
            errors.append(f"sitemap/index.html missing /{slug}/")

    if inv.get("total_admitted") != expected_total:
        errors.append(f"inventory total_admitted {inv.get('total_admitted')} != {expected_total}")

    for slug in SKIP_BRAND_GATE:
        if (SITE / slug / "index.html").exists():
            errors.append(f"brand_gate skip created /{slug}/")
        if (SITE / "data" / f"shortlist-{slug}.json").exists():
            errors.append(f"brand_gate skip wrote shortlist-{slug}.json")
        if f"/{slug}/" in html_map and f'href="../{slug}/"' in html_map:
            errors.append(f"sitemap/index.html lists skipped /{slug}/")

    if errors:
        print("mt10_day_add_assert failed:")
        for err in errors[:60]:
            print(f"- {err}")
        if len(errors) > 60:
            print(f"... +{len(errors) - 60} more")
        return 1
    print("mt10_day_add_assert ok")
    print(f"  niches: {len(NICHES)}")
    print(f"  cards: {expected_total}")
    print(f"  skipped: {', '.join(SKIP_BRAND_GATE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
