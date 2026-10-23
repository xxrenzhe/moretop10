# Robot comparison stamp anti-rollback — 2026-10-24

**waiting_for_部署上线:** yes · draft only · no wrangler · not Live · not Lab / RR / OL

## Bug

Daily Live tree 2026-10-23 had `/robot-vacuums/comparison/` page **As of / Last Updated 2026-10-23** and per-ASIN Checked up to **2026-10-23**. Later scenario-PR apex from git tip rewrote visitor stamps back to **2026-10-20** (card mix 10-18 / 10-20). Fleet rule: day-update may advance catalog stamps; bake / redeploy must never push visitor calendar stamps earlier.

## SoT

`mt10-robot-stamp-sot-2026-10-24/` from the daily-388 bake (page dates 2026-10-23; `asin-checked-from-daily388.json`). Merged stamp fields only into current tip HTML — prices, ASINs, scores, and copy unchanged.

Durable floor: `site/data/robot-vacuums-comparison-stamp-floor.json`.

## Guard

Reusable `site/scripts/stamp_guard.py` (RR-style last-checked max). `build.py` comparison writes clamp proposed HTML against the existing file. `tests/stamp_guard_unit.py` + `tests/robot_stamp_assert.py` fail if the committed robot chart sits earlier than the SoT or if a proposed bake would roll dates back.

```
python3 tests/stamp_guard_unit.py && python3 tests/robot_stamp_assert.py
```

Also hooked into `build.py` `verify()`. #54 home-nav is a separate open PR and is not in this change.

Bake ≠ deploy.
