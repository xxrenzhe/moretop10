# P7 scenario batch draft — 2026-10-24

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the seven type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Parent hubs:** already exist — not recreated.  
**Tip:** `616fee79` (#65 Live).

## Lock

User `lock-p7-1-7` (#1–#7): seven type-07 children from the L1 fill pack (density≥4 only). Products JSON is the ASIN source of truth and was applied **as-is**.

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/hair-dryers/best-hair-dryers-for-men/` | Live `/hair-dryers/` | **10** | `filled` (PB fromsll) |
| 2 | `/dehumidifiers/best-dehumidifiers-for-rv/` | Live `/dehumidifiers/` | **10** | `filled` (PB fromsll) |
| 3 | `/kitchen-rugs/best-washable-kitchen-rugs/` | Live `/kitchen-rugs/` | **10** | `filled` (PB fromsll) |
| 4 | `/noise-cancelling-headphones/best-noise-cancelling-headphones-for-flying/` | Live `/noise-cancelling-headphones/` | **10** | `filled` (PB fromsll) |
| 5 | `/docking-stations/best-docking-stations-for-dual-monitors/` | Live `/docking-stations/` | **10** | `filled` (PB fromsll) |
| 6 | `/office-chairs/best-office-chairs-for-heavy-people/` | Live `/office-chairs/` | **10** | `filled` (PB fromsll) |
| 7 | `/dash-cams/best-dash-cams-for-motorcycle/` | Live `/dash-cams/` | **10** | `filled` (PB fromsll) |

**Skipped:** none. All seven lock scenes passed density ≥4.  
**OUT (not opened):** tinnitus · seniors · mattress hang · robot-mop · TV · litter kittens · Lab.  
**#58/#60/#61/#64/#65:** P6a–d OK scenes stay `published=true`. Day-add shells stay unpublished.

**Total:** 70 distinct ASINs (10 × 7). Parent landings only gained a related-cluster link.

## L1 fill

Applied pack `site/data/p7-l1-fill-pack-2026-10-24.json` (report: `site/data/p7-l1-fill-report-2026-10-24.md`). Scene cards come from uploaded `site/data/products-best-*.json` (as-is SoT). YP site 11767 probed — 0 usable (honest PB-only). Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/p7-occupied-asins-2026-10-24.json` (P6d flat + #65 admitted + sibling/hub bans). Pack sibling hits = 0.

```bash
python3 site/scripts/bake_p7_scenario.py
python3 tests/p7_scenario_assert.py
```

## Collision bans kept

- Hair-dryer curly / fine / travel / thick / frizzy siblings
- Dehumidifier basement / bathroom / crawl-space siblings
- Kitchen-rug main shortlist
- Noise-cancelling work sibling
- Docking-station main + MacBook siblings
- Office-chair back-pain / long-hours / gaming / under-$200 / tall siblings
- Soft parent densify: hub ASINs may appear on a scene; sibling scene ASINs stay banned

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was. Honest shortfall card counts are not padded.

## Brand notes

- Men’s hair dryers: Dreame + Laifen + slopehill + Wavytalk. Laifen titles may ride Wavytalk PB `brand_id`.
- RV dehumidifiers: Medcursor / CLEVAST absorbers plus Waykar powered units. Closet absorbers kept as honest RV densify.
- Washable kitchen rugs: Cosy Homeer / BEQHAUSE / JSEI.
- Flying headphones: OneOdio / Baseus / Soundcore-via-Nebula / EarFun / Edifier. Kids NC banned.
- Dual-monitor docks: WAVLINK / Baseus / Anker. Handheld-console docks banned.
- Heavy office chairs: Dowinx / SEDETA / amseatec / HOMRELEXA big-and-tall.
- Motorcycle dash cams: Vantrue F1 motorcycle kit on top; other dual-channel cams kept as densify.

## Soft parent densify

Prefer, do not block. Sibling scene ASINs stay banned. Parent landings only gained a related-cluster link. Parent hub cards were not rewritten.

## Comparison / reviews stubs

Parent `/comparison/` and `/reviews/` already exist (day-add / prior scenario SoT). This bake does not recreate them and does not roll As of / Checked stamps earlier than 2026-10-24.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Do not merge. Do not Cloudflare Live / wrangler deploy. #54 home nav, #55 stamp, and P6a–d published flags were not touched.
