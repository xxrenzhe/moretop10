#!/usr/bin/env python3
"""Honest list_price / was / discount gates (R8 soft).

R8 soft = pct ≥ 50 and ratio ≥ 2.0. Affiliate / PB original_price is not a
verified Amazon L2 buybox list. Do not invent prices. Do not render strike
from an unverified list. Restore list_price only after Mac L2 buybox.

Amazon L2 buybox > affiliate invent: a queue row with action/verdict
``restore_list_ok`` (or ``l2_verified``) may keep an R8-soft list. ``clear_keep``
stays blank.

Used by day-add L1/affiliate merges and the R8 bake assert. Fail-closed on
malformed amounts (drop the list, keep now) unless L2 restore matches.
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
L2_RESTORE_ACTIONS = frozenset({"restore_list_ok", "l2_verified"})
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


def queue_action(row: dict[str, Any] | None) -> str:
    if not row:
        return ""
    return str(row.get("action") or row.get("verdict") or row.get("l2_verdict") or "").strip().lower()


def l2_restore_list(row: dict[str, Any] | None) -> bool:
    """True when Mac L2 verified an honest Amazon list (allow even if R8-soft)."""
    if not row:
        return False
    if row.get("l2_verified") is False:
        return False
    return queue_action(row) in L2_RESTORE_ACTIONS


def l2_list_amount(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    return parse_money(row.get("list_price") or row.get("l2_list") or row.get("cleared_was"))


def list_price_for_pick(
    asin: str,
    now: Any,
    list_price: Any,
    *,
    queued: set[str] | None = None,
    l2_restore: set[str] | None = None,
) -> Any:
    """Keep a list only when it is not R8-soft, or when Amazon L2 restored it.

    Amazon L2 buybox > affiliate original_price. Queued ASINs stay blank until
    Mac L2 verifies a real list (``restore_list_ok``). A later PB original_price
    that does not match the L2 list is still dropped.
    """
    asin_u = (asin or "").upper()
    restore = l2_restore if l2_restore is not None else l2_verified_restore_asins()
    if asin_u in restore:
        row = next(
            (r for r in r8_soft_queue_rows() if (r.get("asin") or "").upper() == asin_u),
            None,
        )
        want = l2_list_amount(row)
        got = parse_money(list_price)
        if want is not None and (got is None or abs(got - want) > 0.009):
            return row.get("list_price") or row.get("l2_list") or format_display(want)
        return list_price
    blocked = queued if queued is not None else r8_soft_asins()
    if asin_u in blocked:
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
    """ASINs whose unverified list/was must stay blank (not L2 restore_list_ok)."""
    blocked: set[str] = set()
    for row in r8_soft_queue_rows(data):
        asin = (row.get("asin") or "").upper()
        if asin and not l2_restore_list(row):
            blocked.add(asin)
    return blocked


def l2_verified_restore_asins(data: Path | None = None) -> set[str]:
    return {
        (row.get("asin") or "").upper()
        for row in r8_soft_queue_rows(data)
        if row.get("asin") and l2_restore_list(row)
    }


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
        if parse_money(old) is None or parse_money(new) is None:
            return block
        if abs(parse_money(old) - parse_money(new)) < 0.009:  # type: ignore[operator]
            return block
        return _replace_price_token(block, old, new)

    return CARD_RE.sub(repl, html)


def apply_l2_list_strike_to_card(html: str, asin: str, now: Any, list_price: Any) -> str:
    """Restore an L2-verified Amazon list as a native <s> next to now (no new CSS)."""
    now_disp = format_display(now)
    list_disp = format_display(list_price)
    strike = f'<s class="pc-was">{list_disp}</s>'

    def repl(match: re.Match[str]) -> str:
        if match.group(1).upper() != asin.upper():
            return match.group(0)
        block = match.group(0)
        if strike in block:
            return block
        block = re.sub(r'<s class="pc-was">[^<]*</s>', "", block)
        if now_disp not in block:
            return block
        return re.sub(
            r'(<span class="pc-price-value">' + re.escape(now_disp) + r"</span>)",
            rf"\1{strike}",
            block,
            count=1,
        )

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
