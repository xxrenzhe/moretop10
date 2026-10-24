#!/usr/bin/env python3
"""P6c scenario best-of — unpublished shells, products SoT ASINs only, collision bans."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(SITE / "scripts"))

from bake_p6c_scenario import (  # noqa: E402
    DATE,
    DRAFT_COMMENT,
    OCCUPIED_PATH,
    OUT_NICHES,
    PARENT_HUBS,
    PRIOR_KEEP_UNPUBLISHED,
    ROBOTS_NOINDEX,
    SCENES,
    SKIPPED,
    banned_for,
    leftover_terms,
    load_occupied,
    parse_price,
    products_path,
    sibling_asins_from_pack,
)
from seo_geo import VISITOR_LEAK_RE, extract_visible_faqs, html_without_ld_json  # noqa: E402

INV_JSON = SITE / "data" / "p6c-scenario-inventory-2026-10-24.json"
INV_MD = SITE / "data" / "p6c-scenario-inventory-2026-10-24.md"
NOTES = ROOT / "notes" / "p6c-scenario-draft-2026-10-24.md"
PACK_PATH = SITE / "data" / "p6c-l1-fill-pack-2026-10-24.json"
ASIN_RE = re.compile(r"\bB0[A-Z0-9]{8}\b")
OFF_LIMITS = (
    "litter-boxes/best-litter-boxes-for-large-cats/index.html",
    "hearing-aids/best-hearing-aids-for-tinnitus/index.html",
    "mattresses/best-mattresses-for-hanging/index.html",
    "light-therapy/best-red-light-therapy-masks/index.html",
    "robot-vacuums/best-robot-mops/index.html",
)
EXPECTED_TOTAL = 56
SIBLING_MIN = {
    "projector_siblings": 26,
    "humidifier_siblings": 19,
    "doormat_siblings": 20,
    "nc_siblings": 10,
    "bt_siblings": 10,
    "chair_siblings": 28,
}
NEW_PRODUCTS = {scene["path"] for scene in SCENES}


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
    for leak in leftover_terms(scene):
        if leak in html:
            errors.append(f"{rel} leftover {leak!r}")
    if "amazon.com/dp/" in html or "m.media-amazon.com" in html:
        errors.append(f"{rel} invented Amazon gallery or hop")
    if "10%" in html or "12%" in html:
        errors.append(f"{rel} invented or leftover was/%")
    if "yeahpromos.com" in html:
        errors.append(f"{rel} YP rebind is not allowed")
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
    article_start = html.find('<article class="landing-article">')
    article_end = html.find("</article>", article_start) if article_start >= 0 else -1
    if article_start >= 0 and article_end >= 0:
        article = html_without_ld_json(html[article_start:article_end])
        if "kids-bikes" in article or "inventory_blocked" in article:
            errors.append(f"{rel} kids-bikes / inventory chrome leaked into visitor article")
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
    if f"Last verified {DATE}" not in html:
        errors.append(f"{rel} Last verified stamp is not {DATE}")
    return errors


def main() -> int:
    errors: list[str] = []

    if not NOTES.exists():
        errors.append("missing notes/p6c-scenario-draft-2026-10-24.md")
    if not OCCUPIED_PATH.exists():
        errors.append("missing occupied ASIN list")
        print("p6c_scenario_assert failed:\n- " + "\n- ".join(errors))
        return 1
    occupied = load_occupied()
    for key, n in SIBLING_MIN.items():
        got = len(occupied.get(key) or [])
        if got < n:
            errors.append(f"occupied {key} expected >={n}, got {got}")
    if len(occupied.get("global") or []) < 1000:
        errors.append(
            f"occupied global expected the L1 collision set, got {len(occupied.get('global') or [])}"
        )

    if not INV_JSON.exists():
        errors.append("missing inventory json")
        print("p6c_scenario_assert failed:\n- " + "\n- ".join(errors))
        return 1
    if not INV_MD.exists():
        errors.append("missing inventory markdown")
    if not PACK_PATH.exists():
        errors.append("missing p6c-l1-fill-pack-2026-10-24.json")

    inv = json.loads(INV_JSON.read_text(encoding="utf-8"))
    if inv.get("waiting_for_部署上线") is not True:
        errors.append("inventory missing waiting_for_部署上线")
    if inv.get("published") is not False:
        errors.append("inventory published must be false")
    if inv.get("live") is True or inv.get("merged") is True:
        errors.append("inventory must stay draft (not live/merged)")
    if inv.get("parent_hubs") != "exist_not_recreated":
        errors.append("inventory must record existing parent hubs")
    if inv.get("independent_of_shortlist_lab") is not True:
        errors.append("inventory must stay independent of Lab")
    skipped_urls = {row.get("url") for row in inv.get("skipped") or SKIPPED}
    if "/litter-boxes/best-litter-boxes-for-large-cats/" not in skipped_urls:
        errors.append("inventory must record litter large-cats shortfall skip")

    pack = json.loads(PACK_PATH.read_text(encoding="utf-8")) if PACK_PATH.exists() else {}
    siblings = sibling_asins_from_pack(pack)
    pages = {row.get("path"): row for row in inv.get("pages") or []}
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    html_map = (SITE / "sitemap" / "index.html").read_text(encoding="utf-8")
    asins_by_path: dict[str, list[str]] = {}

    for hub in PARENT_HUBS:
        if not (SITE / hub / "index.html").exists():
            errors.append(f"parent hub missing /{hub}/")
        if not (SITE / hub / "comparison" / "index.html").exists():
            errors.append(f"parent comparison stub missing /{hub}/comparison/")
        if not (SITE / hub / "reviews" / "index.html").exists():
            errors.append(f"parent reviews stub missing /{hub}/reviews/")

    for rel in OFF_LIMITS:
        if (SITE / rel).exists():
            errors.append(f"must not exist {rel}")
    if (SITE / "data" / "products-best-litter-boxes-for-large-cats.json").exists():
        errors.append("must not write products-best-litter-boxes-for-large-cats.json")

    for niche in OUT_NICHES:
        if (SITE / "litter-boxes" / niche / "index.html").exists():
            errors.append(f"OUT niche created {niche}")
        if (SITE / "hearing-aids" / niche / "index.html").exists():
            errors.append(f"OUT niche created {niche}")

    landing_keep = {
        "projectors": (
            "best-projectors-for-bedroom",
            "best-projectors-for-outdoor",
            "best-projectors-for-home-theater",
        ),
        "humidifiers": (
            "best-humidifiers-for-babies",
            "best-humidifiers-for-large-rooms",
        ),
        "office-chairs": (
            "best-office-chairs-for-back-pain",
            "best-office-chairs-for-long-hours",
            "best-office-chairs-for-gaming",
        ),
        "bluetooth-speakers": ("best-bluetooth-speakers-for-outdoor",),
    }

    for scene in SCENES:
        url = f"/{scene['slug']}/{scene['path']}/"
        rel = f"{scene['slug']}/{scene['path']}/index.html"
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        banned = banned_for(scene, occupied, siblings)
        errors.extend(common_page_errors(rel, html, scene, banned))

        row = pages.get(url) or {}
        if row.get("published") is not False:
            errors.append(f"{url} inventory published must be false")
        if row.get("type") != "07-best-of":
            errors.append(f"{url} type must be 07-best-of")

        prod = json.loads(products_path(scene).read_text(encoding="utf-8"))
        if prod.get("published") is not False:
            errors.append(f"{products_path(scene).name} published must be false")
        if prod.get("waiting_for_部署上线") is not True:
            errors.append(f"{products_path(scene).name} missing waiting_for_部署上线")
        prod_asins = [p.get("asin") for p in prod.get("products") or []]
        inv_asins = [p.get("asin") for p in row.get("picks") or []]
        if prod_asins != inv_asins:
            errors.append(f"{url} products shell drifted from inventory")
        pack_asins = [
            p.get("asin")
            for p in (pack.get("scenes") or {}).get(scene["path"], {}).get("products") or []
        ]
        if prod_asins != pack_asins:
            errors.append(f"{url} products SoT drifted from L1 pack ASINs")
        if any(a in banned for a in prod_asins):
            errors.append(f"{url} reused a banned ASIN")
        asins_by_path[scene["path"]] = [str(a).upper() for a in prod_asins if a]

        n = int(row.get("density") or 0)
        expected = int(scene["density_expected"])
        if n != expected:
            errors.append(f"{url} expected density {expected} from products SoT, got {n}")
        if row.get("fill_status") != "filled":
            errors.append(f"{url} density {n} must be filled")
        if html.count('class="bestof-visit-card"') != n:
            errors.append(f"{rel} visit cards != {n}")
        if "uid=fromsll" not in html:
            errors.append(f"{rel} packed tracks missing uid=fromsll")
        if html.count("pboost.me") < n:
            errors.append(f"{rel} missing PB tracks")
        if "../../" + scene["slug"] + "/comparison/" not in html:
            errors.append(f"{rel} missing comparison widget/link")
        if "list_price" in html or "was $" in html.lower():
            errors.append(f"{rel} rendered list_price / was")

        if scene["path"] == "best-office-chairs-under-200":
            for pick in prod.get("products") or []:
                price = parse_price(pick)
                if price is None or price > 200:
                    errors.append(
                        f"{url} chair {pick.get('asin')} price {price} is not honest ≤$200"
                    )

        landing = (SITE / scene["slug"] / "index.html").read_text(encoding="utf-8")
        if scene["path"] not in landing:
            errors.append(f"{scene['slug']} landing missing cluster link {url}")
        for keep in landing_keep.get(scene["slug"]) or ():
            if keep not in landing:
                errors.append(f"{scene['slug']} landing lost existing cluster {keep}")
        loc = f"https://moretop10.com{url}"
        if f"<loc>{loc}</loc>" not in sitemap:
            errors.append(f"sitemap missing {url}")
        if f'href="..{url}"' not in html_map:
            errors.append(f"sitemap/index.html missing {url}")

    litter_landing = (SITE / "litter-boxes" / "index.html").read_text(encoding="utf-8")
    if "best-litter-boxes-for-large-cats" in litter_landing:
        errors.append("litter hub must not link skipped large-cats scene")

    for name in PRIOR_KEEP_UNPUBLISHED:
        path = SITE / "data" / name
        if not path.exists():
            errors.append(f"missing prior unpublished shell {name}")
            continue
        blob = json.loads(path.read_text(encoding="utf-8"))
        if blob.get("published") is True:
            errors.append(f"must not flip {name} to published=true")

    for path in (SITE / "data").glob("products-best-*.json"):
        if path.stem.replace("products-", "") in NEW_PRODUCTS:
            continue
        blob = json.loads(path.read_text(encoding="utf-8"))
        if blob.get("published") is True:
            errors.append(f"must not flip {path.name} to published=true")

    p6a_bed = SITE / "projectors" / "best-projectors-for-bedroom" / "index.html"
    if p6a_bed.exists():
        bed = p6a_bed.read_text(encoding="utf-8")
        if f'name="robots" content="{ROBOTS_NOINDEX}"' not in bed:
            errors.append("P6a bedroom projector must stay noindex")
        if "published=true" in bed:
            errors.append("P6a bedroom projector must not flip published=true")
    p6b_game = SITE / "office-chairs" / "best-office-chairs-for-gaming" / "index.html"
    if p6b_game.exists():
        game = p6b_game.read_text(encoding="utf-8")
        if f'name="robots" content="{ROBOTS_NOINDEX}"' not in game:
            errors.append("P6b gaming chair scene must stay noindex")
        if "published=true" in game:
            errors.append("P6b gaming chair scene must not flip published=true")

    all_asins = [a for values in asins_by_path.values() for a in values]
    if len(all_asins) != EXPECTED_TOTAL or len(set(all_asins)) != EXPECTED_TOTAL:
        errors.append(
            f"expected {EXPECTED_TOTAL} distinct ASINs, got {len(all_asins)} / unique {len(set(all_asins))}"
        )

    if errors:
        print("p6c_scenario_assert failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    counts = "/".join(str(len(asins_by_path[s["path"]])) for s in SCENES)
    print(f"p6c_scenario_assert ok (6 scenes / {counts} / litter skipped / p6a+p6b unpublished)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
