# MT10 P6a L1 fill report · 2026-10-24（Asia/Shanghai）
**生成**：2026-10-24T11:06:37.467888+08:00 · **occupied tip**：`c58e0df1` · **lock**：`lock-p6a-rec`  
**waiting_for_部署上线**：yes · **未合 / 未 bake / 未 Live** · L1 PB∪YP refine×4 (soft parent densify)  
**Apply pack**：`/workspace/shared/mt10-p6a-fill-pack-2026-10-24.json` + `/workspace/shared/mt10-p6a-fill-pack-2026-10-24/`  
This executor did **not** open a PR / merge / deploy.

## Counts

| # | Scene slug | Path | N | Status | Brands | Soft-parent |
|---|------------|------|---|--------|--------|-------------|
| 1 | `best-pillows-for-back-sleepers` | `/pillows/best-pillows-for-back-sleepers/` | **2** | SHORTFALL | bedsum | 0 |
| 2 | `best-robotic-pool-cleaners-for-inground-pools` | `/robotic-pool-cleaners/best-robotic-pool-cleaners-for-inground-pools/` | **10** | OK | aiper,aiper us,beatbot,dreame | 0 |
| 3 | `best-bike-racks-for-hitch` | `/bike-racks/best-bike-racks-for-hitch/` | **9** | OK | cravot amz,montek,unknown,young electric | 0 |
| 4 | `best-espresso-machines-under-500` | `/espresso-machines/best-espresso-machines-under-500/` | **9** | OK | amzchef,casabrews,gevi | 0 |
| 5 | `best-hair-dryers-for-thick-hair` | `/hair-dryers/best-hair-dryers-for-thick-hair/` | **10** | OK | dreame,laifen,laifen-us-amz,slopehill,wavytalk | 0 |
| 6 | `best-security-cameras-for-indoor` | `/security-cameras/best-security-cameras-for-indoor/` | **10** | OK | aosu,eufy,eufy security,momcozy us,reolink | 0 |
| 7 | `best-projectors-for-bedroom` | `/projectors/best-projectors-for-bedroom/` | **6** | OK | aurzen,happrun | 0 |
| 8 | `best-dehumidifiers-for-bathroom` | `/dehumidifiers/best-dehumidifiers-for-bathroom/` | **7** | OK | aeocky,knka-us,waykar | 0 |

**Total admitted**：63 · **density≥4**：7/8 · **collision flat**：855

## Notes

- YP 11767 probed — 0 usable (honest PB-only). CTA PB ?uid=fromsll. Soft parent densify on. Hard screens: bed-pillow / indoor-only cam / no galaxy-screen / bathroom≤35pint.
- Soft parent densify: hub ASINs may reappear on scene; sibling scene ASINs stay banned.
- Pillows: bed pillows only; Sweetnight-heavy OK; no duvet/quilt/traction/pillowcase.
- Pool: inground/dual-use; reject above-ground-only + accessories.
- Bike: hitch required.
- Espresso: real PB price ≤$500.
- Hair: ASIN dedupe vs curly/fine/travel.
- Security: hard indoor-only; no doorbell; any outdoor in title rejected.
- Projectors: no galaxy/star/inflatable screens; ASIN dedupe vs outdoor/theater.
- Dehumidifiers: ≤35 pint preference; reject crawl-space/commercial/50+ pint/basement-primary.
- OUT: mattresses/best-mattresses-for-back-pain not reopened.

## Per-slug picks

### `best-pillows-for-back-sleepers` (2) — SHORTFALL

_soft parent densify from pillow_hub (sibling neck/side/stomach still banned); Sweetnight-heavy OK_

_SHORTFALL density=2<4 — skip scaffold._
| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GSFK72ZQ` | $26.99 | PB | Bedsum | BEDSUM Queen Size Bed Pillows Set of 2, Down Alternative Pil |
| Upgrade | `B0GSF92SW7` | $26.99 | PB | Bedsum | BEDSUM Queen Size Bed Pillows Set of 2, Down Alternative Pil |

### `best-robotic-pool-cleaners-for-inground-pools` (10) — OK

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GWGZR9QC` | $799.00 | PB | Beatbot | Beatbot Sora 10 Cordless Robotic Pool Vacuum Cleaner with iS |
| Upgrade | `B0H3YWDJSR` | $799.00 | PB | Beatbot | Beatbot Sora 10 Cordless Robotic Pool Vacuum Cleaner with iS |
| Best value | `B0DPMDQ2RD` | $799.00 | PB | Beatbot | Beatbot AquaSense 2 Cordless Robotic Pool Vacuum Cleaner, Sm |
| Premium | `B0FJ818NNZ` | $559.99 | PB | Aiper US | Aiper Scuba S1 Robotic Pool Cleaner, Wall & Waterline Cleani |
| Alternative | `B0HF51H3FS` | $499.99 | PB | Aiper US | Aiper Scuba S1 2026 Robotic Pool Cleaner,Floor/Wall/Waterlin |
| Also consider | `B0HHRS6FMF` | $499.98 | PB | Aiper | Aiper Scuba S1 2026 Robotic Pool Cleaner,Floor/Wall/Waterlin |
| Editor pick | `B0F2T49DNT` | $499.00 | PB | Dreame | DREAME Cordless Robotic Pool Cleaner, LiFi & APP Control, 80 |
| Budget | `B0F1553HCR` | $499.00 | PB | Dreame | DREAME Z1 Cordless Robotic Pool Cleaner, 8000 GPH Suction, F |
| Runner-up | `B0GR56V139` | $499.00 | PB | Dreame | (2026 New) DREAME Robotic Pool Vacuum, Wall & Waterline Clea |
| Worth a look | `B0HG1MXMF7` | $449.99 | PB | Aiper US | Aiper Scuba S1（2024） - Robotic Pool Cleaner, Powerful Suctio |

### `best-bike-racks-for-hitch` (9) — OK

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0HHS5VMH9` | $449.99 | PB | Young Electric | Young 3 EBikes Rack Hitch Mount, Fat Tire Ebike Carrier with |
| Upgrade | `B0FHGZ9Q1X` | $449.99 | PB | Young Electric | Young Electric 3-Bike Rack, 250LBS, Hitch Carrier with Ramp |
| Best value | `B0DJXHZ4PR` | $379.99 | PB | Young Electric | YOUNG ELECTRIC 250LBS. Capacity Foldable Aluminum 3-Ebike Ra |
| Premium | `B0D13H18W7` | $296.99 | PB | Unknown | Young 2-Bike Ebike Hitch Rack with Ramp, 200 lbs Capacity fo |
| Alternative | `B0F13KDGZ2` | $249.99 | PB | CRAVOT AMZ | CRAVOT E1 Ebike Rack with Ramp 100lbs 5'' Tire 2'' Receiver |
| Also consider | `B09MHB7939` | $159.98 | PB | Unknown | Young 200 lbs 2-Bike Rack Hitch Mount for Car SUV, 2" Receiv |
| Editor pick | `B0G46J5Z9N` | $84.99 | PB | monTEK | monTEK 4-Bike Rack for Cars, Trucks, SUVs with 2” Hitch |
| Budget | `B0G46JDKJS` | $80.99 | PB | monTEK | monTEK 3-Bike Rack for Cars, Trucks, SUVs with 2” Hitch |
| Runner-up | `B0H9W85RFZ` | $79.99 | PB | monTEK | monTEK 2-Bike Rack for Cars, Trucks, SUVs with 2” Hitch |

### `best-espresso-machines-under-500` (9) — OK

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0HJR993B9` | $299.99 | PB | AMZCHEF | AMZCHEF Espresso Machine 7205-7 |
| Upgrade | `B0HJR7GVHZ` | $299.99 | PB | AMZCHEF | AMZCHEF Espresso Machine |
| Best value | `B0HJR4D8PM` | $299.99 | PB | AMZCHEF | AMZCHEF Espresso Machine 7205-5 |
| Premium | `B0HHD19QF7` | $299.98 | PB | Gevi | Gevi 20 Bar Professional Espresso Machines for Latte/Cappucc |
| Alternative | `B0GWQ69YXZ` | $296.98 | PB | Casabrews | CASABREWS CM5418Pro Espresso Machine with Tornado Eletric Co |
| Also consider | `B0GWPXC2V9` | $292.38 | PB | Casabrews | CASABREWS Ultra Espresso Machine with Tornado Electric Conic |
| Editor pick | `B0HG4FK6X6` | $285.28 | PB | Casabrews | CASABREWS Ultra PRO Espresso Machine with 12oz Titanium Mug  |
| Budget | `B0FXM6YCMQ` | $284.96 | PB | Gevi | Gevi 20 Bar Espresso Machine, 58mm Portafilter, 3 Temps, Lat |
| Runner-up | `B0GX1FZL6Z` | $249.99 | PB | Gevi | Gevi 20 Bar Espresso Machine with Conical Burr Anti-Static C |

### `best-hair-dryers-for-thick-hair` (10) — OK

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0H8D51V8S` | $199.99 | PB | wavytalk | Laifen Swift 4 High-Speed Ionic Hair Dryer with Diffuser, Po |
| Upgrade | `B0H82ZR122` | $195.01 | PB | wavytalk | Laifen Black Swift Special Hair Dryer, High Speed 200M with  |
| Best value | `B0H82SY69V` | $195.01 | PB | wavytalk | Laifen White Swift Hair Dryer, High Speed 200M with Laifen G |
| Premium | `B0FK5MBDJZ` | $83.99 | PB | Laifen-US-AMZ | Laifen SE Lite High-Speed Ionic Hair Dryer with Diffuser, Mi |
| Alternative | `B0FK5H24WY` | $83.99 | PB | Laifen-US-AMZ | Laifen SE Lite High-Speed Ionic Hair Dryer with Diffuser, Bi |
| Also consider | `B0GWHGTBDY` | $74.99 | PB | Laifen | Laifen Air Hair Dryer with Diffuser, High-Speed Ionic Blow D |
| Editor pick | `B0H2YTC8VF` | $69.94 | PB | Dreame | Dreame Gleam Travel Hair Dryer for Women, 110,000RPM High Sp |
| Budget | `B0C3M9WBQF` | $39.99 | PB | Slopehill | slopehill Professional Ionic Hair Dryer, Powerful 1800W Fast |
| Runner-up | `B0DZ2SBRYY` | $39.99 | PB | slopehill | slopehill Professional Ionic Hair Dryer, Lime Cream |
| Worth a look | `B0DZ2NG3XT` | $39.99 | PB | slopehill | slopehill Professional Ionic Hair Dryer, Lavender |

### `best-security-cameras-for-indoor` (10) — OK

_hard indoor-only (any outdoor in title rejected)_

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FQ5LMV98` | $199.99 | PB | eufy Security | eufy Security Baby Monitor E20, 2K Camera, 5" 720p Display,  |
| Upgrade | `B0DQWB2YLK` | $129.99 | PB | eufy Security | eufy Security Baby Monitor E21 Add-On Camera, 4K UHD, Pan-Ti |
| Best value | `B0FQ9MNH2Q` | $129.99 | PB | eufy Security | eufy Baby Monitor C10, 2K Camera, 4.5" 480p Display, No Wi-F |
| Premium | `B0CD7F1M9R` | $99.99 | PB | Eufy | eufy Security 4K Indoor Cam S350, No Subscription, Dual Came |
| Alternative | `B0BJZK2L5T` | $93.49 | PB | Reolink | REOLINK 4K Pan Tilt Indoor Camera, 3X Optical Zoom, Dual-Ban |
| Also consider | `B07Z841XYD` | $93.49 | PB | Reolink | REOLINK 4K Indoor Camera, 3X Optical Zoom, Dual-Band WiFi 6, |
| Editor pick | `B0DPKDX9H8` | $79.99 | PB | momcozy US | Momcozy Baby Monitor BM01 Add-on Camera Unit, 1080P HD Resol |
| Budget | `B0DJVGZQW7` | $69.99 | PB | Eufy | eufy Security 4K Indoor Camera E30, No Subscription, Work as |
| Runner-up | `B08RS4C67L` | $64.99 | PB | Reolink | REOLINK E1 Pro(Black) 3K PT Wi-Fi Indoor Camera for Baby & P |
| Worth a look | `B0CKPKBVW9` | $44.99 | PB | aosu | aosu 4MP Indoor Security Camera - Baby & Pet Monitoring with |

### `best-projectors-for-bedroom` (6) — OK

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0H3KTBXRQ` | $399.99 | PB | Aurzen | Aurzen ZIP Tri-Fold DLP Pocket Mini Projector, 1.5-Hour Play |
| Upgrade | `B0HGXXZPWF` | $279.99 | PB | Aurzen | Aurzen ZIP Tri-Fold DLP Pocket Mini Projector with USB-C, Bl |
| Best value | `B0GV3YZ5XH` | $279.99 | PB | Aurzen | Aurzen ZIP Tri-Fold DLP Pocket Mini Projector with USB-C, Bl |
| Premium | `B0DDT9FQCQ` | $268.94 | PB | HAPPRUN | HAPPRUN 2000 ANSI 4K Decoding Projector with WiFi and Blueto |
| Alternative | `B0G2RM3ZBZ` | $199.98 | PB | HAPPRUN | HAPPRUN 4K Decoding Daytime Smart Projector with WiFi and Bl |
| Also consider | `B0B28G5Y4R` | $59.99 | PB | HAPPRUN | HAPPRUN Native 1080P Bluetooth Projector - Standard |

### `best-dehumidifiers-for-bathroom` (7) — OK

_≤35 pint preference; basement-primary rejected unless small pint_

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0GVS2RDLB` | $139.99 | PB | Waykar | Waykar 23 Pint Energy Star Home Dehumidifier, Ultra Quiet 35 |
| Upgrade | `B0HFHG2C6Y` | $190.84 | PB | Waykar | Waykar 34 Pints Energy Star Dehumidifier for Spaces up to 2, |
| Best value | `B0FPD7Y2CQ` | $190.84 | PB | Waykar | Waykar 34 Pints Energy Star Dehumidifier for Spaces up to 2, |
| Premium | `B0GSFWHGCW` | $139.98 | PB | KNKA-US | KNKA 2500 Ft² Max 34 Pints Dehumidifier for Basement with Dr |
| Alternative | `B0DR7TZGV8` | $129.99 | PB | KNKA-US | KNKA 2500 Ft² Max 34 Pints Dehumidifier for Basement with Dr |
| Also consider | `B0G1TCQPZQ` | $260.99 | PB | AEOCKY | AEOCKY Dehumidifier with Pump Up to 16.5ft Energy Star Most  |
| Editor pick | `B0G1WK1LX5` | $242.96 | PB | AEOCKY | AEOCKY Dehumidifier with Pump Up to 16.5ft Energy Star Most  |

## Next

- CloudAgent scaffold draft (`published=false`) for OK: best-robotic-pool-cleaners-for-inground-pools, best-bike-racks-for-hitch, best-espresso-machines-under-500, best-hair-dryers-for-thick-hair, best-security-cameras-for-indoor, best-projectors-for-bedroom, best-dehumidifiers-for-bathroom.
- SKIP scaffold: best-pillows-for-back-sleepers.
- User「部署上线」before merge/Live.

## Stamp

`moretop10 | P6a L1 fill | draft-pack | 7/8 density | /workspace/shared/mt10-p6a-fill-report-2026-10-24.md | next=CloudAgent apply | blockers=shortfall 1/8`
