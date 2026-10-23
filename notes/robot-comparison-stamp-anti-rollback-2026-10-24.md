# Comparison stamp anti-rollback — 2026-10-24

**waiting_for_部署上线:** yes · draft only · no wrangler · not Live · not Lab / RR / OL

## Bug

Daily Live tree 2026-10-23 had 21 `/<hub>/comparison/` pages with **As of / Last Updated 2026-10-23**. Later scenario-PR apex from git tip rewrote visitor stamps back to **2026-10-20**. Fleet rule: day-update may advance catalog stamps; bake / redeploy must never push visitor calendar stamps earlier.

Hubs: air-fryers, air-purifiers, bluetooth-speakers, computer-speakers, cordless-vacuums, dash-cams, dehumidifiers, espresso-machines, hair-dryers, humidifiers, kids-bikes, litter-boxes, massage-guns, noise-cancelling-headphones, projectors, robot-vacuums, security-cameras, standing-desks, tower-fans, video-doorbells, wet-dry-vacuums.

## SoT

`mt10-stamp-sot-all-cmp-2026-10-24/` (daily-388). Merged stamp fields only into current tip HTML — prices, ASINs, scores, ranking, and copy unchanged. Matching-ASIN Checked dates take `max(tip, daily)`. Tip-only ASINs keep their tip Checked (no invented products).

Durable floors:
- `site/data/comparison-stamp-floors.json` (all 21)
- `site/data/robot-vacuums-comparison-stamp-floor.json` (robot, kept)

## Guard

Reusable `site/scripts/stamp_guard.py` (RR-style last-checked max). `build.py` comparison writes (1) clamp proposed HTML against the existing file and (2) raise to the durable fleet floor so a Live-tip rebase cannot roll calendar days backward.

```
python3 tests/stamp_guard_unit.py && python3 tests/robot_stamp_assert.py && python3 tests/comparison_stamp_assert.py
```

Also hooked into `build.py` `verify()`. #54 home-nav is a separate open PR and is not in this change.

Bake ≠ deploy.
