#!/usr/bin/env python3
"""Watch-outs leftover scrub — unit + baked site (no network, no deploy)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "site" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from watchouts import (  # noqa: E402
    CATEGORY_CONFIRM,
    LEFTOVER,
    leftover_in_watchouts,
    scrub_watchouts,
    site_errors,
    watchouts_list_text,
)


def _card(cons: list[str]) -> str:
    items = "".join(f"<li>{c}</li>" for c in cons)
    return (
        '<section class="landing-pick" id="pick-1">'
        '<div class="pc-col-title cons">Watch-outs</div>'
        f"<ul>{items}</ul>"
        "</section>"
    )


def main() -> int:
    errors: list[str] = []

    dehum = _card(
        [
            "Skip if you only need a small closet dehumidifier.",
            LEFTOVER,
        ]
    )
    out = scrub_watchouts(dehum, "dehumidifiers")
    items = watchouts_list_text(out)
    if LEFTOVER in out or leftover_in_watchouts(out):
        errors.append("dehumidifier unit still has robot-vac leftover")
    expected = CATEGORY_CONFIRM["dehumidifiers"]
    if expected not in items:
        errors.append("dehumidifier unit missing tank / drain / sq ft confirm")
    if "Skip if you only need a small closet dehumidifier." not in items:
        errors.append("dehumidifier unit dropped the fitting skip line")

    fry = scrub_watchouts(_card([LEFTOVER]), "air-fryers")
    if CATEGORY_CONFIRM["air-fryers"] not in watchouts_list_text(fry):
        errors.append("air-fryers unit missing basket / counter confirm")

    robot = scrub_watchouts(_card(["Skip if budget is tight.", LEFTOVER]), "robot-vacuums")
    if LEFTOVER not in watchouts_list_text(robot):
        errors.append("robot-vacuums unit must keep mop-pad confirm")

    unknown = scrub_watchouts(_card(["Skip if unsure.", LEFTOVER]), "not-a-cat")
    if LEFTOVER in unknown or leftover_in_watchouts(unknown):
        errors.append("unknown slug must drop leftover")
    if "Skip if unsure." not in watchouts_list_text(unknown):
        errors.append("unknown slug dropped the fitting skip line")

    already_dropped = scrub_watchouts(
        _card(["Skip if you only need a small closet dehumidifier."]),
        "dehumidifiers",
    )
    if CATEGORY_CONFIRM["dehumidifiers"] not in watchouts_list_text(already_dropped):
        errors.append("dehumidifier without leftover must still get tank / drain confirm")

    errors.extend(site_errors(ROOT / "site"))

    if errors:
        print("watchouts_assert failed:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("watchouts_assert: ok")
    print("  unit: dehumidifiers / air-fryers replace; robot-vacuums keep")
    print("  baked landings: leftover gone on non-robot cats")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
