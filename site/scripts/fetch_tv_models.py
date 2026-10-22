#!/usr/bin/env python3
"""Refresh the vendored CleanYourTV examples/ snapshot used by bake_tv.py.

Source of truth: the unofficial project's examples/README.md table
(Folder | TV | OS | Notes), one contributor-tested build per row.

    python3 site/scripts/fetch_tv_models.py
    python3 site/scripts/bake_tv.py

Optional:

    python3 site/scripts/fetch_tv_models.py --from-file /tmp/examples-README.md
    python3 site/scripts/fetch_tv_models.py --out site/data/tv-supported-models.json

Does not invent models. Does not write /tv/cleanyourtv/ paths. Bake ≠ Live.
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DEFAULT_OUT = SITE / "data" / "tv-supported-models.json"

UPSTREAM_REPO = "https://github.com/Gathin23/cleanyourtv"
UPSTREAM_README = (
    "https://raw.githubusercontent.com/Gathin23/cleanyourtv/main/examples/README.md"
)
UPSTREAM_COMMITS = "https://api.github.com/repos/Gathin23/cleanyourtv/commits/main"
UPSTREAM_PATH = "examples/README.md"

ROW_RE = re.compile(
    r"^\|\s*`(?P<slug>[a-z0-9][a-z0-9._-]*)/`\s*"
    r"\|\s*(?P<name>[^|]+?)\s*"
    r"\|\s*(?P<os>[^|]+?)\s*"
    r"\|\s*(?P<notes>[^|]*)\s*\|\s*$",
    re.M,
)

# First path segment of examples/<slug>/ → visitor OEM label.
OEM_BY_PREFIX = {
    "aipro2k": "AiPro2K",
    "aiwa": "AIWA",
    "amazon": "Amazon",
    "anker": "Anker",
    "artel": "Artel",
    "benq": "BenQ",
    "byintek": "BYINTEK",
    "caxium": "Caxium",
    "cecotec": "Cecotec",
    "challenger": "Challenger",
    "chiq": "CHiQ",
    "compac": "Compac",
    "coocaa": "Coocaa",
    "dialog": "Dialog",
    "eko": "EKO",
    "epson": "Epson",
    "ffalcon": "FFalcon",
    "formovie": "Formovie",
    "freebox": "Freebox",
    "gadnic": "Gadnic",
    "google": "Google",
    "grundig": "Grundig",
    "haier": "Haier",
    "hisense": "Hisense",
    "hitachi": "Hitachi",
    "insignia": "Insignia",
    "jmgo": "JMGO",
    "jvc": "JVC",
    "kalley": "Kalley",
    "karbonn": "Karbonn",
    "kogan": "Kogan",
    "motorola": "Motorola",
    "mtc": "MTC",
    "noblex": "Noblex",
    "nokia": "Nokia",
    "nvidia": "NVIDIA",
    "ok": "OK.",
    "oneplus": "OnePlus",
    "onn": "onn",
    "panasonic": "Panasonic",
    "peaq": "PEAQ",
    "philips": "Philips",
    "polytron": "Polytron",
    "portronics": "Portronics",
    "prismplus": "PRISM+",
    "rca": "RCA",
    "redmi": "Redmi",
    "sankey": "Sankey",
    "sanyo": "SANYO",
    "sharp": "SHARP",
    "skyworth": "Skyworth",
    "sony": "Sony",
    "stellamore": "Stellamore",
    "super": "Super General",
    "tcl": "TCL",
    "telesystem": "Tele System",
    "thomson": "Thomson",
    "tornado": "Tornado",
    "toshiba": "Toshiba",
    "turkcell": "Turkcell",
    "verizon": "Verizon",
    "vidda": "Vidda",
    "vision": "Vision",
    "vu": "Vu",
    "wanbo": "Wanbo",
    "xgimi": "XGIMI",
    "xiaomi": "Xiaomi",
}

PROJECTOR_PREFIXES = {
    "anker",
    "byintek",
    "epson",
    "formovie",
    "gadnic",
    "jmgo",
    "portronics",
    "stellamore",
    "wanbo",
    "xgimi",
}


def oem_from_slug(slug: str) -> str:
    head = (slug or "").split("-", 1)[0]
    if head in OEM_BY_PREFIX:
        return OEM_BY_PREFIX[head]
    return head[:1].upper() + head[1:] if head else "Unknown"


def classify_kind(slug: str, name: str, os_label: str) -> str:
    blob = f"{slug} {name} {os_label}".lower()
    if "fire tv stick" in blob or (slug.startswith("amazon-fire-tv-stick") or "fire-tv-stick" in slug):
        return "fire_stick"
    if "fire os" in blob or "fire tv" in blob or slug.startswith("amazon-fire-tv") or "-fire-tv" in slug:
        return "fire_tv"
    if "projector" in blob or slug.split("-", 1)[0] in PROJECTOR_PREFIXES:
        return "projector"
    if slug.startswith("nvidia-shield") or "shield tv" in blob:
        return "streamer"
    if any(
        token in blob
        for token in (
            "streaming box",
            "streaming stick",
            "chromecast",
            "tv stick",
            "mi box",
            "streamer",
            "streaming",
        )
    ):
        return "streamer"
    return "panel"


def classify_platform(os_label: str) -> str:
    text = (os_label or "").strip()
    low = text.lower()
    if "fire" in low:
        return "Fire OS"
    if "google tv" in low:
        return "Google TV"
    if "android tv" in low:
        return "Android TV"
    if low.startswith("android"):
        return "Android"
    return text or "Unknown"


def classify_software_path(os_label: str, notes: str, kind: str) -> str:
    low = f"{os_label} {notes} {kind}".lower()
    if any(token in low for token in ("tizen", "webos", "tvos")):
        return "No ADB path"
    if kind == "fire_stick" or kind == "fire_tv" or "fire os" in low:
        return "Debloat only — not a Google TV twin"
    if "debloat only" in low and (
        "no third-party" in low or "refuse" in low or "cannot be replaced" in low or "no launcher" in low
    ):
        return "Debloat only — launcher blocked"
    if "debloat only" in low:
        return "Debloat only"
    if "google tv" in low or "android tv" in low or low.startswith("android"):
        return "Try software first"
    return "See upstream notes"


def visitor_note(kind: str, notes: str) -> str:
    if kind == "fire_stick":
        return "Debloat only. We will not recommend a Fire Stick."
    if kind == "fire_tv":
        return "Debloat only. Fire OS will not hand Home to a third-party launcher."
    text = re.sub(r"\s+", " ", (notes or "").strip())
    if not text:
        return "See the unofficial examples folder for this build."
    first = re.split(r"(?<=[.!;])\s+", text, maxsplit=1)[0].strip()
    if len(first) > 160:
        first = first[:157].rstrip() + "…"
    return first


def parse_examples_readme(markdown: str) -> list[dict]:
    models: list[dict] = []
    seen: set[str] = set()
    for match in ROW_RE.finditer(markdown or ""):
        slug = match.group("slug").strip()
        if not slug or slug in seen:
            continue
        name = match.group("name").strip()
        os_label = match.group("os").strip()
        notes = match.group("notes").strip()
        if not name or not os_label:
            continue
        kind = classify_kind(slug, name, os_label)
        seen.add(slug)
        models.append(
            {
                "slug": slug,
                "oem": oem_from_slug(slug),
                "name": name,
                "os": os_label,
                "platform": classify_platform(os_label),
                "kind": kind,
                "software_path": classify_software_path(os_label, notes, kind),
                "notes": visitor_note(kind, notes),
            }
        )
    return models


def _http_get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "moretop10-tv-models-refresh/1.0"},
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read().decode("utf-8")


def resolve_commit_sha() -> str:
    try:
        blob = json.loads(_http_get(UPSTREAM_COMMITS))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return ""
    return (blob.get("sha") or "") if isinstance(blob, dict) else ""


def build_snapshot(markdown: str, *, commit: str = "", fetched_at: str | None = None) -> dict:
    models = parse_examples_readme(markdown)
    as_of = fetched_at or date.today().isoformat()
    oems = Counter(m["oem"] for m in models)
    return {
        "as_of": as_of,
        "exhaustive": False,
        "source": {
            "project": "CleanYourTV",
            "repo": UPSTREAM_REPO,
            "path": UPSTREAM_PATH,
            "commit": commit,
            "fetched_at": as_of,
            "affiliation": "third-party open-source; non-official; MoreTop10 is not affiliated",
        },
        "oem_counts": dict(sorted(oems.items(), key=lambda item: (-item[1], item[0]))),
        "models": models,
    }


def write_snapshot(snapshot: dict, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-file", help="Parse a local examples/README.md instead of fetching")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    commit = ""
    if args.from_file:
        markdown = Path(args.from_file).read_text(encoding="utf-8")
    else:
        try:
            markdown = _http_get(UPSTREAM_README)
            commit = resolve_commit_sha()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise SystemExit(f"fetch_tv_models: failed to download upstream README: {exc}") from exc

    snapshot = build_snapshot(
        markdown,
        commit=commit,
        fetched_at=datetime.now(timezone.utc).date().isoformat(),
    )
    n = len(snapshot["models"])
    if n < 20:
        raise SystemExit(f"fetch_tv_models: parsed only {n} rows — refusing to overwrite snapshot")
    dest = Path(args.out)
    write_snapshot(snapshot, dest)
    print(f"wrote {dest} ({n} models, commit={commit or 'unknown'})")


if __name__ == "__main__":
    main()
