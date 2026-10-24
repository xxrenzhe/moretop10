# Visitor-copy batch scrub — 2026-10-24

**waiting_for_部署上线=yes · baked?=yes · no Live deploy**

Lab handoff: `mt10-handoff-visitor-copy-2026-10-24.md` + `visitor-copy-daily-2026-10-24.md` + `true-leaks.json`.

## Root cause of #47 regression

#47 scrubbed baked HTML via `seo_geo.py` `rewrite_visible_jargon`. Later comparison snapshot refreshes (stamp floors / day-add) wrote Live apex HTML — and Live was never deployed with the #47 tip — so Draft card / completeness gate / inventory-blocked came back.

This tip:

- Extends the same rewriter (SoT) for today’s leftover classes
- Re-applies it to baked `site/` **without** a full Live refetch
- Runs rewrite as the last `bake_page` write so a future Live snapshot cannot skip the scrub
- Fixes `bake_tv.py` + `tv-supported-models.json` so a TV rebake does not re-emit `content-only` / `help centre` / retailer-confirm

## Patterns (visitor body)

| Class | Live audit | Baked `site/` after this tip | Visitor English |
|---|---:|---:|---|
| kids-bikes `Draft card` / `PartnerBoost` / `Mac L2` / `Mac CDP` / `L2 In Stock` | comparison + niche pages | 0 | retailer-confirm line; cards kept |
| `completeness gate` | ~125 | 0 | “We only publish products with a title, gallery, and price snapshot.” |
| `inventory-blocked` | ~42 | 0 | “We keep the category unpublished until we can fill ten honest cards.” |
| `confirm on the retailer page` | ~120 | 0 | “Always double-check price and stock on Amazon before you buy” |
| TV `Content-only` | 2 | 0 | “editorial-only until a buy link is ready” |
| UK `centre` | 1 (`/tv/supported-android-tv-models/`) | 0 | center |

Affiliate `pboost.me?uid=fromsll` and `yeahpromos.com` stay. `<time datetime>` stays. JSON-LD Offer / sku stay (Layer A strips scripts). No invented was/%/prices/products.

## Not in this batch

- `/about/` `/faq/` `/disclosure/` — Live **404**; no local pages; not touched
- Full `apply_hub_page` (cite strip / buyer FAQ swap) — out of scope; copy-only
- Merge / `wrangler deploy` / Cloudflare

## Gate

```
python3 tests/visitor_copy_unit.py      # exit 0
python3 tests/visitor_copy_assert.py    # exit 0 (434 files)
```

Kids-bikes comparison stamps still `As of` / `Last Updated` / `Checked` **2026-10-24**.
