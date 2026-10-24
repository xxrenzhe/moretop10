# P6b scenario batch draft — 2026-10-24

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the five new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Parent hubs:** already exist — not recreated.  
**Tip:** `68a6d60e` (#58+#59+IL Live).

## Lock

User `lock-p6b-rec`: five type-07 children from the L1 fill pack (density≥4 only).

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/computer-speakers/best-computer-speakers-for-gaming/` | Live `/computer-speakers/` | **10** | `filled` (PB fromsll) |
| 2 | `/litter-boxes/best-litter-boxes-for-multiple-cats/` | Live `/litter-boxes/` | **4** | `filled` (PB fromsll) |
| 3 | `/light-therapy/best-light-therapy-for-face/` | Live `/light-therapy/` | **7** | `filled` (PB fromsll) |
| 4 | `/office-chairs/best-office-chairs-for-gaming/` | Live `/office-chairs/` | **10** | `filled` (PB fromsll) |
| 5 | `/dehumidifiers/best-dehumidifiers-for-crawl-space/` | Live `/dehumidifiers/` | **10** | `filled` (PB fromsll) |

**Skipped:** `/pillows/best-pillows-for-snoring/` — SHORTFALL n=0 < density 4.  
**Skipped:** `/ceramic-space-heaters/best-ceramic-space-heaters-for-bedroom/` — SHORTFALL n=3 < density 4.  
**OUT (not opened):** tinnitus · mattress hang · red-light masks · robot-mop.  
**#58:** P6a scenes stay `published=false`. Not flipped.

**Total:** 41 distinct ASINs (10 / 4 / 7 / 10 / 10). Parent landings only gained a related-cluster link.

## L1 fill

Applied pack `site/data/p6b-l1-fill-pack-2026-10-24.json` (report: `site/data/p6b-l1-fill-report-2026-10-24.md`). YP site 11767 probed — 0 usable (honest PB-only). Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/p6b-occupied-asins-2026-10-24.json` (918 ASINs). Pack sibling hits = 0.

```bash
python3 site/scripts/bake_p6b_scenario.py
python3 tests/p6b_scenario_assert.py
```

## Collision bans kept

- Computer-speakers desktop sibling
- Litter automatic + odor siblings
- Office-chair back-pain + long-hours siblings
- Dehumidifier basement + bathroom siblings
- Global occupied flat (918)
- Soft parent densify: hub ASINs may appear on a scene; this pack reused `B0DG6KP942` on light-therapy-for-face

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was. Honest shortfall card counts are not padded.

## Soft parent densify

Prefer, do not block. Sibling scene ASINs stay banned. Parent landings only gained a related-cluster link. Parent hub cards were not rewritten.

## Comparison / reviews stubs

Parent `/comparison/` and `/reviews/` already exist (day-add / prior scenario SoT). This bake does not recreate them and does not roll As of / Checked stamps earlier than 2026-10-24.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Do not merge. Do not Cloudflare Live / wrangler deploy. #54 home nav, #55 stamp, and #58 P6a published flags were not touched.
