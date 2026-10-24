# MT10 day-add draft — 2026-10-24

**waiting_for_部署上线:** yes
**published:** false / type-07 `noindex,follow`; hubs match P2 unpublished-hub chrome
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.
**Do not touch:** open #54 (home nav) and #55 (stamp).

## Lock

User day-add 9 niches from the L1 fill pack. Three brand_gate fails skipped.

| # | Path | Density | Fill |
|---|------|---------|------|
| 1 | `/pool-heat-pumps/` | **10** | `filled` (PB fromsll) |
| 2 | `/kitchen-rugs/` | **10** | `filled` (PB fromsll) |
| 3 | `/light-therapy/` | **8** | `filled honest stub (8)` (PB fromsll) |
| 4 | `/bike-racks/` | **10** | `filled` (PB fromsll) |
| 5 | `/nightstands/` | **9** | `filled honest stub (9)` (PB fromsll) |
| 6 | `/robotic-pool-cleaners/` | **8** | `filled honest stub (8)` (PB fromsll) |
| 7 | `/barstools/` | **10** | `filled` (PB fromsll) |
| 8 | `/docking-stations/` | **8** | `filled honest stub (8)` (PB fromsll) |
| 9 | `/bookcases/` | **10** | `filled` (PB fromsll) |

**Skipped:** `/3d-printing-filament/` — brand_gate FAIL · R QIDI Technology-only.
**Skipped:** `/floor-lamps/` — brand_gate FAIL · Honeywell-only.
**Skipped:** `/chef-s-knives/` — brand_gate FAIL · Paudin-only.

**Total:** 83 distinct ASINs.

## L1 fill

Applied pack `site/data/mt10-day-add-l1-fill-pack-2026-10-24.json` (report: `site/data/mt10-day-add-l1-fill-report-2026-10-24.md`). YP site 11767 was discovery-only. Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/mt10-day-add-occupied-2026-10-24.json` (772 ASINs). Pack hits = 0.

```bash
python3 site/scripts/bake_mt10_day_add.py
python3 tests/mt10_day_add_assert.py
```

## Collision bans kept

- Global occupied flat (772)
- Brand-gate fails not scaffolded

No accessories invented as heroes. No invented was / %. Reviews skipped. `list_price` from the pack is not rendered as a strike/was. Shortfalls are not padded.

## Bake ≠ deploy

Pages stay `published=false` until a later 部署上线 order. Do not merge. Do not Cloudflare Live / wrangler deploy. #54 home nav and #55 stamp were not touched.

