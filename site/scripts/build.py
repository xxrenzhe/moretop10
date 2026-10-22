#!/usr/bin/env python3
"""MoreTop10 site bake — chrome + SEO/GEO (local only).

This repo clone does not ship the full inventory generator. `build.py`:

  1. Non-home header mega + mobile: Overview → /{slug}/ plus Compare / Reviews
  2. Footer Categories column: every ALL_CATS (MVP + NON_MVP) landing
  3. Home grid: pin tier=extended / newly published cats, is-more when i >= 8
  4. comparison/ + reviews/ hubs: Related jump back to the landing
  5. Category hubs: honest CollectionPage + ItemList + Product/Offer JSON-LD
  6. /authors/ hub 200 + sitemap entry
  7. llms.txt + /.well-known/llms.txt (Top-pick #geo-ASIN when ASIN is known)
  8. robot-vacuums-match/: cluster link + noindex; drop from sitemap
  9. P1: sitewide robots max-image-preview; How to Cite + #geo-ASIN on
     comparison cards, reviews hubs, and individual review articles
 10. Light G-ENGAGE (sample hub+comparison): Answer-first lead + Check-price
     with price near CTA. Structural only — not bounce %.

Product cards, ASINs, and affiliate URLs are copied from Live snapshots — never
invented here. Do not wrangler-deploy from this script.

Usage:
    python3 site/scripts/build.py
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
CACHE = SITE / ".cache"
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from chrome import (  # noqa: E402
    ensure_hub_reciprocity,
    ensure_tv_home_tile,
    expected_wwnn_codes,
    home_tile_width_codes,
    inject_nav_css,
    rel_prefix,
    reorder_home_tiles,
    rewrite_compare_cta,
    rewrite_footer,
    rewrite_non_home_nav,
    tile_is_tv,
)
from seo_geo import (  # noqa: E402
    LIVE,
    ROBOTS_INDEX,
    apply_hub_page,
    build_llms_txt,
    extract_authors_from_home,
    extract_comparison_products,
    extract_landing_picks,
    merge_hub_products,
    patch_robots,
    patch_sitemap,
    render_authors_hub,
    review_article_specs,
)
from site_config import (  # noqa: E402
    ALL_CATS,
    CATS_BY_SLUG,
    HOME_VISIBLE_TILES,
    load_site_config,
)

UA = "MoreTop10Bake/1.0 (+seo-geo-p1)"
AUTHOR_SLUGS = [
    "alex-rivera",
    "jordan-lee",
    "sam-chen",
    "riley-park",
    "marcus-webb",
    "priya-nair",
    "moretop10-editors",
]


def page_specs(cfg: dict) -> list[dict]:
    specs: list[dict] = [
        {"live": f"{LIVE}/", "out": "index.html", "kind": "home"},
        {"live": f"{LIVE}/about-us/", "out": "about-us/index.html", "kind": "page"},
        {
            "live": f"{LIVE}/robot-vacuums-match/",
            "out": "robot-vacuums-match/index.html",
            "kind": "match",
        },
    ]
    for cat in cfg["ALL_CATS"]:
        slug = cat["slug"]
        specs.append({"live": f"{LIVE}/{slug}/", "out": f"{slug}/index.html", "kind": "landing", "slug": slug})
        specs.append(
            {
                "live": f"{LIVE}/{slug}/comparison/",
                "out": f"{slug}/comparison/index.html",
                "kind": "comparison",
                "slug": slug,
            }
        )
        specs.append(
            {
                "live": f"{LIVE}/{slug}/reviews/",
                "out": f"{slug}/reviews/index.html",
                "kind": "reviews",
                "slug": slug,
            }
        )
    for slug in AUTHOR_SLUGS:
        specs.append(
            {
                "live": f"{LIVE}/authors/{slug}/",
                "out": f"authors/{slug}/index.html",
                "kind": "author",
                "author": slug,
            }
        )
    return specs


class LiveNotFound(RuntimeError):
    """Live snapshot 404 — skip this page rather than invent HTML."""


def fetch(url: str, dest: Path, *, force: bool = False) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not force and dest.exists() and dest.stat().st_size > 500:
        return dest.read_text(encoding="utf-8")
    last_err: Exception | None = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as resp:
                text = resp.read().decode("utf-8", errors="replace")
            dest.write_text(text, encoding="utf-8")
            return text
        except Exception as exc:  # noqa: BLE001 — bake must retry flaky Live snapshots
            last_err = exc
            code = getattr(exc, "code", None)
            if code == 404:
                raise LiveNotFound(f"404 {url}") from exc
            if attempt < 3:
                import time

                time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch failed {url}: {last_err}") from last_err


def prefetch(specs: list[dict]) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    extras = [
        (f"{LIVE}/llms.txt", CACHE / "llms.txt"),
        (f"{LIVE}/robots.txt", CACHE / "robots.txt"),
        (f"{LIVE}/sitemap.xml", CACHE / "sitemap.xml"),
    ]
    jobs = [(s["live"], CACHE / s["out"].replace("/", "__")) for s in specs] + extras

    def one(url: str, dest: Path) -> str:
        try:
            fetch(url, dest)
        except LiveNotFound:
            return f"404:{dest.name}"
        return dest.name

    with ThreadPoolExecutor(max_workers=12) as pool:
        futs = [pool.submit(one, url, dest) for url, dest in jobs]
        for fut in as_completed(futs):
            fut.result()


def bake_page(spec: dict, cfg: dict, cmp_html_by_slug: dict[str, str]) -> Path | None:
    cats = cfg["ALL_CATS"]
    out_rel = spec["out"]
    prefix = rel_prefix(out_rel)
    cache_name = out_rel.replace("/", "__")
    try:
        html = fetch(spec["live"], CACHE / cache_name)
    except LiveNotFound:
        if spec.get("kind") == "review":
            print(f"  skip 404 {spec['live']}")
            return None
        raise
    kind = spec["kind"]
    slug = spec.get("slug")
    cat = cfg["CATS_BY_SLUG"].get(slug) if slug else None

    if kind != "home":
        html = inject_nav_css(html)
    html = rewrite_non_home_nav(html, cats, prefix)
    html = rewrite_footer(html, cats, prefix)
    html = rewrite_compare_cta(html, prefix, slug, kind)

    if kind == "home":
        html = reorder_home_tiles(html, cfg["CATS_BY_SLUG"], cfg["home_visible_tiles"])
        html = ensure_tv_home_tile(
            html, cfg["CATS_BY_SLUG"], cfg["home_visible_tiles"]
        )

    if kind in {"comparison", "reviews"}:
        html = ensure_hub_reciprocity(html, kind)

    cmp_html = (
        cmp_html_by_slug.get(slug or "")
        if kind in {"landing", "reviews", "review"}
        else None
    )
    html = apply_hub_page(
        html,
        kind=kind,
        cat=cat,
        cmp_html=cmp_html,
        prefix=prefix,
        review_slug=spec.get("review_slug"),
    )

    dest = SITE / out_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    return dest


def _first_home_tiles(html: str, n: int = 8) -> list[str]:
    from chrome import split_home_tiles, tile_slug

    m = re.search(
        r'<div class="home-tile-grid"[^>]*>(.*?)</div>\s*<button type="button" class="home-show-more"',
        html,
        re.S,
    )
    if not m:
        return []
    tiles = split_home_tiles(m.group(1))
    slugs = set(CATS_BY_SLUG)
    out = []
    for tile in tiles[:n]:
        if tile_is_tv(tile):
            slug = "tv"
        else:
            slug = tile_slug(tile, slugs) or "?"
        more = " is-more" if "is-more" in tile[:160] else ""
        out.append(f"{slug}{more}")
    return out


def _ld_types(html: str) -> set[str]:
    types: set[str] = set()
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            data = json.loads(blob)
        except json.JSONDecodeError:
            continue

        def walk(x: object) -> None:
            if isinstance(x, dict):
                t = x.get("@type")
                if isinstance(t, list):
                    types.update(str(i) for i in t)
                elif t:
                    types.add(str(t))
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for i in x:
                    walk(i)

        walk(data)
    return types


def verify(cfg: dict) -> None:
    home = (SITE / "index.html").read_text(encoding="utf-8")
    about = (SITE / "about-us" / "index.html").read_text(encoding="utf-8")
    cmp = (SITE / "kids-bikes" / "comparison" / "index.html").read_text(encoding="utf-8")
    rev = (SITE / "kids-bikes" / "reviews" / "index.html").read_text(encoding="utf-8")
    fry = (SITE / "air-fryers" / "index.html").read_text(encoding="utf-8")
    authors = (SITE / "authors" / "index.html").read_text(encoding="utf-8")
    match = (SITE / "robot-vacuums-match" / "index.html").read_text(encoding="utf-8")
    llms = (SITE / "llms.txt").read_text(encoding="utf-8")
    well = (SITE / ".well-known" / "llms.txt").read_text(encoding="utf-8")
    robots = (SITE / "robots.txt").read_text(encoding="utf-8")
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    errors: list[str] = []

    if rel_prefix("index.html") != "":
        errors.append("rel_prefix home")
    if rel_prefix("about-us/index.html") != "../":
        errors.append("rel_prefix about")
    if rel_prefix("kids-bikes/comparison/index.html") != "../../":
        errors.append("rel_prefix comparison")

    from chrome import split_home_tiles, tile_slug

    gm = re.search(
        r'<div class="home-tile-grid"[^>]*>(.*?)</div>\s*<button type="button" class="home-show-more"',
        home,
        re.S,
    )
    if not gm:
        errors.append("home tile grid missing")
    else:
        tiles = split_home_tiles(gm.group(1))
        slugs = set(CATS_BY_SLUG)
        kids = [(i, t) for i, t in enumerate(tiles) if tile_slug(t, slugs) == "kids-bikes"]
        if not kids:
            errors.append("kids-bikes tile missing on home")
        else:
            i, t = kids[0]
            if i >= HOME_VISIBLE_TILES:
                errors.append(f"kids-bikes tile at slot {i} (need < {HOME_VISIBLE_TILES})")
            if i not in (0, 1):
                errors.append(f"kids-bikes tile at slot {i} (need row-1 wide slot 0 or 1)")
            if "is-more" in t[:200]:
                errors.append("kids-bikes tile still has is-more")
        robot = next((t for t in tiles if tile_slug(t, slugs) == "robot-vacuums"), "")
        if robot and "robot-vacuums-match/" in robot and "robot-vacuums/" not in robot:
            errors.append("home robot tile still orphans the hub in favor of match/")
        # CSS ≥960px is WWNN (2.15fr 2.15fr 1fr 1fr). Check every complete row
        # plus the first 8 visible tiles.
        n_check = max(8, (len(tiles) // 4) * 4)
        n_check = min(n_check, len(tiles))
        got_codes = home_tile_width_codes(tiles, n_check)
        want_codes = expected_wwnn_codes(n_check)
        if got_codes != want_codes:
            errors.append(
                "home tiles WWNN expected "
                + "".join(want_codes)
                + " got "
                + "".join(got_codes)
            )
        visible = tiles[:HOME_VISIBLE_TILES]
        if any("is-more" in t[:200] for t in visible):
            errors.append("first visible home tiles still have is-more")
        if any("is-more" not in t[:200] for t in tiles[HOME_VISIBLE_TILES:]):
            errors.append("tiles past home_visible_tiles must have is-more")
        tv_idxs = [i for i, t in enumerate(tiles) if tile_is_tv(t)]
        if not tv_idxs:
            errors.append("home missing editorial /tv/ tile in grid")
        else:
            tv_i = tv_idxs[0]
            if tv_i >= HOME_VISIBLE_TILES:
                errors.append(f"tv tile at slot {tv_i} (need < {HOME_VISIBLE_TILES})")
            if tv_i not in (2, 3):
                errors.append(f"tv tile at slot {tv_i} (need row-1 narrow slot 2 or 3)")

    if "nav-home-simple" not in home:
        errors.append("home header should stay nav-home-simple")
    if 'class="mega"' in home and "site-header-home" in home:
        if "mega-overview" in home.split("<main", 1)[0]:
            errors.append("home header must not grow a category mega")

    head = about.split("<main", 1)[0]
    if "kids-bikes/" not in head or "kids-bikes/comparison/" not in head:
        errors.append("about mega missing kids-bikes landing and/or comparison")
    if not re.search(r'href="\.\./kids-bikes/"', head):
        errors.append("about mega missing ../kids-bikes/ landing href")
    if not re.search(r'href="\.\./\.\./kids-bikes/"', cmp.split("<main", 1)[0]):
        errors.append("comparison mega missing ../../kids-bikes/ landing href")

    if not re.search(r'href="(?:\.\./)*kids-bikes/"', home) and 'href="kids-bikes/"' not in home:
        errors.append("home footer missing kids-bikes landing")
    if "kids-bikes/" not in about.split("<footer", 1)[-1]:
        errors.append("about footer missing kids-bikes")

    if not re.search(r'href="(?:\.\./|../kids-bikes/)"', cmp) and 'href="../"' not in cmp:
        if "kids-bikes/" not in cmp:
            errors.append("comparison missing landing href")
    if "Category overview" not in cmp and "Full guide" not in cmp:
        errors.append("comparison missing Category overview / Full guide copy")
    if 'href="../"' not in rev and "kids-bikes/" not in rev:
        errors.append("reviews hub missing landing href")
    if "Category overview" not in rev and "Full guide" not in rev:
        errors.append("reviews hub missing landing href copy")

    # Compare CTA: comparison must not self-link to comparison.
    cmp_head = cmp.split("<main", 1)[0]
    if re.search(r'nav-cta-soft" href="[^"]*comparison/', cmp_head):
        errors.append("kids comparison Compare CTA still points at a comparison URL")
    fry_head = fry.split("<main", 1)[0]
    if not re.search(r'nav-cta-soft" href="[^"]*air-fryers/comparison/', fry_head):
        errors.append("air-fryers hub Compare CTA should point at air-fryers/comparison/")
    for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', fry, re.S):
        if '"@type":"FAQPage"' not in blob:
            continue
        if '"name":"Compare"' in blob or '"name":"Categories"' in blob:
            errors.append("air-fryers FAQPage ingested nav <details>")

    fry_types = _ld_types(fry)
    for needed in ("CollectionPage", "ItemList", "Product", "Offer", "FAQPage", "SpeakableSpecification"):
        if needed not in fry_types:
            errors.append(f"air-fryers hub missing JSON-LD {needed}")
    if "AggregateRating" in fry_types:
        errors.append("air-fryers hub leaked AggregateRating")
    kids_hub = (SITE / "kids-bikes" / "index.html").read_text(encoding="utf-8")
    if "ItemList" not in _ld_types(kids_hub):
        errors.append("kids-bikes hub missing ItemList")
    if "AggregateRating" in _ld_types(kids_hub):
        errors.append("kids-bikes hub leaked AggregateRating")
    if 'class="geo-answer-first"' not in fry and "geo-answer-first" not in fry:
        errors.append("air-fryers hub missing Speakable geo-answer-first")
    if "geo-cite-strip" not in fry:
        errors.append("air-fryers hub missing cite strip")
    if "How to cite:" not in fry:
        errors.append("air-fryers hub cite strip missing How to cite label")
    if ROBOTS_INDEX not in fry:
        errors.append("air-fryers hub missing robots max-image-preview")
    if ROBOTS_INDEX not in home:
        errors.append("home missing robots max-image-preview")
    if ROBOTS_INDEX not in about:
        errors.append("about missing robots max-image-preview")
    if ROBOTS_INDEX not in rev:
        errors.append("kids-bikes reviews hub missing robots max-image-preview")
    if "geo-cite-strip" not in rev:
        errors.append("kids-bikes reviews hub missing cite strip")

    fry_cmp = (SITE / "air-fryers" / "comparison" / "index.html").read_text(encoding="utf-8")
    if 'id="geo-' not in fry_cmp:
        errors.append("air-fryers comparison missing #geo-ASIN on product cards")
    cite_at = fry_cmp.find('class="geo-cite-strip"')
    last_card = fry_cmp.rfind('class="product-card"')
    if cite_at == -1:
        errors.append("air-fryers comparison missing cite strip")
    elif last_card != -1 and cite_at < last_card:
        errors.append("air-fryers comparison cite strip is still inside the product stack")
    if ROBOTS_INDEX not in fry_cmp:
        errors.append("air-fryers comparison missing robots max-image-preview")

    tests_dir = str(ROOT / "tests")
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    from footer_cats_columns_assert import sample_errors as footer_cats_errors  # noqa: E402
    from g_engage_assert import sample_errors  # noqa: E402

    errors.extend(footer_cats_errors(SITE))
    errors.extend(sample_errors(SITE))

    sample_review = SITE / "air-fryers" / "reviews" / "cosori-twinfry-9-qt-double-air" / "index.html"
    if not sample_review.exists():
        errors.append("missing sample review article air-fryers/reviews/cosori-twinfry-9-qt-double-air/")
    else:
        rev_html = sample_review.read_text(encoding="utf-8")
        if ROBOTS_INDEX not in rev_html:
            errors.append("review article missing robots max-image-preview")
        if "geo-cite-strip" not in rev_html:
            errors.append("review article missing cite strip")
        if 'id="geo-' not in rev_html:
            errors.append("review article missing #geo-ASIN")
        if re.search(r"completeness gate|publishable|inventory-blocked|PartnerBoost", rev_html, re.I):
            errors.append("review article still contains visitor jargon")
        if "AggregateRating" in rev_html:
            errors.append("review article leaked AggregateRating")

    faq_chunk = fry[fry.lower().find("faq") :] if "faq" in fry.lower() else fry
    for term in ("publishable", "inventory-blocked", "completeness gate", "PartnerBoost"):
        if re.search(term, faq_chunk, re.I) and "<details" in faq_chunk:
            # flag only if it sits inside FAQ details
            if re.search(rf"<details[^>]*>[^<]*{term}", fry, re.I | re.S):
                errors.append(f"air-fryers FAQ still contains {term}")

    if "<h1>" not in authors or "Our editors" not in authors:
        errors.append("authors hub missing H1 listing")
    for slug in AUTHOR_SLUGS:
        if f"authors/{slug}/" not in authors and f"{slug}/" not in authors:
            errors.append(f"authors hub missing link to {slug}")
    if "CollectionPage" not in _ld_types(authors):
        errors.append("authors hub missing CollectionPage")
    if "https://moretop10.com/authors/" not in sitemap:
        errors.append("sitemap missing /authors/")
    if "robot-vacuums-match" in sitemap:
        errors.append("sitemap still lists robot-vacuums-match/")
    if "/search/" in sitemap:
        errors.append("sitemap lists /search/")

    if 'content="noindex,follow"' not in match:
        errors.append("match page should be noindex,follow")
    if 'rel="canonical" href="https://moretop10.com/robot-vacuums/"' not in match:
        errors.append("match page canonical should point at /robot-vacuums/")
    rv = (SITE / "robot-vacuums" / "index.html").read_text(encoding="utf-8")
    if "robot-vacuums-match" not in rv:
        errors.append("robot-vacuums hub should cluster-link the match demo")

    if "#geo-" not in llms:
        errors.append("llms.txt missing #geo-ASIN top-pick links")
    if "## Methodology" not in llms:
        errors.append("llms.txt missing Methodology")
    if "/authors/" not in llms:
        errors.append("llms.txt missing authors hub")
    if "aff_pb_autoads" in llms or "uid=fromsll" in llms:
        errors.append("llms.txt still contains affiliate-backend jargon")
    if well != llms:
        errors.append(".well-known/llms.txt must match /llms.txt")
    if "Content-Signal:" not in robots:
        errors.append("robots.txt missing Content-Signal")
    if "OAI-SearchBot" not in robots:
        errors.append("robots.txt missing AI search bots")

    missing_hubs = [c["slug"] for c in cfg["ALL_CATS"] if not (SITE / c["slug"] / "index.html").exists()]
    if missing_hubs:
        errors.append("missing hub HTML: " + ", ".join(missing_hubs))
    if any(c["slug"] == "tv" for c in cfg["ALL_CATS"]):
        errors.append("tv must not be registered in ALL_CATS (density exception)")
    if not (SITE / "tv" / "index.html").exists():
        errors.append("missing editorial hub tv/")
    if not (SITE / "tv" / "smart-tv-ad-alternatives" / "index.html").exists():
        errors.append("missing editorial L2 tv/smart-tv-ad-alternatives/")
    if 'data-editorial-cluster="tv"' not in home:
        errors.append("home missing editorial /tv/ tile")

    if errors:
        raise SystemExit("verify failed:\n- " + "\n- ".join(errors))

    print("verify ok")
    print("  home first 8 tiles:", ", ".join(_first_home_tiles(home)))
    if gm:
        print("  home WWNN:", "".join(home_tile_width_codes(tiles, min(len(tiles), 8))))
    print("  ALL_CATS:", ", ".join(c["slug"] for c in ALL_CATS))
    print("  authors:", ", ".join(AUTHOR_SLUGS))


def main() -> None:
    cfg = load_site_config()
    specs = page_specs(cfg)
    CACHE.mkdir(parents=True, exist_ok=True)
    sitemap_raw = fetch(f"{LIVE}/sitemap.xml", CACHE / "sitemap.xml")
    review_specs = review_article_specs(
        sitemap_raw, {c["slug"] for c in cfg["ALL_CATS"]}
    )
    specs.extend(review_specs)
    print(
        f"bake {len(cfg['ALL_CATS'])} cats "
        f"(MVP={len(cfg['MVP_CATS'])} NON_MVP={len(cfg['NON_MVP_CATS'])}) "
        f"pages={len(specs)} review_articles={len(review_specs)}"
    )
    print("  prefetch live snapshots…")
    prefetch(specs)

    cmp_html_by_slug: dict[str, str] = {}
    for spec in specs:
        if spec["kind"] == "comparison":
            cmp_html_by_slug[spec["slug"]] = fetch(spec["live"], CACHE / spec["out"].replace("/", "__"))

    wrote = 0
    skipped = 0
    for spec in specs:
        dest = bake_page(spec, cfg, cmp_html_by_slug)
        if dest is None:
            skipped += 1
            continue
        wrote += 1
        print(f"  wrote {dest.relative_to(ROOT)}")
    print(f"  baked {wrote} pages (skipped {skipped} missing live snapshots)")

    home_html = (SITE / "index.html").read_text(encoding="utf-8")
    authors = extract_authors_from_home(home_html)
    about = (SITE / "about-us" / "index.html").read_text(encoding="utf-8")
    hub = render_authors_hub(chrome_html=about, authors=authors, prefix="../")
    authors_dest = SITE / "authors" / "index.html"
    authors_dest.parent.mkdir(parents=True, exist_ok=True)
    authors_dest.write_text(hub, encoding="utf-8")
    print(f"  wrote {authors_dest.relative_to(ROOT)}")

    products_by_slug: dict[str, list] = {}
    for cat in cfg["ALL_CATS"]:
        slug = cat["slug"]
        landing = (SITE / slug / "index.html").read_text(encoding="utf-8")
        cmp = cmp_html_by_slug.get(slug, "")
        products_by_slug[slug] = merge_hub_products(
            extract_landing_picks(landing),
            extract_comparison_products(cmp, slug),
        )

    live_llms = fetch(f"{LIVE}/llms.txt", CACHE / "llms.txt")
    llms = build_llms_txt(
        cats=cfg["ALL_CATS"],
        products_by_slug=products_by_slug,
        live_llms=live_llms,
        authors=authors,
    )
    (SITE / "llms.txt").write_text(llms, encoding="utf-8")
    well = SITE / ".well-known" / "llms.txt"
    well.parent.mkdir(parents=True, exist_ok=True)
    well.write_text(llms, encoding="utf-8")
    print("  wrote site/llms.txt")
    print("  wrote site/.well-known/llms.txt")

    robots = patch_robots(fetch(f"{LIVE}/robots.txt", CACHE / "robots.txt"))
    (SITE / "robots.txt").write_text(robots, encoding="utf-8")
    print("  wrote site/robots.txt")

    sitemap = patch_sitemap(
        fetch(f"{LIVE}/sitemap.xml", CACHE / "sitemap.xml"),
        authors_exist=bool(authors),
        drop_match=True,
    )
    (SITE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("  wrote site/sitemap.xml")

    from bake_tv import main as bake_tv_main  # noqa: E402

    bake_tv_main()
    verify(cfg)


if __name__ == "__main__":
    main()
