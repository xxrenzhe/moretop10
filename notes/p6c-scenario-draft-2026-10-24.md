# P6c scenario batch draft — 2026-10-24

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the six new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Parent hubs:** already exist — not recreated.  
**Tip:** `007d73ffe4e27a012c952f92499c9073e6fcda56` (#60 Live).

## Lock

User `lock-p6c-rec`: six type-07 children from the L1 fill pack (density≥4 only). Products JSON is the ASIN source of truth.

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/projectors/best-projectors-for-gaming/` | Live `/projectors/` | **6** | `filled` (PB fromsll) |
| 2 | `/humidifiers/best-humidifiers-for-plants/` | Live `/humidifiers/` | **10** | `filled` (PB fromsll) |
| 3 | `/doormats/best-doormats-for-outdoors/` | Live `/doormats/` | **10** | `filled` (PB fromsll) |
| 4 | `/noise-cancelling-headphones/best-noise-cancelling-headphones-for-work/` | Live `/noise-cancelling-headphones/` | **10** | `filled` (PB fromsll) |
| 5 | `/bluetooth-speakers/best-bluetooth-speakers-for-shower/` | Live `/bluetooth-speakers/` | **10** | `filled` (PB fromsll) |
| 6 | `/office-chairs/best-office-chairs-under-200/` | Live `/office-chairs/` | **10** | `filled` (PB fromsll) |

**Skipped:** `/litter-boxes/best-litter-boxes-for-large-cats/` — SHORTFALL n=1 < density 4. Not scaffolded.  
**OUT (not opened):** tinnitus · mattress hang · robot-mop · TV blocked · Lab.  
**#58 / #60:** P6a and P6b scenes stay `published=false`. Not flipped. Day-add shells stay unpublished.

**Total:** 56 distinct ASINs (6 / 10 / 10 / 10 / 10 / 10). Parent landings only gained a related-cluster link.

## L1 fill

Applied pack `site/data/p6c-l1-fill-pack-2026-10-24.json` (report: `site/data/p6c-l1-fill-report-2026-10-24.md`). Scene cards come from `site/data/products-best-*.json` (uploaded SoT). YP site 11767 probed — 0 usable (honest PB-only). Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/p6c-occupied-asins-2026-10-24.json` (1012 ASINs). Pack sibling hits = 0.

```bash
python3 site/scripts/bake_p6c_scenario.py
python3 tests/p6c_scenario_assert.py
```

## Collision bans kept

- Projector bedroom / outdoor / home-theater siblings
- Humidifier baby / bedroom / large-room siblings
- Doormat sibling set (hub ASINs soft-densify only)
- NC travel siblings
- Outdoor Bluetooth siblings
- Office-chair back-pain / long-hours / gaming siblings
- Global occupied flat (1012)
- Soft parent densify: hub ASINs may appear on a scene; sibling scene ASINs stay banned

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was. Honest shortfall card counts are not padded.

## Brand notes

- Gaming projectors: Aurzen + HAPPRUN (N=6, density≥4).
- Outdoor doormats: JSEI brand_gate risk reported; multi-brand with BEQHAUSE, density 10, not a hard fail.
- Office chairs under $200: honest now price ≤$200 on every card.

## Soft parent densify

Prefer, do not block. Sibling scene ASINs stay banned. Parent landings only gained a related-cluster link. Parent hub cards were not rewritten.

## Comparison / reviews stubs

Parent `/comparison/` and `/reviews/` already exist (day-add / prior scenario SoT). This bake does not recreate them and does not roll As of / Checked stamps earlier than 2026-10-24.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Do not merge. Do not Cloudflare Live / wrangler deploy. #54 home nav, #55 stamp, #58 P6a, and #60 P6b published flags were not touched.
