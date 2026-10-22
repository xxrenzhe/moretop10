#!/usr/bin/env python3
"""Editorial /tv/ cluster: intent routes, YP as-is, density exception."""

from __future__ import annotations

import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from site_config import ALL_CATS, EDITORIAL_CLUSTERS  # noqa: E402

REQUIRED = [
    "tv/index.html",
    "tv/remove-smart-tv-ads/index.html",
    "tv/supported-android-tv-models/index.html",
    "tv/smart-tv-ad-alternatives/index.html",
    "tv/best-launcher-for-android-tv/index.html",
    "tv/adb-debloat-not-working/index.html",
    "tv/best-non-smart-tv/index.html",
    "tv/best-tv-for-privacy/index.html",
    "tv/samsung-smart-tv-ads/index.html",
    "tv/lg-smart-tv-ads/index.html",
    "tv/fire-tv-ads/index.html",
    "tv/google-tv-ads/index.html",
]
P2 = [
    "tv/best-launcher-for-android-tv/index.html",
    "tv/adb-debloat-not-working/index.html",
]
P3 = [
    "tv/best-non-smart-tv/index.html",
    "tv/best-tv-for-privacy/index.html",
]
P4 = [
    "tv/samsung-smart-tv-ads/index.html",
    "tv/lg-smart-tv-ads/index.html",
    "tv/fire-tv-ads/index.html",
    "tv/google-tv-ads/index.html",
]
P4_EMPTY_SKU = [
    "tv/samsung-smart-tv-ads/index.html",
    "tv/lg-smart-tv-ads/index.html",
]
MODELS_PAGE = "tv/supported-android-tv-models/index.html"
MODELS_SNAPSHOT = SITE / "data" / "tv-supported-models.json"
MODELS_SCAFFOLD_PHRASES = (
    "this table is a scaffold",
    "will replace this scaffold",
    "absence from this scaffold",
    "hisense u8 / u7 google tv (current us 4k panels)",
    "other android tv / google tv (sony, tcl, and similar)",
)
MODELS_REQUIRED_OEMS = ("TCL", "Xiaomi", "Sony", "Hisense")
MIN_MODEL_ROWS = 50
CONTENT_ONLY = [
    "tv/best-launcher-for-android-tv/index.html",
    "tv/adb-debloat-not-working/index.html",
    "tv/best-non-smart-tv/index.html",
    "tv/best-tv-for-privacy/index.html",
    "tv/samsung-smart-tv-ads/index.html",
    "tv/lg-smart-tv-ads/index.html",
]
MIN_P4_WORDS = 280
MIN_P4_H2 = 4
P4_REQUIRED_HEADINGS = {
    "tv/samsung-smart-tv-ads/index.html": (
        "Why ADB and sideload usually fail",
        "Honest next steps",
        "Product zone",
    ),
    "tv/lg-smart-tv-ads/index.html": (
        "Why ADB and sideload usually fail",
        "Honest next steps",
        "Product zone",
    ),
    "tv/fire-tv-ads/index.html": (
        "Buying Fire is not escape ads",
        "Software on Fire TV panels",
        "Product zone",
    ),
    "tv/google-tv-ads/index.html": (
        "Software first",
        "When to leave for a whole-TV replacement",
        "Product zone",
    ),
}
STUB_PHRASES = (
    "when we publish scores",
    "ranking note",
    "p2 stub",
    "coming soon",
    "placeholder",
    "thin stub",
)
MIN_P2_WORDS = 400
MIN_P2_H2 = 5
P2_REQUIRED_HEADINGS = {
    "tv/best-launcher-for-android-tv/index.html": (
        "What a launcher can and cannot do",
        "How we rank (validation, not scores)",
        "After you install",
        "When to leave this page",
        "No product list",
    ),
    "tv/adb-debloat-not-working/index.html": (
        "Confirm the platform first",
        "Network and ADB over IP",
        "Honest next steps",
        "No product list",
    ),
}


def legal_body_html(html: str) -> str:
    match = re.search(r'<div class="legal-body">(.*)</div>\s*</div>\s*</main>', html, re.S)
    return match.group(1) if match else ""


def visible_words(html_chunk: str) -> list[str]:
    text = re.sub(r"<[^>]+>", " ", html_chunk)
    text = unescape(text)
    return [w for w in re.split(r"\s+", text) if w]


def assert_models_table(errors: list[str]) -> None:
    """Scaffold-only / empty-fake tables must fail. Rows come from a vendored snapshot."""
    if not MODELS_SNAPSHOT.exists():
        errors.append("missing site/data/tv-supported-models.json snapshot")
        return
    try:
        snap = json.loads(MODELS_SNAPSHOT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"models snapshot is not JSON: {exc}")
        return
    models = snap.get("models") or []
    if not isinstance(models, list) or len(models) < MIN_MODEL_ROWS:
        errors.append(
            f"models snapshot has {len(models) if isinstance(models, list) else 0} rows, "
            f"need {MIN_MODEL_ROWS}+ real upstream models"
        )
        return
    slugs = {(m.get("slug") or "").strip() for m in models if isinstance(m, dict)}
    oems = {(m.get("oem") or "").strip() for m in models if isinstance(m, dict)}
    for oem in MODELS_REQUIRED_OEMS:
        if oem not in oems:
            errors.append(f"models snapshot missing OEM {oem}")
    invented = [m for m in models if isinstance(m, dict) and not (m.get("slug") or "").strip()]
    if invented:
        errors.append("models snapshot has rows without an upstream examples/ slug")

    html = (SITE / MODELS_PAGE).read_text(encoding="utf-8")
    body = legal_body_html(html)
    lowered = body.lower()
    for phrase in MODELS_SCAFFOLD_PHRASES:
        if phrase in lowered:
            errors.append(f"{MODELS_PAGE} still has scaffold phrase {phrase!r}")

    if 'data-tv-models-table' not in html:
        errors.append(f"{MODELS_PAGE} missing data-tv-models-table")
    rows = re.findall(r"<tr[^>]*data-tv-model-row[^>]*>", html)
    if len(rows) < MIN_MODEL_ROWS:
        errors.append(
            f"{MODELS_PAGE} has {len(rows)} data-tv-model-row cells, need {MIN_MODEL_ROWS}+"
        )
    baked_slugs = set(re.findall(r'data-slug="([^"]+)"', html))
    extra = baked_slugs - slugs
    if extra:
        errors.append(f"{MODELS_PAGE} invented slugs not in snapshot: {sorted(extra)[:8]}")
    missing_sample = {"tcl-65c7k-google-tv", "xiaomi-mi-tv-4a", "sony-kd-55x85j", "hisense-u75-hengshan"}
    for slug in missing_sample:
        if slug in slugs and slug not in html:
            errors.append(f"{MODELS_PAGE} missing baked upstream slug {slug}")
    for oem in MODELS_REQUIRED_OEMS:
        if oem not in html:
            errors.append(f"{MODELS_PAGE} missing OEM {oem}")

    if "as of" not in lowered:
        errors.append(f"{MODELS_PAGE} missing as-of date")
    if "third-party" not in lowered or "not affiliated" not in lowered:
        errors.append(f"{MODELS_PAGE} missing third-party / not-affiliated source disclosure")
    if "non-official" not in lowered and "unofficial" not in lowered:
        errors.append(f"{MODELS_PAGE} missing unofficial / non-official disclosure")
    if "not exhaustive" not in lowered:
        errors.append(f"{MODELS_PAGE} missing not-exhaustive caveat")
    if "github.com/gathin23/cleanyourtv" not in lowered:
        errors.append(f"{MODELS_PAGE} missing upstream source URL")
    if "/tv/cleanyourtv" in html.lower():
        errors.append(f"{MODELS_PAGE} leaked cleanyourtv into a site path")
    if "tv/remove-smart-tv-ads/" not in html:
        errors.append(f"{MODELS_PAGE} missing L1 /tv/remove-smart-tv-ads/ CTA")
    if "tv/smart-tv-ad-alternatives/" not in html:
        errors.append(f"{MODELS_PAGE} missing L2 /tv/smart-tv-ad-alternatives/ CTA")
    if "tv/adb-debloat-not-working/" not in html:
        errors.append(f"{MODELS_PAGE} missing ADB troubleshooting link")
    if re.search(r'href="[^"]*tv/"', html) is None:
        errors.append(f"{MODELS_PAGE} missing hub /tv/ back-link")
    if "yeahpromos.com" in html or "pboost.me" in html or "btn-cta-yellow" in html:
        errors.append(f"{MODELS_PAGE} must not add affiliate Check price CTAs")
    if "Fire Stick" in html and not re.search(
        r"(will not|never|not)[^.]*Fire Stick|Fire Stick[^.]*not",
        html,
        re.I,
    ):
        errors.append(f"{MODELS_PAGE} mentions Fire Stick outside a prohibition")
    for path in (
        "tv/samsung-smart-tv-ads/",
        "tv/lg-smart-tv-ads/",
        "tv/fire-tv-ads/",
        "tv/google-tv-ads/",
    ):
        if path not in html:
            errors.append(f"{MODELS_PAGE} missing P4 G-IL {path}")
FORBIDDEN = [
    "tv/cleanyourtv/index.html",
    "tv/cleanyourtv/supported-models/index.html",
    "tv/cleanyourtv-alternatives/index.html",
    "tv/cleanyourtv/not-working/index.html",
    "tv/cleanyourtv-best-non-smart/index.html",
    "tv/cleanyourtv/privacy/index.html",
    "tv/cleanyourtv/samsung/index.html",
    "tv/cleanyourtv/lg/index.html",
    "tv/cleanyourtv/fire/index.html",
    "tv/cleanyourtv/google/index.html",
]


def page_asins(html: str) -> set[str]:
    return set(re.findall(r"\bB0[A-Z0-9]{8}\b", html))


def page_tracks(html: str) -> set[str]:
    return set(re.findall(r"https://yeahpromos\.com/[^\"'\s]+", unescape(html)))
DO_NOT_HERO = {"B0DGHZ1C8V", "B0FHGNWZXT", "B0FMK1B4LW", "B0HGXYM1WD"}
HUB_OG_ASIN = "B0F1DRNWP7"
HUB_OG_IMAGE = "https://m.media-amazon.com/images/I/81IgwvJG9GL._AC_SL1500_.jpg"
SHARE_IMAGE_RE = re.compile(
    r'<meta (?:property|name)="(?:og:image|twitter:image)" content="([^"]*)"'
)


def main() -> None:
    errors: list[str] = []
    if any(c["slug"] == "tv" for c in ALL_CATS):
        errors.append("tv registered in ALL_CATS (density-10 shortlist) — forbidden")
    if not any(c["slug"] == "tv" for c in EDITORIAL_CLUSTERS):
        errors.append("EDITORIAL_CLUSTERS missing tv")

    sl = json.loads((SITE / "data" / "shortlist-tv.json").read_text(encoding="utf-8"))
    hero = sl.get("hero_google_tv") or []
    fire = sl.get("honest_fire_tv") or []
    hero_og = next((item for item in hero if item.get("asin") == HUB_OG_ASIN), None)
    if not hero_og:
        errors.append(f"shortlist missing hub og ASIN {HUB_OG_ASIN}")
    elif (hero_og.get("image") or "") != HUB_OG_IMAGE:
        errors.append(f"hub og image does not match shortlist {HUB_OG_ASIN}")
    if len(hero) != 9:
        errors.append(f"hero_google_tv expected 9, got {len(hero)}")
    if len(fire) != 20:
        errors.append(f"honest_fire_tv expected 20, got {len(fire)}")
    oos_asins = {item.get("asin") for item in hero + fire if item.get("oos")}
    if "B0GV4Q9XSF" not in oos_asins:
        errors.append("B0GV4Q9XSF should be marked oos in shortlist")
    for item in hero + fire:
        link = item.get("affiliate_link") or ""
        if item.get("affiliate_network") != "yp":
            errors.append(f"{item.get('asin')} network {item.get('affiliate_network')}")
        if not link.startswith("https://yeahpromos.com/"):
            errors.append(f"{item.get('asin')} track host is not yeahpromos.com")
        if "uid=" in link or "subid=" in link:
            errors.append(f"{item.get('asin')} track has uid/subid")
        if item.get("asin") in DO_NOT_HERO:
            errors.append(f"do_not_hero ASIN in shortlist products {item.get('asin')}")

    for rel in REQUIRED:
        path = SITE / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        html = path.read_text(encoding="utf-8")
        if "data-tv-disclosure" not in html:
            errors.append(f"{rel} missing unofficial disclosure")
        if "geo-answer-first" not in html:
            errors.append(f"{rel} missing answer-first")
        if re.search(r"uid=", html):
            errors.append(f"{rel} contains uid=")
        if "PartnerBoost" in html or "YeahPromos" in html:
            errors.append(f"{rel} visitor jargon")
        share_imgs = SHARE_IMAGE_RE.findall(html)
        if not share_imgs:
            errors.append(f"{rel} missing og:image / twitter:image")
        for url in share_imgs:
            if "icon-512.png" in url:
                errors.append(f"{rel} share image still uses icon-512.png")
            elif url != HUB_OG_IMAGE:
                errors.append(f"{rel} share image {url} != hub hero")

    for rel in FORBIDDEN:
        if (SITE / rel).exists():
            errors.append(f"forbidden path exists {rel}")

    alt = (SITE / "tv/smart-tv-ad-alternatives/index.html").read_text(encoding="utf-8")
    alt_hrefs = unescape(alt)
    for item in hero:
        if item.get("oos"):
            if item["affiliate_link"] in alt_hrefs:
                errors.append(f"OOS hero {item['asin']} still has Check price")
            continue
        if item["affiliate_link"] not in alt_hrefs:
            errors.append(f"L2 missing hero track {item['asin']}")
        if item["asin"] not in alt:
            errors.append(f"L2 missing hero ASIN {item['asin']}")
    oos_row = re.search(r'<tr[^>]*id="geo-B0GV4Q9XSF"[\s\S]*?</tr>', alt)
    if not oos_row:
        errors.append("honest table missing OOS B0GV4Q9XSF")
    elif "Check price" in oos_row.group(0) or "yeahpromos.com" in oos_row.group(0):
        errors.append("OOS B0GV4Q9XSF still has a Check price CTA")
    elif "Currently unavailable" not in oos_row.group(0):
        errors.append("OOS B0GV4Q9XSF missing unavailable label")
    if "$1299.99" not in alt:
        errors.append("L2 price $1299.99 (B0GHZXKT1T) not baked")
    if "$2497.99" not in alt:
        errors.append("L2 price $2497.99 (B0GR9C4H3H) not baked")
    for asin in DO_NOT_HERO:
        if asin in alt:
            errors.append(f"L2 includes do_not_hero {asin}")
    if "Primary recommendations — Google TV" not in alt:
        errors.append("L2 missing Google TV hero heading")
    if "Fire TV panels — honest section" not in alt:
        errors.append("L2 missing honest Fire section")
    if "No retailer link yet" not in alt and "stay empty" not in alt.lower():
        errors.append("L2 missing empty-slot honesty")

    hub = (SITE / "tv/index.html").read_text(encoding="utf-8")
    if "tv/best-non-smart-tv/" not in hub:
        errors.append("hub missing /tv/best-non-smart-tv/ G-IL")
    if "tv/best-tv-for-privacy/" not in hub:
        errors.append("hub missing /tv/best-tv-for-privacy/ G-IL")
    if "tv/best-launcher-for-android-tv/" not in hub:
        errors.append("hub missing /tv/best-launcher-for-android-tv/ G-IL")
    if "tv/adb-debloat-not-working/" not in hub:
        errors.append("hub missing /tv/adb-debloat-not-working/ G-IL")
    if "tv/samsung-smart-tv-ads/" not in hub:
        errors.append("hub missing /tv/samsung-smart-tv-ads/ G-IL")
    if "tv/lg-smart-tv-ads/" not in hub:
        errors.append("hub missing /tv/lg-smart-tv-ads/ G-IL")
    if "tv/fire-tv-ads/" not in hub:
        errors.append("hub missing /tv/fire-tv-ads/ G-IL")
    if "tv/google-tv-ads/" not in hub:
        errors.append("hub missing /tv/google-tv-ads/ G-IL")
    if "ranking notes" in hub.lower() or "p2 stub" in hub.lower():
        errors.append("hub still labels P2 pages as stubs / ranking notes")

    for rel in CONTENT_ONLY:
        path = SITE / rel
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        if "yeahpromos.com" in html or "pboost.me" in html or "btn-cta-yellow" in html:
            errors.append(f"{rel} invented a Check price CTA on an empty product zone")
        if "cleanyourtv" in rel.replace("\\", "/").lower():
            errors.append(f"forbidden cleanyourtv path {rel}")

    for rel in P2:
        html = (SITE / rel).read_text(encoding="utf-8")
        body = legal_body_html(html)
        words = visible_words(body)
        h2s = re.findall(r"<h2>[^<]+</h2>", body)
        if len(words) < MIN_P2_WORDS:
            errors.append(f"{rel} still stub-thin ({len(words)} words, need {MIN_P2_WORDS}+)")
        if len(h2s) < MIN_P2_H2:
            errors.append(f"{rel} still stub-thin ({len(h2s)} h2, need {MIN_P2_H2}+)")
        lowered = body.lower()
        for phrase in STUB_PHRASES:
            if phrase in lowered:
                errors.append(f"{rel} still has stub phrase {phrase!r}")
        if re.search(r'href="[^"]*tv/"', html) is None:
            errors.append(f"{rel} missing hub /tv/ back-link")
        if "tv/remove-smart-tv-ads/" not in html:
            errors.append(f"{rel} missing L1 /tv/remove-smart-tv-ads/ back-link")
        if "tv/smart-tv-ad-alternatives/" not in html:
            errors.append(f"{rel} missing L2 /tv/smart-tv-ad-alternatives/ back-link")
        if "tv/best-non-smart-tv/" not in html:
            errors.append(f"{rel} missing P3 /tv/best-non-smart-tv/ link")
        if "tv/best-tv-for-privacy/" not in html:
            errors.append(f"{rel} missing P3 /tv/best-tv-for-privacy/ link")
        for heading in P2_REQUIRED_HEADINGS[rel]:
            if heading not in body:
                errors.append(f"{rel} missing first-class heading {heading!r}")
        if "Fire Stick" in html and not re.search(
            r"(will not|never|not)[^.]*Fire Stick|Fire Stick[^.]*not",
            html,
            re.I,
        ):
            errors.append(f"{rel} mentions Fire Stick outside a prohibition")

    for rel in P3:
        html = (SITE / rel).read_text(encoding="utf-8")
        if re.search(r'href="[^"]*tv/"', html) is None:
            errors.append(f"{rel} missing hub /tv/ back-link")
        if "tv/remove-smart-tv-ads/" not in html:
            errors.append(f"{rel} missing L1 /tv/remove-smart-tv-ads/ back-link")
        if "tv/smart-tv-ad-alternatives/" not in html:
            errors.append(f"{rel} missing L2 /tv/smart-tv-ad-alternatives/ back-link")
        zone = re.search(r'<div class="tv-empty"[^>]*data-tv-empty-products[\s\S]*?</div>', html)
        if not zone:
            errors.append(f"{rel} missing honest empty product zone")
        elif "<a " in zone.group(0) or "btn-cta" in zone.group(0):
            errors.append(f"{rel} empty product zone has a checkout link")
        if "No affiliate-tracked" not in html:
            errors.append(f"{rel} missing empty-feed honesty copy")
        if "Fire Stick" in html and not re.search(
            r"(will not|never|not)[^.]*Fire Stick|Fire Stick[^.]*not",
            html,
            re.I,
        ):
            errors.append(f"{rel} mentions Fire Stick outside a prohibition")

    hero_asins = {item.get("asin") for item in hero}
    fire_shortlist_asins = {item.get("asin") for item in fire}
    hero_tracks = {item.get("affiliate_link") for item in hero if item.get("affiliate_link")}
    fire_tracks = {item.get("affiliate_link") for item in fire if item.get("affiliate_link")}
    allowed_asins = hero_asins | fire_shortlist_asins
    oos_track_by_asin = {
        item.get("asin"): item.get("affiliate_link")
        for item in hero + fire
        if item.get("oos") and item.get("affiliate_link")
    }

    for rel in P4:
        path = SITE / rel
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        body = legal_body_html(html)
        words = visible_words(body)
        h2s = re.findall(r"<h2>[^<]+</h2>", body)
        if len(words) < MIN_P4_WORDS:
            errors.append(f"{rel} still stub-thin ({len(words)} words, need {MIN_P4_WORDS}+)")
        if len(h2s) < MIN_P4_H2:
            errors.append(f"{rel} still stub-thin ({len(h2s)} h2, need {MIN_P4_H2}+)")
        lowered = body.lower()
        for phrase in STUB_PHRASES:
            if phrase in lowered:
                errors.append(f"{rel} still has stub phrase {phrase!r}")
        if re.search(r'href="[^"]*tv/"', html) is None:
            errors.append(f"{rel} missing hub /tv/ back-link")
        if "tv/remove-smart-tv-ads/" not in html:
            errors.append(f"{rel} missing L1 /tv/remove-smart-tv-ads/ back-link")
        if "tv/smart-tv-ad-alternatives/" not in html:
            errors.append(f"{rel} missing L2 /tv/smart-tv-ad-alternatives/ back-link")
        for heading in P4_REQUIRED_HEADINGS[rel]:
            if heading not in body:
                errors.append(f"{rel} missing first-class heading {heading!r}")
        if "Fire Stick" in html and not re.search(
            r"(will not|never|not)[^.]*Fire Stick|Fire Stick[^.]*not",
            html,
            re.I,
        ):
            errors.append(f"{rel} mentions Fire Stick outside a prohibition")
        if "cleanyourtv" in rel.replace("\\", "/").lower():
            errors.append(f"forbidden cleanyourtv path {rel}")
        found_asins = page_asins(html)
        unknown = found_asins - allowed_asins
        if unknown:
            errors.append(f"{rel} invented ASINs {sorted(unknown)}")
        leaked_oos = [
            asin for asin, track in oos_track_by_asin.items() if track and track in unescape(html)
        ]
        if leaked_oos:
            errors.append(f"{rel} rendered OOS Check price for {leaked_oos}")

    for rel in P4_EMPTY_SKU:
        path = SITE / rel
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        if "yeahpromos.com" in html or "pboost.me" in html or "btn-cta-yellow" in html:
            errors.append(f"{rel} invented a Check price CTA on an empty product zone")
        zone = re.search(r'<div class="tv-empty"[^>]*data-tv-empty-products[\s\S]*?</div>', html)
        if not zone:
            errors.append(f"{rel} missing honest empty product zone")
        elif "<a " in zone.group(0) or "btn-cta" in zone.group(0):
            errors.append(f"{rel} empty product zone has a checkout link")
        if "tv/adb-debloat-not-working/" not in html:
            errors.append(f"{rel} missing P2 /tv/adb-debloat-not-working/ link")
        if "tv/best-non-smart-tv/" not in html and "tv/best-tv-for-privacy/" not in html:
            errors.append(f"{rel} missing relevant P3 link")

    google_path = SITE / "tv/google-tv-ads/index.html"
    if google_path.exists():
        google_html = google_path.read_text(encoding="utf-8")
        if "tv/best-launcher-for-android-tv/" not in google_html:
            errors.append("google-tv page missing P2 launcher link")
        if "tv/adb-debloat-not-working/" not in google_html:
            errors.append("google-tv page missing P2 ADB link")
        if "tv/supported-android-tv-models/" not in google_html:
            errors.append("google-tv page missing P2 supported-models link")
        google_asins = page_asins(google_html)
        if google_asins - hero_asins:
            errors.append(f"google-tv page used non-hero tracks {sorted(google_asins - hero_asins)}")
        google_yp = page_tracks(google_html)
        if google_yp - hero_tracks:
            errors.append("google-tv page used a track that is not a shortlist Google TV hero")

    fire_path = SITE / "tv/fire-tv-ads/index.html"
    if fire_path.exists():
        fire_html = fire_path.read_text(encoding="utf-8")
        if "Buying Fire is not escape ads" not in fire_html and "escape ads" not in fire_html.lower():
            errors.append("fire-tv page missing honest 'buying Fire is not escape ads' copy")
        page_fire_asins = page_asins(fire_html)
        if page_fire_asins - fire_shortlist_asins:
            errors.append(
                f"fire-tv page used non-Fire tracks {sorted(page_fire_asins - fire_shortlist_asins)}"
            )
        fire_yp = page_tracks(fire_html)
        if fire_yp - fire_tracks:
            errors.append("fire-tv page used a track that is not a shortlist Fire TV panel")
        if "Fire Stick" not in fire_html:
            errors.append("fire-tv page must prohibit Fire Stick explicitly")

    assert_models_table(errors)

    l1 = (SITE / "tv/remove-smart-tv-ads/index.html").read_text(encoding="utf-8")
    if "<video" not in l1:
        errors.append("L1 missing <video tag")
    if "assets/video/cleanyourtv-demo-hfcorriez.mp4" not in l1:
        errors.append("L1 missing vendored mp4 path")
    if "https://x.com/hfcorriez/status/2112732522937553003" not in l1:
        errors.append("L1 missing X status credit link")
    if not (SITE / "assets/video/cleanyourtv-demo-hfcorriez.mp4").is_file():
        errors.append("vendored mp4 missing from site/assets/video/")
    if not (SITE / "assets/video/cleanyourtv-demo-hfcorriez-poster.jpg").is_file():
        errors.append("vendored poster missing from site/assets/video/")

    home = (SITE / "index.html").read_text(encoding="utf-8")
    if 'data-editorial-cluster="tv"' not in home:
        errors.append("home missing /tv/ tile")
    footer = (SITE / "about-us" / "index.html").read_text(encoding="utf-8").split("<footer", 1)[-1]
    if "tv/" not in footer:
        errors.append("about footer missing /tv/")
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    if "https://moretop10.com/tv/" not in sitemap:
        errors.append("sitemap missing /tv/")
    if "https://moretop10.com/tv/supported-android-tv-models/" not in sitemap:
        errors.append("sitemap missing /tv/supported-android-tv-models/")
    if "https://moretop10.com/tv/best-launcher-for-android-tv/" not in sitemap:
        errors.append("sitemap missing P2 /tv/best-launcher-for-android-tv/")
    if "https://moretop10.com/tv/adb-debloat-not-working/" not in sitemap:
        errors.append("sitemap missing P2 /tv/adb-debloat-not-working/")
    if "https://moretop10.com/tv/best-non-smart-tv/" not in sitemap:
        errors.append("sitemap missing P3 /tv/best-non-smart-tv/")
    if "https://moretop10.com/tv/best-tv-for-privacy/" not in sitemap:
        errors.append("sitemap missing P3 /tv/best-tv-for-privacy/")
    if "https://moretop10.com/tv/samsung-smart-tv-ads/" not in sitemap:
        errors.append("sitemap missing P4 /tv/samsung-smart-tv-ads/")
    if "https://moretop10.com/tv/lg-smart-tv-ads/" not in sitemap:
        errors.append("sitemap missing P4 /tv/lg-smart-tv-ads/")
    if "https://moretop10.com/tv/fire-tv-ads/" not in sitemap:
        errors.append("sitemap missing P4 /tv/fire-tv-ads/")
    if "https://moretop10.com/tv/google-tv-ads/" not in sitemap:
        errors.append("sitemap missing P4 /tv/google-tv-ads/")
    if "https://moretop10.com/tv/cleanyourtv/" in sitemap:
        errors.append("sitemap lists a forbidden branded path")
    if "cleanyourtv" in sitemap:
        errors.append("sitemap contains cleanyourtv")

    llms = (SITE / "llms.txt").read_text(encoding="utf-8")
    if "https://moretop10.com/tv/best-launcher-for-android-tv/" not in llms:
        errors.append("llms.txt missing P2 /tv/best-launcher-for-android-tv/")
    if "https://moretop10.com/tv/adb-debloat-not-working/" not in llms:
        errors.append("llms.txt missing P2 /tv/adb-debloat-not-working/")
    if "https://moretop10.com/tv/best-non-smart-tv/" not in llms:
        errors.append("llms.txt missing P3 /tv/best-non-smart-tv/")
    if "https://moretop10.com/tv/best-tv-for-privacy/" not in llms:
        errors.append("llms.txt missing P3 /tv/best-tv-for-privacy/")
    if "https://moretop10.com/tv/samsung-smart-tv-ads/" not in llms:
        errors.append("llms.txt missing P4 /tv/samsung-smart-tv-ads/")
    if "https://moretop10.com/tv/lg-smart-tv-ads/" not in llms:
        errors.append("llms.txt missing P4 /tv/lg-smart-tv-ads/")
    if "https://moretop10.com/tv/fire-tv-ads/" not in llms:
        errors.append("llms.txt missing P4 /tv/fire-tv-ads/")
    if "https://moretop10.com/tv/google-tv-ads/" not in llms:
        errors.append("llms.txt missing P4 /tv/google-tv-ads/")

    if errors:
        raise SystemExit("tv_cluster_assert failed:\n- " + "\n- ".join(errors))
    print("tv_cluster_assert ok")


if __name__ == "__main__":
    main()
