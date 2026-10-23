# P1a deep reviews (Top pick + Upgrade only)

**waiting_for_部署上线:** yes
**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live. Do not merge.
**Gemini:** not used (`GEMINI_API_KEY` unset; `site/scripts/gemini_review_write.py` is not in this repo).
**SoT:** landing taglines, titles, visible bullets, L2 price/score/stars/review counts, P1a scene inventory.

| Hub | Role | ASIN | Path |
| --- | --- | --- | --- |
| `/dehumidifiers/best-dehumidifiers-for-basements/` | Top pick | `B0C9THG48W` | `/dehumidifiers/reviews/waykar-80-pints-2025-energy-star/` |
| `/dehumidifiers/best-dehumidifiers-for-basements/` | Upgrade | `B0D1C6HWFF` | `/dehumidifiers/reviews/aeocky-5500-sqft-energy-star-most/` |
| `/air-purifiers/best-air-purifiers-for-pets/` | Top pick | `B0GXKSC38S` | `/air-purifiers/reviews/levoit-smart-pet-air-purifier-home/` |
| `/air-purifiers/best-air-purifiers-for-pets/` | Upgrade | `B0FS68R44C` | `/air-purifiers/reviews/dreame-pet-air-purifier-ap10-suck/` |
| `/robot-vacuums/pet-homes/` | Top pick | `B0FK2HPNCB` | `/robot-vacuums/reviews/eufy-e25-robot-vacuum-mop-combo/` |
| `/robot-vacuums/pet-homes/` | Upgrade | `B0GGRTD2ZY` | `/robot-vacuums/reviews/roborock-2026-new-qrevo-s-pro/` |

## Six ASINs

1. `B0C9THG48W` — `/dehumidifiers/reviews/waykar-80-pints-2025-energy-star/`
2. `B0D1C6HWFF` — `/dehumidifiers/reviews/aeocky-5500-sqft-energy-star-most/`
3. `B0GXKSC38S` — `/air-purifiers/reviews/levoit-smart-pet-air-purifier-home/`
4. `B0FS68R44C` — `/air-purifiers/reviews/dreame-pet-air-purifier-ap10-suck/`
5. `B0FK2HPNCB` — `/robot-vacuums/reviews/eufy-e25-robot-vacuum-mop-combo/`
6. `B0GGRTD2ZY` — `/robot-vacuums/reviews/roborock-2026-new-qrevo-s-pro/`

## Quality bar

- Answer-first 2–4 sentences in `.review-summary`.
- 5–8 bounded facts in Key insights from shortlist/L2/P1a SoT only.
- H2s are purchase questions + Key insights + FAQ; cluster links match existing reviews.
- Day-two, who should skip, and why-this-slot are on every page.
- No invented specs, was/%, ratings, awards, or ASINs in visitor copy.
- Amazon `【】` PDP leftovers removed from Pros/Cons and glance.
- Type-06 FAQ: 4 product-specific questions; no lab-test FAQ; no price-snapshot FAQ.

## Honest limits

- Reviews reuse existing `/{cat}/reviews/{slug}/` HTML chrome, galleries, facts bars, and tracks.
- E25 is Top pick on `/robot-vacuums/pet-homes/` and remains the mopping Upgrade on the category landing.
- Qrevo S Pro badge is Upgrade for the niche (was Rank 7 leftover).
- Full Top 10 reviews were not written. Scene hubs stay density-10 cards; recommend slots are two.
