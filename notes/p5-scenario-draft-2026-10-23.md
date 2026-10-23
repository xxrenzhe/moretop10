# P5a scenario batch draft — 2026-10-23

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the eight new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Parent hubs:** already exist — not recreated.

## Lock

User `lock-p5a`: eight type-07 children. Density 10 from the L1 pack.

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/hair-dryers/best-hair-dryers-for-fine-hair/` | Live `/hair-dryers/` | **10** | `filled` (PB fromsll) |
| 2 | `/projectors/best-projectors-for-home-theater/` | Live `/projectors/` | **10** | `filled` (PB fromsll) |
| 3 | `/espresso-machines/best-espresso-machines-for-beginners/` | Live `/espresso-machines/` | **10** | `filled` (PB fromsll) |
| 4 | `/bluetooth-speakers/best-bluetooth-speakers-for-outdoor/` | Live `/bluetooth-speakers/` | **10** | `filled` (PB fromsll) |
| 5 | `/cordless-vacuums/best-cordless-vacuums-for-cars/` | Live `/cordless-vacuums/` | **10** | `filled` (PB fromsll) |
| 6 | `/hair-dryers/best-hair-dryers-for-travel/` | Live `/hair-dryers/` | **10** | `filled` (PB fromsll) |
| 7 | `/cordless-vacuums/best-cordless-vacuums-for-hardwood-floors/` | Live `/cordless-vacuums/` | **10** | `filled` (PB fromsll) |
| 8 | `/computer-speakers/best-computer-speakers-for-desktop/` | Live `/computer-speakers/` | **10** | `filled` (PB fromsll) |

**Total:** 80 distinct ASINs. Parent landings only gained a related-cluster link.

## L1 fill

Applied pack `site/data/p5-l1-fill-pack-2026-10-23.json` (report: `site/data/p5-l1-fill-report-2026-10-23.md`). YP site 11767 timed out or returned HTTP 500; unused. Pack is PB-only. Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/p5-occupied-asins-2026-10-23.json` (429 ASINs). Pack hits = 0.

```bash
python3 site/scripts/bake_p5_scenario.py
python3 tests/p5_scenario_assert.py
```

## Collision bans kept

- P4 curly-hair dryers
- P4 outdoor projectors
- P4 for-home espresso
- P4 pet-hair cordless + robot / pet-homes
- fine↛travel
- car↛hardwood
- outdoor-BT↛#8 desktop (no portable bluetooth bleed)

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Parent landings only gained a related-cluster link. Live cards, P4 pages, Lab, RR, and OL were not edited.
