# MT10 P5b L1 fill report · 2026-10-24（Asia/Shanghai）
**生成**：2026-10-24T01:09:13.287575+08:00 · **refined**：2026-10-24T01:09:38.090503+08:00 · **occupied tip**：`bf966921` · **lock**：`lock-p5b-rec`  
**waiting_for_部署上线**：yes · **未合 / 未 bake / 未 Live** · L1 PB discovery (YP timeout)  
**Apply pack**：`/workspace/shared/mt10-p5b-fill-pack-2026-10-24.json` + dir `/workspace/shared/mt10-p5b-fill-pack-2026-10-24/`  
This executor did **not** open a PR / merge / deploy.

## Counts

| # | Scene slug | Path | N | Density≥4 | Track mix | Brand gate |
|---|------------|------|---|-----------|-----------|------------|
| 1 | `best-mattresses-for-back-pain` | `/mattresses/best-mattresses-for-back-pain/` | **0** | NO · SHORTFALL | — | FAIL·Sweetnight-only |
| 2 | `best-office-chairs-for-long-hours` | `/office-chairs/best-office-chairs-for-long-hours/` | **10** | YES | PB10 | OK·dowinx,felixking,heroset,primy |
| 3 | `best-pillows-for-stomach-sleepers` | `/pillows/best-pillows-for-stomach-sleepers/` | **10** | YES | PB10 | OK·sweetnight |
| 4 | `best-tower-fans-for-bedroom` | `/tower-fans/best-tower-fans-for-bedroom/` | **2** | NO · SHORTFALL | PB2 | OK·dreame,levoit |

**Total admitted**：22 · **scenes density≥4**：2/4 · **collision ban size**：326 · **fake ASIN rejects**：0

## Collisions avoided

- Global occupied flat: 326 (`mt10-p5b-occupied-asins-2026-10-24.json`)
- Mattress side+hub: 11 · office back-pain: 12 · pillow neck+side: 17 · tower hub: 10
- Reject counts: {"accessory": 257, "collision": 76, "fake_asin": 0, "unhealthy": 73, "price": 25, "no_match": 5296, "title_ban": 17, "extra_ban": 0, "require": 37, "brand_gate": 10}
- OUT (not filled): `#4 back-sleepers pillow` · `#6 heavy mattress`

## Brand / YP / shortfall notes

- Probed YP site 11767 (YP_TOKEN_MT10LAB). Keyword calls timed out (read timeout) on firm mattress / hybrid / ergonomic office chair; 0 usable rows. Pack is honest PB-only (same stance as P5a). Live CTA remains PB ?uid=fromsll — do not rebind to YP.
- Mattress brand gate: **FAIL** — PB∪YP only yielded Sweetnight mattress heroes after accessory/collision filters; shortlist rejected (would_have_picked=10). Do **not** scaffold until multi-brand.
- Tower bedroom: **SHORTFALL 2/10** — tip hub already holds 10/10 LEVOIT/DREO/dreame tower ASINs; remaining PB tower-named SKUs outside hub = 2 (Levoit + dreame variant). Did **not** pad with pedestal/table/ceiling fans (route lock `tower-fans`).
- Pillows stomach: 10/10 Sweetnight soft/hotel/gusseted/cooling shredded (cervical/neck/side banned). Multi-brand not required for pillows.
- Office long-hours: 10/10 multi-brand FelixKing/Primy/HeroSet/Dowinx; hard-screen vs back-pain ASINs.
- Soft parent densify (mattresses/pillows/office hubs) did **not** hard-block scenes.

## Per-slug picks

### `best-mattresses-for-back-pain` (0)

_Brand gate FAIL — Sweetnight-only / single-brand after honest PB∪YP — reject shortlist; do not pad fake brands (would_have_picked=10, brands=['sweetnight']). Shortfall left empty; do not scaffold until multi-brand PB∪YP._

### `best-office-chairs-for-long-hours` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FPWSRW2P` | $499.99 | PB | FelixKing | FelixKing Office Desk Chairs, Ergonomic PC Desk Chair with W |
| Upgrade | `B0FPWZ7DNG` | $314.99 | PB | FelixKing | FelixKing Office Desk Chairs, Ergonomic PC Desk Chair with W |
| Best value | `B0FPWP2WXG` | $170.99 | PB | FelixKing | FelixKing Office Desk Chairs, Ergonomic PC Desk Chair with W |
| Premium | `B0FZBQHXZP` | $179.99 | PB | Primy | 2-Pack Office Chair Ergonomic Desk Chair with Flip up Armres |
| Alternative | `B0B41WB554` | $129.99 | PB | Primy | Office Chair Ergonomic Desk Chair with Flip up Armrests Swiv |
| Also consider | `B0F4D8ZN7C` | $106.00 | PB | Primy | Office Chair Ergonomic Desk Chair with Flip up Armrests Swiv |
| Editor pick | `B0GRVN1QXK` | $69.98 | PB | HeroSet | Ergonomic Office Chair, High Back Desk Chair with Flip-up Ar |
| Budget | `B0DM1JR73Q` | $129.99 | PB | HeroSet | Office Chair, Ergonomic Big and Tall Computer Desk Chair wit |
| Runner-up | `B0HGYCK7Q1` | $139.99 | PB | HeroSet | Office Chair, Ergonomic Big and Tall Computer Desk Chairs, E |
| Worth a look | `B0GXW2DTNR` | $179.99 | PB | Dowinx | Dowinx Big and Tall Office Chair, Ergonomic Desk Chair with  |

### `best-pillows-for-stomach-sleepers` (10)

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0FNCJKZ6J` | $47.76 | PB | Sweetnight | Sweetnight Pillows Queen Size Set of 2, Bed Hotel Pillows, A |
| Upgrade | `B0DT97KHGT` | $81.31 | PB | Sweetnight | Sweetnight Cooling Pillows Queen Size Set of 2, Shredded Mem |
| Best value | `B0HFJMX34K` | $79.99 | PB | Sweetnight | Sweetnight CoolNest Gel Memory Foam Pillows, Queen Size Cool |
| Premium | `B0H5VQC5F6` | $63.99 | PB | Sweetnight | Sweetnight Cooling Pillows King Size Set of 2, Shredded Memo |
| Alternative | `B0FMJXJXGB` | $43.10 | PB | Sweetnight | Sweetnight Cooling Pillows Queen Size Set of 2, CertiPUR-US  |
| Also consider | `B0H5WGBQWR` | $41.70 | PB | Sweetnight | Sweetnight Cooling Pillows Queen Size Set of 2, Shredded Mem |
| Editor pick | `B0H5VXT4PQ` | $41.70 | PB | Sweetnight | Sweetnight Cooling Pillows Queen Size Set of 2, Shredded Mem |
| Budget | `B0HKSGBMN7` | $35.49 | PB | Sweetnight | Sweetnight Gusseted Pillows King Size Set of 2,Fluffy Luxury |
| Runner-up | `B0HN1YQYY6` | $31.99 | PB | Sweetnight | Sweetnight Gusseted Pillows Standard Size Set of 2, Luxury H |
| Worth a look | `B0HMWQDHMZ` | $31.99 | PB | Sweetnight | Sweetnight Gusseted Pillows Standard Size Set of 2, Luxury H |

### `best-tower-fans-for-bedroom` (2)

_Density shortfall 2/10 — listed honest admits only; do not invent ASINs to pad._

| Role | ASIN | Price | Net | Brand | Title (trunc) |
|------|------|-------|-----|-------|---------------|
| Top pick | `B0BVZFQ4DF` | $54.91 | PB | LEVOIT | Levoit Tower Fan for Bedroom, 28ft/s Fans that Blow Cold Air |
| Upgrade | `B0GGHX7HCY` | $169.99 | PB | Dreame | dreame Bladeless Tower Fan MF10 for Bedroom with 270° Spatia |

## Method

- ① Seaker ABA ASINs → PB `asins=` healthy track
- ② PB `brand_id` dig (Sweetnight/RESTCLOUD/FelixKing/Dowinx/Primy/HeroSet/LEVOIT/DREO/Dreame/…)
- ③ YP keyword on site 11767 — timed out; honest PB-only
- Mattress: multi-brand required (≥2); Sweetnight-only → reject shortlist
- Live CTA PB `?uid=fromsll`
- Independent from Lab shortlists
- No invented prices / was / % / gallery / specs

## Next

- Parent may launch CloudAgent apply draft PR (`published=false`) for scenes that passed density (≥4): **office-chairs-for-long-hours** + **pillows-for-stomach-sleepers**; optionally include tower shortlist (2) as stub or wait for supply.
- **Do not** scaffold mattresses-for-back-pain until multi-brand gate clears.
- User must say「部署上线」before merge/Live.

## Stamp

`moretop10 | P5b L1 fill | draft-pack | 2/4 density | /workspace/shared/mt10-p5b-fill-report-2026-10-24.md | next=CloudAgent apply | blockers=shortfall 2/4 (mattress brand_gate + tower 2/10)`
