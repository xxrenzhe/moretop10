# Visitor-copy batch scrub — 2026-10-23

**waiting_for_部署上线=yes · baked?=yes · no Live deploy**

Lab handoff: `mt10-handoff-visitor-copy-2026-10-23.md` + `visitor-copy-daily-2026-10-23.md` + `findings__mt10.json`.  
Fix at bake source (`site/scripts/seo_geo.py` `JARGON_PATTERNS` / `rewrite_visible_jargon`), not one-off baked HTML. Density rules unchanged. Lab / RatingsRoom / OfferLuck untouched.

The sentence rewriter landed on main in #35 (chrome + kids-bikes + US English) and #44 (TV / Snapshot $ / residual ASIN). Live `moretop10.com` still serves the pre-scrub snapshot — this draft does not deploy it.

## Patterns (visitor body)

| Class | Live audit (Lab) | Baked `site/` after this tip | Visitor English |
|---|---:|---:|---|
| `completeness gate` | ~305 pages | 0 | “We only publish products with a title, gallery, and price snapshot.” |
| `inventory-blocked` | ~42 pages | 0 | “We keep the category unpublished until we can fill ten honest cards.” |
| kids-bikes `PartnerBoost` / `Mac L2` / `Draft card…` | ~13 pages | 0 | “Confirm current specs, stock, and returns on the retailer page.” |
| kids-bikes `Mac CDP` | ~6 pages | 0 | same retailer-confirm line (no invented why-copy) |
| `whilst` / `towards` / `Utilize` | 3 + 1 + 1 | 0 | while / toward / Use |

Affiliate `pboost.me?uid=fromsll` and `yeahpromos.com` hostnames stay. `<time datetime>` stays. Product-copy “Utilizes …” stays. JSON-LD Offer / sku / Speakable stay.

## Sample URLs (Live still leaks until 部署上线)

Chrome methodology:

- https://moretop10.com/air-fryers/
- https://moretop10.com/air-fryers/comparison/
- https://moretop10.com/air-fryers/reviews/cosori-iconic-stainless-steel-air-fryer/
- https://moretop10.com/about-us/

Kids-bikes (cards kept — each already has title, gallery, price snapshot, Check price; leak was the L1/L2 sentence):

- https://moretop10.com/kids-bikes/
- https://moretop10.com/kids-bikes/best-balance-to-pedal-kids-bikes/
- https://moretop10.com/kids-bikes/comparison/
- https://moretop10.com/kids-bikes/reviews/royalbaby-ez-kids-bike-12-20-inch/

US English:

- https://moretop10.com/litter-boxes/ (PETKIT reviews: whilst → while)
- https://moretop10.com/espresso-machines/premium-espresso-machine-alternatives/ (towards → toward)
- https://moretop10.com/humidifiers/best-humidifiers-for-bedrooms/ (Utilize → Use)

## This PR

Handoff classes 1–3 were already rewritten on main (#35). This tip:

- Stops P1/P2 bakers from re-emitting ops copy: `Snapshot price` / `Snapshot $` / `healthy tracks` / `invent ASINs` in `bake_p1a` / `bake_p1b` / `bake_p1c` / `bake_p2`.
- Extends `seo_geo.py` so those leftovers rewrite to visitor English (price kept; “verified retailer link”).
- Rebaked the unpublished P1/P2 pages that still had the leftovers (scene best-of + ceramic / mattresses / office-chairs / pillows / water-flossers hubs).
- Wires `visitor_copy_assert.collect_errors()` into bake `verify()` (body only — `ld+json` stripped, matching #44).

Not a full Live refetch — that would smash unpublished P1/P2/P3 drafts that are not on apex.

Baked `site/` after this tip: **371 HTML pages, 0 visitor-body leak pages**. Approved chrome phrases present on **251** pages (`PUBLISH_RULE`) and **21** pages (`UNPUBLISHED_UNTIL_TEN`). Kids-bikes draft-card replacement on **15** pages (`RETAILER_CONFIRM`).

## Residual risks

- Apex is stale until someone says「部署上线」and ships this tip (or current main, which already has the HTML scrub).
- Future inventory generators that emit jargon still need `rewrite_visible_jargon` on write. Bake verify now catches a miss.
- Do not treat JSON-LD Speakable/FAQPage, alliance track URLs, or “amplifier on the desk” product copy as leaks.

## Gate

- Draft PR only — do not merge, do not `wrangler deploy`, do not touch Cloudflare.
