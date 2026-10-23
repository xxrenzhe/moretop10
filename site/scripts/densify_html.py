#!/usr/bin/env python3
"""Turn leaked densify Markdown into visitor HTML.

`div.gemini-shell-densify` (and similar editorial bodies) were sometimes baked
with raw GFMD — `###` headings and `| :--- |` pipe tables inside `<p>` tags.
Bake must emit HTML. No new product claims; cell/heading copy is preserved.

Usage:
    python3 site/scripts/densify_html.py
"""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

SKIP_DIRS = {".cache", "fixtures", "data", "assets"}

P_HEADING_RE = re.compile(r"<p>\s*(#{1,6})\s+([\s\S]*?)</p>", re.I)
P_TABLE_RE = re.compile(r"<p>(\s*\|[\s\S]*?\|\s*)</p>", re.I)
P_FENCE_RE = re.compile(r"<p>\s*```([\s\S]*?)```\s*</p>", re.I)
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BT_PATH_RE = re.compile(r"`(/[a-z0-9][-a-z0-9/]*/?)`")
ALIGN_CELL_RE = re.compile(r"^:?-{3,}:?$")
ROLE_PREFIX = r"(?:Top pick|Best value|Upgrade|Premium|Baseline Top pick)"
TITLE_ROLE_RE = re.compile(
    r"^(.+? — (?:Top pick|Premium|Best value|Upgrade|#\d+) \([B0-9A-Z]+\))\s+(.+)$"
)
PRICED_ROLE_RE = re.compile(rf"^({ROLE_PREFIX}: .+?\(\$[\d.,]+\))\s+(.+)$")
QUOTED_TITLE_RE = re.compile(r"^(.+?[“\"][^”\"]+[”\"])\s+(.+)$")
THE_TITLE_RE = re.compile(
    r"^((?:[A-Za-z0-9][A-Za-z0-9'’\-]*(?:[ \t]+[A-Za-z0-9'’\-]+){0,7}))\s+(The\s+.+)$"
)

LEAK_P_HEADING_RE = re.compile(r"<p>\s*#{1,6}\s")
LEAK_ALIGN_RE = re.compile(r"\|\s*:?-{3,}:?\s*\|")


def split_heading_text(text: str) -> tuple[str, str]:
    """Split `### Title rest…` into title + leftover sentence."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "", ""

    for rx in (PRICED_ROLE_RE, TITLE_ROLE_RE, QUOTED_TITLE_RE):
        match = rx.match(text)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    match = THE_TITLE_RE.match(text)
    if match and ":" not in match.group(1):
        return match.group(1).strip(), match.group(2).strip()

    return text, ""


def _heading_repl(match: re.Match[str]) -> str:
    hashes, body = match.group(1), match.group(2)
    level = min(max(len(hashes), 2), 3)
    tag = f"h{level}"
    title, rest = split_heading_text(body)
    if not title:
        return match.group(0)
    out = f"<{tag}>{title}</{tag}>"
    if rest:
        out += f"<p>{rest}</p>"
    return out


def _split_gfmd_rows(text: str) -> list[list[str]]:
    parts = [part.strip() for part in text.split("|")]
    rows: list[list[str]] = []
    current: list[str] = []
    for part in parts:
        if part == "":
            if current:
                rows.append(current)
                current = []
            continue
        current.append(part)
    if current:
        rows.append(current)
    return [row for row in rows if row]


def _is_align_row(row: list[str]) -> bool:
    return bool(row) and all(ALIGN_CELL_RE.match(re.sub(r"\s+", "", cell) or "") for cell in row)


def gfmd_table_html(text: str) -> str:
    rows = _split_gfmd_rows(text)
    rows = [row for row in rows if not _is_align_row(row)]
    if len(rows) < 2:
        return ""
    header, body = rows[0], rows[1:]
    width = len(header)
    if width < 2 or any(len(row) != width for row in body):
        return ""
    thead = "<thead><tr>" + "".join(f"<th>{cell}</th>" for cell in header) + "</tr></thead>"
    tbody_rows = []
    for row in body:
        tbody_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    tbody = "<tbody>" + "".join(tbody_rows) + "</tbody>"
    return (
        '<div class="densify-table-wrap"><table class="densify-table">'
        f"{thead}{tbody}</table></div>"
    )


def _table_repl(match: re.Match[str]) -> str:
    inner = match.group(1)
    if not LEAK_ALIGN_RE.search(inner):
        return match.group(0)
    html = gfmd_table_html(inner)
    return html or match.group(0)


def _fence_repl(match: re.Match[str]) -> str:
    inner = match.group(1).strip()
    inner = inner.strip("`").strip()
    parts = [part.strip() for part in re.split(r"\s*│\s*", inner) if part.strip()]
    if len(parts) >= 2:
        return "<ul>" + "".join(f"<li>{part}</li>" for part in parts) + "</ul>"
    return f"<p>{inner}</p>" if inner else ""


def _md_link_repl(match: re.Match[str]) -> str:
    label, href = match.group(1), match.group(2).strip()
    if href.startswith("<"):
        return match.group(0)
    return f'<a href="{escape(href, quote=True)}">{label}</a>'


def _bt_path_repl(match: re.Match[str]) -> str:
    href = match.group(1)
    return f'<a href="{escape(href, quote=True)}">{escape(href)}</a>'


def _match_div_end(html: str, start: int) -> int:
    """Return index after the closing </div> that matches the <div at start."""
    open_tag = re.compile(r"<div\b", re.I)
    close_tag = re.compile(r"</div>", re.I)
    first = open_tag.search(html, start)
    if not first or first.start() != start:
        return start
    depth = 0
    i = start
    while i < len(html):
        nxt_open = open_tag.search(html, i)
        nxt_close = close_tag.search(html, i)
        if not nxt_close:
            return len(html)
        if nxt_open and nxt_open.start() < nxt_close.start():
            depth += 1
            i = nxt_open.end()
            continue
        depth -= 1
        i = nxt_close.end()
        if depth == 0:
            return i
    return len(html)


def _map_class_inner(html: str, class_name: str, fn) -> str:
    needle = f'class="{class_name}"'
    out: list[str] = []
    i = 0
    while True:
        pos = html.find(needle, i)
        if pos < 0:
            out.append(html[i:])
            break
        start = html.rfind("<div", i, pos + 1)
        if start < 0:
            out.append(html[i : pos + len(needle)])
            i = pos + len(needle)
            continue
        end = _match_div_end(html, start)
        block = html[start:end]
        inner_open = block.find(">")
        inner_close = block.rfind("</div>")
        if inner_open < 0 or inner_close < 0:
            out.append(html[i:end])
            i = end
            continue
        inner = block[inner_open + 1 : inner_close]
        converted = block[: inner_open + 1] + fn(inner) + block[inner_close:]
        out.append(html[i:start])
        out.append(converted)
        i = end
    return "".join(out)


def _htmlify_inline_md(inner: str) -> str:
    inner = MD_LINK_RE.sub(_md_link_repl, inner)
    inner = BT_PATH_RE.sub(_bt_path_repl, inner)
    return inner


def htmlify_leaked_markdown(html: str) -> str:
    """Convert leaked MD headings/tables/fences/links. Idempotent on clean HTML."""
    if not html:
        return html
    html = P_HEADING_RE.sub(_heading_repl, html)
    html = P_TABLE_RE.sub(_table_repl, html)
    html = P_FENCE_RE.sub(_fence_repl, html)
    html = _map_class_inner(html, "gemini-shell-densify", _htmlify_inline_md)
    return html


def _visible_html(html: str) -> str:
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.S | re.I)
    return html


def leak_errors(html: str, label: str) -> list[str]:
    """Fail if visitor HTML still contains `| :---` or `<p>### ` (or fences)."""
    vis = _visible_html(html)
    errors: list[str] = []
    if LEAK_P_HEADING_RE.search(vis):
        errors.append(f"{label} still has <p>### heading leak")
    if LEAK_ALIGN_RE.search(vis):
        errors.append(f"{label} still has | :--- pipe-table leak")
    if "```" in vis:
        errors.append(f"{label} still has leftover ``` fence")
    return errors


def iter_site_html(site: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(site.rglob("*.html")):
        if set(path.relative_to(site).parts) & SKIP_DIRS:
            continue
        paths.append(path)
    return paths


def scan_site(site: Path) -> tuple[int, int, list[str]]:
    """Return (pages_scanned, pages_with_leaks, error_lines)."""
    errors: list[str] = []
    leaked = 0
    scanned = 0
    for path in iter_site_html(site):
        scanned += 1
        rel = str(path.relative_to(site))
        page_errors = leak_errors(path.read_text(encoding="utf-8"), rel)
        if page_errors:
            leaked += 1
            errors.extend(page_errors)
    return scanned, leaked, errors


def site_errors(site: Path) -> list[str]:
    _scanned, _leaked, errors = scan_site(site)
    return errors


def rewrite_site(site: Path) -> list[Path]:
    wrote: list[Path] = []
    for path in iter_site_html(site):
        text = path.read_text(encoding="utf-8")
        new = htmlify_leaked_markdown(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            wrote.append(path)
    return wrote


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    site = root / "site"
    wrote = rewrite_site(site)
    scanned, leaked, errors = scan_site(site)
    print(f"densify_html rewrote {len(wrote)} pages (scanned {scanned})")
    for path in wrote:
        print(f"  wrote {path.relative_to(root)}")
    if errors:
        print("densify_html leaks remain:")
        for err in errors:
            print(f"- {err}")
        return 1
    print(f"densify_html ok (leaked={leaked})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
