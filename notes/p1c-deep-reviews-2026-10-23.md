# P1c deep reviews (Top pick + Upgrade only)

**waiting_for_部署上线:** yes
**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live. Do not merge.
**Gemini:** not used (`GEMINI_API_KEY` unset; `site/scripts/gemini_review_write.py` is not in this repo).
**SoT:** shortlist/L2/landing titles, bullets, prices, scores, and P1c ceramic inventory.
**Tip:** `p1c-ceramic-inventory-2026-10-23` SHA-256 `f23596ced1a4681996736db1baa01e242680e01b79ebb6357a0b9edecef3307d`.

| Hub | Role | ASIN | Path |
| --- | --- | --- | --- |
| `/ceramic-space-heaters/` | Top pick | `B0C6FFK1GV` | `/ceramic-space-heaters/reviews/dreo-space-heater-portable-electric-remote/` |
| `/ceramic-space-heaters/` | Upgrade | `B097RG67QB` | `/ceramic-space-heaters/reviews/dreo-atom-one-space-heater-thermostat/` |
| `/ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/` | Top pick | `B095PP1GZR` | `/ceramic-space-heaters/reviews/dreo-space-heaters-indoor-thermostat-1500w/` |
| `/ceramic-space-heaters/best-ceramic-space-heaters-for-large-rooms/` | Upgrade | `B097RG67QB` | `/ceramic-space-heaters/reviews/dreo-atom-one-space-heater-thermostat/` |
| `/ceramic-space-heaters/best-ceramic-space-heaters-for-garages/` | Top pick | `B097RG67QB` | `/ceramic-space-heaters/reviews/dreo-atom-one-space-heater-thermostat/` |
| `/ceramic-space-heaters/best-ceramic-space-heaters-for-garages/` | Upgrade | `B095PP1GZR` | `/ceramic-space-heaters/reviews/dreo-space-heaters-indoor-thermostat-1500w/` |

## Unique paths (3)

1. `B0C6FFK1GV` — `/ceramic-space-heaters/reviews/dreo-space-heater-portable-electric-remote/`
2. `B097RG67QB` — `/ceramic-space-heaters/reviews/dreo-atom-one-space-heater-thermostat/`
3. `B095PP1GZR` — `/ceramic-space-heaters/reviews/dreo-space-heaters-indoor-thermostat-1500w/`

## Skips

- No P1c hubs skipped. Category + large-rooms + garages exist on main with honest density 4.
- No deep review for Best-value Gold `B0C6FCKQML`. Review default is Top pick + Upgrade only.
- No ASINs invented. Slots come from the Live tip inventory `p1c-ceramic-inventory-2026-10-23`.
- 6 recommend slots map to 3 unique `/{cat}/reviews/{slug}/` files. One article per ASIN.

## Quality bar

- Answer-first 2–4 sentences in `.review-summary`.
- 5–8 bounded facts in Key insights from shortlist/L2/P1c SoT only.
- H2s are purchase questions + Key insights + FAQ; cluster links match sibling reviews.
- Day-two, who should skip, and why-this-slot are on every page.
- No invented specs, was/%, ratings, awards, or ASINs in visitor copy.
- Amazon `【】` PDP leftovers stripped from Pros/Cons and glance (no glance leftover shipped).
- Type-06 FAQ: 4 product-specific questions; no lab-test FAQ; no price-snapshot FAQ.

## Honest limits

- Ceramic had no existing review HTML. Chrome is cloned from the humidifier bedroom template, then leftover humidifier JSON-LD is stripped and depth-3 chrome prefixes (`favicon` / CSS / logo / Categories / blog / footer legal) are rewritten to `../../../` without touching review-main `../../comparison/` links. Gallery and facts bar reuse the one SoT packshot and the live `pboost.me?uid=fromsll` track. Extra gallery thumbs were not invented.
- Shared ASINs keep one badge (category Upgrade for Atom One; first Top pick for the other two) and cluster-link every P1c hub they recommend.
- Full Top 4 / Top 10 reviews were not written. Hubs stay density 4; recommend slots are two per hub.
