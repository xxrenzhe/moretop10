# MT10 P6d L1 fill report · 2026-10-24（Asia/Shanghai）
**生成**：2026-10-24T14:32:59.536503+08:00 · **occupied tip**：`c7fc1914` · **lock**：`lock-p6d-rec`  
**waiting_for_部署上线**：yes · **未合 / 未 bake / 未 Live** · L1 PB∪YP discovery  
**Apply pack**：`/workspace/shared/mt10-p6d-fill-pack-2026-10-24.json` + dir `/workspace/shared/mt10-p6d-fill-pack-2026-10-24/`  
This executor did **not** open a PR / merge / deploy.

## Counts

| # | Scene slug | Path | N | Status | Brands | Notes |
|---|------------|------|---|--------|--------|-------|
| 1 | `best-hair-dryers-for-frizzy-hair` | `/hair-dryers/best-hair-dryers-for-frizzy-hair/` | **10** | OK | laifen-us-amz,slopehill (beauty),wavytalk | OK density≥4 |
| 2 | `best-office-chairs-for-tall-people` | `/office-chairs/best-office-chairs-for-tall-people/` | **10** | OK | amseatec,dowinx,felixking,heroset,homrelexa | OK density≥4 |
| 3 | `best-barstools-for-kitchen-island` | `/barstools/best-barstools-for-kitchen-island/` | **10** | OK | hoobro,songmics home | OK density≥4 |
| 4 | `best-bike-racks-for-suv` | `/bike-racks/best-bike-racks-for-suv/` | **10** | OK | montek - us,young electric | OK density≥4 |
| 5 | `best-bookcases-for-small-spaces` | `/bookcases/best-bookcases-for-small-spaces/` | **10** | OK | bhg,hoobro,leyaoyao,songmics home | OK density≥4 |
| 6 | `best-docking-stations-for-macbook` | `/docking-stations/best-docking-stations-for-macbook/` | **10** | OK | anker,baseus us bbs,wavlink so | OK density≥4 |
| 7 | `best-massage-guns-for-athletes` | `/massage-guns/best-massage-guns-for-athletes/` | **10** | OK | arboleaf,bob and brad(loypa),heychy,renpho wellness - us,skgamz | OK density≥4 |

**Total admitted**：70 · **scenes density≥4**：7/7 · **collision ban size**：1098 · **fake ASIN rejects**：0

## Collisions avoided

- Global occupied flat: 1098 (`scenario-p6d-occupied-2026-10-24.json`)
- Scene bans hair=50 chair=38 bar=10 bike=19 book=10 dock=8 massage=10
- Reject counts: {"accessory": 616, "collision": 388, "fake_asin": 0, "unhealthy": 79, "price": 33, "no_match": 25748, "title_ban": 0, "extra_ban": 51, "require": 105, "brand_gate": 0}
- OUT: hearing seniors · mattress hang · robot-mop · TV · litter kittens · published flip

## Brand / YP notes

- Probed YP site 11767 (YP_TOKEN_MT10LAB). 0 usable relevant rows (timeout/empty/non-match) — pack honest PB-only where YP failed. Live CTA remains PB ?uid=fromsll.
- Brand gates: `{"best-hair-dryers-for-frizzy-hair": {"fail": false, "brands": ["laifen-us-amz", "slopehill (beauty)", "wavytalk"]}, "best-office-chairs-for-tall-people": {"fail": false, "brands": ["amseatec", "dowinx", "felixking", "heroset", "homrelexa"]}, "best-barstools-for-kitchen-island": {"fail": false, "brands": ["hoobro", "songmics home"]}, "best-bike-racks-for-suv": {"fail": false, "brands": ["montek - us", "young electric"]}, "best-bookcases-for-small-spaces": {"fail": false, "brands": ["bhg", "hoobro", "leyaoyao", "songmics home"]}, "best-docking-stations-for-macbook": {"fail": false, "brands": ["anker", "baseus us bbs", "wavlink so"]}, "best-massage-guns-for-athletes": {"fail": false, "brands": ["arboleaf", "bob and brad(loypa)", "heychy", "renpho wellness - us", "skgamz"]}}`
- Soft parent densify preferred; did **not** hard-block scenes.

## Per-slug picks

### `best-hair-dryers-for-frizzy-hair` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0HGF14RFX` | $74.99 | PB | wavytalk | Laifen Air Hair Dryer with Diffuser, High-Speed Ionic Blow D |
| Upgrade | `B0H79SCDJ5` | $89.99 | PB | wavytalk | Laifen Air Pro High Speed Ionic Hair Dryer with Diffuser, Se |
| Best value | `B0H7993WVK` | $89.99 | PB | wavytalk | Laifen Air Pro High Speed Ionic Hair Dryer with Diffuser, Mi |
| Premium | `B0CLZSF4MQ` | $39.99 | PB | slopehill (Beauty) | Slopehill Professional Ionic Hair Dryer, Powerful 1800W Fast |
| Alternative | `B086SR1KML` | $39.99 | PB | slopehill (Beauty) | slopehill Professional Ionic Hair Dryer, Powerful 1800W Fast |
| Also consider | `B0C37BT16J` | $32.99 | PB | slopehill (Beauty) | slopehill Professional Ionic Hair Dryer, Powerful 1800W Fast |
| Editor pick | `B0FMYTMKR6` | $112.49 | PB | Laifen-US-AMZ | Laifen SE 2 Diffuser Hair Dryer for Women, 21.5m/s Air Speed |
| Budget | `B0HDZ4B8MT` | $135.99 | PB | wavytalk | Laifen Air Diffuser Hair Dryer, 15 × High-Speed Ionic Hairdr |
| Runner-up | `B0GWHX7275` | $74.99 | PB | wavytalk | Laifen Air Diffuser Hair Dryer, 15 × High-Speed Ionic Hairdr |
| Worth a look | `B0GWHGDG86` | $74.99 | PB | wavytalk | Laifen Air Diffuser Hair Dryer, 15 × High-Speed Ionic Hairdr |

### `best-office-chairs-for-tall-people` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0F4Y4XJKK` | $179.99 | PB | Dowinx | Dowinx Big and Tall Office Chair with Pocket Spring Cushion, |
| Upgrade | `B0GXVYXX1C` | $179.99 | PB | Dowinx | Dowinx Big and Tall Office Chair, Ergonomic Desk Chair with  |
| Best value | `B0GXVWD9J8` | $179.99 | PB | Dowinx | Dowinx Big and Tall Office Chair, Ergonomic Desk Chair with  |
| Premium | `B0DFWPRZ85` | $139.99 | PB | HeroSet | Office Chair, Ergonomic Big and Tall Computer Desk Chairs, E |
| Alternative | `B0FKGZ2N11` | $139.99 | PB | HeroSet | Office Chair, Ergonomic Big and Tall Computer Desk Chairs, E |
| Also consider | `B0GK142GW8` | $199.99 | PB | HOMRELEXA | HOMRELEXA Criss Cross Office Chair with Armrests & Wheels, C |
| Editor pick | `B0BG1NBFFT` | $119.99 | PB | FelixKing | FelixKing Office Chair, Desk Chair with Adjustable Lumbar Su |
| Budget | `B0HJW9HYF4` | $109.99 | PB | FelixKing | FelixKing Ergonomic Office Chair, Headrest Desk Chair Office |
| Runner-up | `B0D78V9S63` | $109.99 | PB | FelixKing | FelixKing Office Chair, Desk Chair with Adjustable Lumbar Su |
| Worth a look | `B0CRTM67Q8` | $134.99 | PB | AMSEATEC | amseatec Big and Tall Office Chair with Footrest, Lumbar Sup |

### `best-barstools-for-kitchen-island` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0CNK4W4QK` | $89.99 | PB | Songmics Home | VASAGLE Bar Stools Set of 2, Counter Height Bar Stools with  |
| Upgrade | `B0BTBV6233` | $50.99 | PB | HOOBRO | HOOBRO Bar Stools, Set of 2 Bar Chairs, Counter Height Stool |
| Best value | `B0D3PS6NVF` | $59.99 | PB | HOOBRO | HOOBRO Bar Stools,25.4" Saddle Stools with PU Upholstery, Co |
| Premium | `B0F4X9DFQX` | $49.99 | PB | HOOBRO | HOOBRO Barstools,25.4" Saddle Stools with PU Upholstery, Cou |
| Alternative | `B0CNK2QKY7` | $98.57 | PB | Songmics Home | VASAGLE Bar Stools Set of 2, Bar Height, with Back, 28.5-Inc |
| Also consider | `B0F3841R33` | $46.01 | PB | HOOBRO | HOOBRO Bar Stools,25.4" Saddle Stools with PU Upholstery, Co |
| Editor pick | `B0CFGTDMJ7` | $53.99 | PB | HOOBRO | HOOBRO Bar Stools, Set of 2 Chairs, 23.6 Inch Saddle Kitchen |
| Budget | `B0BVYR5CTJ` | $53.99 | PB | HOOBRO | HOOBRO Bar Stools, Set of 2 Bar Chairs, 23.6 Inch Saddle Sto |
| Runner-up | `B0GWYZ9YLX` | $72.99 | PB | HOOBRO | HOOBRO 360° Swivel Bar Stools Set of 2, 25.6" Counter Height |
| Worth a look | `B0D2W6Q35J` | $53.99 | PB | HOOBRO | HOOBRO Bar Stools, Set of 2 Bar Chairs, 23.6 Inch Saddle Sto |

### `best-bike-racks-for-suv` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FCFS8B9G` | $349.99 | PB | Young Electric | Young Hitch Bike Rack for 2 E-Bikes, Heavy Duty Platform Car |
| Upgrade | `B0FGCW46C5` | $314.99 | PB | Young Electric | Young Bike Rack Hitch Mount for 2 E-Bikes, Fat Tire, Electri |
| Best value | `B0B4MYP24M` | $229.99 | PB | Young Electric | Young 4-Bike Rack Hitch Mount Platform Style Carrier for Car |
| Premium | `B0G46FC51T` | $199.99 | PB | monTEK - US | monTEK Premier Locking Quick Release 4-Bike Rack for Cars, T |
| Alternative | `B0G46H9391` | $171.46 | PB | monTEK - US | monTEK Premier Locking Quick Release 3-Bike Rack for Cars, T |
| Also consider | `B0HN6PH9WV` | $159.99 | PB | monTEK - US | monTEK Premier Locking Quick Release 2-Bike Rack for Cars, T |
| Editor pick | `B0FHKBKG5N` | $205.99 | PB | Young Electric | Young 4-Bike Rack Hitch Mount Platform Style Carrier for Car |
| Budget | `B0GT94B9VB` | $99.99 | PB | Young Electric | Young 2 Bike Rack Hitch Mount Foldable Platform Style, Bicyc |
| Runner-up | `B0D95YCD5H` | $99.99 | PB | Young Electric | Young 2 Bike Rack Hitch Mount Foldable Platform Style, Bicyc |
| Worth a look | `B0FWBSC9YK` | $314.48 | PB | Young Electric | Young Bike Rack Hitch Mount - Ebike Racks for Car SUV Truck  |

### `best-bookcases-for-small-spaces` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0F6LH5SJ6` | $64.99 | PB | HOOBRO | HOOBRO 5-Tier Corner Shelf Stand, Corner Shelf with LED Ligh |
| Upgrade | `B0F6LH71B5` | $54.99 | PB | HOOBRO | HOOBRO 5-Tier Corner Shelf Stand, Corner Shelf with LED Ligh |
| Best value | `B0FJWHFDVQ` | $39.99 | PB | HOOBRO | HOOBRO Narrow Corner Shelf Stand, 5-Tier Corner Shelf, 63” T |
| Premium | `B0DPGHCC35` | $32.99 | PB | LEYAOYAO | Lerliuo 5 Tier Kids Bookshelf, White Children Sling Book She |
| Alternative | `B0DP9CHLQP` | $32.99 | PB | LEYAOYAO | Lerliuo 5 Tier Kids Bookshelf, White Children Sling Book She |
| Also consider | `B0F9KVD896` | $189.99 | PB | BHG | No Assembly Folding Bookshelf for Living Room,Collapsible Bo |
| Editor pick | `B0F9KV48WX` | $189.99 | PB | BHG | No Assembly Folding Bookshelf for Living Room,Collapsible Bo |
| Budget | `B0DNS1B7VC` | $149.99 | PB | BHG | No Assembly Folding Bookshelf for Living Room, 5 Tier Gold C |
| Runner-up | `B0CN6J4VVM` | $39.99 | PB | Songmics Home | VASAGLE 5-Tier Corner Shelf Stand, Boho Bookshelf with Polyr |
| Worth a look | `B08M8Z2NZS` | $27.99 | PB | Songmics Home | VASAGLE Corner Shelf Wall Mount, 5-Tier Floating Corner Book |

### `best-docking-stations-for-macbook` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B019XOJ874` | $78.86 | PB | WAVLINK SO | WAVLINK USB Laptop Docking Station Dual Monitors, DisplayLin |
| Upgrade | `B0BNNCXR6J` | $159.87 | PB | WAVLINK SO | WAVLINK USB C Docking Station 4K@60Hz 3 Monitor for Mac(M1-M |
| Best value | `B0GZ3VXCCS` | $119.68 | PB | Baseus US BBS | Baseus Spacemate Docking Station, 11-in-1 USB-C Dock for Win |
| Premium | `B0GZVFL899` | $168.98 | PB | Baseus US BBS | Baseus Spacemate Laptop Docking Station, 11-in-1 USB-C Docki |
| Alternative | `B0H1CP7XKK` | $128.78 | PB | Baseus US BBS | Baseus Spacemate Docking Station, 11-in-1 USB-C Dock for Win |
| Also consider | `B088F7SY6S` | $139.99 | PB | Anker | Anker Laptop Docking Station, 13-in-1 USB C Docking Station, |
| Editor pick | `B07JHZX4GH` | $151.99 | PB | WAVLINK SO | WAVLINK USB Docking Station Dual Monitor 4K 60Hz for Mac M1- |
| Budget | `B0DSVVJXK5` | $339.99 | PB | Anker | Anker Prime TB5 Docking Station, 14-in-1 Thunderbolt 5 Dock  |
| Runner-up | `B0874M3KW4` | $39.99 | PB | Anker | Anker Laptop Docking Station Dual Monitor, 8-in-1 USB C Hub  |
| Worth a look | `B0HF84T4YC` | $41.39 | PB | Baseus US BBS | Baseus Docking Station, Quadruple Display 8K@30Hz DisplayPor |

### `best-massage-guns-for-athletes` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0DWSPM68F` | $149.98 | PB | Bob and Brad(Loypa) | BOB AND BRAD D5 Pro Plus Handheld Massage Gun with Heat, FSA |
| Upgrade | `B0FKN7XPQW` | $249.98 | PB | Bob and Brad(Loypa) | BOB AND BRAD D6 Ultra Massage Gun with Infrared Light, Deep  |
| Best value | `B0DFLPJ29F` | $205.98 | PB | Bob and Brad(Loypa) | BOB AND BRAD D6 Pro Plus Massage Gun with Heat, Deep Tissue  |
| Premium | `B0CST2LDS5` | $54.99 | PB | HEYCHY | HEYCHY Mini Massage Gun Deep Tissue with Heat, FSA Eligible  |
| Alternative | `B0CKVG5VR1` | $52.99 | PB | HEYCHY | HEYCHY Super Mini Massage Gun, Percussion Deep Tissues Muscl |
| Also consider | `B0FW4W967X` | $139.99 | PB | HEYCHY | HEYCHY Massage Gun Deep Tissue with Heat Therapy, 12mm Ampli |
| Editor pick | `B0F28LGSQV` | $59.99 | PB | skgamz | SKG Mini Massage Gun Deep Tissue for Women Men, FSA and HSA  |
| Budget | `B089Y1L5DW` | $76.46 | PB | Renpho Wellness - US | RENPHO Active Massage Gun, Percussion Deep Tissue Back Massa |
| Runner-up | `B0DKSYFK5Z` | $59.99 | PB | Renpho Wellness - US | RENPHO Active Evo Massage Gun, Gifts for Men Women Deep Tiss |
| Worth a look | `B0CRKN2VJ6` | $58.49 | PB | Arboleaf | arboleaf Mini Massage Gun Deep Tissue, Portable Percussion M |

## Method

- ① Seaker ABA ASINs → PB `asins=` healthy track
- ② PB `brand_id` dig from healthy Seaker hits + known P4/P5/day-add brands
- ③ YP keyword on site 11767
- Massage: Bob-and-Brad lean reported not hard-fail. Chairs: tall soft densify; docks: real TB/USB-C dock not cable.
- Live CTA PB `?uid=fromsll`; YP track_link as-is
- Independent from Lab shortlists
- No invented prices / was / % / gallery / specs

## Next

- Parent launches CloudAgent apply draft PR (`published=false`) for scenes that passed density + brand gate.
- User must say「部署上线」before merge/Live.

## Stamp

`moretop10 | P6d L1 fill | draft-pack | 7/7 density | /workspace/shared/mt10-p6d-fill-report-2026-10-24.md | next=CloudAgent apply | blockers=none`

## QA post-filter (same run)

- Dropped **hair dryer brush** / hot-brush form factors; Steam Deck / handheld docks; kids **toy storage organizer**.
- Hair picks are ionic / high-speed blow dryers (Laifen · Slopehill · Wavytalk brand_ids; several Laifen titles ride Wavytalk PB brand_id — display from title).
- Bookcases: 2× Lerliuo kids sling bookshelves kept as soft small-space densify (narrow/toddler).
- Docks: WAVLINK Mac M1–M5 + Anker TB5/USB-C + Baseus USB-C (Windows-lean titles but real multi-port docks).
- Massage: 3/10 Bob-and-Brad — lean noted, multi-brand OK (5 brands).
- YP site 11767 returned 0 usable rows → **honest PB-only**. Live CTA stays PB `?uid=fromsll`.
- **No PR / no scaffold / no merge / no bake / no Live** from this fill executor.
