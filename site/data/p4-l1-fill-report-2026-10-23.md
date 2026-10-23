# MT10 P4 L1 fill report · 2026-10-23（Asia/Shanghai）
**生成**：2026-10-23T22:30:26.457272+08:00 · **occupied tip**：`586db343`  
**waiting_for_部署上线**：yes · **未合 / 未 bake / 未 Live** · L1 PB discovery (YP non-matching)  
**Apply pack**：`/workspace/shared/mt10-p4-fill-pack-2026-10-23.json` + dir `/workspace/shared/mt10-p4-fill-pack-2026-10-23/`  
This executor did **not** open a PR / merge / deploy.

## Counts

| # | Scene slug | Path | N | Density≥4 | Track mix |
|---|------------|------|---|-----------|-----------|
| 1 | `best-espresso-machines-for-home` | `/espresso-machines/best-espresso-machines-for-home/` | **10** | YES | PB10 |
| 2 | `best-automatic-litter-boxes` | `/litter-boxes/best-automatic-litter-boxes/` | **10** | YES | PB10 |
| 3 | `best-security-cameras-for-outdoor` | `/security-cameras/best-security-cameras-for-outdoor/` | **10** | YES | PB10 |
| 4 | `best-cordless-vacuums-for-pet-hair` | `/cordless-vacuums/best-cordless-vacuums-for-pet-hair/` | **10** | YES | PB10 |
| 5 | `best-hair-dryers-for-curly-hair` | `/hair-dryers/best-hair-dryers-for-curly-hair/` | **10** | YES | PB10 |
| 6 | `best-humidifiers-for-large-rooms` | `/humidifiers/best-humidifiers-for-large-rooms/` | **10** | YES | PB10 |
| 7 | `best-projectors-for-outdoor` | `/projectors/best-projectors-for-outdoor/` | **10** | YES | PB10 |
| 8 | `best-pillows-for-side-sleepers` | `/pillows/best-pillows-for-side-sleepers/` | **10** | YES | PB10 |

**Total admitted**：80 distinct ASINs · **collision ban size**：155 · **fake ASIN rejects**：0

## Pillows hub

- `/pillows/` **exists** on tip `586db343` (shortlist + `best-pillows-for-neck-pain` child). **No new hub required** for #8.

## Collisions avoided

- Global occupied flat: 155 ASINs (`mt10-p4-occupied-asins-2026-10-23.json`)
- #2 litter main / #3 doorbells / #4 robot+cordless / #6 babies+humid hub / #8 pillows+neck — all enforced; pack hits = 0
- Reject counts: {"accessory": 634, "collision": 120, "fake_asin": 0, "unhealthy": 88, "price": 69, "no_match": 17051, "title_ban": 0, "extra_ban": 0, "require": 87}

## YP note

- Probed YP sites 11767 (+11211). Keyword/asin-style params returned unrelated supplement catalog; **not used to fill**. Pack is honest PB-only.

## Per-slug picks

### `best-espresso-machines-for-home` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FMR5QPHW` | $109.99 | PB | AMZCHEF | AMZCHEF Espresso Machine 20 Bar, Compact Coffee Maker wi |
| Upgrade | `B0F2SWVC9N` | $103.52 | PB | AMZCHEF | AMZCHEF Espresso Machine 20 Bar – Professional Coffee Ma |
| Best value | `B0F6BFV1ZB` | $153.97 | PB | Casabrews | CASABREWS Espresso Machine 20 Bar, Professional Espresso |
| Premium | `B0BQ6PPQGZ` | $144.49 | PB | Casabrews | CASABREWS CM5418 Espresso Maker, Compact Espresso Machin |
| Alternative | `B0GX8WDTCJ` | $299.99 | PB | AMZCHEF | AMZCHEF Espresso Machine with Grinder, All-in-One Coffee |
| Also consider | `B0HDRXVXGP` | $129.99 | PB | AMZCHEF | AMZCHEF Espresso Machine with LED Touch Screen, DIY Mode |
| Editor pick | `B0GYR96XTF` | $199.99 | PB | AMZCHEF | AMZCHEF Espresso Machine 20 Bar, Easy-to-Use Compact Cof |
| Budget | `B0DY3X1MB8` | $129.99 | PB | Casabrews | CASABREWS 3700 Essential Espresso Machine, Stainless Ste |
| Runner-up | `B0HDND86K3` | $129.99 | PB | AMZCHEF | AMZCHEF Compact Espresso Machine for Home, 20 Bar Italia |
| Worth a look | `B0HJPRWSPK` | $199.99 | PB | AMZCHEF | AMZCHEF Espresso Machine, Auto Milk Frother, 20 Bar Pres |

### `best-automatic-litter-boxes` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GL7G2SXC` | $199.49 | PB | PetPivot | PetPivot Open Top Self Cleaning Cat Litter Box, Automati |
| Upgrade | `B0HMX593WK` | $459.99 | PB | Neakasa | Neakasa M9 Automatic Cat Litter Box with 2-Year Protecti |
| Best value | `B0DGXV26TL` | $430.63 | PB | Neakasa | Neakasa M1 Plus Automatic Cat Litter Box with 17.6 lbs M |
| Premium | `B0F1YMM29X` | $395.99 | PB | PETKIT | PETKIT Purobot Max 3 Premium Bundle Automatic Litter Box |
| Alternative | `B0DW41V1LN` | $484.98 | PB | Neakasa | Neakasa M1 Open-Top Self Cleaning Cat Litter Box and P2  |
| Also consider | `B0GD69KW7J` | $443.63 | PB | Neakasa | Neakasa M1 Plus Open-Top Self Cleaning Cat Litter Box wi |
| Editor pick | `B0F5499CSD` | $415.78 | PB | Neakasa | Neakasa M1 Plus Self Cleaning Cat Litter Box with Entran |
| Budget | `B0FJL8KQT1` | $399.99 | PB | Neakasa | Neakasa M1 Plus Self-Cleaning Litter Box Bundle with 2-Y |
| Runner-up | `B0H26KDLRR` | $369.99 | PB | PETKIT | PETKIT Purobot Max 3 Odor Free&Leak Control, Self-Cleani |
| Worth a look | `B0HNT18TPZ` | $279.99 | PB | Neakasa | Neakasa M1 Model Open-Top Self Cleaning Cat Litter Box ( |

### `best-security-cameras-for-outdoor` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GCLFNMQ4` | $199.99 | PB | Reolink | REOLINK TrackMix 4K Dual-lens PTZ Solar Security Cameras |
| Upgrade | `B0D1R47YCH` | $159.98 | PB | eufy Security | eufy Security Solar Wall Light Cam S120 (2-Pack), Solar  |
| Best value | `B0CJF9NJWQ` | $79.94 | PB | aosu | aosu 3K 5MP Solar Security Camera Wireless Outdoor PTZ 3 |
| Premium | `B0GLHKZMRW` | $699.99 | PB | aosu | aosu 4K Solar Security Cameras System Wireless Outdoor,  |
| Alternative | `B0FQ5PW8X2` | $599.99 | PB | aosu | aosu D1 Classic 6-Cam Kit, Security Cameras Wireless Out |
| Also consider | `B0D1BG66F6` | $499.99 | PB | Reolink | REOLINK 4K Solar Security Camera Wireless Outdoor 2.4/5G |
| Editor pick | `B0GLHRL89M` | $489.99 | PB | aosu | aosu D1 Max, 4-Cam Kit, 4K Solar Security Cameras System |
| Budget | `B0FM7186NR` | $449.99 | PB | Reolink | REOLINK 360° PT Solar Security Cameras Wireless Outdoor  |
| Runner-up | `B0CNRDG796` | $359.99 | PB | aosu | aosu D1 Classic 4-Cam Kit, Security Cameras Wireless Out |
| Worth a look | `B0DQ894R9L` | $309.99 | PB | Reolink | REOLINK 4K Dual Lens Cellular Security Camera Outdoor, S |

### `best-cordless-vacuums-for-pet-hair` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FC5MJ5T6` | $369.99 | PB | Dreame | DREAME Cordless Stick Vacuum Cleaner Z30 Essential, 210A |
| Upgrade | `B0D9XLCP28` | $169.95 | PB | Eureka | Eureka Stylus Elite NEC490BL Cordless Stick Vacuum, 350W |
| Best value | `B0CB6B2JWG` | $139.94 | PB | LEVOIT | Levoit Cordless Vacuum Cleaner, Anti-Tangle for Pet Hair |
| Premium | `B0GXJVW633` | $199.99 | PB | Dreame | DREAME Z10 Station T Cordless Vacuum with Auto-Empty Bas |
| Alternative | `B0F5WT2Q8W` | $154.95 | PB | Eureka | Eureka Cordless Vacuum Cleaner Lightweight, Stick Vacuum |
| Also consider | `B0GX93T8X7` | $199.99 | PB | LEVOIT | Levoit VortexIQ® Cordless Vacuum Cleaner for Pet Hair, 5 |
| Editor pick | `B0FLX94VCL` | $148.29 | PB | Eureka | Eureka RapidClean Pro Pet Hair Cordless Vacuum, NEC280WH |
| Budget | `B0FLJPZD5B` | $429.99 | PB | Dreame | DREAME H15 Pro CarpetFlex Cordless Vacuum Mop, Wet Dry V |
| Runner-up | `B0F9L92BTC` | $179.99 | PB | Eureka | Eureka ReactiSense 350W Anti-Tangle Cordless Stick Vacuu |
| Worth a look | `B0DK4QTRF5` | $329.99 | PB | roborock | roborock F25 Combo Wet Dry Vacuum Cleaner, 5-in-1 Cordle |

### `best-hair-dryers-for-curly-hair` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FG2N9M9N` | $36.71 | PB | Wavytalk | Wavytalk Blown Away Ionic Hair Dryer with Diffuser for C |
| Upgrade | `B0CY8DS8B1` | $89.97 | PB | slopehill | slopehill Professional Hair Dryer with Diffuser, Ionic H |
| Best value | `B0F8QH8XHV` | $109.94 | PB | Dreame | Dreame Pocket Pro Hair Dryer, Dual Voltage Travel Blow D |
| Premium | `B0CY4QMMBH` | $89.99 | PB | slopehill | slopehill Professional Ionic Hair Dryer with Diffuser -  |
| Alternative | `B0CYLVK9JJ` | $61.35 | PB | Wavytalk | Hair Dryer, Wavytalk Turblow Pro Fast Drying Blow Dryer  |
| Also consider | `B0CSFTC3GT` | $39.99 | PB | slopehill | Slopehill Professional Ionic Hair Dryer, Powerful 1800W  |
| Editor pick | `B0H2YXNQYB` | $69.95 | PB | Dreame | Dreame Gleam Travel Hair Dryer for Women, 110,000RPM Hig |
| Budget | `B0CYZCJNYZ` | $89.98 | PB | slopehill | slopehill Professional Ionic Hair Dryer with Diffuser 20 |
| Runner-up | `B0DRF7M6H5` | $71.97 | PB | Dreame | DREAME Pocket Pure High-Speed Hair Dryer, Lightweight Fo |
| Worth a look | `B0FL1R84WL` | $62.99 | PB | slopehill | slopehill Dual Voltage Travel Hair Dryer with Diffuser,  |

### `best-humidifiers-for-large-rooms` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B08FHZTYJB` | $99.99 | PB | LEVOIT | Levoit LV600HH 6L Warm&Cool Mist Humidifier for Bedroom  |
| Upgrade | `B08HS45N13` | $69.96 | PB | LEVOIT | Levoit Humidifiers for Bedroom Large Room, 6L, 60H Runti |
| Best value | `B0GR99R7XD` | $67.99 | PB | LEVOIT | Levoit Humidifiers for Bedroom Large Room, 6.2L Tank, Sm |
| Premium | `B0DG5G7GDN` | $31.49 | PB | Homvana | Homvana Cool Mist Humidifiers for Bedroom, Baby, Large R |
| Alternative | `B01MYGNGKK` | $99.99 | PB | LEVOIT | Levoit Humidifiers for Bedroom Large Room Home, Warm and |
| Also consider | `B0G1SQ5C11` | $249.99 | PB | LEVOIT | Levoit Evaporative Humidifiers for Home Whole House, 23L |
| Editor pick | `B09WQJZ7ZN` | $69.99 | PB | LEVOIT | Levoit Classic300 Ultrasonic Top Fill Humidifier, Extra  |
| Budget | `B0GQH7J1SW` | $49.99 | PB | LEVOIT | LEVOIT Smart Humidifier for Bedroom, 4.2L Top Fill Cool  |
| Runner-up | `B0B38TQK54` | $45.99 | PB | LEVOIT | Levoit Humidifiers for Bedroom, 3L Cool Mist Top Fill fo |
| Worth a look | `B0H41G86YL` | $44.99 | PB | LEVOIT | Levoit Humidifiers for Bedroom 3.2L for Large Room, Dish |

### `best-projectors-for-outdoor` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0CHW168LV` | $509.99 | PB | Nebula | NEBULA Mars 3 Air Portable Outdoor Projector, Built-In B |
| Upgrade | `B0FDGGQVXC` | $249.99 | PB | Aurzen | Aurzen Roku TV Smart Projector with Wifi and Bluetooth,  |
| Best value | `B0FKMHPCCB` | $129.98 | PB | Aurzen | Aurzen Roku TV D1R Smart Portable Outdoor Projector with |
| Premium | `B0D3T44YZ2` | $109.99 | PB | Aurzen | Aurzen EAZZE D1 Smart Portable Outdoor Projector with Wi |
| Alternative | `B0GSQKP7RF` | $149.97 | PB | Aurzen | Aurzen Roku TV D1R air USB-C Powered Smart Portable Outd |
| Also consider | `B0FG322D4R` | $139.96 | PB | HAPPRUN | HAPPRUN Portable Smart Mini Projector with WiFi and Blue |
| Editor pick | `B0H4TKY7WG` | $89.99 | PB | Aurzen | Aurzen Roku TV E1R Smart Portable Mini Projector with Wi |
| Budget | `B0F832HNG4` | $669.99 | PB | HAPPRUN | HAPPRUN 2000 ANSI Lumens Outdoor Projector with Built-in |
| Runner-up | `B0G78PKNCJ` | $499.96 | PB | HAPPRUN | HAPPRUN 3000 ANSI Lumens Outdoor Projector with Official |
| Worth a look | `B0H7J15S7R` | $449.95 | PB | HAPPRUN | HAPPRUN 3000 ANSI Lumens Outdoor Projector with Built-in |

### `best-pillows-for-side-sleepers` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0DT9MGL6H` | $89.99 | PB | Sweetnight | Sweetnight Cooling Pillows King Size Set of 2, Shredded  |
| Upgrade | `B0FFGLQ5YR` | $81.31 | PB | Sweetnight | Sweetnight Cooling Pillows Queen Size Set of 2, Shredded |
| Best value | `B0HKMHRNV5` | $79.99 | PB | Sweetnight | Sweetnight CoolNest Gel Memory Foam Pillows, Queen Size  |
| Premium | `B0HFJKJZ8M` | $109.99 | PB | Sweetnight | Sweetnight CoolNest Gel Memory Foam Pillows, Pillows Que |
| Alternative | `B0FMJWRVM8` | $60.91 | PB | Sweetnight | Sweetnight Cooling Pillows King Size Set of 2, CertiPUR- |
| Also consider | `B0GWK7Q33H` | $43.10 | PB | Sweetnight | Sweetnight Cooling Pillows Queen Size Set of 2, CertiPUR |
| Editor pick | `B0D7Q9H63S` | $32.27 | PB | Sweetnight | SweetNight Bed Pillows Standard Size Set of 2, Fluffy Lu |
| Budget | `B0D7Q997YS` | $31.41 | PB | Sweetnight | SweetNight Bed Pillows King Size Set of 2, Fluffy Luxury |
| Runner-up | `B0D7Q9FRHF` | $29.99 | PB | Sweetnight | SweetNight Bed Pillows Queen Size Set of 2, Fluffy Luxur |
| Worth a look | `B0GSFGD75J` | $26.99 | PB | Bedsum | BEDSUM Queen Size Bed Pillows Set of 2, Down Alternative |

## Method

- ① Seaker ABA ASINs (reference) → PB `asins=` healthy track
- ② PB `brand_id` dig (seaker + tip-hub brands: Reolink/AOSU/eufy/soundcore/Homvana/Dreame/Sweetnight/…)
- ③ YP attempted — catalog non-matching; unused
- Live CTA binding PB `?uid=fromsll`
- Independent from Lab shortlists
- Hard bans: accessories, doorbells (#3), pregnancy/maternity/nursing/mattress-topper (#8), babies humid ASINs (#6), robot pet-hair (#4)
- No invented prices / was / % / gallery / specs

## Next

- CloudAgent apply draft PR (published=false).
- User must say「部署上线」before merge/Live.
