#!/usr/bin/env python3
"""Unit tests for the CleanYourTV examples/README.md table parser."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from fetch_tv_models import classify_kind, classify_software_path, oem_from_slug, parse_examples_readme  # noqa: E402

SAMPLE = """
# Examples

One folder per TV model.

| Folder | TV | OS | Notes |
|---|---|---|---|
| `tcl-65c7k-google-tv/` | TCL 65" C7K QD-Mini LED Google TV, Brazil | Google TV 14 | setupwraith must go with launcherx |
| `xiaomi-mi-tv-4a/` | Xiaomi Mi TV 4A (MiTV-MOOQ1) | Android TV 10 | stock launcher replaced |
| `sony-kd-55x85j/` | Sony BRAVIA KD-55X85J (2021, BRAVIA_VH2), South America | Google TV 12 | reboot-checked |
| `hisense-u75-hengshan/` | Hisense U75 (hengshan, MediaTek), Latin America | Google TV 12 | Vtp_ACR content recognition |
| `amazon-fire-tv-stick-4k-2018/` | Amazon Fire TV Stick 4K, 1st gen 2018 (AFTMM) | Fire OS 6.7.1.1 / Android 7.1 | debloat only, sponsored rows need DNS blocking |
| `xgimi-mogo-2/` | XGIMI MoGo 2 projector (MoGo, xgimiapollo) | Android TV 11 | projector manager kept |
| not-a-row | skip me | |
"""


def main() -> None:
    errors: list[str] = []
    models = parse_examples_readme(SAMPLE)
    slugs = [m["slug"] for m in models]
    if slugs != [
        "tcl-65c7k-google-tv",
        "xiaomi-mi-tv-4a",
        "sony-kd-55x85j",
        "hisense-u75-hengshan",
        "amazon-fire-tv-stick-4k-2018",
        "xgimi-mogo-2",
    ]:
        errors.append(f"unexpected slugs {slugs}")
    if oem_from_slug("tcl-65c7k-google-tv") != "TCL":
        errors.append("TCL oem mapping failed")
    if oem_from_slug("xiaomi-mi-tv-4a") != "Xiaomi":
        errors.append("Xiaomi oem mapping failed")
    if classify_kind("amazon-fire-tv-stick-4k-2018", "Amazon Fire TV Stick 4K", "Fire OS 6") != "fire_stick":
        errors.append("Fire Stick kind mapping failed")
    if classify_kind("xgimi-mogo-2", "XGIMI MoGo 2 projector", "Android TV 11") != "projector":
        errors.append("projector kind mapping failed")
    path = classify_software_path("Fire OS 6.7.1.1 / Android 7.1", "debloat only", "fire_stick")
    if "Debloat only" not in path:
        errors.append(f"Fire Stick software path should be debloat-only, got {path!r}")
    gtv = classify_software_path("Google TV 14", "setupwraith must go", "panel")
    if gtv != "Try software first":
        errors.append(f"Google TV path should try software first, got {gtv!r}")
    if any(m["slug"] == "not-a-row" for m in models):
        errors.append("parser accepted a non-table line")
    if errors:
        raise SystemExit("tv_models_parse_unit failed:\n- " + "\n- ".join(errors))
    print("tv_models_parse_unit ok")


if __name__ == "__main__":
    main()
