# P4 scenario batch draft — 2026-10-23

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the eight new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Do not touch:** open #48 (computer-speakers / tower-fans R8) and #49 (P1a Top+Upgrade reviews).

## Lock

User `lock-p4a-p4b`: eight hubs. Paths from `scenario-keyword-batch-locked-2026-10-23.md`.

| # | Path | Parent hub | Fill |
|---|------|------------|------|
| 1 | `/espresso-machines/best-espresso-machines-for-home/` | Live `/espresso-machines/` | `need_fill` |
| 2 | `/litter-boxes/best-automatic-litter-boxes/` | Live `/litter-boxes/` | `need_fill` |
| 3 | `/security-cameras/best-security-cameras-for-outdoor/` | Live `/security-cameras/` | `need_fill` |
| 4 | `/cordless-vacuums/best-cordless-vacuums-for-pet-hair/` | Live `/cordless-vacuums/` | `need_fill` |
| 5 | `/hair-dryers/best-hair-dryers-for-curly-hair/` | Live `/hair-dryers/` | `need_fill` |
| 6 | `/humidifiers/best-humidifiers-for-large-rooms/` | Live `/humidifiers/` | `need_fill` |
| 7 | `/projectors/best-projectors-for-outdoor/` | Live `/projectors/` | `need_fill` |
| 8 | `/pillows/best-pillows-for-side-sleepers/` | Existing P2 `/pillows/` (not recreated) | `need_fill` |

`/pillows/` already exists from P2 (`shortlist-pillows.json` density 6, neck-pain scene). This batch only adds the side-sleeper best-of.

## Inventory

Affiliate tokens are not available in this cloud VM. Sibling fill pack
`/workspace/shared/mt10-p4-fill-pack-2026-10-23.json` was **not attached** at bake time.

Honest empty shells (`products-best-*.json` with `products: []`) beat invented ASINs / was / %. Re-run:

```bash
python3 site/scripts/bake_p4_scenario.py
python3 tests/p4_scenario_assert.py
```

when the pack lands. Bake reads the shared path first, then `site/data/p4-l1-fill-pack-2026-10-23.json`.

## Collision bans (even after fill)

Stored in `site/data/p4-occupied-asins-2026-10-23.json`:

- **#2** litter-boxes main 10
- **#3** video-doorbells 10 (no doorbells)
- **#4** robot pet-homes / pet-hair 10 (cordless ≠ robot)
- **#6** P1b baby-humidifier 10
- **#8** P2 neck-pain pillow 6

No accessories as primary picks. Reviews skipped (Top + Upgrade articles do not exist for these scenes).

## Bake ≠ deploy

New pages stay `published=false` / noindex until a later 部署上线 order. Parent landings only gained a related-cluster link. Live cards, #48/#49, Lab, RR, and OL were not edited.
