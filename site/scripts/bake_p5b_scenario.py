#!/usr/bin/env python3
"""Bake P5b MT10 scenario best-of pages (office long-hours + stomach pillows + tower bedroom stub).

Draft only. Do not merge / Live deploy. No Lab / RR / OL.
Do not recreate live parent hubs. Do not rebind CTA to YeahPromos.
Do not scaffold mattresses-for-back-pain (brand_gate FAIL · Sweetnight-only).
Do not create OUT niches (back-sleepers pillow, heavy-people mattress).

Hard rules:
  - Type-07 pages only. published=false / noindex until 部署上线.
  - Use L1 pack ASINs / roles / prices / tracks as given. No invented ASINs / was / %.
  - Density 10 where stock allows. Tower bedroom is an honest stub (2).
  - Collision bans: office back-pain, pillow neck+side, tower hub, global occupied.
  - No accessories as hero picks. Lab independent.
  - Reviews: none (Top + Upgrade articles do not exist for these scenes).

Usage:
    python3 site/scripts/bake_p5b_scenario.py
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
SCRIPTS = Path(__file__).resolve().parent
DATA = SITE / "data"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from affiliate_uid import classify_network  # noqa: E402
from bake_p4_scenario import (  # noqa: E402
    ACCESSORY_RE,
    ASIN_RE,
    TEMPLATE,
    TEMPLATE_LEFTOVER,
    TEMPLATE_LEFTOVER_NON_HUMIDIFIER,
    _asin_set,
    _esc,
    add_landing_cluster,
    bump_or_insert_sitemap,
    clone_chrome,
    healthy_track,
    replace_head,
    replace_main,
    scene_article,
    scene_faqs,
    token_env,
)
from seo_geo import LIVE, ROBOTS_NOINDEX, rewrite_visible_jargon, set_robots_meta  # noqa: E402

from stamp_guard import bake_stamp_date  # noqa: E402

DATE = bake_stamp_date("2026-10-24")
DRAFT_COMMENT = (
    "<!-- waiting_for_部署上线: yes. P5b scenario best-of draft only. "
    "Do not merge. Do not Cloudflare Live deploy. published=false. -->"
)
OCCUPIED_PATH = DATA / "p5b-occupied-asins-2026-10-24.json"
PACK_CANDIDATES = (
    Path("/workspace/shared/mt10-p5b-fill-pack-2026-10-24.json"),
    DATA / "mt10-p5b-fill-pack-2026-10-24.json",
    DATA / "p5b-l1-fill-pack-2026-10-24.json",
)
PACK_INREPO = DATA / "p5b-l1-fill-pack-2026-10-24.json"
PARENT_HUBS = (
    "office-chairs",
    "pillows",
    "tower-fans",
    "mattresses",
)
SKIPPED = (
    {
        "path": "best-mattresses-for-back-pain",
        "url": "/mattresses/best-mattresses-for-back-pain/",
        "reason": "brand_gate FAIL · Sweetnight-only — do not scaffold until multi-brand",
    },
)
OUT_NICHES = (
    "best-pillows-for-back-sleepers",
    "best-mattresses-for-heavy-people",
)
TOWER_OFF_ROUTE_RE = re.compile(
    r"pedestal fan|table fan|ceiling fan|box fan|desk fan|usb fan",
    re.I,
)

SCENES: list[dict[str, Any]] = [
    {
        "n": 1,
        "slug": "office-chairs",
        "name": "Office Chairs",
        "path": "best-office-chairs-for-long-hours",
        "label": "Best for long hours",
        "keyword": "best office chairs for long hours",
        "title": "Best Office Chairs for Long Hours",
        "h1": "Best Office Chairs for Long Hours (2026)",
        "job": "office chairs built for long sitting days, not a paste of the back-pain shortlist",
        "confirm": (
            "Confirm lumbar support, adjustability, and seat comfort notes on the retailer page. "
            "We do not invent hour ratings."
        ),
        "skip": (
            "Skip this slice if you want a back-pain chair already on Best office chairs for "
            "back pain. Seat cushions and lumbar pillows are not a primary pick here."
        ),
        "lede": (
            "Long-hour desk work is a full office-chair job — not a lumbar pillow and not a "
            "paste of the back-pain shortlist."
        ),
        "ban_groups": ["office_back_pain"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-office-chairs-for-back-pain", "label": "Best for back pain"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-office-chairs.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-office-chairs.jpg",
    },
    {
        "n": 2,
        "slug": "pillows",
        "name": "Pillows",
        "path": "best-pillows-for-stomach-sleepers",
        "label": "Best for stomach sleepers",
        "keyword": "best pillows for stomach sleepers",
        "title": "Best Pillows for Stomach Sleepers",
        "h1": "Best Pillows for Stomach Sleepers (2026)",
        "job": "stomach-sleeper pillows that are not already on the neck-pain or side-sleeper slices",
        "confirm": (
            "Confirm loft, fill, and whether the listing names stomach sleepers on the retailer page."
        ),
        "skip": (
            "Skip this slice if you want a neck-pain or side-sleeper pillow. Those jobs live on "
            "Best pillows for neck pain and Best pillows for side sleepers."
        ),
        "lede": (
            "Stomach-sleeper pillows are a low-loft and fill job — not a pillowcase and not a "
            "paste of the neck-pain or side-sleeper shortlists."
        ),
        "ban_groups": ["pillow_neck_side"],
        "cross_ban_scenes": [],
        "siblings": [
            {"path": "best-pillows-for-neck-pain", "label": "Best for neck pain"},
            {"path": "best-pillows-for-side-sleepers", "label": "Best for side sleepers"},
        ],
        "density_expected": 10,
        "stub": False,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-pillows.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-pillows.jpg",
    },
    {
        "n": 3,
        "slug": "tower-fans",
        "name": "Tower Fans",
        "path": "best-tower-fans-for-bedroom",
        "label": "Best for bedroom",
        "keyword": "best tower fans for bedroom",
        "title": "Best Tower Fans for Bedroom",
        "h1": "Best Tower Fans for Bedroom (2026)",
        "job": "tower fans for a bedroom that are not already on the main tower-fans chart",
        "confirm": (
            "Confirm noise notes, oscillation, and whether the listing names bedroom use on the "
            "retailer page. We do not invent dB ratings."
        ),
        "skip": (
            "Skip this slice if you want a pedestal, table, or ceiling fan, or a tower already "
            "on the main tower-fans comparison. Replacement filters are not a primary pick here."
        ),
        "lede": (
            "Bedroom tower airflow is a full tower-fan job — not a filter pack and not a paste "
            "of the parent chart."
        ),
        "ban_groups": ["tower_hub"],
        "cross_ban_scenes": [],
        "siblings": [],
        "density_expected": 2,
        "stub": True,
        "og_image": f"{LIVE}/assets/img/lifestyle/cmp-hero-tower-fans.jpg",
        "lifestyle_src": "../../assets/img/lifestyle/cmp-hero-tower-fans.jpg",
    },
]


def load_occupied() -> dict[str, set[str]]:
    blob = json.loads(OCCUPIED_PATH.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = {}
    for key, values in (blob.get("scene_ban_keys") or {}).items():
        out[key] = _asin_set(values)
    out["global"] = _asin_set(blob.get("flat"))
    if not out["global"]:
        extra: set[str] = set()
        for key, values in out.items():
            if key != "global":
                extra |= values
        out["global"] = extra
    return out


def pack_blob(pack: dict[str, Any] | None, scene: dict[str, Any]) -> dict[str, Any]:
    if not pack:
        return {}
    scenes = pack.get("scenes") or {}
    return (
        scenes.get(scene["path"])
        or scenes.get(f"/{scene['slug']}/{scene['path']}/")
        or scenes.get(scene.get("scene_slug") or "")
        or {}
    )


def sibling_asins_from_pack(pack: dict[str, Any] | None) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for scene in SCENES:
        asins: set[str] = set()
        for row in pack_blob(pack, scene).get("products") or pack_blob(pack, scene).get("picks") or []:
            asin = str(row.get("asin") or "").strip().upper()
            if ASIN_RE.fullmatch(asin):
                asins.add(asin)
        out[scene["path"]] = asins
    return out


def banned_for(
    scene: dict[str, Any],
    occupied: dict[str, set[str]],
    sibling_asins: dict[str, set[str]] | None = None,
) -> set[str]:
    banned = set(occupied.get("global") or ())
    for key in scene.get("ban_groups") or []:
        banned |= occupied.get(key) or set()
    for sib in scene.get("cross_ban_scenes") or []:
        banned |= (sibling_asins or {}).get(sib) or set()
    return banned


def find_fill_pack() -> Path | None:
    for path in PACK_CANDIDATES:
        if path.exists():
            return path
    return None


def pick_from_pack(row: dict[str, Any], banned: set[str], scene: dict[str, Any]) -> dict[str, Any] | None:
    asin = str(row.get("asin") or "").strip().upper()
    title = str(row.get("title") or "").strip()
    track = healthy_track(row.get("track_url") or row.get("affiliate_link"))
    if not asin or not title or not track:
        return None
    if not ASIN_RE.fullmatch(asin):
        return None
    if asin.upper().startswith("B0X") and set(asin[2:]) <= set("X"):
        return None
    if asin in banned:
        return None
    if ACCESSORY_RE.search(title):
        return None
    if scene["path"] == "best-tower-fans-for-bedroom" and TOWER_OFF_ROUTE_RE.search(title):
        return None
    network = classify_network(row.get("track_url") or row.get("affiliate_link") or "")
    if network != "pb":
        return None
    price = row.get("price")
    price_str = row.get("price_str") or row.get("price_displayed")
    if price is not None and not price_str:
        price_str = f"${price}"
    return {
        "asin": asin,
        "title": title,
        "title_source": "l1_pack",
        "brand": str(row.get("brand") or "").strip() or None,
        "role": str(row.get("role") or "").strip() or None,
        "affiliate_network": "pb",
        "affiliate_link": track,
        "track_status": "ok",
        "price": f"{price}" if price is not None else None,
        "price_displayed": price_str,
        "image": None,
        "feature_bullets": [],
        "availability": row.get("availability"),
    }


def scene_picks_from_pack(
    pack: dict[str, Any] | None, scene: dict[str, Any], banned: set[str]
) -> list[dict[str, Any]]:
    if not pack:
        return []
    blob = pack_blob(pack, scene)
    picks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in blob.get("products") or blob.get("picks") or []:
        pick = pick_from_pack(row, banned, scene)
        if not pick or pick["asin"] in seen:
            continue
        seen.add(pick["asin"])
        picks.append(pick)
    return picks


def products_path(scene: dict[str, Any]) -> Path:
    return DATA / f"products-{scene['path']}.json"


def write_products_shell(scene: dict[str, Any], picks: list[dict[str, Any]]) -> None:
    dest = products_path(scene)
    dest.write_text(
        json.dumps(
            {
                "path": f"/{scene['slug']}/{scene['path']}/",
                "published": False,
                "fill_status": "filled" if picks else "need_fill",
                "waiting_for_部署上线": True,
                "stub": bool(scene.get("stub")),
                "products": [
                    {
                        "asin": p["asin"],
                        "title": p["title"],
                        "role": p.get("role"),
                        "brand": p.get("brand"),
                        "track_url": p.get("affiliate_link"),
                        "price": p.get("price"),
                        "price_str": p.get("price_displayed"),
                    }
                    for p in picks
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _pick_public(pick: dict[str, Any]) -> dict[str, Any]:
    return {
        "asin": pick["asin"],
        "title": pick["title"],
        "role": pick.get("role"),
        "brand": pick.get("brand"),
        "affiliate_link": pick.get("affiliate_link"),
        "track_status": pick.get("track_status"),
        "price": pick.get("price_displayed"),
        "image": None,
    }


def hub_product_count(slug: str) -> int:
    html = (SITE / slug / "index.html").read_text(encoding="utf-8")
    return len(set(ASIN_RE.findall(html.upper())))


def build_inventory(
    by_path: dict[str, list[dict[str, Any]]],
    pack_path: Path | None,
    occupied: dict[str, set[str]],
) -> dict[str, Any]:
    tokens = token_env()
    pages = []
    for scene in SCENES:
        picks = by_path[scene["path"]]
        n = len(picks)
        pages.append(
            {
                "n": scene["n"],
                "path": f"/{scene['slug']}/{scene['path']}/",
                "type": "07-best-of",
                "parent": f"/{scene['slug']}/",
                "published": False,
                "robots": ROBOTS_NOINDEX,
                "density": n,
                "density_target": 10,
                "density_expected": scene["density_expected"],
                "stub": bool(scene.get("stub")),
                "fill_status": "filled" if n else "need_fill",
                "cta_status": "pb_fromsll" if n else "empty",
                "cta_rule": "PB fromsll only when a verified track exists; never invent hops; do not rebind to YP",
                "reviews": "none — Top pick + Upgrade articles do not exist for this scene",
                "ban_groups": scene["ban_groups"],
                "cross_ban_scenes": scene["cross_ban_scenes"],
                "picks": [_pick_public(p) for p in picks],
            }
        )
    filled = sum(1 for row in pages if row["fill_status"] == "filled")
    hub_counts = {hub: hub_product_count(hub) for hub in ("mattresses", "pillows", "office-chairs")}
    return {
        "date": DATE,
        "batch": "P5b",
        "waiting_for_部署上线": True,
        "published": False,
        "live": False,
        "merged": False,
        "independent_of_shortlist_lab": True,
        "do_not_touch": ["Lab", "RR", "OL", "#54 home nav", "#55 stamp", "parent hub cards"],
        "parent_hubs": "exist_not_recreated",
        "soft_parent_densify": (
            "cluster_links_only — L1 pack has no extra hub SKUs; "
            f"hub ASINs mattresses={hub_counts['mattresses']} "
            f"pillows={hub_counts['pillows']} office={hub_counts['office-chairs']}; "
            "prefer not block scenes"
        ),
        "skipped": SKIPPED,
        "out_of_scope": list(OUT_NICHES),
        "fill_pack": str(pack_path) if pack_path else None,
        "fill_status": "partial" if 0 < filled < len(pages) else ("filled" if filled else "need_fill"),
        "need_fill": [row["path"] for row in pages if row["fill_status"] == "need_fill"],
        "counts": {scene["path"]: len(by_path[scene["path"]]) for scene in SCENES},
        "sources": {
            "1_pb": {
                "live_query": "skipped_no_token" if not tokens["available"] else "ran",
                "note": tokens["note"],
            },
            "2_yp": {
                "live_query": "skipped_yp_timeout_or_500",
                "note": "YP unused. Pack is PB-only. Live CTA stays PB ?uid=fromsll.",
            },
            "l1_fill_pack": pack_path.name if pack_path else None,
        },
        "occupied_groups": {k: sorted(v) for k, v in occupied.items() if k != "global"},
        "occupied_global_n": len(occupied.get("global") or ()),
        "pages": pages,
        "notes": [
            "No invented ASINs, prices, was/%, gallery, or Check price hops.",
            "Parent hubs already exist. Not recreated. Soft densify = cluster links only.",
            "published=false / noindex until a later 部署上线 order.",
            "Independent of Shortlist Lab.",
            "Mattress back-pain skipped (brand_gate FAIL · Sweetnight-only).",
            "Tower bedroom is an honest 2-product stub. Do not pad.",
        ],
    }


def assert_clean_page(
    html: str, scene: dict[str, Any], banned: set[str], picks: list[dict[str, Any]]
) -> None:
    errors: list[str] = []
    n = len(picks)
    if DRAFT_COMMENT not in html:
        errors.append("missing waiting_for_部署上线 draft comment")
    if f'name="robots" content="{ROBOTS_NOINDEX}"' not in html:
        errors.append("robots is not noindex,follow")
    leftovers = list(TEMPLATE_LEFTOVER)
    if scene["slug"] != "humidifiers":
        leftovers.extend(TEMPLATE_LEFTOVER_NON_HUMIDIFIER)
    leftovers.extend(
        (
            "inventory_blocked",
            "best-tower-fans-for-bedrooms",
            "best-mattresses-for-back-pain",
            "best-pillows-for-back-sleepers",
            "best-mattresses-for-heavy-people",
        )
    )
    for leak in leftovers:
        if leak in html:
            errors.append(f"template leftover {leak!r}")
    visits = html.count('class="bestof-visit-card"')
    if visits != n:
        errors.append(f"visit cards={visits} (need {n})")
    inline_need = min(3, n)
    if html.count('class="inline-pick-card"') != inline_need:
        errors.append(f"inline picks != {inline_need}")
    if n == 0:
        if "btn-cta-yellow" in html:
            errors.append("invented Check price CTA")
        if "pboost.me" in html or "yeahpromos.com" in html:
            errors.append("invented affiliate hop")
        if re.search(r"\$\d", html):
            errors.append("invented price")
        if "Density is honest at 0" not in html:
            errors.append("missing honest density copy")
    else:
        if html.count("pboost.me") < n:
            errors.append("missing PB tracks on visit cards")
        if "uid=fromsll" not in html:
            errors.append("PB tracks missing uid=fromsll")
        if "yeahpromos.com" in html:
            errors.append("YP rebind is not allowed")
        if f"Density is honest at {n}" not in html:
            errors.append("missing honest density copy")
        for pick in picks:
            if pick["asin"] not in html:
                errors.append(f"missing packed ASIN {pick['asin']}")
            if pick["affiliate_link"] not in html:
                errors.append(f"missing track for {pick['asin']}")
    if "amazon.com/dp/" in html or "m.media-amazon.com" in html:
        errors.append("invented Amazon gallery or hop")
    if "10%" in html or "12%" in html:
        errors.append("invented or leftover was/%")
    if "was $" in html.lower() or "list_price" in html:
        errors.append("invented or leftover was/list_price")
    for asin in banned:
        if asin in html:
            errors.append(f"banned ASIN leaked {asin}")
    visible_article = ""
    start = html.find('<article class="landing-article">')
    end = html.find("</article>", start) if start >= 0 else -1
    if start >= 0 and end >= 0:
        visible_article = html[start:end]
    if "kids-bikes" in visible_article:
        errors.append("kids-bikes chrome leaked into visitor article")
    if errors:
        raise SystemExit(f"{scene['path']} bake assert failed: " + "; ".join(errors))


def write_scene(
    scene: dict[str, Any],
    banned: set[str],
    picks: list[dict[str, Any]],
) -> None:
    faqs = scene_faqs(scene, picks)
    out_rel = f"{scene['slug']}/{scene['path']}/index.html"
    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{LIVE}/{scene['slug']}/{scene['path']}/"
    title = f"{scene['title']} | MoreTop10"
    n = len(picks)
    if n:
        desc = (
            f"{scene['lede']} This best-of lists {n} verified products that fit this job."
        )
        page_desc = (
            f"Editorial slice of {scene['name'].lower()} for {scene['keyword']} — "
            f"honest density {n} from verified retailer links."
        )
    else:
        desc = (
            f"{scene['lede']} This best-of stays empty until a verified retailer "
            "link exists — we do not invent a padded Top 10."
        )
        page_desc = (
            f"Editorial slice of {scene['name'].lower()} for {scene['keyword']} — "
            "honest density 0 until a verified retailer link exists."
        )
    html = clone_chrome(out_rel, scene["slug"])
    html = replace_head(
        html,
        title=title,
        description=desc,
        url=url,
        og_image=scene["og_image"],
        faqs=faqs,
        page_desc=page_desc,
        picks=picks,
        scene=scene,
    )
    html = replace_main(
        html,
        h1=scene["h1"],
        article=scene_article(scene, faqs, picks),
        scene=scene,
    )
    html = rewrite_visible_jargon(html)
    html = set_robots_meta(html, ROBOTS_NOINDEX)
    if DRAFT_COMMENT not in html:
        html = html.replace("<head>", "<head>\n" + DRAFT_COMMENT, 1)
    assert_clean_page(html, scene, banned, picks)
    dest.write_text(html, encoding="utf-8")


def patch_html_sitemap() -> None:
    path = SITE / "sitemap" / "index.html"
    html = path.read_text(encoding="utf-8")
    for scene in SCENES:
        href = f'../{scene["slug"]}/{scene["path"]}/'
        if href not in html:
            marker = f'<a href="../{scene["slug"]}/comparison/">Compare</a>'
            if marker not in html:
                raise SystemExit(f"sitemap/index.html missing {scene['slug']} row")
            html = html.replace(
                marker,
                f'{marker} · <a href="{href}">{_esc(scene["label"])}</a>',
                1,
            )
        li_re = re.compile(
            rf'(<li><a href="../{re.escape(scene["slug"])}/">.*?</li>)'
        )
        match = li_re.search(html)
        if match and href not in match.group(1):
            html = (
                html[: match.end() - 5]
                + f' · <a href="{href}">{_esc(scene["label"])}</a></li>'
                + html[match.end() :]
            )
    path.write_text(html, encoding="utf-8")


def write_inventory(inv: dict[str, Any]) -> None:
    dest = DATA / "p5b-scenario-inventory-2026-10-24.json"
    dest.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    rows = []
    for row in inv["pages"]:
        rows.append(
            f"| `{row['path']}` | **{row['density']}** | `{row['fill_status']}` | "
            f"{row['cta_status']} | none |"
        )
    need = inv.get("need_fill") or []
    md = DATA / "p5b-scenario-inventory-2026-10-24.md"
    md.write_text(
        "\n".join(
            [
                "# P5b scenario best-of inventory (2026-10-24)",
                "",
                "**waiting_for_部署上线:** yes",
                "**published:** false / noindex",
                "**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.",
                "**Parent hubs:** already exist — not recreated.",
                "",
                "## Fill status",
                "",
                f"- Global fill status: `{inv['fill_status']}`",
                f"- Fill pack: `{inv.get('fill_pack') or 'missing — need_fill shells'}`",
                f"- Occupied collision set: `{inv.get('occupied_global_n')} ASINs`",
                f"- Affiliate tokens on VM: `{inv['sources']['1_pb']['live_query']}` / `{inv['sources']['2_yp']['live_query']}`",
                f"- Hubs that need_fill: {len(need)}",
                f"- Soft parent densify: `{inv.get('soft_parent_densify')}`",
                "",
                "## Paths",
                "",
                "| Path | Density | Fill | CTA | Reviews |",
                "| --- | --- | --- | --- | --- |",
                *rows,
                "",
                "## Skipped",
                "",
                "- `/mattresses/best-mattresses-for-back-pain/` — brand_gate FAIL · Sweetnight-only. Not scaffolded.",
                "- OUT: back-sleepers pillow, heavy-people mattress — not created.",
                "",
                "## Hard rules kept",
                "",
                "- No invented ASINs / prices / was / % / gallery / CTAs.",
                "- No accessories as primary picks.",
                "- Office back-pain / pillow neck+side / tower hub collision banned.",
                "- Tower bedroom is an honest 2-product stub. Do not pad.",
                "- Reviews skipped.",
                "- Independent of Shortlist Lab.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def refuse_skipped_pages() -> None:
    mattress = SITE / "mattresses" / "best-mattresses-for-back-pain" / "index.html"
    if mattress.exists():
        raise SystemExit("must not scaffold /mattresses/best-mattresses-for-back-pain/")
    for slug in OUT_NICHES:
        if slug.startswith("best-pillows"):
            path = SITE / "pillows" / slug / "index.html"
        else:
            path = SITE / "mattresses" / slug / "index.html"
        if path.exists():
            raise SystemExit(f"must not create OUT niche {slug}")


def main() -> int:
    if not TEMPLATE.exists():
        raise SystemExit(f"missing type-07 template {TEMPLATE}")
    for hub in PARENT_HUBS:
        if not (SITE / hub / "index.html").exists():
            raise SystemExit(f"expected existing /{hub}/ hub — do not invent a new hub here")
    occupied = load_occupied()
    pack_path = find_fill_pack()
    pack = None
    if pack_path:
        pack = json.loads(pack_path.read_text(encoding="utf-8"))
        if pack_path.resolve() != PACK_INREPO.resolve():
            shutil.copy2(pack_path, PACK_INREPO)
            pack_path = PACK_INREPO
    siblings = sibling_asins_from_pack(pack)
    by_path: dict[str, list[dict[str, Any]]] = {}
    for scene in SCENES:
        banned = banned_for(scene, occupied, siblings)
        picks = scene_picks_from_pack(pack, scene, banned)
        expected = int(scene["density_expected"])
        if pack and len(picks) != expected:
            raise SystemExit(
                f"{scene['path']} expected density {expected} from L1 pack, got {len(picks)}"
            )
        by_path[scene["path"]] = picks
        write_products_shell(scene, picks)
        write_scene(scene, banned, picks)
        add_landing_cluster(scene)
    refuse_skipped_pages()
    inv = build_inventory(by_path, pack_path, occupied)
    write_inventory(inv)
    bump_or_insert_sitemap([f"{s['slug']}/{s['path']}/" for s in SCENES])
    patch_html_sitemap()
    counts = "/".join(str(len(by_path[s["path"]])) for s in SCENES)
    print(
        "bake_p5b_scenario ok "
        f"(fill={inv['fill_status']} counts={counts} mattress=skipped)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
