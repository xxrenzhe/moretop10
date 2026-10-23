#!/usr/bin/env python3
"""Densify Markdown → HTML (no network). Watch this fail before the converter exists."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from densify_html import htmlify_leaked_markdown, leak_errors  # noqa: E402


def main() -> int:
    errors: list[str] = []

    heading_rest = htmlify_leaked_markdown(
        "<p>### Balance-to-pedal converts The RoyalBaby EZ Kids Bike "
        "(B0BCQ1VJDP, $239.99 snapshot) is the everyday Top pick.</p>"
    )
    if "<h3>Balance-to-pedal converts</h3>" not in heading_rest:
        errors.append(f"heading+rest missing h3: {heading_rest!r}")
    if "<p>The RoyalBaby EZ Kids Bike" not in heading_rest:
        errors.append(f"heading+rest missing leftover paragraph: {heading_rest!r}")
    if "###" in heading_rest:
        errors.append(f"heading+rest still shows hashes: {heading_rest!r}")

    heading_h2 = htmlify_leaked_markdown("<p>## Step title leftover sentence here.</p>")
    if "<h2>Step title leftover sentence here.</h2>" not in heading_h2 and "<h2>Step title</h2>" not in heading_h2:
        errors.append(f"## did not become h2: {heading_h2!r}")
    if "##" in heading_h2:
        errors.append(f"## still visible: {heading_h2!r}")

    priced = htmlify_leaked_markdown(
        "<p>### Top pick: RoyalBaby EZ Kids Bike ($239.99) Balance-first learning "
        "with a one-button switch.</p>"
    )
    if "<h3>Top pick: RoyalBaby EZ Kids Bike ($239.99)</h3>" not in priced:
        errors.append(f"priced role heading split wrong: {priced!r}")
    if "<p>Balance-first learning with a one-button switch.</p>" not in priced:
        errors.append(f"priced role rest missing: {priced!r}")

    title_only = htmlify_leaked_markdown(
        "<p>### Dual Handbrake beginners bike (B0CPDZ7R5P)</p>"
    )
    if "<h3>Dual Handbrake beginners bike (B0CPDZ7R5P)</h3>" not in title_only:
        errors.append(f"title-only heading missing: {title_only!r}")
    if "<p>" in title_only:
        errors.append(f"title-only should not keep empty p: {title_only!r}")

    quoted = htmlify_leaked_markdown(
        "<p>### Lightweight magnesium “grow with me” RoyalBaby Astro 14–18 magnesium "
        "(B0HNJZDPWQ, $219.99) leans on Mg-Al frames.</p>"
    )
    if "<h3>Lightweight magnesium “grow with me”</h3>" not in quoted:
        errors.append(f"quoted title split wrong: {quoted!r}")
    if "RoyalBaby Astro 14–18 magnesium" not in quoted or "<p>" not in quoted:
        errors.append(f"quoted rest missing: {quoted!r}")

    table_src = (
        "<p>| Role | Model | Snapshot Price | | :--- | :--- | :--- | | "
        "<strong>Top pick</strong> | RoyalBaby EZ 12–20 Balance &amp; Pedal | $239.99 | | "
        "<strong>Best value</strong> | Dual Handbrake beginners 12–20 | $149.99 |</p>"
    )
    table = htmlify_leaked_markdown(table_src)
    if "<table" not in table or "<thead>" not in table or "<tbody>" not in table:
        errors.append(f"GFMD did not become table: {table!r}")
    if "<th>Role</th>" not in table or "<th>Model</th>" not in table:
        errors.append(f"table header cells missing: {table!r}")
    if "<strong>Top pick</strong>" not in table or "$239.99" not in table:
        errors.append(f"table dropped cell HTML/price: {table!r}")
    if "| :---" in table or "<p>|" in table:
        errors.append(f"table still leaked GFMD: {table!r}")

    fence = htmlify_leaked_markdown(
        "<p>``` [CASABREWS CM5418] --&gt; Lowest spend │ "
        "[CASABREWS 5418 PRO] --&gt; Adds FlashHeat ```</p>"
    )
    if "```" in fence:
        errors.append(f"fence ticks remain: {fence!r}")
    if "CASABREWS CM5418" not in fence or "Lowest spend" not in fence:
        errors.append(f"fence dropped diagram copy: {fence!r}")

    wrapped = (
        '<div class="gemini-shell-densify">'
        "<p>See the live [Kids Bikes comparison](/kids-bikes/comparison/).</p>"
        '<section class="key-insights prose-block" aria-label="Key insights">'
        "<h2>Key insights</h2><ul class=\"card-bullets\"><li>Keep me</li></ul>"
        "</section>"
        "</div>"
    )
    linked = htmlify_leaked_markdown(wrapped)
    if 'href="/kids-bikes/comparison/"' not in linked:
        errors.append(f"markdown link not htmlified: {linked!r}")
    if "[Kids Bikes comparison]" in linked:
        errors.append(f"markdown link text leftover: {linked!r}")
    if 'aria-label="Key insights"' not in linked or "<li>Keep me</li>" not in linked:
        errors.append("converter ate Key insights HTML")

    already_ok = (
        "<h2>Key insights</h2><p>No hashes here.</p>"
        '<table class="vs-table"><thead><tr><th>A</th></tr></thead></table>'
    )
    if htmlify_leaked_markdown(already_ok) != already_ok:
        errors.append("converter mutated already-valid HTML")

    leftover = leak_errors(
        "<p>### still leaked</p><p>| Role | X | | :--- | :--- | | a | b |</p>",
        "sample",
    )
    if not leftover:
        errors.append("leak_errors missed synthetic heading+table")
    if not any("| :---" in e or "###" in e or "heading" in e for e in leftover):
        errors.append(f"leak_errors message weak: {leftover!r}")

    clean = leak_errors("<h3>Ok</h3><table><thead><tr><th>A</th></tr></thead></table>", "clean")
    if clean:
        errors.append(f"leak_errors false positive: {clean!r}")

    if errors:
        print("densify_markdown_unit failed:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("densify_markdown_unit ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
