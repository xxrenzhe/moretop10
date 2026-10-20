# MoreTop10 SEO/GEO P0 local bake — 2026-10-20

**Bake ≠ Deploy.** This PR bakes static HTML in `site/` only. Do **not** wrangler-deploy, swap DNS, or ping IndexNow until the user explicitly says **「部署上线」** and the MT10 Cloudflare token is used (one site, one token).

Facts baseline: fleet strategy + four-site inventory (2026-10-20). Live apex `moretop10.com`, density 10, PB affiliate.

---

## Before (Live / pre-bake)

| Item | Live fact |
|------|-----------|
| Category hub `/{cat}/` JSON-LD | `WebPage` + `Organization` + `BreadcrumbList` only. **No ItemList / Product / Offer / FAQPage / Speakable.** Comparison + review pages were richer. |
| `/authors/` | **404**. Seven child URLs in sitemap (`/authors/{slug}/`). Breadcrumb “Authors” pointed at `/authors/moretop10-editors/`. |
| `llms.txt` | ~17KB, comparison-centric. No Methodology block, no hub URLs, no `#geo-{ASIN}` top-pick anchors. Contained `uid=fromsll` / `aff_pb_autoads`. `/.well-known/llms.txt` **404**. |
| `robot-vacuums-match/` | Indexed (`index,follow`), in sitemap, home tile “Find Your Match” skipped `/robot-vacuums/`. Demo quiz + “publishable shortlist” jargon. Not a real extra category. |
| G-IL Compare CTA | Many non-home pages hard-linked **robot-vacuums comparison**, including kids-bikes comparison (self-type / wrong cat). |
| Visitor FAQ | Hub intros still said “completeness-gated” / “completeness gate”. Match page said “publishable”. |
| `robots.txt` | AI bots already Allow. **No** `Content-Signal` line. |

---

## After (this local bake)

Generator: `python3 site/scripts/build.py` (chrome + new `site/scripts/seo_geo.py`). Products/ASINs/prices copied from Live comparison `data-asin` + hub picks — **nothing invented**. **No `AggregateRating`.**

| Item | Local result |
|------|----------------|
| 21 category hubs | `CollectionPage` + `ItemList` (`numberOfItems` = rendered picks, typically 10) + nested `Product` + `Offer` (price/ASIN only when present on Live cards) + `FAQPage` (from `.landing-faq`, not nav `<details>`) + `SpeakableSpecification` (`.geo-answer-first`, `.landing-faq`) + cite strip. `#geo-{ASIN}` anchors on picks. |
| `/authors/` | **200** listing of 7 editors with links to `/authors/{slug}/`. `CollectionPage` + `ItemList`. Footer “Editors” → `/authors/`. Hub added to `sitemap.xml`. |
| `llms.txt` + `/.well-known/llms.txt` | Dual 200, identical (~24KB). Methodology, primary hubs, authors, Top-pick `#geo-{ASIN}` (21 cats when ASIN known). Backend uid / `aff_pb_autoads` stripped. Existing BoFu URLs kept from Live llms (not invented). |
| `robot-vacuums-match/` | Kept as **demo in the robot-vacuums cluster** (not a new category). `noindex,follow`, canonical → `/robot-vacuums/`, **removed from sitemap**. Hub related cluster links the quiz. Home tile “Find Your Match” → **Browse category** `/robot-vacuums/`. |
| Compare picks CTA | Context-aware: hub/reviews → `/{cat}/comparison/`. Comparison pages that had a CTA now go to **Category overview** `/{cat}/` (no self-link). Live air-fryers comparison already omitted the header CTA — left omitted. Mega/footer still list **all 21** published landings. |
| Visitor FAQ | Jargon scrub on FAQ + visible copy: no `publishable` / `inventory-blocked` / `completeness gate` / `PartnerBoost` in hub FAQs. American plain English. |
| `robots.txt` | Existing AI Allow table kept; added `Content-Signal: search=yes, ai-input=yes, ai-train=no`. |

### Local smoke (this run)

```bash
python3 site/scripts/build.py          # verify ok
python3 tests/seo_geo_p0_assert.py     # ok
node tests/pc-card-layout-assert.mjs   # ok (layout regression unchanged)

python3 -m http.server 8765 --directory site
# curl http://127.0.0.1:8765/air-fryers/          → 200, ItemList n=10, Product+Offer, sku B0GLX9TGJV
# curl http://127.0.0.1:8765/authors/             → 200, H1 “Our editors”
# curl http://127.0.0.1:8765/llms.txt             → 200, #geo- anchors
# curl http://127.0.0.1:8765/.well-known/llms.txt → 200, same body
# curl http://127.0.0.1:8765/robot-vacuums-match/ → 200 + noindex,follow
# curl http://127.0.0.1:8765/sitemap.xml          → has /authors/, no match, no /search/
```

No wrangler / CF deploy was run.

---

## Pending deploy list (blocked until 「部署上线」)

Use **MoreTop10’s own CF token only**. Do not reuse Lab or RatingsRoom tokens.

1. Review this draft PR; do not merge until a human is ready to ship HTML.
2. After explicit **「部署上线」**: deploy the baked `site/` tree to `moretop10.com` with the MT10 token (worker/pages as this site already ships). **Bake ≠ Deploy.**
3. Live curl:
   - `https://moretop10.com/authors/` → 200
   - `/{cat}/` JSON-LD contains ItemList + Product, **no AggregateRating**
   - `https://moretop10.com/.well-known/llms.txt` → 200, matches `/llms.txt`
   - `https://moretop10.com/robot-vacuums-match/` → `noindex,follow` + canonical hub
   - `robots.txt` includes Content-Signal; sitemap has `/authors/`, omits match + `/search/`
4. IndexNow (MT10 key only) + GSC URL inspection for `/authors/` and a sample of 21 hubs.
5. Human **G-GEO-CF**: Cloudflare AI Crawl Control / WAF must still Allow OAI-SearchBot, PerplexityBot, Claude-SearchBot, Googlebot, Bingbot.
6. Not in this PR: OpenSEO project bind, monthly GEO probe table, comparison `Thing`→`Product` already applied locally on baked comparison HTML but Live will only change after deploy.

---

## Out of scope / leftover Live issues (not blockers for P0)

- Hub FAQs still include a generic “automated dock” question on non-vacuum cats (Live copy; not invented here).
- Some comparison templates never rendered a header Compare CTA; those stay CTA-less (compliant: no self-link).
- Next.js `src/` ConsumerVoice clone is unused by this SSG bake.
- OfferLuck / RatingsRoom / Lab P0 items are other repos.
