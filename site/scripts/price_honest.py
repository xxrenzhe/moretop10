#!/usr/bin/env python3
"""Honest list_price / was / discount gates (R8 soft).

R8 soft = pct ≥ 50 and ratio ≥ 2.0. Affiliate / PB original_price is not a
verified Amazon L2 buybox list. Do not invent prices. Do not render strike
from an unverified list. Restore list_price only after Mac L2 buybox.

Used by day-add L1/affiliate merges and the R8 bake assert. Fail-closed on
malformed amounts (drop the list, keep now).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
DATA = SITE / "data"

R8_SOFT_PCT = 50.0
R8_SOFT_RATIO = 2.0
WAS_KEYS = (
    "list_price",
    "was",
    "was_price",
    "original_price",
    "discount",
    "discount_pct",
    "percent_off",
    "pct_off",
)
STRIKE_HINT_RE = re.compile(
    r"was-price|pc-was|list-price|pc-discount|percent-off|%\s*off|<s>|<del>|<strike",
    re.I,
)
CARD_RE = re.compile(
    r'<article class="product-card"[^>]*data-asin="([^"]+)"[^>]*>.*?</article>',
    re.S,
)
GLANCE_ROW_RE = re.compile(r"<tr>.*?</tr>", re.S)


def parse_money(raw: Any) -> float | None:
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        value = float(raw)
        return value if value > 0 else None
    match = re.search(r"(\d[\d,]*(?:\.\d+)?)", str(raw))
    if not match:
        return None
    try:
        value = float(match.group(1).replace(",", ""))
    except ValueError:
        return None
    return value if value > 0 else None


def r8_soft(now: Any, was: Any) -> bool:
    """True when was/now is R8 soft (pct≥50 and ratio≥2)."""
    now_n = parse_money(now)
    was_n = parse_money(was)
    if now_n is None or was_n is None or now_n <= 0 or was_n <= now_n:
        return False
    ratio = was_n / now_n
    pct = (was_n - now_n) / was_n * 100.0
    return pct >= R8_SOFT_PCT and ratio >= R8_SOFT_RATIO


def list_price_for_pick(asin: str, now: Any, list_price: Any, *, queued: set[str] | None = None) -> Any:
    """Keep a list only when it is not R8-soft and the ASIN is not in the soft queue.

    Amazon L2 buybox > affiliate original_price. Queued ASINs stay blank until
    Mac L2 verifies a real list (see shortlist r8_soft_queue.restore_only).
    """
    blocked = queued if queued is not None else r8_soft_asins()
    if (asin or "").upper() in blocked:
        return None
    if r8_soft(now, list_price):
        return None
    return list_price


def load_shortlist(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def shortlist_paths(data: Path | None = None) -> list[Path]:
    data = data or DATA
    return sorted(data.glob("shortlist-*.json"))


def r8_soft_queue_rows(data: Path | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in shortlist_paths(data):
        blob = load_shortlist(path)
        for row in blob.get("r8_soft_queue") or []:
            if isinstance(row, dict) and row.get("asin"):
                item = dict(row)
                item.setdefault("src", path.name)
                item.setdefault("category", blob.get("slug") or path.stem.replace("shortlist-", "", 1))
                rows.append(item)
    return rows


def r8_soft_asins(data: Path | None = None) -> set[str]:
    return {(row.get("asin") or "").upper() for row in r8_soft_queue_rows(data) if row.get("asin")}


def pick_was_fields(pick: dict[str, Any]) -> dict[str, Any]:
    return {key: pick.get(key) for key in WAS_KEYS if pick.get(key) not in (None, "", [])}


def scrub_pick_was(pick: dict[str, Any]) -> dict[str, Any]:
    """Blank was / list / discount. Keep now / price* fields."""
    out = dict(pick)
    for key in WAS_KEYS:
        if key in out:
            out[key] = None
    return out


def format_display(amount: Any) -> str:
    value = parse_money(amount)
    if value is None:
        raise ValueError("cannot format empty price")
    return f"${value:.2f}"


def _replace_price_token(text: str, old: Any, new: Any) -> str:
    old_disp = format_display(old)
    new_disp = format_display(new)
    return text.replace(old_disp, new_disp)


def apply_now_to_card(html: str, asin: str, old: Any, new: Any) -> str:
    """Swap the published snapshot on one comparison card; strip strike/was/%."""

    def repl(match: re.Match[str]) -> str:
        if match.group(1).upper() != asin.upper():
            return match.group(0)
        block = match.group(0)
        block = STRIKE_HINT_RE.sub("", block)
        return _replace_price_token(block, old, new)

    return CARD_RE.sub(repl, html)


def apply_now_to_glance(html: str, needle: str, old: Any, new: Any) -> str:
    old_disp = format_display(old)
    new_disp = format_display(new)

    def repl(match: re.Match[str]) -> str:
        row = match.group(0)
        if needle not in row or old_disp not in row:
            return row
        return row.replace(old_disp, new_disp, 1)

    return GLANCE_ROW_RE.sub(repl, html)


def apply_now_to_review(html: str, old: Any, new: Any) -> str:
    """Review pages are one ASIN; rewrite snapshot mentions of the scrubbed was."""
    return _replace_price_token(html, old, new)
