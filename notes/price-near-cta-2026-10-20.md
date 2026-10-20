# Comparison cards — price next to Check price

Date: 2026-10-20. Do not wrangler deploy from this PR. Parent ships after 「部署上线」.

## Answer (user screenshot, eufy E25)

Yes. `$629.99` + `Checked 2026-10-17` is a purchase-decision cue and belongs next to the yellow Check price CTA. The purple score (8.8 / stars / Very good) stays top-right.

## Before

Live `/robot-vacuums/comparison/` (and the overlap-fix fixture) nested price inside the score column:

```
.pc-right > .pc-score-block
  .pc-score-row     → 8.8 + stars + Very good
  .pc-price-decision → $629.99 / Checked YYYY-MM-DD
.pc-footer
  Read review (left) | Check price (right)
```

A CSS-only tuck (`align-self:start` / `justify-content:flex-start` on `.pc-right`) parked price under the score and left a large empty gap above the footer CTA. Price and Check price were not adjacent.

`site/scripts/build.py` is **not in this clone** (static fixture + CSS only). Live bake still emits the old nesting; this PR is the HTML contract bake should copy.

## After

```
.pc-right > .pc-score-block > .pc-score-row     → score stays top-right
.pc-footer
  .pc-secondary-link                            → Read review, left
  .pc-footer-buy
    .pc-price-decision                          → $n / Checked YYYY-MM-DD
    .product-cta.btn-cta-yellow                 → Check price
```

Desktop: score top-right in `.pc-right`. Footer is full-width; Read review left-aligned to the CTA baseline; price stacked immediately above the 147px yellow button on the right.

Mobile: same footer cluster (price above CTA, right); score still its own row; no overlap with the title.

Unchanged: affiliate hrefs (fixture uses `#`), price strings, Checked day-only `YYYY-MM-DD`, brand yellow CTA, purple score.

## Verify

```bash
node tests/pc-card-layout-assert.mjs
# or: npm run test:pc-card-layout
```

Local chrome (this clone has no `/robot-vacuums/` Next route; Live comparison is `/robot-vacuums/comparison/`):

```bash
python3 -m http.server 4173 --directory site
# open http://127.0.0.1:4173/fixtures/comparison-card.html
# desktop ~1280px: card #2 eufy E25 — price sits on the CTA, score stays top-right
# mobile ~375px: same adjacency, no title/score overlap
```

On Live after bake: `/robot-vacuums/comparison/` card #2 (eufy E25, `$629.99`, `Checked 2026-10-17`).
