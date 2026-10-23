# P4 scenario batch draft — 2026-10-23

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the eight new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Do not touch:** open #48 (computer-speakers / tower-fans R8) and #49 (P1a Top+Upgrade reviews).

## Lock

User `lock-p4a-p4b`: eight hubs. Paths from `scenario-keyword-batch-locked-2026-10-23.md`.

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/espresso-machines/best-espresso-machines-for-home/` | Live `/espresso-machines/` | **10** | `filled` (PB fromsll) |
| 2 | `/litter-boxes/best-automatic-litter-boxes/` | Live `/litter-boxes/` | **10** | `filled` (PB fromsll) |
| 3 | `/security-cameras/best-security-cameras-for-outdoor/` | Live `/security-cameras/` | **10** | `filled` (PB fromsll) |
| 4 | `/cordless-vacuums/best-cordless-vacuums-for-pet-hair/` | Live `/cordless-vacuums/` | **10** | `filled` (PB fromsll) |
| 5 | `/hair-dryers/best-hair-dryers-for-curly-hair/` | Live `/hair-dryers/` | **10** | `filled` (PB fromsll) |
| 6 | `/humidifiers/best-humidifiers-for-large-rooms/` | Live `/humidifiers/` | **10** | `filled` (PB fromsll) |
| 7 | `/projectors/best-projectors-for-outdoor/` | Live `/projectors/` | **10** | `filled` (PB fromsll) |
| 8 | `/pillows/best-pillows-for-side-sleepers/` | Existing P2 `/pillows/` (not recreated) | **10** | `filled` (PB fromsll) |

**Total:** 80 distinct ASINs. `/pillows/` already existed from P2 (`shortlist-pillows.json` density 6, neck-pain scene). This batch only adds the side-sleeper best-of.

## L1 fill

Applied sibling pack `site/data/p4-l1-fill-pack-2026-10-23.json` (report: `site/data/p4-l1-fill-report-2026-10-23.md`). YP catalog was non-matching and unused. Pack is PB-only.

Occupied collision set: `site/data/p4-occupied-asins-2026-10-23.json` (155 ASINs). Pack hits = 0.

```bash
python3 site/scripts/bake_p4_scenario.py
python3 tests/p4_scenario_assert.py
```

## Collision bans kept

- **#2** litter-boxes main
- **#3** video-doorbells (no doorbells)
- **#4** robot pet-homes / pet-hair (cordless ≠ robot)
- **#6** P1b baby-humidifier + humidifier hub
- **#8** P2 neck-pain pillow / shortlist-pillows

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Parent landings only gained a related-cluster link. Live cards, #48/#49, Lab, RR, and OL were not edited.
