# Page-type taxonomy (types 01–21)

Canonical page classes for MoreTop10. FAQ rules for each type live in [`FAQ-BY-PAGE-TYPE.md`](FAQ-BY-PAGE-TYPE.md) — do not reuse one generic FAQ across types.

**Status:** inventory is mixed. Money hubs (01, 02, 04–06) are baked in `site/`. Types 07–11 are live on `/tv/` and **linked** from category related clusters but often not yet baked as HTML. Types 12–13 are thin. Type 18 is a `noindex` demo.

| ID | Type | Typical URL | Live today | FAQ |
| --- | --- | --- | --- | --- |
| 01 | Home | `/` | Yes | Yes — site-level visitor questions |
| 02 | Comparison | `/{cat}/comparison/` | Yes (21 cats) | Yes — buying criteria, not chart mechanics |
| 03 | Niche | `/{cat}/{niche}/` (e.g. `/robot-vacuums/pet-homes/`) | Linked; HTML often unpublished | Yes — top + bottom when the page exists |
| 04 | Category landing | `/{cat}/` | Yes (21 cats + `/tv/` hub) | Yes — category buying criteria |
| 05 | Reviews hub | `/{cat}/reviews/` | Yes | Omit (optional 0–2 only if unique) |
| 06 | Product review | `/{cat}/reviews/{slug}/` | Yes | Yes — product-specific ownership |
| 07 | Best-of | `/{cat}/best-*/`, `/tv/best-*` | `/tv/` yes; category URLs often 404 | Yes when the article exists |
| 08 | VS | `/{cat}/{a}-vs-{b}/` | Linked; HTML often unpublished | Yes when the article exists |
| 09 | Alternatives | `/{cat}/*-alternatives/`, `/tv/smart-tv-ad-alternatives/` | `/tv/` yes; category URLs often 404 | Yes when the article exists |
| 10 | Guide | `/{cat}/how-to-choose-*/`, `/tv/remove-smart-tv-ads/` | `/tv/` yes; category URLs often 404 | Yes when the article exists |
| 11 | How-to (procedural) | `/tv/adb-debloat-not-working/` and similar | `/tv/` yes | Yes — task questions only |
| 12 | Blog hub | `/blog/` | Yes, thin inventory | Omit until the hub has a real feed |
| 13 | Blog article | `/blog/{slug}/` | Thin (`how-we-pick-products` is type 20) | Optional; omit on methodology posts |
| 14 | Authors hub | `/authors/` | Yes | Omit |
| 15 | Author profile | `/authors/{slug}/` | Yes | Omit |
| 16 | Contact | `/contact/` | Yes | Omit |
| 17 | Partner | `/partner-with-us/` | Yes | Omit |
| 18 | Match | `/robot-vacuums-match/` | Yes (`noindex,follow` demo) | Yes — matching intent, not quiz-ops |
| 19 | About | `/about-us/` | Yes | Omit — no marketing FAQ |
| 20 | Methodology / advertising disclosure | `/blog/how-we-pick-products/`, About “Advertising disclosure”, top-bar disclosure | Yes | Omit — this **is** the destination for rank/commission/price-snapshot copy |
| 21 | Legal | `/privacy-policy/`, `/terms-of-use/`, `/cookie/`, `/cookie-policy/` | Yes | Omit |

## Notes

- **21 category landings** (type 04) are the density-10 shortlist hubs in `site/instances/moretop10.site.yaml`. `/tv/` is an editorial cluster, not a density-10 category.
- **Niche (03)** is a use-case slice (pets, indoor, basement), not a second copy of the category landing. Kids Bikes is type 04, not 03.
- **Type 20 vs 13:** `/blog/how-we-pick-products/` is methodology. Do not give it a buyer-intent FAQ.
- FAQPage JSON-LD and visible FAQ must stay in lockstep — see the FAQ spec.
