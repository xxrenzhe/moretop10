# MT10 P6c L1 fill report · 2026-10-24（Asia/Shanghai）
**生成**：2026-10-24T13:45:46.822829+08:00 · **occupied tip**：`007d73ff` · **lock**：`lock-p6c-rec`  
**waiting_for_部署上线**：yes · **未合 / 未 bake / 未 Live** · L1 PB∪YP discovery  
**Apply pack**：`/workspace/shared/mt10-p6c-fill-pack-2026-10-24.json` + dir `/workspace/shared/mt10-p6c-fill-pack-2026-10-24/`  
This executor did **not** open a PR / merge / deploy. Did **not** flip #58/#60 published.

## Counts

| # | Scene slug | Path | N | Status | Brands | Notes |
|---|------------|------|---|--------|--------|-------|
| 1 | `best-projectors-for-gaming` | `/projectors/best-projectors-for-gaming/` | **6** | OK | aurzen,happrun | OK; soft densify smart/FHD; sibling bedroom/outdoor/theater banned |
| 2 | `best-humidifiers-for-plants` | `/humidifiers/best-humidifiers-for-plants/` | **10** | OK | homvana,levoit,vivosun | OK; grow-tent bundles rejected; soft densify cool mist |
| 3 | `best-doormats-for-outdoors` | `/doormats/best-doormats-for-outdoors/` | **10** | OK | beqhause,jsei | JSEI brand_gate risk reported; multi-brand OK |
| 4 | `best-noise-cancelling-headphones-for-work` | `/noise-cancelling-headphones/best-noise-cancelling-headphones-for-work/` | **10** | OK | edifier,soundcore | OK over-ear ANC; earbuds banned; travel siblings banned |
| 5 | `best-bluetooth-speakers-for-shower` | `/bluetooth-speakers/best-bluetooth-speakers-for-shower/` | **10** | OK | bassbloom,comiso,edifier,insmy,soundcore | OK IP/waterproof hard; outdoor BT siblings banned |
| 6 | `best-office-chairs-under-200` | `/office-chairs/best-office-chairs-under-200/` | **10** | OK | amseatec,brick attic,felixking,primy | OK hard price≤200; gaming/back/long-hours siblings banned |
| 7 | `best-litter-boxes-for-large-cats` | `/litter-boxes/best-litter-boxes-for-large-cats/` | **1** | SHORTFALL | neakasa | SHORTFALL: sibling multi-cat/automatic/odor consumed units; accessories rejected; N=1 no invent |

**Total admitted**：57 · **scenes density≥4**：6/7 · **collision ban size**：1012 · **fake ASIN rejects**：0

## Collisions avoided

- Global occupied flat: 1012 (`mt10-p6c-occupied-asins-2026-10-24.json`)
- Scene bans proj=26 hum=19 door=20 nc=10 bt=10 chair=28 litter=24
- Reject counts: {"accessory": 184, "collision": 221, "fake_asin": 0, "unhealthy": 73, "price": 64, "no_match": 12115, "title_ban": 0, "extra_ban": 19, "require": 39, "brand_gate": 0}
- OUT: tinnitus · mattress hang · red-light masks · robot-mop · #58/#60 published flip

## Brand / YP notes

- Probed YP site 11767 (YP_TOKEN_MT10LAB). 0 usable relevant rows (timeout/empty/non-match) — pack honest PB-only where YP failed. Live CTA remains PB ?uid=fromsll.
- Brand gates: `{"best-projectors-for-gaming": {"fail": false, "brands": ["aurzen", "happrun"]}, "best-humidifiers-for-plants": {"fail": false, "brands": ["homvana", "levoit", "vivosun"]}, "best-doormats-for-outdoors": {"fail": false, "brands": ["beqhause", "jsei"], "risk": "JSEI present — brand_gate risk reported (doormat); multi-brand OK if density≥4"}, "best-noise-cancelling-headphones-for-work": {"fail": false, "brands": ["edifier", "soundcore"]}, "best-bluetooth-speakers-for-shower": {"fail": false, "brands": ["bassbloom", "comiso", "edifier", "insmy", "soundcore"]}, "best-office-chairs-under-200": {"fail": false, "brands": ["amseatec", "brick attic", "felixking", "primy"]}, "best-litter-boxes-for-large-cats": {"fail": false, "brands": ["neakasa"], "risk": "single-brand after honest PB∪YP — report brand_gate risk; density may still OK"}}`
- Soft parent densify preferred; did **not** hard-block scenes.

## Per-slug picks

### `best-projectors-for-gaming` (6)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0HFQPY1FW` | $299.97 | PB | HAPPRUN | HAPPRUN 2000 ANSI Outdoor 4K Decoding Full HD Smart Projecto |
| Upgrade | `B0FDGLZKKM` | $169.98 | PB | Aurzen | Aurzen Roku TV D1R Cube 1080P FHD Smart Projector, Sealed Op |
| Best value | `B0G91DDGWR` | $129.99 | PB | Aurzen | Aurzen EAZZE D1 air Smart Portable Projector, USB-C Powered, |
| Premium | `B0FDQFZ6HM` | $250.70 | PB | HAPPRUN | HAPPRUN 1500 ANSI Official Licensed Google TV Outdoor 4K Ful |
| Alternative | `B0F7XFRHC2` | $199.96 | PB | HAPPRUN | HAPPRUN 3000 ANSI Official Licensed Google TV Outdoor 4K Ful |
| Also consider | `B0FDQFD1R7` | $159.96 | PB | HAPPRUN | HAPPRUN 1500 ANSI Smart Outdoor Projector, Built-in Apps, 30 |

### `best-humidifiers-for-plants` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0HLKW21NB` | $47.49 | PB | VIVOSUN | VIVOSUN 4L Cool Mist Humidifier with Remote Control for Bedr |
| Upgrade | `B0GR9JX71D` | $69.99 | PB | LEVOIT | Levoit Humidifiers for Bedroom Large Room Home, 6.2L Cool Mi |
| Best value | `B09KT9ZK7Q` | $44.35 | PB | LEVOIT | Levoit Smart Cool Mist Top Fill Humidifiers for Bedroom with |
| Premium | `B0C9HBKQ5D` | $39.99 | PB | LEVOIT | Levoit Humidifiers for Bedroom,Top-Fill Ultrasonic Cool Mist |
| Alternative | `B0F5W9968Q` | $39.99 | PB | Homvana | Homvana Cool Mist Humidifiers for Bedroom, Baby, Large Room  |
| Also consider | `B0DKH7G5WM` | $38.88 | PB | Homvana | Homvana Cool Mist Humidifiers for Bedroom, Baby, Large Room  |
| Editor pick | `B09LM1588Z` | $29.97 | PB | Homvana | Homvana Cool Mist Humidifiers for Bedroom, Baby, Large Room  |
| Budget | `B0DHGP2JQ8` | $59.99 | PB | VIVOSUN | VIVOSUN AeroStream H05 1.32 Gal Smart WiFi Humidifier with H |
| Runner-up | `B0CB1F4ZG2` | $21.50 | PB | Homvana | Homvana Cool Mist Humidifiers for Bedroom, Baby, Large Room  |
| Worth a look | `B0GPWP16GL` | $42.49 | PB | LEVOIT | Levoit Humidifiers for Bedroom 4.2L Top Fill for Large Room, |

### `best-doormats-for-outdoors` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0CYGTNJHQ` | $19.99 | PB | BEQHAUSE | BEQHAUSE Door Mat Dirt Trapper Non Slip Entryway Rugs Absorb |
| Upgrade | `B0G2PG8JC7` | $59.99 | PB | BEQHAUSE | BEQHAUSE Dirt Trapper Door Mat 36" x 60" Non-Slip Washable,  |
| Best value | `B0DX1JMB2M` | $59.99 | PB | BEQHAUSE | BEQHAUSE Door Mats 36" x 60", Dirt Trapper Doormats, Green / |
| Premium | `B0FLTYJSS5` | $34.99 | PB | JSEI | JSEI Dirt Trapper Door Mat 24"x36", Non-Slip Entryway Rugs D |
| Alternative | `B0GXV6PXWC` | $59.99 | PB | JSEI | JSEI Door Mat for Entrance 36"x60", Dirt Trapper Doormat, Li |
| Also consider | `B0GXTYCG8H` | $59.99 | PB | JSEI | JSEI Door Mat for Entrance 36"x60", Dirt Trapper Doormat, Be |
| Editor pick | `B0DSCSWPGH` | $40.60 | PB | BEQHAUSE | BEQHAUSE Door Mats 36" x 60", Dirt Trapper Doormats, Black / |
| Budget | `B0CYGJBP14` | $37.99 | PB | BEQHAUSE | BEQHAUSE Dirt Trapper Door Mat 24" x 36" Non-Slip Washable,  |
| Runner-up | `B0CYGGLFZM` | $29.99 | PB | BEQHAUSE | BEQHAUSE Dirt Trapper Door Mat 32" x 48" Non-Slip Washable,  |
| Worth a look | `B0CYGWRPPX` | $21.59 | PB | BEQHAUSE | BEQHAUSE Dirt Trapper Door Mat 24" x 36" Non-Slip Washable,  |

### `best-noise-cancelling-headphones-for-work` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0D1QR8NL8` | $39.99 | PB | Nebula | Soundcore Anker Life Q20 Hybrid Active Noise Cancelling Head |
| Upgrade | `B0DCZ4JSNK` | $49.99 | PB | EDIFIER | Edifier W800BT Pro Hybrid Active Noise Cancelling Headphones |
| Best value | `B0F2HF8FHG` | $49.99 | PB | EDIFIER | Edifier W80 Over Ear Headphones with -49dB Active Noise Canc |
| Premium | `B0DR7NJMWV` | $49.99 | PB | EDIFIER | Edifier W80 Over Ear Headphones with -49dB Active Noise Canc |
| Alternative | `B0DKW75VC5` | $71.99 | PB | Nebula | Soundcore by Anker Q30 Hybrid Active Noise Cancelling Headph |
| Also consider | `B08Q8C3LHT` | $71.99 | PB | Nebula | soundcore Life Q30 by Anker, Hybrid Active Noise Cancelling  |
| Editor pick | `B0D41KBMFY` | $49.99 | PB | EDIFIER | Edifier W800BT Pro Hybrid Active Noise Cancelling Over Ear H |
| Budget | `B0D41KDQ7J` | $49.99 | PB | EDIFIER | Edifier W800BT Pro Hybrid Active Noise Cancelling Over Ear H |
| Runner-up | `B0F9DR3ZPG` | $149.99 | PB | EDIFIER | Edifier WH950NB Gen 2 8-Level Active Noise Cancelling Headph |
| Worth a look | `B08Q89DN6V` | $71.99 | PB | Nebula | Soundcore by Anker Q30 Hybrid Active Noise Cancelling Headph |

### `best-bluetooth-speakers-for-shower` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B07XDJVJKY` | $27.99 | PB | INSMY | INSMY C12 IP67 Waterproof Shower Bluetooth Speakers Portable |
| Upgrade | `B07KRK3FZ9` | $26.99 | PB | INSMY | INSMY C12 IP67 Waterproof Shower Bluetooth Speakers Portable |
| Best value | `B08BYPGVY6` | $26.99 | PB | INSMY | INSMY C12 IP67 Waterproof Shower Bluetooth Speakers Portable |
| Premium | `B08L7XK2FL` | $16.97 | PB | COMISO | comiso Portable Bluetooth Speaker, Small Shower Speaker with |
| Alternative | `B0C2YB62ZQ` | $21.99 | PB | COMISO | comiso Shower Bluetooth Speaker, IPX7 Waterproof Speaker wit |
| Also consider | `B0C2XYD3PS` | $21.99 | PB | COMISO | comiso Shower Bluetooth Speaker, IPX7 Waterproof Speaker wit |
| Editor pick | `B0BXCHDSTF` | $49.99 | PB | EDIFIER | Edifier MP100 Plus Portable Bluetooth Speaker, Lightweight T |
| Budget | `B0HJSW1G3J` | $17.99 | PB | BassBloom | BassBloom ROAR 3 Portable Bluetooth Speaker,IPX6 Waterproof, |
| Runner-up | `B0DHFZW4CV` | $25.99 | PB | Nebula | Soundcore Select 4 Go Bluetooth Shower Speaker by Anker, IP6 |
| Worth a look | `B0DB1B7WG6` | $23.99 | PB | Nebula | Soundcore Select 4 Go Bluetooth Shower Speaker by Anker, IP6 |

### `best-office-chairs-under-200` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0H5QT1HC5` | $149.99 | PB | FelixKing | FelixKing Office Chair, Ergonomic Desk Chair Breathable Mesh |
| Upgrade | `B0G4VSV2TF` | $149.99 | PB | FelixKing | FelixKing Office Chair, Ergonomic Desk Chair Breathable Mesh |
| Best value | `B0GD7J3P3C` | $188.99 | PB | FelixKing | FelixKing Office Chair, Desk Chair with Adjustable Lumbar Su |
| Premium | `B0B41TGY8P` | $106.00 | PB | Primy | Office Chair Ergonomic Desk Chair with Flip up Armrests Swiv |
| Alternative | `B0B41TVP2Z` | $106.00 | PB | Primy | Office Chair Ergonomic Desk Chair with Flip up Armrests Swiv |
| Also consider | `B0B41W3455` | $106.00 | PB | Primy | Office Chair Ergonomic Desk Chair with Flip up Armrests Swiv |
| Editor pick | `B0H142B4XM` | $119.99 | PB | Brick Attic | Leather Office Chair with Flip Up Arms, 360° Swivel Ergonomi |
| Budget | `B0H13XHXCH` | $119.99 | PB | Brick Attic | Leather Office Chair with Flip Up Arms, 360° Swivel Ergonomi |
| Runner-up | `B0H13TVRS5` | $119.99 | PB | Brick Attic | Leather Office Chair with Flip Up Arms, 360° Swivel Ergonomi |
| Worth a look | `B0F91VGV23` | $62.99 | PB | AMSEATEC | amseatec Mesh Office Chair, Ergonomic Home Office Chair with |

### `best-litter-boxes-for-large-cats` (1)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FH2FYWZK` | $425.98 | PB | Neakasa | Neakasa Open Top Cat Litter Box with PooGuard Trash Can – 9. |

## Method

- ① Seaker ABA ASINs → PB `asins=` healthy track
- ② PB `brand_id` dig from healthy Seaker hits + known P4/P5/day-add brands
- ③ YP keyword on site 11767
- Doormat: JSEI brand_gate risk reported not hard-fail. Chairs: hard price≤200.
- Live CTA PB `?uid=fromsll`; YP track_link as-is
- Independent from Lab shortlists
- No invented prices / was / % / gallery / specs

## Next

- Parent launches CloudAgent apply draft PR (`published=false`) for scenes that passed density + brand gate.
- User must say「部署上线」before merge/Live.

## Stamp

`moretop10 | P6c L1 fill | draft-pack | 6/7 density | /workspace/shared/mt10-p6c-fill-report-2026-10-24.md | next=CloudAgent apply | blockers=shortfall 1/7`
