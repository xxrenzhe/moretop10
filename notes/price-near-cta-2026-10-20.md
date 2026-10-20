# Comparison cards — price next to Check price, above the divider

Date: 2026-10-20. Do not wrangler deploy from this PR. Parent ships after 「部署上线」.

## Answer

Yes. `$629.99` + `Checked 2026-10-17` is a purchase-decision cue and belongs next to the yellow Check price CTA. The purple score stays top-right.

Desktop follow-up: price must sit **above** the footer `border-top`, not in `.pc-footer`. Putting it under the divider stacked it on the CTA and stretched the card.

## DOM (fixture contract; no `build.py` in this clone)

```
.pc-main
  .pc-left
  .pc-mid
  .pc-right
    .pc-score-block > .pc-score-row     → 8.8 / stars / Very good (top-right)
  .pc-price-decision                    → $n + Checked YYYY-MM-DD (above divider)
  .pc-footer
    .pc-secondary-link                  → Read review
    .product-cta.btn-cta-yellow         → Check price
```

Do **not** nest `.pc-price-decision` in `.pc-score-block` or `.pc-footer`.

## CSS (desktop ≥768, SoT in `pages-comparison.css`)

```
grid-template-areas:
  "pc-left pc-mid pc-right"
  "pc-left pc-mid pc-price"
  "pc-foot pc-foot pc-foot";
grid-template-rows: minmax(0,1fr) auto auto;
```

- `.pc-price-decision { grid-area: pc-price; justify-self: end; }` — right-aligned onto the 147px CTA, **above** the line.
- `.pc-footer { border-top; align-items: center; }` — one short row: Read review | Check price.

Mobile: flex column; price `align-self: flex-end` so it stays on the CTA side; footer still one row.

Unchanged: affiliate hrefs (fixture `#`), price strings, Checked day-only `YYYY-MM-DD`, yellow CTA, purple score.

## Verify

```bash
node tests/pc-card-layout-assert.mjs
python3 -m http.server 4173 --directory site
# http://127.0.0.1:4173/fixtures/comparison-card.html  (1280 desktop / 375 mobile)
```

Live after bake: `/robot-vacuums/comparison/` card #2 (eufy E25).
