#!/usr/bin/env python3
"""P4 scenario best-of — unpublished shells, no invented inventory."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p4_scenario import (  # noqa: E402
    DRAFT_COMMENT,
    OCCUPIED_PATH,
    ROBOTS_NOINDEX,
    SCENES,
    TEMPLATE_LEFTOVER,
    TEMPLATE_LEFTOVER_NON_HUMIDIFIER,
    banned_for,
    load_occupied,
    products_path,
)
from seo_geo import VISITOR_LEAK_RE, extract_visible_faqs, html_without_ld_json  # noqa: E402

INV_JSON = SITE / "data" / "p4-scenario-inventory-2026-10-23.json"
INV_MD = SITE / "data" / "p4-scenario-inventory-2026-10-23.md"
NOTES = ROOT / "notes" / "p4-scenario-draft-2026-10-23.md"
ASIN_RE = re.compile(r"\bB0[A-Z0-9]{8}\b")
OFF_LIMITS = (
    "computer-speakers/index.html",
    "computer-speakers/comparison/index.html",
    "tower-fans/index.html",
    "tower-fans/comparison/index.html",
)


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
    if f'name="robots" content="{ROBOTS_NOINDEX}"' not in html:
        errors.append(f"{rel} robots is not {ROBOTS_NOINDEX}")
    if scene["h1"] not in html:
        errors.append(f"{rel} missing h1")
    if "Priya Nair" not in html:
        errors.append(f"{rel} author is not Priya Nair")
    if 'class="landing-related-cluster"' in html:
        errors.append(f"{rel} must not ship landing-related-cluster (landing only)")
    leftovers = list(TEMPLATE_LEFTOVER)
    if scene["slug"] != "humidifiers":
        leftovers.extend(TEMPLATE_LEFTOVER_NON_HUMIDIFIER)
    for leak in leftovers:
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

    if not NOTES.exists():
        errors.append("missing notes/p4-scenario-draft-2026-10-23.md")
    if not OCCUPIED_PATH.exists():
        errors.append("missing occupied ASIN list")
        print("p4_scenario_assert failed:\n- " + "\n- ".join(errors))
        return 1
    occupied = load_occupied()
    expected_groups = {
        "litter_main": 10,
        "video_doorbells": 10,
        "robot_pet_hair": 10,
        "humidifiers_babies": 10,
        "pillows_neck_pain": 6,
    }
    for key, n in expected_groups.items():
        got = len(occupied.get(key) or [])
        if got != n:
            errors.append(f"occupied {key} expected {n}, got {got}")

    if not INV_JSON.exists():
        errors.append("missing inventory json")
        print("p4_scenario_assert failed:\n- " + "\n- ".join(errors))
        return 1
    if not INV_MD.exists():
        errors.append("missing inventory markdown")

    inv = json.loads(INV_JSON.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")
    if inv.get("published") is not False:
        errors.append("inventory published must be false")
    if inv.get("live") is True or inv.get("merged") is True:
        errors.append("inventory must stay draft (not live/merged)")
    if inv.get("pillows_hub") != "exists_p2_not_recreated":
        errors.append("inventory must record existing pillows hub")

    pages = {row.get("path"): row for row in inv.get("pages") or []}
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    html_map = (SITE / "sitemap" / "index.html").read_text(encoding="utf-8")
    pillows_shortlist = json.loads((SITE / "data" / "shortlist-pillows.json").read_text(encoding="utf-8"))
    if pillows_shortlist.get("density") != 6:
        errors.append("do not recreate / empty the P2 pillows hub shortlist")

    for scene in SCENES:
        url = f"/{scene['slug']}/{scene['path']}/"
        rel = f"{scene['slug']}/{scene['path']}/index.html"
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        banned = banned_for(scene, occupied)
        errors.extend(common_page_errors(rel, html, scene, banned))

        row = pages.get(url) or {}
        if row.get("published") is not False:
            errors.append(f"{url} inventory published must be false")
        if row.get("type") != "07-best-of":
            errors.append(f"{url} type must be 07-best-of")

        prod = json.loads(products_path(scene).read_text(encoding="utf-8"))
        if prod.get("published") is not False:
            errors.append(f"{products_path(scene).name} published must be false")
        prod_asins = [p.get("asin") for p in prod.get("products") or []]
        inv_asins = [p.get("asin") for p in row.get("picks") or []]
        if prod_asins != inv_asins:
            errors.append(f"{url} products shell drifted from inventory")
        if any(a in banned for a in prod_asins):
            errors.append(f"{url} reused a banned ASIN")

        n = int(row.get("density") or 0)
        if n == 0:
            if row.get("fill_status") != "need_fill":
                errors.append(f"{url} empty shell must be need_fill")
            if prod.get("products"):
                errors.append(f"{url} products shell invented picks")
            if html.count('class="bestof-visit-card"'):
                errors.append(f"{rel} unexpected visit cards")
            if "btn-cta-yellow" in html or "pboost.me" in html:
                errors.append(f"{rel} invented Check price CTA")
            if re.search(r"\$\d", html):
                errors.append(f"{rel} invented price")
            if "Density is honest at 0" not in html:
                errors.append(f"{rel} missing honest density 0 copy")
            if 'data-fill-status="need_fill"' not in html:
                errors.append(f"{rel} missing need_fill empty stub")
            item_list = next((b for b in jsonld_blocks(html) if b.get("@type") == "ItemList"), None)
            if not item_list or item_list.get("numberOfItems") != 0:
                errors.append(f"{rel} ItemList numberOfItems expected 0")
        else:
            if row.get("fill_status") != "filled":
                errors.append(f"{url} density {n} must be filled")
            if html.count('class="bestof-visit-card"') != n:
                errors.append(f"{rel} visit cards != {n}")
            if "uid=fromsll" not in html:
                errors.append(f"{rel} packed tracks missing uid=fromsll")

        landing = (SITE / scene["slug"] / "index.html").read_text(encoding="utf-8")
        if scene["path"] not in landing:
            errors.append(f"{scene['slug']} landing missing cluster link {url}")
        loc = f"https://moretop10.com{url}"
        if f"<loc>{loc}</loc>" not in sitemap:
            errors.append(f"sitemap missing {url}")
        if f'href="..{url}"' not in html_map:
            errors.append(f"sitemap/index.html missing {url}")

        if scene["slug"] == "pillows":
            if "best-pillows-for-neck-pain" not in landing:
                errors.append("pillows landing lost neck-pain cluster")
            if "B0F6LR3CYP" not in landing and pillows_shortlist.get("density") != 6:
                errors.append("do not recreate the P2 pillows hub")

        if scene["slug"] == "humidifiers" and "best-humidifiers-for-babies" not in landing:
            errors.append("humidifiers landing lost babies cluster")

    for rel in OFF_LIMITS:
        if not (SITE / rel).exists():
            errors.append(f"off-limits hub missing {rel}")

    if errors:
        print("p4_scenario_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    need = inv.get("need_fill") or []
    print(f"p4_scenario_assert ok (8 hubs / fill={inv.get('fill_status')} / need_fill={len(need)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
