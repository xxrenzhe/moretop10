# P2 MT10 greenfield inventory (2026-10-23)

**waiting_for_部署上线:** yes
**Scope:** MoreTop10 draft only. No Lab / RR / OL. No Cloudflare Live deploy.
**Do not touch:** ceramic P1c #40 files, blog hub, authors CSS (beyond coexistence).

## /pillows/

- Type: new plural main category (landing + comparison + reviews hub)
- Density: 0 (honest shortfall; not padded to 10)
- Comparison order: (none)
- Top pick: none
- Upgrade: none
- New reviews: none (MT10 review articles do not exist)
- Tracks: none
- Sources checked: in-repo shortlists; live moretop10.com/data; public Lab/RR/OL shortlist JSON. All 404 or empty for this slug.

## /pillows/best-pillows-for-neck-pain/

- Scene: best pillows for neck pain
- Density: 0 (scene page exists; no cards to reorder)
- Top pick: none — review skipped
- Upgrade: none — review skipped
- New reviews: none
- Tracks: none

## /mattresses/

- Type: new plural main category (landing + comparison + reviews hub)
- Density: 0 (honest shortfall; not padded to 10)
- Comparison order: (none)
- Top pick: none
- Upgrade: none
- New reviews: none (MT10 review articles do not exist)
- Tracks: none
- Sources checked: in-repo shortlists; live moretop10.com/data; public Lab/RR/OL shortlist JSON. All 404 or empty for this slug.

## /mattresses/best-mattresses-for-side-sleepers/

- Scene: best mattresses for side sleepers
- Density: 0 (scene page exists; no cards to reorder)
- Top pick: none — review skipped
- Upgrade: none — review skipped
- New reviews: none
- Tracks: none

## /office-chairs/

- Type: new plural main category (landing + comparison + reviews hub)
- Density: 0 (honest shortfall; not padded to 10)
- Comparison order: (none)
- Top pick: none
- Upgrade: none
- New reviews: none (MT10 review articles do not exist)
- Tracks: none
- Sources checked: in-repo shortlists; live moretop10.com/data; public Lab/RR/OL shortlist JSON. All 404 or empty for this slug.

## /office-chairs/best-office-chairs-for-back-pain/

- Scene: best office chairs for back pain
- Density: 0 (scene page exists; no cards to reorder)
- Top pick: none — review skipped
- Upgrade: none — review skipped
- New reviews: none
- Tracks: none

## /water-flossers/

- Type: new plural main category (landing + comparison + reviews hub)
- Density: 0 (honest shortfall; not padded to 10)
- Comparison order: (none)
- Top pick: none
- Upgrade: none
- New reviews: none (MT10 review articles do not exist)
- Tracks: none
- Sources checked: in-repo shortlists; live moretop10.com/data; public Lab/RR/OL shortlist JSON. All 404 or empty for this slug.

## /water-flossers/best-water-flossers-for-braces/

- Scene: best water flossers for braces
- Density: 0 (scene page exists; no cards to reorder)
- Top pick: none — review skipped
- Upgrade: none — review skipped
- New reviews: none
- Tracks: none

## Shortfalls (honest)

- Density is 0 healthy PB fromsll cards per category, not a padded Top 10. No invented ASINs, prices, images, or was/%.
- PARTNERBOOST_API_TOKEN is unset in this environment, so get_fba_products was not used to invent a catalog.
- Accessories (pillowcases, mattress toppers, chair mats/casters, flosser tips-only) stay excluded.
- Reviews: skipped. Existing type-07 chrome does not require new review HTML when reviews do not exist.
- Lab `/shortlists/*` paths from the locked batch are out of scope (MT10 draft only).
- `robots` stays `index,follow` to match live type-07. The deploy gate is the draft PR + `waiting_for_部署上线=yes`. Do not Cloudflare Live deploy.
