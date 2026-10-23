#!/usr/bin/env python3
"""P3 water-filter scenario best-of — well 8 / hard 0 shortfall, no occupied reuse."""

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
    EXPECTED_HARD,
    EXPECTED_WELL,
    LAB_P3_BAN,
    OCCUPIED_PATH,
    PACK_PATH,
    PRODUCTS_HARD_PATH,
    PRODUCTS_WELL_PATH,
    SCENES,
    TEMPLATE_LEFTOVER,
    load_banned,
    load_occupied,
)
from seo_geo import VISITOR_LEAK_RE, extract_visible_faqs, html_without_ld_json  # noqa: E402

INV_JSON = SITE / "data" / "p3-water-bestof-inventory-2026-10-23.json"
INV_MD = SITE / "data" / "p3-water-bestof-inventory-2026-10-23.md"
WELL_REL = "water-filters/best-water-filters-for-well-water/index.html"
HARD_REL = "water-filters/best-water-filters-for-hard-water/index.html"
WELL_URL = "/water-filters/best-water-filters-for-well-water/"
HARD_URL = "/water-filters/best-water-filters-for-hard-water/"
WELL_ASINS = [
    "B0H29R9MJW",
    "B07C5P8NC7",
    "B0C9ZY8L1C",
    "B0F43LV539",
    "B09SM2ZN3X",
    "B0F43PC2JX",
    "B0DTKC58F6",
    "B08XXJSN29",
]
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


def common_page_errors(rel: str, html: str, scene: dict, banned: set[str]) -> list[str]:
    errors: list[str] = []
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
    if 'class="landing-related-cluster"' in html:
        errors.append(f"{rel} must not ship landing-related-cluster (landing only)")
    for leak in TEMPLATE_LEFTOVER:
        if leak in html:
            errors.append(f"{rel} leftover {leak!r}")
    if "amazon.com/dp/" in html or "m.media-amazon.com" in html:
        errors.append(f"{rel} invented Amazon gallery or hop")
    if "10%" in html or "12%" in html:
        errors.append(f"{rel} invented or leftover was/%")
    leaked = sorted({a for a in ASIN_RE.findall(html.upper()) if a in banned})
    if leaked:
        errors.append(f"{rel} banned ASIN leaked {', '.join(leaked)}")
    visible = html_without_ld_json(html)
    hit = VISITOR_LEAK_RE.search(visible)
    if hit:
        errors.append(f"{rel} visitor leak {hit.group(0)!r}")
    for banned_word in ("inventory_blocked", "PartnerBoost", "YeahPromos", "ASIN"):
        if banned_word in visible:
            errors.append(f"{rel} visible ops jargon {banned_word}")
    if re.search(r">[^<]*need_fill", visible):
        errors.append(f"{rel} visible need_fill jargon")
    if re.search(r">[^<]*fromsll", visible):
        errors.append(f"{rel} visible fromsll jargon")
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
    return errors


def main() -> int:
    errors: list[str] = []

    if not OCCUPIED_PATH.exists():
        errors.append("missing occupied ASIN list")
        print("p3_water_bestof_assert failed:\n- " + "\n- ".join(errors))
        return 1
    occupied = load_occupied()
    banned = load_banned()
    if len(occupied) != 61:
        errors.append(f"occupied list expected 61, got {len(occupied)}")
    if "B0H5JZZ3GK" not in occupied:
        errors.append("occupied list missing WHF21-PBL B0H5JZZ3GK")
    if len(LAB_P3_BAN) != 6 or not LAB_P3_BAN <= banned:
        errors.append("Lab P3 six-ASIN ban missing")
    if not PACK_PATH.exists() or not PRODUCTS_WELL_PATH.exists() or not PRODUCTS_HARD_PATH.exists():
        errors.append("missing L1 fill pack or products JSON")

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
    if inv.get("occupied_count") != 61:
        errors.append(f"inventory occupied_count expected 61, got {inv.get('occupied_count')}")

    pages = {row.get("path"): row for row in inv.get("pages") or []}
    well = pages.get(WELL_URL) or {}
    hard = pages.get(HARD_URL) or {}
    if well.get("density") != EXPECTED_WELL or well.get("fill_status") != "filled":
        errors.append(f"well expected density {EXPECTED_WELL} filled, got {well.get('density')} {well.get('fill_status')}")
    if well.get("cta_status") != "pb_fromsll":
        errors.append("well cta_status expected pb_fromsll")
    well_asins = [p.get("asin") for p in well.get("picks") or []]
    if well_asins != WELL_ASINS:
        errors.append(f"well picks mismatch pack order: {well_asins}")
    if any(a in banned for a in well_asins):
        errors.append("well reused a banned ASIN")
    if hard.get("density") != EXPECTED_HARD or hard.get("fill_status") != "inventory_shortfall":
        errors.append(
            f"hard expected density 0 inventory_shortfall, got {hard.get('density')} {hard.get('fill_status')}"
        )
    if hard.get("picks"):
        errors.append("hard inventory invented picks")
    if hard.get("cta_status") != "empty":
        errors.append("hard cta_status expected empty")
    if hard.get("inventory_shortfall") is not True:
        errors.append("hard must be marked inventory_shortfall")

    landing = (SITE / "water-filters" / "index.html").read_text(encoding="utf-8")
    if DRAFT_COMMENT not in landing:
        errors.append("water-filters landing missing draft comment")
    cluster = re.search(r'<p class="landing-related-cluster">.*?</p>', landing, flags=re.S)
    if not cluster:
        errors.append("water-filters landing missing related-cluster")
    else:
        block = cluster.group(0)
        for href in ("best-water-filters-for-well-water/", "best-water-filters-for-hard-water/"):
            if href not in block:
                errors.append(f"landing cluster missing {href}")
    if "B0H5JZZ3GK" not in landing:
        errors.append("do not recreate / empty the live water-filters main chart")

    comparison = (SITE / "water-filters" / "comparison" / "index.html").read_text(encoding="utf-8")
    if "best-water-filters-for-well-water" in comparison:
        errors.append("related-cluster leaked onto comparison (landing only)")

    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    html_map = (SITE / "sitemap" / "index.html").read_text(encoding="utf-8")
    for url in (WELL_URL, HARD_URL):
        loc = f"https://moretop10.com{url}"
        if f"<loc>{loc}</loc>" not in sitemap:
            errors.append(f"sitemap missing {url}")
        if f'href="..{url}"' not in html_map:
            errors.append(f"sitemap/index.html missing {url}")

    well_html = (SITE / WELL_REL).read_text(encoding="utf-8")
    hard_html = (SITE / HARD_REL).read_text(encoding="utf-8")
    errors.extend(common_page_errors(WELL_REL, well_html, SCENES[0], banned))
    errors.extend(common_page_errors(HARD_REL, hard_html, SCENES[1], banned))

    if well_html.count('class="bestof-visit-card"') != EXPECTED_WELL:
        errors.append(f"well visit cards != {EXPECTED_WELL}")
    if well_html.count('class="inline-pick-card"') != 3:
        errors.append("well inline picks != 3")
    if well_html.count("pboost.me") < EXPECTED_WELL:
        errors.append("well missing PB Check price hops")
    if "uid=fromsll" not in well_html:
        errors.append("well PB tracks missing uid=fromsll")
    if "Density is honest at 8" not in well_html:
        errors.append("well missing honest density 8 copy")
    for asin in WELL_ASINS:
        if asin not in well_html:
            errors.append(f"well missing packed ASIN {asin}")
    well_list = next((b for b in jsonld_blocks(well_html) if b.get("@type") == "ItemList"), None)
    if not well_list or well_list.get("numberOfItems") != 8:
        errors.append("well ItemList numberOfItems expected 8")
    elif len(well_list.get("itemListElement") or []) != 8:
        errors.append("well ItemList elements != 8")

    if hard_html.count('class="bestof-visit-card"'):
        errors.append("hard unexpected visit cards")
    if hard_html.count('class="inline-pick-card"'):
        errors.append("hard unexpected inline picks")
    if "btn-cta-yellow" in hard_html or "pboost.me" in hard_html:
        errors.append("hard invented Check price CTA")
    if re.search(r"\$\d", hard_html):
        errors.append("hard invented price")
    if "Density is honest at 0" not in hard_html:
        errors.append("hard missing honest density 0 copy")
    if 'data-fill-status="inventory_shortfall"' not in hard_html:
        errors.append("hard missing inventory_shortfall empty stub")
    hard_list = next((b for b in jsonld_blocks(hard_html) if b.get("@type") == "ItemList"), None)
    if not hard_list or hard_list.get("numberOfItems") != 0:
        errors.append("hard ItemList numberOfItems expected 0")
    elif hard_list.get("itemListElement"):
        errors.append("hard ItemList has invented elements")

    if errors:
        print("p3_water_bestof_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("p3_water_bestof_assert ok (well 8 / hard 0 shortfall / 61+6 banned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
