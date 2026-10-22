#!/usr/bin/env python3
"""YP track as-is; PB still gets uid=fromsll. No network."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "scripts"))

from affiliate_uid import (  # noqa: E402
    AffiliateTrackError,
    classify_network,
    ensure_affiliate_uid,
    prepare_affiliate_link,
)


def main() -> None:
    errors: list[str] = []
    yp = "https://yeahpromos.com/index/index/openurlproduct?track=c93120b29c3785fb&pid=2287787"
    out = ensure_affiliate_uid(yp, "yp")
    if out != yp:
        errors.append(f"YP track was rewritten: {out}")
    if "uid=" in out:
        errors.append("YP track gained uid=")
    if prepare_affiliate_link(yp, "yp") != yp:
        errors.append("prepare_affiliate_link changed a YP track")

    maas = "https://www.amazon.com/dp/B0F1DRNWP7?tag=example-20"
    if ensure_affiliate_uid(maas, "yp") != maas:
        errors.append("Amazon maas URL was rewritten")
    if "uid=" in ensure_affiliate_uid(maas):
        errors.append("Amazon URL gained uid=")

    pb = "https://pboost.me/d5qev5gHd"
    pb_out = ensure_affiliate_uid(pb, "pb")
    if "uid=fromsll" not in pb_out:
        errors.append(f"PB hop missing uid=fromsll: {pb_out}")
    already = "https://pboost.me/d5qev5gHd?uid=other"
    if ensure_affiliate_uid(already, "pb") != "https://pboost.me/d5qev5gHd?uid=fromsll":
        errors.append("PB uid was not normalized to fromsll")

    if classify_network(yp) != "yp":
        errors.append("yeahpromos host should classify as yp")
    if classify_network(pb) != "pb":
        errors.append("pboost.me host should classify as pb")

    try:
        ensure_affiliate_uid("")
        errors.append("empty track should refuse")
    except AffiliateTrackError:
        pass
    try:
        ensure_affiliate_uid("https://evil.example/click")
        errors.append("wrong-host track should refuse")
    except AffiliateTrackError:
        pass

    if prepare_affiliate_link("#") is not None:
        errors.append("empty # slot should not mint a CTA")
    if prepare_affiliate_link("") is not None:
        errors.append("blank slot should not mint a CTA")

    if errors:
        raise SystemExit("affiliate_uid_assert failed:\n- " + "\n- ".join(errors))
    print("affiliate_uid_assert ok")


if __name__ == "__main__":
    main()
