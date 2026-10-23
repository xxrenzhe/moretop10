# P1b deep reviews (Top pick + Upgrade only)

**waiting_for_部署上线:** yes
**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live. Do not merge.
**Gemini:** not used (`GEMINI_API_KEY` unset; `site/scripts/gemini_review_write.py` is not in this repo).
**SoT:** landing taglines, titles, visible bullets, L2 price/score/stars/review counts, P1b scene inventory.

| Hub | Role | ASIN | Path |
| --- | --- | --- | --- |
| `/air-purifiers/best-air-purifiers-for-allergies/` | Top pick | `B0GXKSC38S` | `/air-purifiers/reviews/levoit-smart-pet-air-purifier-home/` |
| `/air-purifiers/best-air-purifiers-for-smoke/` | Upgrade | `B0GXKSC38S` | `/air-purifiers/reviews/levoit-smart-pet-air-purifier-home/` |
| `/air-purifiers/best-air-purifiers-for-bedrooms/` | Top pick | `B07X25BNBR` | `/air-purifiers/reviews/levoit-air-purifier-home-bedroom-small/` |
| `/air-purifiers/best-air-purifiers-for-dust/` | Top pick | `B07X25BNBR` | `/air-purifiers/reviews/levoit-air-purifier-home-bedroom-small/` |
| `/air-purifiers/best-air-purifiers-for-allergies/` | Upgrade | `B07X25BNBR` | `/air-purifiers/reviews/levoit-air-purifier-home-bedroom-small/` |
| `/air-purifiers/best-air-purifiers-for-mold/` | Top pick | `B0CXJ97TV1` | `/air-purifiers/reviews/mooka-air-purifier-home-bedroom-large/` |
| `/air-purifiers/best-air-purifiers-for-large-rooms/` | Top pick | `B0CXJ97TV1` | `/air-purifiers/reviews/mooka-air-purifier-home-bedroom-large/` |
| `/air-purifiers/best-air-purifiers-for-bedrooms/` | Upgrade | `B0CXJ97TV1` | `/air-purifiers/reviews/mooka-air-purifier-home-bedroom-large/` |
| `/air-purifiers/best-air-purifiers-for-mold/` | Upgrade | `B0F32TGRMR` | `/air-purifiers/reviews/dreame-air-purifier-pm20-home-large/` |
| `/air-purifiers/best-air-purifiers-for-large-rooms/` | Upgrade | `B0F32TGRMR` | `/air-purifiers/reviews/dreame-air-purifier-pm20-home-large/` |
| `/air-purifiers/best-air-purifiers-for-dust/` | Upgrade | `B0FS68R44C` | `/air-purifiers/reviews/dreame-pet-air-purifier-ap10-suck/` |
| `/air-purifiers/best-air-purifiers-for-smoke/` | Top pick | `B0F2G5DPJN` | `/air-purifiers/reviews/dreame-smart-air-purifier-pm10-home/` |
| `/humidifiers/best-humidifiers-for-babies/` | Top pick | `B0DF567NW8` | `/humidifiers/reviews/homvana-36l-cool-mist-humidifiers-bedroom/` |
| `/humidifiers/best-humidifiers-for-babies/` | Upgrade | `B0C369CCDY` | `/humidifiers/reviews/homvana-humidifier-large-room-7l-807ft/` |
| `/standing-desks/best-standing-desks-for-home-office/` | Top pick | `B0B68QSN6Y` | `/standing-desks/reviews/fezibo-60-x-30-inch-standing/` |
| `/standing-desks/best-standing-desks-for-home-office/` | Upgrade | `B0GD75Y6SC` | `/standing-desks/reviews/fezibo-63-x-37-inch-large/` |

## Unique paths (10)

1. `B0GXKSC38S` — `/air-purifiers/reviews/levoit-smart-pet-air-purifier-home/`
2. `B07X25BNBR` — `/air-purifiers/reviews/levoit-air-purifier-home-bedroom-small/`
3. `B0CXJ97TV1` — `/air-purifiers/reviews/mooka-air-purifier-home-bedroom-large/`
4. `B0F32TGRMR` — `/air-purifiers/reviews/dreame-air-purifier-pm20-home-large/`
5. `B0FS68R44C` — `/air-purifiers/reviews/dreame-pet-air-purifier-ap10-suck/`
6. `B0F2G5DPJN` — `/air-purifiers/reviews/dreame-smart-air-purifier-pm10-home/`
7. `B0DF567NW8` — `/humidifiers/reviews/homvana-36l-cool-mist-humidifiers-bedroom/`
8. `B0C369CCDY` — `/humidifiers/reviews/homvana-humidifier-large-room-7l-807ft/`
9. `B0B68QSN6Y` — `/standing-desks/reviews/fezibo-60-x-30-inch-standing/`
10. `B0GD75Y6SC` — `/standing-desks/reviews/fezibo-63-x-37-inch-large/`

## Skips

- No P1b hubs skipped. All 8 locked-batch hubs exist on main with density 10.
- No ASINs invented. Top pick + Upgrade come from `site/data/p1b-scene-inventory-2026-10-23.json`.
- 16 recommend slots map to 10 unique `/{cat}/reviews/{slug}/` files because some ASINs are Top pick or Upgrade on more than one hub. One article per ASIN.

## Quality bar

- Answer-first 2–4 sentences in `.review-summary`.
- 5–8 bounded facts in Key insights from shortlist/L2/P1b SoT only.
- H2s are purchase questions + Key insights + FAQ; cluster links match existing reviews.
- Day-two, who should skip, and why-this-slot are on every page.
- No invented specs, was/%, ratings, awards, or ASINs in visitor copy.
- Amazon `【】` PDP leftovers and `[BRACKET]` Amazon headings stripped from Pros/Cons.
- Type-06 FAQ: 4 product-specific questions; no lab-test FAQ; no price-snapshot FAQ.

## Honest limits

- Reviews reuse existing `/{cat}/reviews/{slug}/` HTML chrome, galleries, facts bars, and tracks.
- Shared ASINs keep one badge (first locked-batch Top pick, else Upgrade) and cluster-link every P1b hub they recommend.
- No live air-purifier card names mold. The MOOKA / PM20 pair uses HEPA, 0.1μm, and 2200 ft² language already on the cards.
- FEZIBO 63×37 follows the title (63×37), not a leftover 71×37 tagline.
- Full Top 10 reviews were not written. Scene hubs stay density-10 cards; recommend slots are two per hub.
