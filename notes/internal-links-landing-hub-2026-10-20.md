# Internal links: category landings as first-class money URLs

Date: 2026-10-20. Do not wrangler-deploy from this PR.

## Problem

`/{slug}/` landings (including new/extended `kids-bikes`) were orphans:

- Non-home Compare / Reviews megas pointed only at `comparison/` and `reviews/`
- Footer Explore was a hand-picked subset (no kids-bikes)
- Home tile grid hid everything after the first 8 behind `is-more` / Show more — `kids-bikes` sat at slot 21
- `reviews/` hubs linked breadcrumb + foot to comparison, not the landing. Comparison already had some “Category overview” copy on Live; reviews did not.

Home header stays Top10-simple (About / Partner). That is unchanged.

## SoT

This GitHub clone does not ship the full inventory generator. Chrome + landing-hub links are now baked by:

- `site/scripts/build.py`
- `site/scripts/chrome.py`
- `site/scripts/site_config.py` → `load_site_config` / `ALL_CATS` = MVP + NON_MVP
- `site/instances/moretop10.site.yaml`

Product cards / ASINs are copied from Live snapshots. Nothing is invented here.

## Rules

1. **Desktop mega (non-home):** Under Compare, every `ALL_CATS` row is `{name} overview` → `/{slug}/` plus Compare → `/{slug}/comparison/`. Reviews mega still lists review hubs. Same pairing in mobile Compare `<details>`.
2. **Footer:** Explore/Categories column lists **all** `ALL_CATS` landings (plus Home / Blog / Sitemap). No curated short list.
3. **Home grid:** tiles with `tier: extended` or `published` are pinned to the front; `is-more` still applies when `i >= home_visible_tiles` (8). `kids-bikes` is `tier: extended`, so it is tile 0 — not slot 11 behind Show more.
4. **Hub reciprocity:** `comparison/` and `reviews/` get a Related cluster (`Category overview` / `Full guide` → `../`). Reviews breadcrumb + foot also point at the landing.

## Verify

```bash
python3 site/scripts/build.py
```

Checks (also asserted at the end of the bake):

- `site/index.html`: kids-bikes tile has **no** `is-more` and is in the first 8
- `site/about-us/index.html` header mega contains `kids-bikes/` (landing), not only comparison/reviews
- Home + sitewide footer contain a kids-bikes landing href
- `site/kids-bikes/comparison/index.html` and `site/kids-bikes/reviews/index.html` link to `../` (landing)
