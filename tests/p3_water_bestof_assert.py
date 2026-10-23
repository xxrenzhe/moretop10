#!/usr/bin/env python3
"""P3 water-filter scenario best-of — honest empty / need_fill, no occupied reuse."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p3_water_bestof import (  # noqa: E402
    DRAFT_COMMENT,
    OCCUPIED_PATH,
    SCENES,
    TEMPLATE_LEFTOVER,
    load_occupied,
)
from seo_geo import VISITOR_LEAK_RE, extract_visible_faqs, html_without_ld_json  # noqa: E402

INV_JSON = SITE / "data" / "p3-water-bestof-inventory-2026-10-23.json"
INV_MD = SITE / "data" / "p3-water-bestof-inventory-2026-10-23.md"
PAGES = [
    "water-filters/best-water-filters-for-well-water/index.html",
    "water-filters/best-water-filters-for-hard-water/index.html",
]
URLS = [
    "/water-filters/best-water-filters-for-well-water/",
    "/water-filters/best-water-filters-for-hard-water/",
]
FORBIDDEN_TOUCH = (
    "site/scripts/bake_p1b_scene_pages.py",
    "site/scripts/bake_p1c_ceramic.py",
    "site/scripts/bake_p2_greenfield.py",
    "tests/p1b_scene_assert.py",
    "tests/p1c_ceramic_assert.py",
    "tests/p2_greenfield_assert.py",
    "site/ceramic-space-heaters/index.html",
    "site/water-flossers/index.html",
)
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

    if not OCCUPIED_PATH.exists():
        errors.append("missing occupied ASIN list")
        print("p3_water_bestof_assert failed:\n- " + "\n- ".join(errors))
        return 1
    occupied = load_occupied()
    if len(occupied) != 61:
        errors.append(f"occupied list expected 61, got {len(occupied)}")
    if "B0H5JZZ3GK" not in occupied:
        errors.append("occupied list missing WHF21-PBL B0H5JZZ3GK")

    if not INV_JSON.exists():
        errors.append("missing inventory json")
        print("p3_water_bestof_assert failed:\n- " + "\n- ".join(errors))
        return 1
    if not INV_MD.exists():
        errors.append("missing inventory markdown")

    inv = json.loads(INV_JSON.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")
    if inv.get("live") is True or inv.get("merged") is True:
        errors.append("inventory must stay draft (not live/merged)")
    if inv.get("fill_status") != "need_fill":
        errors.append(f"expected fill_status need_fill, got {inv.get('fill_status')!r}")
    if inv.get("inventory_blocked") is True:
        errors.append("inventory_blocked must be false when affiliate tokens are missing")
    if inv.get("occupied_count") != 61:
        errors.append(f"inventory occupied_count expected 61, got {inv.get('occupied_count')}")

    pages = {row.get("path"): row for row in inv.get("pages") or []}
    for url in URLS:
        row = pages.get(url)
        if not row:
            errors.append(f"inventory missing {url}")
            continue
        if row.get("density") != 0:
            errors.append(f"{url} density expected 0, got {row.get('density')}")
        if row.get("fill_status") != "need_fill":
            errors.append(f"{url} fill_status expected need_fill")
        if row.get("inventory_blocked") is True:
            errors.append(f"{url} marked inventory_blocked")
        if row.get("cta_status") != "empty":
            errors.append(f"{url} cta_status expected empty")
        if row.get("picks"):
            errors.append(f"{url} inventory has invented picks")
        if row.get("type") != "07-best-of":
            errors.append(f"{url} type expected 07-best-of")

    sources = inv.get("sources") or {}
    if (sources.get("1_pb") or {}).get("live_query") != "skipped_no_token":
        errors.append("① PB live_query should be skipped_no_token on this VM")
    if (sources.get("2_yp") or {}).get("live_query") != "skipped_no_token":
        errors.append("② YP live_query should be skipped_no_token on this VM")
    repo = sources.get("3_in_repo") or {}
    if repo.get("scene_fit_well_unoccupied"):
        errors.append("③ reported unoccupied well systems — collision or accessory leak")
    if repo.get("scene_fit_hard_unoccupied"):
        errors.append("③ reported unoccupied hard-water systems — collision or accessory leak")

    for rel in FORBIDDEN_TOUCH:
        if (ROOT / rel).exists():
            errors.append(f"must not add P1/P2 file {rel} on the P3 branch")

    landing = (SITE / "water-filters" / "index.html").read_text(encoding="utf-8")
    if DRAFT_COMMENT not in landing:
        errors.append("water-filters landing missing draft comment")
    cluster = re.search(
        r'<p class="landing-related-cluster">.*?</p>', landing, flags=re.S
    )
    if not cluster:
        errors.append("water-filters landing missing related-cluster")
    else:
        block = cluster.group(0)
        for href in (
            "best-water-filters-for-well-water/",
            "best-water-filters-for-hard-water/",
        ):
            if href not in block:
                errors.append(f"landing cluster missing {href}")
        if 'href="water-filters/"' in block or 'href="./"' in block:
            errors.append("landing cluster self-links")
    if "B0H5JZZ3GK" not in landing:
        errors.append("do not recreate / empty the live water-filters main chart")

    comparison = (SITE / "water-filters" / "comparison" / "index.html").read_text(
        encoding="utf-8"
    )
    if "best-water-filters-for-well-water" in comparison:
        errors.append("related-cluster leaked onto comparison (landing only)")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    html_map = (SITE / "sitemap" / "index.html").read_text(encoding="utf-8")
    for url in URLS:
        loc = f"https://moretop10.com{url}"
        loc_at = sitemap.find(f"<loc>{loc}</loc>")
        if loc_at < 0:
            errors.append(f"sitemap missing {url}")
        else:
            block = sitemap[loc_at : loc_at + 180]
            if "2026-10-23" not in block:
                errors.append(f"sitemap lastmod not bumped for {url}")
        if f'href="..{url}"' not in html_map:
            errors.append(f"sitemap/index.html missing {url}")

    for rel, url, scene in zip(PAGES, URLS, SCENES, strict=True):
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if DRAFT_COMMENT not in html:
            errors.append(f"{rel} missing draft comment")
        if 'name="robots" content="index,follow' not in html:
            errors.append(f"{rel} robots is not index,follow")
        if scene["h1"] not in html:
            errors.append(f"{rel} missing h1")
        if "Priya Nair" not in html:
            errors.append(f"{rel} author is not Priya Nair")
        if "cmp-hero-water-filters.jpg" not in html:
            errors.append(f"{rel} missing water-filters lifestyle cover")
        if "data-fill-status=\"need_fill\"" not in html:
            errors.append(f"{rel} missing need_fill empty stub")
        if "Density is honest at 0" not in html:
            errors.append(f"{rel} missing honest density copy")
        if 'class="landing-related-cluster"' in html:
            errors.append(f"{rel} must not ship landing-related-cluster (landing only)")
        for leak in TEMPLATE_LEFTOVER:
            if leak in html:
                errors.append(f"{rel} leftover {leak!r}")
        if html.count('class="bestof-visit-card"'):
            errors.append(f"{rel} unexpected visit cards")
        if html.count('class="inline-pick-card"'):
            errors.append(f"{rel} unexpected inline picks")
        if "btn-cta-yellow" in html:
            errors.append(f"{rel} invented Check price CTA")
        if "pboost.me" in html or "yeahpromos.com" in html:
            errors.append(f"{rel} invented affiliate hop")
        if "amazon.com/dp/" in html or "m.media-amazon.com" in html:
            errors.append(f"{rel} invented Amazon gallery or hop")
        if re.search(r"\$\d", html):
            errors.append(f"{rel} invented price")
        if "10%" in html or "12%" in html:
            errors.append(f"{rel} invented or leftover was/%")
        leaked = sorted({a for a in ASIN_RE.findall(html.upper()) if a in occupied})
        if leaked:
            errors.append(f"{rel} occupied ASIN leaked {', '.join(leaked)}")
        visible = html_without_ld_json(html)
        hit = VISITOR_LEAK_RE.search(visible)
        if hit:
            errors.append(f"{rel} visitor leak {hit.group(0)!r}")
        for banned in (
            "inventory_blocked",
            "need_fill",
            "fromsll",
            "PartnerBoost",
            "YeahPromos",
            "ASIN",
        ):
            if banned == "need_fill":
                if re.search(r">[^<]*need_fill", visible):
                    errors.append(f"{rel} visible need_fill jargon")
                continue
            if banned in visible:
                errors.append(f"{rel} visible ops jargon {banned}")

        faqs = extract_visible_faqs(html)
        ld = faq_ld_pairs(html)
        if not (3 <= len(faqs) <= 5):
            errors.append(f"{rel} FAQ count={len(faqs)} (need 3–5)")
        if faqs != ld:
            errors.append(f"{rel} FAQPage JSON-LD does not match visible FAQ")
        blob = " ".join(q + " " + a for q, a in faqs).lower()
        if "what does" not in blob or "who should skip" not in blob:
            errors.append(f"{rel} FAQ missing type-07 job / skip questions")
        if "commission" in blob or "how do you rank" in blob:
            errors.append(f"{rel} FAQ still has methodology / commission")

        item_list = next((b for b in jsonld_blocks(html) if b.get("@type") == "ItemList"), None)
        if not item_list:
            errors.append(f"{rel} missing ItemList JSON-LD")
        elif item_list.get("numberOfItems") != 0:
            errors.append(f"{rel} ItemList numberOfItems expected 0")
        elif item_list.get("itemListElement"):
            errors.append(f"{rel} ItemList has invented elements")

        canonical = f"https://moretop10.com{url}"
        if f'<link rel="canonical" href="{canonical}"/>' not in html:
            errors.append(f"{rel} canonical mismatch")

    if errors:
        print("p3_water_bestof_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print(
        "p3_water_bestof_assert ok "
        "(well 0 / hard 0 / need_fill / 61 occupied banned)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
