# P5b scenario batch draft — 2026-10-24

**waiting_for_部署上线:** yes  
**published:** false / `noindex,follow` on the three new type-07 pages  
**Scope:** MoreTop10 draft only. No Lab / RR / OL. Do not merge. Do not Cloudflare Live deploy.  
**Parent hubs:** already exist — not recreated.

## Lock

User `lock-p5b-rec`: three type-07 children from the L1 fill pack. Mattress skipped.

| # | Path | Parent hub | Density | Fill |
|---|------|------------|---------|------|
| 1 | `/office-chairs/best-office-chairs-for-long-hours/` | Live `/office-chairs/` | **10** | `filled` (PB fromsll) |
| 2 | `/pillows/best-pillows-for-stomach-sleepers/` | Live `/pillows/` | **10** | `filled` (PB fromsll) |
| 3 | `/tower-fans/best-tower-fans-for-bedroom/` | Live `/tower-fans/` | **2** | `filled` honest stub (PB fromsll) |

**Skipped:** `/mattresses/best-mattresses-for-back-pain/` — brand_gate FAIL · Sweetnight-only.  
**OUT (not created):** back-sleepers pillow · heavy-people mattress.

**Total:** 22 distinct ASINs (10 / 10 / 2). Parent landings only gained a related-cluster link.

## L1 fill

Applied pack `site/data/p5b-l1-fill-pack-2026-10-24.json` (report: `site/data/p5b-l1-fill-report-2026-10-24.md`). YP site 11767 timed out; unused. Pack is PB-only. Live CTA stays PB `?uid=fromsll`.

Occupied collision set: `site/data/p5b-occupied-asins-2026-10-24.json` (326 ASINs). Pack hits = 0.

```bash
python3 site/scripts/bake_p5b_scenario.py
python3 tests/p5b_scenario_assert.py
```

## Collision bans kept

- Office back-pain scene + hub
- Pillow neck-pain + side-sleepers
- Tower-fans hub (10/10 already occupied)
- Global occupied flat (326)

No accessories as primary picks. No invented was / %. Reviews skipped (Top + Upgrade articles do not exist for these scenes). `list_price` from the pack is not rendered as a strike/was. Tower bedroom is not padded past the 2 honest admits.

## Soft parent densify

Prefer, do not block. L1 pack has no extra hub SKUs, so mattresses / pillows / office hub cards were not rewritten. Parent landings only gained a related-cluster link.

## Bake ≠ deploy

Pages stay `published=false` / noindex until a later 部署上线 order. Do not merge. Do not Cloudflare Live / wrangler deploy. #54 home nav and #55 stamp were not touched.
