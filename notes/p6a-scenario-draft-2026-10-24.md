# P6a scenario batch draft — 2026-10-24

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the seven new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Parent hubs:** already exist — not recreated.  
**Tip:** `c58e0df1` (#54+#55+#57).

## Lock

User `lock-p6a-rec`: seven type-07 children from the L1 fill pack (density≥4 only).

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/robotic-pool-cleaners/best-robotic-pool-cleaners-for-inground-pools/` | Live `/robotic-pool-cleaners/` | **10** | `filled` (PB fromsll) |
| 2 | `/bike-racks/best-bike-racks-for-hitch/` | Live `/bike-racks/` | **9** | `filled` (PB fromsll) |
| 3 | `/espresso-machines/best-espresso-machines-under-500/` | Live `/espresso-machines/` | **9** | `filled` (PB fromsll) |
| 4 | `/hair-dryers/best-hair-dryers-for-thick-hair/` | Live `/hair-dryers/` | **10** | `filled` (PB fromsll) |
| 5 | `/security-cameras/best-security-cameras-for-indoor/` | Live `/security-cameras/` | **10** | `filled` (PB fromsll) |
| 6 | `/projectors/best-projectors-for-bedroom/` | Live `/projectors/` | **6** | `filled` (PB fromsll) |
| 7 | `/dehumidifiers/best-dehumidifiers-for-bathroom/` | Live `/dehumidifiers/` | **7** | `filled` (PB fromsll) |

**Skipped:** `/pillows/best-pillows-for-back-sleepers/` — SHORTFALL n=2 < density 4.  
**OUT (not reopened):** `/mattresses/best-mattresses-for-back-pain/`.

**Total:** 61 distinct ASINs (10 / 9 / 9 / 10 / 10 / 6 / 7). Parent landings only gained a related-cluster link.

## L1 fill

Applied pack `site/data/p6a-l1-fill-pack-2026-10-24.json` (report: `site/data/p6a-l1-fill-report-2026-10-24.md`). YP site 11767 probed — 0 usable (honest PB-only). Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/p6a-occupied-asins-2026-10-24.json` (855 ASINs). Pack hits = 0.

```bash
python3 site/scripts/bake_p6a_scenario.py
python3 tests/p6a_scenario_assert.py
```

## Collision bans kept

- Espresso home + beginners siblings
- Hair curly / fine / travel siblings
- Security outdoor sibling
- Projector outdoor + home-theater siblings
- Dehumidifier basement sibling
- Global occupied flat (855)
- Soft parent densify: hub ASINs may appear on a scene; this pack did not reuse any (`soft_parent_count=0`)

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was. Honest shortfall card counts are not padded.

## Soft parent densify

Prefer, do not block. Sibling scene ASINs stay banned. Parent landings only gained a related-cluster link. Parent hub cards were not rewritten.

## Comparison / reviews stubs

Parent `/comparison/` and `/reviews/` already exist (day-add / prior scenario SoT). This bake does not recreate them and does not roll As of / Checked stamps earlier than 2026-10-24.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Do not merge. Do not Cloudflare Live / wrangler deploy. #54 home nav and #55 stamp were not touched.
