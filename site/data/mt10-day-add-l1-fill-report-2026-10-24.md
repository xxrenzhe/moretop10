# MT10 day-add L1 fill report · 2026-10-24（Asia/Shanghai）
**生成**：2026-10-24T09:30:12.423440+08:00 · **occupied tip**：`d96fed71+#56+daily-e1841465` · **lock**：`day-add-12-ready`  
**waiting_for_部署上线**：yes · **未合 / 未 bake / 未 Live** · L1 PB∪YP  
**Apply pack**：`/workspace/shared/mt10-day-add-fill-pack-2026-10-24.json` + dir `/workspace/shared/mt10-day-add-fill-pack-2026-10-24/`  
This executor did **not** open a PR / merge / deploy. No Lab complementarity.

## Counts

| # | Niche slug | Path | N | Density≥4 | Track mix | Brand gate |
|---|------------|------|---|-----------|-----------|------------|
| 1 | `pool-heat-pumps` | `/pool-heat-pumps/` | **10** | YES | PB10 | OK·della,varpoolfaye,warmblu |
| 2 | `kitchen-rugs` | `/kitchen-rugs/` | **10** | YES | PB10 | OK·beqhause,garvee_sc,jsei |
| 3 | `light-therapy` | `/light-therapy/` | **8** | YES | PB8 | OK·megelin,swirise |
| 4 | `bike-racks` | `/bike-racks/` | **10** | YES | PB10 | OK·della,montek - us,young electric |
| 5 | `nightstands` | `/nightstands/` | **9** | YES | PB9 | OK·della,garvee_sc,lvifur |
| 6 | `3d-printing-filament` | `/3d-printing-filament/` | **0** | NO · brand_gate | — | FAIL·r qidi technology-only |
| 7 | `floor-lamps` | `/floor-lamps/` | **0** | NO · brand_gate | — | FAIL·honeywell smart lighting-only |
| 8 | `robotic-pool-cleaners` | `/robotic-pool-cleaners/` | **8** | YES | PB8 | OK·beatbot amazon,wybot |
| 9 | `barstools` | `/barstools/` | **10** | YES | PB10 | OK·della,fervorfurn |
| 10 | `docking-stations` | `/docking-stations/` | **8** | YES | PB8 | OK·v av access-us,wavlink |
| 11 | `chef-s-knives` | `/chef-s-knives/` | **0** | NO · brand_gate | — | FAIL·paudin-only |
| 12 | `bookcases` | `/bookcases/` | **10** | YES | PB10 | OK·della,garvee_sc,lvifur |

**Total admitted**：83 · **niches density≥4**：9/12 · **collision ban size**：772 · **fake ASIN rejects**：0

## Collisions avoided

- Global occupied flat: 772 (`mt10-day-add-occupied-2026-10-24.json`)
- Reject counts: {'no_match': 22024, 'price': 41, 'collision': 1742, 'accessory': 24, 'brand_gate': 30}
- Brand gate fails: ['3d-printing-filament', 'floor-lamps', 'chef-s-knives']
- Shortfalls (honest <10, gate OK): ['light-therapy', 'nightstands', 'robotic-pool-cleaners', 'docking-stations']

## Brand / YP / shortfall notes

- Probed YP site 11767 (YP_TOKEN_MT10LAB) first pass: 12 kw → 0 rows; re-run SKIP_YP after filter tighten. Live CTA remains PB ?uid=fromsll — do not rebind to YP. YP track_link discovery-only. Filters: pool must_also heat pump (drop resistive/HVAC mini-split); filament must contain "filament" (drop abs/leggings false positives).
- `3d-printing-filament` brand gate: **FAIL** — single-brand after honest PB∪YP — reject shortlist; do not pad fake brands (brands=['r qidi technology']) (would_have_picked=10). Do **not** scaffold until multi-brand.
- `floor-lamps` brand gate: **FAIL** — single-brand after honest PB∪YP — reject shortlist; do not pad fake brands (brands=['honeywell smart lighting']) (would_have_picked=10). Do **not** scaffold until multi-brand.
- `chef-s-knives` brand gate: **FAIL** — single-brand after honest PB∪YP — reject shortlist; do not pad fake brands (brands=['paudin']) (would_have_picked=10). Do **not** scaffold until multi-brand.
- `light-therapy`: **SHORTFALL 8/10** — listed honest admits only; do not invent ASINs to pad.
- `nightstands`: **SHORTFALL 9/10** — listed honest admits only; do not invent ASINs to pad.
- `robotic-pool-cleaners`: **SHORTFALL 8/10** — listed honest admits only; do not invent ASINs to pad.
- `docking-stations`: **SHORTFALL 8/10** — listed honest admits only; do not invent ASINs to pad.

## Per-slug picks

### `pool-heat-pumps` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FDK69645` | $1399.99 | PB | Varpoolfaye | 40000 BTU Pool Heater Above Ground 12000 Gallon Swimming Poo |
| Upgrade | `B0G4BRGJJ8` | $3399.99 | PB | WARMBLU | 33,000 Gallons Inverter Pool Heat Pump for Inground Pools 22 |
| Best value | `B0HK7LGG4Q` | $649.96 | PB | DELLA | Della Omi Spark 21,000 BTU Inverter Pool Heat Pump up to 7,0 |
| Premium | `B0HC29WFFN` | $1151.98 | PB | Varpoolfaye | 2XSwimming Pool Heat Pumps 16000 BTU Above Ground Pool Heate |
| Alternative | `B0G4BQTMJJ` | $2080.03 | PB | WARMBLU | 28,000 Gallons Inverter Pool Heat Pump for Inground Pools 22 |
| Also consider | `B0HJYSG5TF` | $649.96 | PB | DELLA | Della Omi Spark 21,000 BTU Inverter Pool Heat Pump up to 7,0 |
| Editor pick | `B0DX26RFPR` | $1099.99 | PB | Varpoolfaye | 30000 BTU Above Ground Pool Heater Swimming Pool Heat Pump E |
| Budget | `B0G48LGBZM` | $1999.99 | PB | WARMBLU | 21,000 Gallons Inverter Pool Heat Pump for Inground Pools 22 |
| Runner-up | `B0FQMSHRMC` | $3899.99 | PB | Varpoolfaye | 140000BTU Swimming Pool Heat Pumps Up to 42000 Gallons 220v |
| Worth a look | `B0G48YMM9R` | $1889.10 | PB | WARMBLU | 23,000 Gallons Inverter Pool Heat Pump for Inground Pools 22 |

### `kitchen-rugs` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GYQTJ7KQ` | $27.99 | PB | JSEI | JSEI Kitchen Rugs 24"x36", Non-Slip Kitchen Mats for Floor,  |
| Upgrade | `B0FY17MZ3R` | $27.35 | PB | BEQHAUSE | BEQHAUSE Kitchen Rugs Non-Slip Washable Kitchen Mats, 32"x48 |
| Best value | `B0HNW942BJ` | $38.80 | PB | Garvee_SC | Garvee Snowman Christmas Runner Rug 2x8 Washable Rug Kitchen |
| Premium | `B0GYQLGR7G` | $27.99 | PB | JSEI | JSEI Kitchen Rugs 24"x36", Non-Slip Kitchen Mats for Floor,  |
| Alternative | `B0FY19LY15` | $19.99 | PB | BEQHAUSE | BEQHAUSE Kitchen Rugs Non-Slip Washable Kitchen Mats, 32"x48 |
| Also consider | `B0HNVR8PR8` | $46.41 | PB | Garvee_SC | Garvee Christmas Scalloped Kitchen Runner Rug 2x6 Bathroom R |
| Editor pick | `B0FYBVPN1K` | $14.99 | PB | JSEI | JSEI Kitchen Rugs 17"x30", Non-Slip Kitchen Mats for Floor,  |
| Budget | `B0FY1DWKP3` | $19.99 | PB | BEQHAUSE | BEQHAUSE Kitchen Rugs Non-Slip Washable Kitchen Mats, 32"x48 |
| Runner-up | `B0HNW3R91L` | $46.05 | PB | Garvee_SC | Garvee Christmas Scalloped Kitchen Runner Rug 2x6 Bathroom R |
| Worth a look | `B0FYC54CF4` | $14.99 | PB | JSEI | JSEI Kitchen Rugs 17"x30", Non-Slip Kitchen Mats for Floor,  |

### `light-therapy` (8)

_Density shortfall 8/10 — listed honest admits only; do not invent ASINs to pad._

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GF84HMBY` | $799.00 | PB | SWIRISE | Red and Near-Infrared Light Therapy Mat Pro |
| Upgrade | `B0HHFC3HH5` | $368.00 | PB | MEGELIN | Megelin Red and Near Infrared Light Therapy Vest (SD001) |
| Best value | `B0F6C7XQHJ` | $728.00 | PB | SWIRISE | Red Light Therapy Mat for Whole Body - 1280 LEDs with 660nm  |
| Premium | `B0H8F4D92Z` | $939.00 | PB | MEGELIN | Megelin Red Light Therapy Mat (JML3) |
| Alternative | `B0DG6KP942` | $232.00 | PB | SWIRISE | Infrared Light Therapy Panel with Stand, 660nm Red Light and |
| Also consider | `B0CPXZ33M8` | $362.70 | PB | MEGELIN | MEGELIN Led Red Light Therapy Face & Neck Mask |
| Editor pick | `B0F66WMM61` | $899.00 | PB | SWIRISE | Red Light Therapy with 660nm&850nm High Power Panel(Elite 15 |
| Budget | `B0G1YGQQJT` | $74.00 | PB | MEGELIN | MEGELIN Led Red Light Therapy Face & Neck Mask, 7 Colors Led |

### `bike-racks` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0HF52DJCY` | $229.99 | PB | Young Electric | Bike Rack for Car Hitch Mount - Young Electric Single E-Bike |
| Upgrade | `B0GX673PXJ` | $269.99 | PB | monTEK - US | monTEK Rolling 4-Bike Rack Garage, Up to 4.5" Tire Width |
| Best value | `B0HK8C3D98` | $169.96 | PB | DELLA | 2-Bike Hitch Mount Bike Rack, Foldable Platform Carrier w/Sm |
| Premium | `B0FRS89LL3` | $229.99 | PB | Young Electric | Bike Rack for Car Hitch Mount - Young Electric Single E-Bike |
| Alternative | `B0HN3RCQBB` | $249.99 | PB | monTEK - US | monTEK Swivel Automatic Lift Bike Rack Up to 71LBS |
| Also consider | `B0HMC8BZJ5` | $139.96 | PB | DELLA | 2-Bike Hitch Mount Bike Rack, Foldable Platform Carrier w/Sm |
| Editor pick | `B0HHRDW1D1` | $229.99 | PB | Young Electric | Bike Rack for Car Hitch Mount - Young Electric Single E-Bike |
| Budget | `B0HC3J2S1Q` | $249.99 | PB | monTEK - US | monTEK Swivel Automatic Lift Bike Rack Up to 71LBS |
| Runner-up | `B0FMR57Q8N` | $525.89 | PB | Young Electric | Young Electric Bike Rack Hitch Mount - Heavy Duty Bike Racks |
| Worth a look | `B0H83DH228` | $249.99 | PB | monTEK - US | monTEK Rolling 3-Bike Rack Garage, Up to 4.5" Tire Width |

### `nightstands` (9)

_Density shortfall 9/10 — listed honest admits only; do not invent ASINs to pad._

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FYFWBRW6` | $139.99 | PB | Lvifur | Lvifur Fluted Night Stand Set of 2 - with Bluetooth Speaker, |
| Upgrade | `B0C6LSM7MS` | $339.99 | PB | DELLA | BELLEZE LED Nightstands Set of 2, Bedside Table with 3 Drawe |
| Best value | `B0HNVJPTJL` | $108.03 | PB | Garvee_SC | Garvee Metal Locker Nightstand with Shelf, Lockable Metal En |
| Premium | `B0FYFVWY29` | $139.99 | PB | Lvifur | Lvifur Fluted Night Stand Set of 2 - with Bluetooth Speaker, |
| Alternative | `B0C4F5X6LT` | $329.99 | PB | DELLA | BELLEZE Nightstands Set of 2, LED Night Stand with Drawers B |
| Also consider | `B0D8DVSQBN` | $159.99 | PB | Lvifur | Lvifur Nightstand with Wireless Charging Station and LED Lig |
| Editor pick | `B0C6LS2ZKF` | $279.99 | PB | DELLA | BELLEZE Nightstand with 3 Drawers, Bedside Table with LED Li |
| Budget | `B0D8DT1NQS` | $159.99 | PB | Lvifur | Lvifur Nightstand with Wireless Charging Station and LED Lig |
| Runner-up | `B0C6LQ9GBC` | $269.99 | PB | DELLA | BELLEZE Nightstand with 2 Drawers, Drawers Night Stand Bedsi |

### `3d-printing-filament` (0)

_Brand gate FAIL — single-brand after honest PB∪YP — reject shortlist; do not pad fake brands (brands=['r qidi technology'])_

### `floor-lamps` (0)

_Brand gate FAIL — single-brand after honest PB∪YP — reject shortlist; do not pad fake brands (brands=['honeywell smart lighting'])_

### `robotic-pool-cleaners` (8)

_Density shortfall 8/10 — listed honest admits only; do not invent ASINs to pad._

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0HD764RKJ` | $2299.00 | PB | Beatbot Amazon | (2026 Upgrade) Beatbot AquaSense 2 Ultra Robotic Pool Cleane |
| Upgrade | `B0GYWX2HWK` | $626.41 | PB | WYBOT | Cordless Pool Vacuum for Inground Pools, Pool Cleaner Robot |
| Best value | `B0D38X6SLW` | $1499.00 | PB | Beatbot Amazon | Beatbot AquaSense Pro Pool Robot, Cordless Pool Vacuum for I |
| Premium | `B0GYWHXXYG` | $399.99 | PB | WYBOT | WYBOT Cordless Robotic Pool Vacuum for Inground Pools |
| Alternative | `B0HBB2ZJPQ` | $1298.00 | PB | Beatbot Amazon | (2026 Upgrade) Beatbot AquaSense 2 Cordless Pool Vacuum Robo |
| Also consider | `B0GYWJMNWK` | $399.99 | PB | WYBOT | WYBOT C1 Cordless Robotic Pool Vacuum for Inground Pools, Pr |
| Editor pick | `B0DMN6NV6H` | $1143.50 | PB | Beatbot Amazon | (2025) Beatbot Cordless Robotic Pool Cleaner for Complex Poo |
| Budget | `B0GYWSJMPH` | $334.99 | PB | WYBOT | WYBOT Cordless Robotic Pool Vacuum for Inground Pools |

### `barstools` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0H6P4T4MQ` | $219.99 | PB | FervorFurn | 26 Inch Swivel Bar Stools Set of 2, Counter Height Bar Chair |
| Upgrade | `B073R117SK` | $89.99 | PB | DELLA | BELLEZE Retro Faux Leather Barstools, Modern Counter Stool f |
| Best value | `B0H6P53T8W` | $219.99 | PB | FervorFurn | 26 Inch Swivel Bar Stools Set of 2, Counter Height Bar Chair |
| Premium | `B0BB29VGBP` | $89.99 | PB | DELLA | BELLEZE Retro Faux Leather Barstools, Modern Counter Stool f |
| Alternative | `B0H6NWMY4T` | $219.99 | PB | FervorFurn | 26 Inch Swivel Bar Stools Set of 2, Counter Height Bar Chair |
| Also consider | `B0H6NYCF7L` | $219.99 | PB | FervorFurn | 26 Inch Swivel Bar Stools Set of 2, Counter Height Bar Chair |
| Editor pick | `B0HB4W7LDJ` | $189.99 | PB | FervorFurn | Swivel Bar Stools Set of 2, Mid-Century Modern Counter Bar C |
| Budget | `B0GLDY7QTB` | $189.99 | PB | FervorFurn | Swivel Bar Stools Set of 2, Mid-Century Modern Counter Bar C |
| Runner-up | `B0GLFFPP4R` | $179.99 | PB | FervorFurn | Swivel Bar Stools Set of 2, Mid-Century Modern Counter Bar C |
| Worth a look | `B0H6P1JD93` | $399.99 | PB | FervorFurn | 26 Inch Swivel Bar Stools Set of 4, Counter Height Bar Chair |

### `docking-stations` (8)

_Density shortfall 8/10 — listed honest admits only; do not invent ASINs to pad._

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FWC9NS9V` | $299.99 | PB | v AV Access-US | AV Access 8K KVM Switch 3 Monitors 2 Computers, KVM Docking  |
| Upgrade | `B0GWL5R69W` | $119.99 | PB | WAVLINK | WAVLINK Laptop Docking Station 3 Monitors, 11-in-1 USB C Doc |
| Best value | `B0H6J7JSSM` | $269.99 | PB | v AV Access-US | AV Access iDock X20 Dual USB C KVM Docking Station 2 Laptops |
| Premium | `B0GWL479JX` | $119.99 | PB | WAVLINK | WAVLINK Laptop Docking Station 3 Monitors, 11-in-1 USB C Doc |
| Alternative | `B0F6MTC9LR` | $251.99 | PB | v AV Access-US | AV Access KVM Switch 2 Monitors 2 Computers, 8K KVM Docking  |
| Also consider | `B0C58H1CDL` | $299.99 | PB | WAVLINK | WAVLINK DisplayLink Laptop Docking Station Quad Monitor 4K@6 |
| Editor pick | `B0H6HVFLHQ` | $235.99 | PB | v AV Access-US | AV Access Dual Monitor KVM Docking Station for 2 Computers,  |
| Budget | `B09FT8BXZR` | $257.20 | PB | WAVLINK | WAVLINK DisplayLink Laptop Docking Station Quad Monitor 4K@6 |

### `chef-s-knives` (0)

_Brand gate FAIL — single-brand after honest PB∪YP — reject shortlist; do not pad fake brands (brands=['paudin'])_

### `bookcases` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GV3NYVKX` | $219.99 | PB | Lvifur | Lvifur 71''H Office Storage Cabinet - with Glass Doors and A |
| Upgrade | `B0HMRVYTT3` | $259.99 | PB | Garvee_SC | Garvee 71.5" Tall Triple Wide Bookshelf with 2 Drawers & 2 C |
| Best value | `B0FYQ5PGBM` | $617.49 | PB | DELLA | BELLEZE Display Storage Cabinet with Hutch Set of 2, 72" Tal |
| Premium | `B0GTDYW8DP` | $219.99 | PB | Lvifur | Lvifur 71''H Office Storage Cabinet - with Glass Doors and A |
| Alternative | `B0HMRVTJXP` | $259.99 | PB | Garvee_SC | Garvee 71.5" Tall Triple Wide Bookshelf with 2 Drawers & 2 C |
| Also consider | `B0FYQ5PGBL` | $329.99 | PB | DELLA | BELLEZE Display Storage Cabinet with Hutch, 72" Tall Wood Mo |
| Editor pick | `B0GT4YT3GG` | $208.99 | PB | Lvifur | Lvifur 71" Tall LED Bookshelf with Glass Doors and Adjustabl |
| Budget | `B0HMRTY85T` | $259.99 | PB | Garvee_SC | Garvee 71.5" Tall Triple Wide Bookshelf with 2 Drawers & 2 C |
| Runner-up | `B0GK1B4NN4` | $329.99 | PB | DELLA | BELLEZE Tall Arched Storage Cabinet with Hutch and Drawers,  |
| Worth a look | `B0GTLLT4NQ` | $199.99 | PB | Lvifur | Lvifur 71" Tall Bookcase with Glass Doors and Adjustable She |

## Method

- Source niches: `/workspace/shared/day-add-from-inventory-2026-10-24.md` § MT10
- ① Day-add pool ASINs → PB `asins=` healthy track
- ② PB `brand_id` dig for brands seen in pool
- ③ YP keyword on site 11767 — discovery only
- Multi-brand required (≥2) for all 12 hubs; single-brand → reject shortlist (same stance as P5b mattress)
- Live CTA PB `?uid=fromsll`
- Independent from Lab shortlists / no Lab complementarity
- No invented prices / was / % / gallery / specs

## Next

- Parent may launch CloudAgent apply draft PR (`published=false`) for niches that passed density (≥4): **pool-heat-pumps, kitchen-rugs, light-therapy, bike-racks, nightstands, robotic-pool-cleaners, barstools, docking-stations, bookcases**.
- **Do not** scaffold brand_gate fails until multi-brand: 3d-printing-filament, floor-lamps, chef-s-knives.
- User must say「部署上线」before merge/Live.

## Stamp

`moretop10 | day-add L1 fill | draft-pack | 9/12 density | /workspace/shared/mt10-day-add-fill-report-2026-10-24.md | next=CloudAgent draft | blockers=gate_fail 3 shortfall 4`
