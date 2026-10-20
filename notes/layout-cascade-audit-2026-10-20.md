# Comparison product-card overlap — root cause + site-wide audit

Date: 2026-10-20. Live CSS load order: `tokens.css` → `site.css` → `pages-*.css`.
Do not wrangler deploy from this PR. Parent ships after 「部署上线」.

## Root cause

Pre-Wave2, one stylesheet set `.pc-main{display:flex}` then later `display:grid` + `grid-template-areas`. Grid won.

After the Wave2 split:

| File | Loads | What it declared (Live, broken) |
| --- | --- | --- |
| `site.css` | earlier | `@media (min-width:768px){.pc-main{display:grid; grid-template-areas:"pc-left pc-mid pc-right" "pc-foot pc-foot pc-foot"; …}}` plus `grid-area` on children |
| `pages-comparison.css` | **later** | unscoped `.pc-main{display:flex;flex-direction:column}` and at `@768` **only** `flex-direction:row` — never `display:grid` |

`display` specificity is equal. Later file wins, so desktop computed `display:flex`. `grid-area` on `.pc-left/.pc-mid/.pc-right/.pc-footer` is ignored. The four children sit in one nowrap flex row. `.pc-footer{width:100%}` + `.pc-mid{flex:1;min-width:0}` shrinks mid to ~0. Title overflows onto score / stars / `$209.99`. Pros wrap one word per line.

Evidence (Live before this PR):

- `pages-comparison.css` L27: `.pc-main{…display:flex;flex-direction:column…}`
- `pages-comparison.css` L28: `@media (min-width:768px){.pc-main{flex-direction:row;…}}` — no `display`
- `site.css` (near file end): `@768 .pc-main{display:grid; grid-template-areas:"pc-left pc-mid pc-right" "pc-foot pc-foot pc-foot"}`

## Fix (this PR)

1. **SoT** for desktop `.pc-main` is `pages-comparison.css` (last sheet): `@768 { display:grid; areas; columns 200px | minmax(0,1fr) | 168px; footer row pc-foot }`.
2. **Removed** the conflicting `display:grid` + areas block from earlier `site.css` so the split cannot invert again.
3. Mobile stays `display:flex; flex-direction:column`.
4. Guard: `tests/pc-card-layout-assert.mjs`.

## Blast radius — 22 comparison/niche pages, one CSS fix

Same chrome: `article.product-card > .pc-main` + `pages-comparison.css`.

**20 Live sitemap `/{category}/comparison/`:**

air-fryers, air-purifiers, bluetooth-speakers, computer-speakers, cordless-vacuums, dash-cams, dehumidifiers, espresso-machines, hair-dryers, humidifiers, litter-boxes, massage-guns, noise-cancelling-headphones, projectors, robot-vacuums, security-cameras, standing-desks, tower-fans, video-doorbells, wet-dry-vacuums.

**2 niche templates** (same `pages-comparison.css` / `.pc-main` chrome; not in today’s sitemap, 404 on Live as HTML but still in the generator set): pet-homes/comparison, indoor-comparison.

All 22 are fixed by this CSS. No HTML churn.

## Site-wide scan (same class of bug)

Scanned Live sheets: `tokens.css`, `site.css`, `pages-comparison.css`, `pages-home.css`, `pages-landing.css`.
Scanned page types: home, `/{cat}/`, `/{cat}/comparison/`, `/{cat}/reviews/`, review slug, vs/how-to articles, match, blog, about, contact.

| Surface | Sheets | Cross-file flex-over-grid on layout parent? |
| --- | --- | --- |
| `.pc-main` product cards | site + pages-comparison | **Yes — only hit. Fixed.** |
| `.top3-card` / `.sug-card` | pages-comparison only | No. Flex throughout. |
| `.cmp-glance` | site + pages-comparison | Grid/minmax only; no flex override. |
| `.home-tile*` | pages-home (+ site `!important` expand) | No `.pc-main`. Grid/flex by variant, same file. |
| `.explore-mini-card` | pages-home | Flex column only. |
| `.landing-pick*` / review hero | pages-landing | No `.pc-main`. |
| `.match-choice-card` | pages-landing | Same-file grid then flex (intentional restyle). |
| `.bestof-visit-main` | pages-landing | Grid only. |

Home / landing / vs / review hubs **unaffected** (no `.pc-main`).

## Residual

- Stale `@768 .pc-main{align-items:center}` in `site.css` (~L618) is overridden by the later page-sheet `align-items:stretch`. Harmless; leave unless a later pass cleans Wave1 leftovers.
- `pages-comparison.css` still has stacked historical `@768` gap/padding tweaks; the trailing SoT block wins.
- Other brands’ repos (if they copied the Wave2 split) need the same SoT move. This PR is moretop10 only.
- **No Live deploy in this PR.**

## Verify

```bash
node tests/pc-card-layout-assert.mjs
# optional: open site/fixtures/comparison-card.html at 1280 and 375
```

Before: espresso-machines/comparison card #1 title / `8.8` / stars / `$209.99` overlapping; pros one-word column.
After: image | title+pros | score+price; footer full-width; mobile stacked, no overlap.
