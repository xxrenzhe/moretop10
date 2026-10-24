#!/usr/bin/env python3
"""Monotonic visitor calendar stamps for comparison pages.

Day-update may advance As of / Last Updated / per-card Checked.
Bake, chrome rebase, or apex-from-git-tip must never write those dates
earlier than already present for the same page or ASIN.

RR-style last-checked anti-rollback: keep max(current, incoming).
Does not invent prices, ASINs, or copy.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_DATE = r"(\d{4}-\d{2}-\d{2})"
FLEET_FLOOR_NAME = "comparison-stamp-floors.json"
ROBOT_FLOOR_NAME = "robot-vacuums-comparison-stamp-floor.json"
CARD_RE = re.compile(
    r'<article class="product-card"[^>]*data-asin="([^"]+)"[^>]*>.*?</article>',
    re.S,
)
CARD_CHECKED_RE = re.compile(
    r'(<span class="pc-price-checked">Checked\s+)(\d{4}-\d{2}-\d{2})(</span>)'
)

# Page-level only. Card "Checked YYYY-MM-DD" is handled separately.
PAGE_STAMP_RES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("last_updated", re.compile(r"Last Updated:\s*" + ISO_DATE, re.I)),
    ("last_updated", re.compile(r"Last updated\s+" + ISO_DATE)),
    ("as_of", re.compile(r"As of\s+" + ISO_DATE)),
    ("date_modified", re.compile(r'"dateModified":\s*"' + ISO_DATE + r'"')),
    ("last_checked", re.compile(r"last checked\s+" + ISO_DATE)),
    ("glance_as_of", re.compile(r"checked as of\s+" + ISO_DATE)),
    ("snapshot", re.compile(r"publish-time snapshot\s*\(" + ISO_DATE + r"\)")),
)

PAGE_REWRITE_RES: tuple[re.Pattern[str], ...] = (
    re.compile(r"(Last Updated:\s*)(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"(Last updated\s+)(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(As of\s+)(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r'("dateModified":\s*")(\d{4}-\d{2}-\d{2})(")'),
    re.compile(r"(last checked\s+)(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(checked as of\s+)(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(publish-time snapshot\s*\()(\d{4}-\d{2}-\d{2})(\))"),
)

# Sitewide visitor stamps, including comparison cards and hub extras.
# Anti-rollback: later_iso_date never writes a day earlier than current.
VISITOR_STAMP_REWRITE_RES: tuple[re.Pattern[str], ...] = PAGE_REWRITE_RES + (
    re.compile(r"(Last Updated\s+)(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(Last verified\s+)(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"(<lastmod>)(\d{4}-\d{2}-\d{2})(</lastmod>)"),
    re.compile(r"(<lastmod>)(\d{4}-\d{2}-\d{2})(T[^<]*</lastmod>)"),
    re.compile(r"(Checked\s+)(\d{4}-\d{2}-\d{2})"),
    re.compile(r"(· checked\s+)(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"(price checked\s+)(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r"(?<![A-Za-z])(checked\s+)(\d{4}-\d{2}-\d{2})", re.I),
    re.compile(r'(<span class="ed-pick-date">)(\d{4}-\d{2}-\d{2})(</span>)'),
)

VISITOR_STAMP_FIND_RE = re.compile(
    r'(?:Last Updated:?|Last updated:?|As of|last checked|checked as of|'
    r'Checked|· checked|Last verified|dateModified"|<lastmod>|'
    r'publish-time snapshot\s*\(|ed-pick-date">)'
    r"\s*:?\s*(\d{4}-\d{2}-\d{2})",
    re.I,
)


def later_iso_date(*dates: str | None) -> str | None:
    """Return the later YYYY-MM-DD among valid ISO dates. None/junk ignored."""
    valid = [d for d in dates if d and ISO_DATE_RE.fullmatch(d)]
    return max(valid) if valid else None


def _without_cards(html: str) -> str:
    return CARD_RE.sub("", html)


def extract_page_stamps(html: str) -> dict[str, str]:
    """Max As of / Last Updated / dateModified / cite / glance / snapshot."""
    stripped = _without_cards(html)
    out: dict[str, str] = {}
    for kind, rx in PAGE_STAMP_RES:
        found = rx.findall(stripped)
        if not found:
            continue
        kept = later_iso_date(out.get(kind), *found)
        if kept:
            out[kind] = kept
    return out


def extract_card_checked(html: str) -> dict[str, str]:
    """Map comparison-card ASIN → Checked YYYY-MM-DD (max if duplicated)."""
    out: dict[str, str] = {}
    for m in CARD_RE.finditer(html):
        asin = m.group(1)
        cm = CARD_CHECKED_RE.search(m.group(0))
        if not cm:
            continue
        kept = later_iso_date(out.get(asin), cm.group(2))
        if kept:
            out[asin] = kept
    return out


def catalog_page_floor(data_dir=None) -> str:
    """Catalog SoT page_floor from comparison-stamp-floors.json."""
    data_dir = Path(data_dir) if data_dir else Path(__file__).resolve().parents[1] / "data"
    path = data_dir / FLEET_FLOOR_NAME
    if path.is_file():
        fleet = json.loads(path.read_text(encoding="utf-8"))
        floor = fleet.get("page_floor")
        if floor and ISO_DATE_RE.fullmatch(floor):
            return floor
    return "2026-10-24"


def bake_stamp_date(default: str | None = None) -> str:
    """Day-update / bake date: max(script default, catalog page_floor)."""
    return later_iso_date(default, catalog_page_floor()) or catalog_page_floor()


def apply_visitor_stamp_floor(text: str, floor: str) -> str:
    """Raise labeled visitor calendar stamps to floor. Never invent prices."""
    if not floor or not ISO_DATE_RE.fullmatch(floor):
        return text

    def repl(m: re.Match[str]) -> str:
        groups = m.groups()
        prefix = groups[0]
        current = groups[1]
        suffix = groups[2] if len(groups) > 2 else ""
        kept = later_iso_date(current, floor) or current
        return f"{prefix}{kept}{suffix}"

    out = text
    for rx in VISITOR_STAMP_REWRITE_RES:
        out = rx.sub(repl, out)
    return out


def apply_page_stamp_floor(html: str, floor: str) -> str:
    """Raise page-level calendar stamps that are earlier than floor. Cards stay."""
    if not floor or not ISO_DATE_RE.fullmatch(floor):
        return html

    def raise_page(chunk: str) -> str:
        def repl(m: re.Match[str]) -> str:
            groups = m.groups()
            prefix = groups[0]
            current = groups[1]
            suffix = groups[2] if len(groups) > 2 else ""
            kept = later_iso_date(current, floor) or current
            return f"{prefix}{kept}{suffix}"

        out = chunk
        for rx in PAGE_REWRITE_RES:
            out = rx.sub(repl, out)
        return out

    parts: list[str] = []
    last = 0
    for m in CARD_RE.finditer(html):
        parts.append(raise_page(html[last : m.start()]))
        parts.append(m.group(0))
        last = m.end()
    parts.append(raise_page(html[last:]))
    return "".join(parts)


def apply_card_checked_floors(html: str, floors: dict[str, str]) -> str:
    """Raise per-ASIN Checked dates to max(current, floor). Other fields untouched."""

    def card_repl(m: re.Match[str]) -> str:
        card = m.group(0)
        asin = m.group(1)
        floor = floors.get(asin)
        if not floor or not ISO_DATE_RE.fullmatch(floor):
            return card

        def date_repl(dm: re.Match[str]) -> str:
            kept = later_iso_date(dm.group(2), floor) or dm.group(2)
            return f"{dm.group(1)}{kept}{dm.group(3)}"

        return CARD_CHECKED_RE.sub(date_repl, card)

    return CARD_RE.sub(card_repl, html)


def clamp_comparison_stamps(
    existing_html: str, proposed_html: str
) -> tuple[str, list[str]]:
    """Rewrite proposed stamps so none go earlier than existing. Prices unchanged."""
    notes: list[str] = []
    if not existing_html or not proposed_html:
        return proposed_html, notes

    exist_page = extract_page_stamps(existing_html)
    prop_page = extract_page_stamps(proposed_html)
    page_floor = later_iso_date(*exist_page.values())
    out = proposed_html
    if page_floor:
        for kind, current in prop_page.items():
            floor_kind = later_iso_date(current, exist_page.get(kind), page_floor)
            if current and floor_kind and current < floor_kind:
                notes.append(f"clamped page {kind} {current} -> {floor_kind}")
        out = apply_page_stamp_floor(out, page_floor)

    exist_cards = extract_card_checked(existing_html)
    prop_cards = extract_card_checked(proposed_html)
    card_floors: dict[str, str] = {}
    for asin, exist_date in exist_cards.items():
        incoming = prop_cards.get(asin)
        kept = later_iso_date(exist_date, incoming)
        if not kept:
            continue
        card_floors[asin] = kept
        if incoming and incoming < exist_date:
            notes.append(f"clamped {asin} Checked {incoming} -> {exist_date}")
    if card_floors:
        out = apply_card_checked_floors(out, card_floors)
    return out, notes


def stamp_rollback_errors(
    existing_html: str,
    proposed_html: str,
    *,
    page_id: str = "",
) -> list[str]:
    """Errors when proposed page/card dates are earlier than existing."""
    label = page_id or "comparison"
    errors: list[str] = []
    exist_page = extract_page_stamps(existing_html)
    prop_page = extract_page_stamps(proposed_html)
    for kind, exist_date in exist_page.items():
        incoming = prop_page.get(kind)
        if incoming and incoming < exist_date:
            errors.append(
                f"{label}: would roll back page {kind} {exist_date} -> {incoming}"
            )
    exist_cards = extract_card_checked(existing_html)
    prop_cards = extract_card_checked(proposed_html)
    for asin, exist_date in exist_cards.items():
        incoming = prop_cards.get(asin)
        if incoming and incoming < exist_date:
            errors.append(
                f"{label}: would roll back {asin} Checked {exist_date} -> {incoming}"
            )
    return errors


def page_stamp_floor_errors(
    html: str,
    *,
    page_floor: str,
    checked_floors: dict[str, str],
    page_id: str = "",
) -> list[str]:
    """Errors when committed HTML sits earlier than a known daily SoT floor."""
    label = page_id or "comparison"
    errors: list[str] = []
    page = extract_page_stamps(html)
    for kind in ("as_of", "last_updated", "date_modified", "last_checked"):
        current = page.get(kind)
        if current and page_floor and current < page_floor:
            errors.append(f"{label}: {kind} {current} is earlier than {page_floor}")
        if kind in {"as_of", "last_updated"} and not current:
            errors.append(f"{label}: missing {kind} stamp")
    cards = extract_card_checked(html)
    for asin, floor in checked_floors.items():
        current = cards.get(asin)
        if not current:
            errors.append(f"{label}: missing Checked for {asin}")
        elif current < floor:
            errors.append(
                f"{label}: {asin} Checked {current} is earlier than SoT {floor}"
            )
    return errors


def iter_comparison_html(site_root, slugs: Iterable[str] | None = None):
    """Yield (rel_path, html) for comparison pages under site_root."""
    root = Path(site_root)
    if slugs is None:
        paths = sorted(root.glob("*/comparison/index.html"))
    else:
        paths = [root / slug / "comparison" / "index.html" for slug in slugs]
    for path in paths:
        if path.is_file():
            yield path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")


def load_comparison_floors(data_dir) -> dict[str, dict]:
    """Load per-slug page_floor + checked floors. Fleet JSON wins; robot JSON fills."""
    data_dir = Path(data_dir)
    floors: dict[str, dict] = {}

    fleet_path = data_dir / FLEET_FLOOR_NAME
    if fleet_path.is_file():
        fleet = json.loads(fleet_path.read_text(encoding="utf-8"))
        default_floor = fleet.get("page_floor")
        for slug, page in (fleet.get("pages") or {}).items():
            if not isinstance(page, dict):
                continue
            floors[slug] = {
                "page_floor": page.get("page_floor") or default_floor,
                "checked": dict(page.get("checked") or {}),
                "page": page.get("page") or f"{slug}/comparison/",
            }

    robot_path = data_dir / ROBOT_FLOOR_NAME
    if robot_path.is_file() and "robot-vacuums" not in floors:
        robot = json.loads(robot_path.read_text(encoding="utf-8"))
        floors["robot-vacuums"] = {
            "page_floor": robot.get("page_floor"),
            "checked": dict(robot.get("checked") or {}),
            "page": robot.get("page") or "robot-vacuums/comparison/",
        }
    return floors


def apply_known_stamp_floors(
    html: str,
    slug: str | None,
    floors: dict[str, dict] | None,
) -> tuple[str, list[str]]:
    """Raise page/card stamps to a durable SoT floor. Prices and copy stay."""
    notes: list[str] = []
    if not html or not slug or not floors:
        return html, notes
    spec = floors.get(slug)
    if not spec:
        return html, notes
    page_floor = spec.get("page_floor")
    checked = spec.get("checked") or {}
    before_page = extract_page_stamps(html)
    before_cards = extract_card_checked(html)
    out = html
    if page_floor:
        out = apply_page_stamp_floor(out, page_floor)
    if checked:
        out = apply_card_checked_floors(out, checked)
    after_page = extract_page_stamps(out)
    after_cards = extract_card_checked(out)
    for kind, after in after_page.items():
        before = before_page.get(kind)
        if before and after and before < after:
            notes.append(f"floor page {kind} {before} -> {after}")
    for asin, after in after_cards.items():
        before = before_cards.get(asin)
        if before and after and before < after:
            notes.append(f"floor {asin} Checked {before} -> {after}")
    return out, notes
