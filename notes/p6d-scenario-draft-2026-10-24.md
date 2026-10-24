# P6d scenario batch draft — 2026-10-24

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the seven new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Parent hubs:** already exist — not recreated.  
**Tip:** `b594ea30af37d7471540e048fd1d64caa7ffe9c1` (#62 Live).

## Lock

User `lock-p6d-rec` (#1–#7): seven type-07 children from the L1 fill pack (density≥4 only). Products JSON is the ASIN source of truth.

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/hair-dryers/best-hair-dryers-for-frizzy-hair/` | Live `/hair-dryers/` | **10** | `filled` (PB fromsll) |
| 2 | `/office-chairs/best-office-chairs-for-tall-people/` | Live `/office-chairs/` | **10** | `filled` (PB fromsll) |
| 3 | `/barstools/best-barstools-for-kitchen-island/` | Live `/barstools/` | **10** | `filled` (PB fromsll) |
| 4 | `/bike-racks/best-bike-racks-for-suv/` | Live `/bike-racks/` | **10** | `filled` (PB fromsll) |
| 5 | `/bookcases/best-bookcases-for-small-spaces/` | Live `/bookcases/` | **10** | `filled` (PB fromsll) |
| 6 | `/docking-stations/best-docking-stations-for-macbook/` | Live `/docking-stations/` | **10** | `filled` (PB fromsll) |
| 7 | `/massage-guns/best-massage-guns-for-athletes/` | Live `/massage-guns/` | **10** | `filled` (PB fromsll) |

**Skipped:** none. All seven lock scenes passed density ≥4.  
**OUT (not opened):** tinnitus · seniors · mattress hang · robot-mop · TV · litter kittens · Lab.  
**#58 / #60 / #61:** P6a, P6b, and P6c scenes stay `published=false`. Not flipped. Day-add shells stay unpublished.

**Total:** 70 distinct ASINs (10 × 7). Parent landings only gained a related-cluster link.

## L1 fill

Applied pack `site/data/p6d-l1-fill-pack-2026-10-24.json` (report: `site/data/p6d-l1-fill-report-2026-10-24.md`). Scene cards come from `site/data/products-best-*.json` (uploaded SoT). YP site 11767 probed — 0 usable (honest PB-only). Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/p6d-occupied-asins-2026-10-24.json` (P6c flat + #61 admitted + sibling/hub bans). Pack sibling hits = 0.

```bash
python3 site/scripts/bake_p6d_scenario.py
python3 tests/p6d_scenario_assert.py
```

## Collision bans kept

- Hair-dryer curly / fine / travel / thick siblings (plus hub in the 50-ASIN fill ban)
- Office-chair back-pain / long-hours / gaming / under-$200 siblings
- Barstool main shortlist
- Bike-rack hitch + main shortlist
- Bookcase main shortlist
- Docking-station main shortlist
- Massage-gun hub (no sibling scene)
- Soft parent densify: hub ASINs may appear on a scene; sibling scene ASINs stay banned

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was. Honest shortfall card counts are not padded.

## Brand notes

- Frizzy hair dryers: Laifen titles may ride Wavytalk PB `brand_id`; display from title. Slopehill + Wavytalk + Laifen-US-AMZ.
- Tall office chairs: tall / big-and-tall soft densify. Sibling gaming / back / long / under-$200 stay banned.
- MacBook docks: WAVLINK Mac M1–M5 + Anker TB5/USB-C + Baseus USB-C. Windows-lean titles kept only when they are real multi-port docks.
- Massage guns: Bob-and-Brad lean **3/10** — honest, not a hard-fail. Five brands total (arboleaf, Bob and Brad, HEYCHY, RENPHO, SKG).
- Small-space bookcases: 2× Lerliuo kids sling bookshelves kept as soft small-space densify.

## Soft parent densify

Prefer, do not block. Sibling scene ASINs stay banned. Parent landings only gained a related-cluster link. Parent hub cards were not rewritten.

## Comparison / reviews stubs

Parent `/comparison/` and `/reviews/` already exist (day-add / prior scenario SoT). This bake does not recreate them and does not roll As of / Checked stamps earlier than 2026-10-24.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Do not merge. Do not Cloudflare Live / wrangler deploy. #54 home nav, #55 stamp, #58 P6a, #60 P6b, and #61 P6c published flags were not touched.
