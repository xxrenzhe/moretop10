"""Load MoreTop10 instance YAML and expose ALL_CATS / MVP / NON_MVP.

Stdlib only — the instance file is a small YAML subset (scalars + lists of maps).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INSTANCE = ROOT / "site" / "instances" / "moretop10.site.yaml"


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        return _parse_flow_map(raw[1:-1])
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    if raw in ("true", "false"):
        return raw == "true"
    if raw.isdigit():
        return int(raw)
    return raw


def _parse_flow_map(body: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for part in body.split(","):
        if ":" not in part:
            continue
        key, val = part.split(":", 1)
        out[key.strip()] = _parse_scalar(val)
    return out


def _load_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    current_list_key: str | None = None
    cats: dict[str, list] | None = None

    while i < len(lines):
        raw = lines[i]
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0 and stripped.endswith(":") and not stripped.startswith("-"):
            key = stripped[:-1].strip()
            current_list_key = None
            cats = None
            # peek: mapping or scalar next?
            if key == "categories":
                cats = {}
                data[key] = cats
            else:
                data[key] = None
            i += 1
            continue

        if indent == 0 and ":" in stripped and not stripped.startswith("-"):
            key, val = stripped.split(":", 1)
            data[key.strip()] = _parse_scalar(val)
            current_list_key = None
            cats = None
            i += 1
            continue

        if indent == 2 and stripped.endswith(":") and cats is not None:
            current_list_key = stripped[:-1].strip()
            cats[current_list_key] = []
            i += 1
            continue

        if stripped.startswith("- ") and current_list_key and cats is not None:
            item = _parse_scalar(stripped[2:])
            if not isinstance(item, dict):
                item = {"value": item}
            cats[current_list_key].append(item)
            i += 1
            continue

        i += 1

    return data


def load_site_config(path: Path | str | None = None) -> dict[str, Any]:
    cfg_path = Path(path) if path else DEFAULT_INSTANCE
    parsed = _load_simple_yaml(cfg_path.read_text(encoding="utf-8"))
    cats_block = parsed.get("categories") or {}
    mvp = list(cats_block.get("mvp") or [])
    non_mvp = list(cats_block.get("non_mvp") or [])
    all_cats = mvp + non_mvp
    parsed["MVP_CATS"] = mvp
    parsed["NON_MVP_CATS"] = non_mvp
    parsed["ALL_CATS"] = all_cats
    parsed["CATS_BY_SLUG"] = {c["slug"]: c for c in all_cats if c.get("slug")}
    parsed["home_visible_tiles"] = int(parsed.get("home_visible_tiles") or 8)
    parsed["EDITORIAL_CLUSTERS"] = list(EDITORIAL_CLUSTERS)
    return parsed


# Editorial content clusters — NOT density-10 ALL_CATS product categories.
# /tv/ is a G-IL guide hub (footer + home tile). Do not add `tv` to mvp/non_mvp.
EDITORIAL_CLUSTERS = [
    {
        "slug": "tv",
        "name": "Smart TV ads",
        "short_name": "Smart TV ads",
        "kind": "guide",
        "home_label": "Smart TV ads",
        "home_cta": "Read the guide",
    },
]


# Module-level SoT used by build.py (refreshed on import / explicit load).
_CFG = load_site_config()
MVP_CATS = _CFG["MVP_CATS"]
NON_MVP_CATS = _CFG["NON_MVP_CATS"]
ALL_CATS = _CFG["ALL_CATS"]
CATS_BY_SLUG = _CFG["CATS_BY_SLUG"]
HOME_VISIBLE_TILES = _CFG["home_visible_tiles"]
