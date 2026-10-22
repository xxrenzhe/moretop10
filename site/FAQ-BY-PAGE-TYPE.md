# FAQ by page type

Authoritative FAQ规范 for MoreTop10. FAQ is keyed to page positioning in [`page-type-taxonomy.md`](page-type-taxonomy.md) (types 01–21). **There is no site-wide generic FAQ.**

**This PR is spec-first.** Do not treat this file as a license to rewrite every Live FAQ block. A parallel HTML scrub (cross-category robot-vac leftovers) is out of scope here.

**Bake ≠ Deploy.** No Live wrangler/CF ship from this document.

---

## Global rules

### Purpose

FAQ answers **buyer / reader intent** questions that attract search and referrals: size, use case, who should skip, what to confirm on the retailer listing, how this page’s shortlist differs from a sibling page.

FAQ is **not** a site-ops help desk. How we rank, commission, “are prices live?”, “how many products appear”, score formula, completeness gates, and L2 jargon belong on type **20** (methodology / advertising disclosure) and the site top-bar disclosure — not as the main FAQ surface.

### Length

- Typical money page: **3–5** visible Q&As.
- Niche (03): **top FAQ (3–4)** plus **bottom FAQ (2–4)** when the page is long enough to need both.
- Hard cap **8** visible Q&As on any single page (matches `seo_geo.extract_visible_faqs` ingest). Prefer fewer strong questions over padding.
- If the page type is **omit**, ship **zero** visitor FAQ widgets and **no** `FAQPage` JSON-LD.

### Question phrasing

Write natural search questions a shopper would type or ask aloud.

- Good: “What size air fryer do I need for a family of four?”
- Good: “Who should skip the Laifen SE 2?”
- Bad: “How do you rank products on this chart?”
- Bad: “Do you run lab tests on this product?” as the primary question on a review

Questions name the **category, product, or use case** — not MoreTop10 internals.

### Grounding (no invented claims)

Answers must be grounded in the **on-page shortlist, review body, or retailer snapshot already published**. Do not invent wattage, chamber results, “lab tested”, award badges, or features that do not appear on the card / review.

If a fact is only on the retailer listing, say so and point at **Check price** — do not restated-as-ours.

### Forbidden FAQ topics (all types)

Do **not** use these as the main FAQ surface (one sentence + link to type 20 is not a substitute for filling the slot):

| Forbidden | Put it here instead |
| --- | --- |
| Commission / “do you earn a commission?” / PartnerBoost | Top-bar advertising disclosure + About (19/20) |
| Score formula, “stars × 2”, L2, card checklist as the hook | `/blog/how-we-pick-products/` and About methodology |
| “Are prices live?” / “How often do prices change?” as a lead question | Disclosure + on-page “Last updated” / price-snapshot line |
| “How many products do you rank?” / completeness gate / publishable / inventory-blocked | Methodology (20). Not visitor FAQ. |
| Cross-niche leftovers (robot-vac “automated dock / mop” on air fryers, kids bikes, hair dryers, etc.) | Delete. Rewrite for **this** category only. |
| Nav `<details>` titles (Categories / Compare / Reviews) ingested as FAQ | Never. `FAQPage` is visitor FAQ only. |

Template bleed examples that are already on Live and **fail this spec**:

- Air-fryer and kids-bike landings asking “Do I need the most automated dock?”
- Hair-dryer reviews answering “who should choose” with floors, pets, and weekly jobs
- Comparison FAQs that are eight questions about rank, commission, and live prices

### Methodology and disclosure homes

| Surface | URL / chrome | Holds |
| --- | --- | --- |
| About | `/about-us/` | Who we are, editorial independence, advertising disclosure section |
| How we pick | `/blog/how-we-pick-products/` | Shortlist loop, card checklist, score mapping |
| Advertising disclosure | Site top bar + footer | Commission, “we are not the seller” |
| Price snapshot | On-card / glance line, not FAQ | “Checked YYYY-MM-DD — confirm on the retailer page” |

FAQ may **link** to these. FAQ must not **rehearse** them.

### Schema sync (hard)

Visible FAQ and `FAQPage` JSON-LD **must match**:

1. Same questions, same order, same answer text (plain-text equivalent).
2. Only visitor FAQ widgets feed schema: `.landing-faq`, `.review-faq .faq`, home/match FAQ `<details>` that are not nav.
3. Never ingest header/mobile mega `<details>` (`Compare`, `Categories`, `Reviews`).
4. If FAQ is omitted for the page type, omit `FAQPage` entirely. Do not ship an empty `mainEntity`.
5. No `AggregateRating` invented to “support” FAQ.

`site/scripts/seo_geo.py` (`extract_visible_faqs` / `faq_node`) is the current bake path. A future rewrite must keep that lockstep.

### Assert / test expectation

No dedicated FAQ-content assert exists today. Adjacent checks:

- `site/scripts/build.py` — hub `FAQPage` must not ingest nav titles; jargon scrub on a sample FAQ chunk
- `tests/seo_geo_p0_assert.py` — hub schema types (includes `FAQPage` on type 04 today)
- `site/scripts/seo_geo.py` — visible FAQ → JSON-LD

**Name the follow-on file:** [`tests/faq_by_page_type_assert.py`](../tests/faq_by_page_type_assert.py) (create in a later PR). It should fail a bake when:

1. Visible Q/A pairs ≠ `FAQPage.mainEntity` (name + acceptedAnswer text)
2. A forbidden-topic question appears on types that this spec marks **exclude**
3. Cross-category bleed strings appear off their niche (e.g. `automated dock` outside `robot-vacuums`)
4. An **omit** type ships `.landing-faq` / `.review-faq` / `FAQPage`
5. Count is outside the type’s band (after FAQ is rewritten to this spec)

Until that file exists, treat this document as the review checklist.

---

## Per page type

### 01 Home

| | |
| --- | --- |
| **Role** | Orient a first-time visitor. Answer “what is this site / who is it for / where do I start” without affiliate or ranking jargon. |
| **Include** | What MoreTop10 is (comparison + reviews, not a store). Which kinds of home products we cover. How to start (pick a category → landing or comparison). Brand identity: we are not Top10.com / Natural Intelligence. |
| **Exclude** | How we rank, score formula, how many products, commission, “are prices live?”, completeness / publishable language. |
| **Count band** | 3–5 |
| **Optional / omit** | Required. Current Live home FAQ is mostly forbidden ops copy and must be rewritten to this role. |

Example themes (not required verbatim):

- “Do you sell the products on MoreTop10?” → No; Check price opens a retailer. (No commission paragraph.)
- “Which categories can I compare here?”
- “Are you related to Top10.com?”

---

### 02 Comparison

| | |
| --- | --- |
| **Role** | Help a shopper **use the shortlist**: size, use case, skip-if, what to do if #1 is wrong. Not a tour of the chart UI. |
| **Include** | Category buying criteria grounded in the ten cards on **this** page (capacity, floor type, pets, noise, budget band). Who should skip the top card. What to confirm on the retailer listing (tax, shipping, bundle). |
| **Exclude** | “How do you rank / what do the scores mean / do you earn a commission / are these prices live / how many products / how often do rankings change” as FAQ questions. Chart mechanics stay in the glance intro + methodology link. |
| **Count band** | 3–5 |
| **Optional / omit** | Required on every published comparison. |

Example themes (air fryers — not robot vac):

- “What size basket do I need for a family of four?”
- “When should I skip a dual-zone model?”
- “What if the #1 is out of stock or over budget?” → next on-page card that matches the use case.

---

### 03 Niche (top + bottom)

| | |
| --- | --- |
| **Role** | Answer the **slice** (pets, indoor, basement, hardwood) more deeply than the parent landing. Top FAQ captures the search questions that brought the reader; bottom FAQ covers leftover ownership / skip-if after they have seen the niche shortlist. |
| **Include** | Slice-specific criteria only (e.g. pet hair + litter tracking on `/robot-vacuums/pet-homes/`). Name the parent category and how this slice differs. |
| **Exclude** | Parent-category generics that ignore the slice. Other niches’ leftovers. Site-ops copy. |
| **Count band** | Top 3–4 + bottom 2–4 (combined ≤ 8). Both blocks must appear in the same `FAQPage` in document order. |
| **Optional / omit** | **Omit until the niche HTML exists.** Do not FAQ a 404 related-cluster link. |

`automated dock` / mop-pad / self-empty questions are valid **only** on robot-vacuum niches and the robot-vac landing/comparison — never on kids bikes, air fryers, hair dryers, or other cats.

---

### 04 Category landing

| | |
| --- | --- |
| **Role** | Answer category-level buying questions so the landing can rank and refer. Push chart work to comparison; push product work to reviews. |
| **Include** | Size, room / household, skip-if, “do I need feature X **in this category**”. Point to comparison when the next step is the ten-card chart. |
| **Exclude** | Chart mechanics, commission, score formula, “how many products”, other categories’ feature questions. |
| **Count band** | 3–5 |
| **Optional / omit** | Required on each published `/{cat}/` hub. `/tv/` uses type 10/07/09 themes, not density-10 shortlist FAQ. |

Landing FAQ is **per category**. Copy-paste across the 21 hubs is a spec violation.

---

### 05 Reviews hub

| | |
| --- | --- |
| **Role** | Index of reviews. Buyer intent lives on 04 / 02 / 06. |
| **Include** | None by default. |
| **Exclude** | Repeating the landing FAQ. Site-ops. “How we review” (that is type 20). |
| **Count band** | 0 |
| **Optional / omit** | **Omit.** Optional 0–2 only if the hub has a unique reader question that is not on the landing (e.g. “Which reviews are new this month?”) **and** that fact is on the page. Prefer omit. No `FAQPage` when count is 0. |

---

### 06 Product review

| | |
| --- | --- |
| **Role** | Product-specific ownership: who it is for, who should skip, how it differs from the next shortlist pick. Attract “{product} vs / should I buy / who is it for” queries. |
| **Include** | Who should choose / skip **this** model, using on-page fit notes. One vs-alternative question naming a sibling **on this category shortlist**. Ownership facts already in the review (tank size, attachments, first-use step from the manufacturer copy already quoted). |
| **Exclude** | Generic category FAQ. Other categories’ jobs-to-be-done (floors/pets on a hair dryer). “Do you run lab tests?” / score formula as a primary question. Invented specs. Price-snapshot-as-FAQ when the price is already beside Check price (one ownership question may mention the snapshot date if it is on the page). |
| **Count band** | 3–5 |
| **Optional / omit** | Required on every published review. Answers must change between SKUs — a shared four-question template with only the product name swapped fails this spec. |

---

### 07 Best-of

| | |
| --- | --- |
| **Role** | Defend the “best for {job}” framing. Why this slice, who should ignore “best” and use the full comparison. |
| **Include** | What “best” means **on this page** (job, not a paid badge). Who should skip this slice. How it relates to the parent comparison shortlist (only products that actually appear). |
| **Exclude** | Site-wide ranking methodology as FAQ. Products not on the page. |
| **Count band** | 3–5 |
| **Optional / omit** | Required when the article HTML exists (`/tv/best-*` today). **Omit** on related-cluster hrefs that 404. |

---

### 08 VS

| | |
| --- | --- |
| **Role** | Settle the head-to-head the URL promises. |
| **Include** | Who should pick A vs B, using on-page differences. When neither is the fit (point at comparison or alternatives). One ownership / skip question per model **only if** it is already in the article. |
| **Exclude** | A third product not discussed. Chart-ops. Cross-category feature questions. |
| **Count band** | 3–5 |
| **Optional / omit** | Required when the VS article exists. **Omit** while the URL is only a related-cluster stub. |

---

### 09 Alternatives

| | |
| --- | --- |
| **Role** | Help readers who already rejected a default pick. |
| **Include** | Why someone would switch (budget, size, feature they do not need). Which alternative on **this** page matches which skip-if. |
| **Exclude** | Re-pitching the #1 as if this were a comparison FAQ. Commission / rank formula. |
| **Count band** | 3–5 |
| **Optional / omit** | Required when the article exists (`/tv/smart-tv-ad-alternatives/` is the live pattern). **Omit** on unpublished category stubs. |

---

### 10 Guide

| | |
| --- | --- |
| **Role** | Answer the buying-education queries the guide title already targets (how to choose, what to look for). |
| **Include** | Criteria questions that match H2s already on the page. “Which MoreTop10 page do I open next?” (landing vs comparison) without ops language. |
| **Exclude** | Product SKUs not named in the guide. Score formula. Other categories. |
| **Count band** | 3–5 |
| **Optional / omit** | Required when the guide HTML exists. **Omit** on unpublished `/{cat}/how-to-choose-*` stubs. |

---

### 11 How-to (procedural)

| | |
| --- | --- |
| **Role** | Unblock a task (e.g. ADB debloat not working, remove smart-TV ads). |
| **Include** | Symptom → next step already documented on the page. What this procedure does **not** do. Safety / warranty caveats that are already stated. |
| **Exclude** | Product-ranking FAQ. Invented commands or lab claims. Affiliate copy. |
| **Count band** | 3–5 |
| **Optional / omit** | Required on published `/tv/` procedure pages. Omit if the page is a stub. |

---

### 12 Blog hub

| | |
| --- | --- |
| **Role** | Inventory index. Thin today. |
| **Include** | — |
| **Exclude** | Placeholder FAQ, methodology FAQ, “what is MoreTop10”. |
| **Count band** | 0 |
| **Optional / omit** | **Omit until the hub has a real article feed.** Then optional 2–3 about what the blog covers vs comparisons. |

---

### 13 Blog article

| | |
| --- | --- |
| **Role** | Only when the post is a reader-intent essay (not methodology). |
| **Include** | Questions the post already answers, phrased as search queries. |
| **Exclude** | `/blog/how-we-pick-products/` (type **20**). Thin posts with no unique Q. |
| **Count band** | 0–4 |
| **Optional / omit** | **Omit by default** while inventory is thin. No `FAQPage` on type-20 posts filed under `/blog/`. |

---

### 14 Authors hub · 15 Author profile

| | |
| --- | --- |
| **Role** | People index / bio. |
| **Include** | — |
| **Exclude** | Marketing FAQ, “how we rank”. |
| **Count band** | 0 |
| **Optional / omit** | **Omit.** |

---

### 16 Contact · 17 Partner

| | |
| --- | --- |
| **Role** | Action pages (write us / partner). |
| **Include** | — |
| **Exclude** | Buyer FAQ, commission explainer-as-FAQ (partner page body may disclose commercially; that is not `FAQPage`). |
| **Count band** | 0 |
| **Optional / omit** | **Omit.** |

---

### 18 Match

| | |
| --- | --- |
| **Role** | Help someone finish the matcher and land on a real shortlist. Today `/robot-vacuums-match/` is a `noindex` cluster demo — FAQ must stay honest about that **without** becoming a backend-ops FAQ. |
| **Include** | What inputs matter (floors, pets, mop vs vacuum-only) **for this category**. That results use the same published robot-vac shortlist (no invented SKUs). That the reader can skip to comparison. |
| **Exclude** | “Is this a live quiz backend?” as the lead. Publishable / inventory language. FAQ for other categories. Commission. |
| **Count band** | 3–4 |
| **Optional / omit** | Required while the match URL exists. If the demo is removed, omit FAQ with the page. |

---

### 19 About · 20 Methodology / advertising disclosure · 21 Legal

| | |
| --- | --- |
| **Role** | These pages **are** the destination for ops, rank, commission, and legal copy. They do not need a marketing FAQ. |
| **Include** | — |
| **Exclude** | Buyer-intent FAQ, `FAQPage` used to recast disclosure as Q&A, “are prices live?” widgets. |
| **Count band** | 0 |
| **Optional / omit** | **Omit.** No marketing FAQ on About, How we pick, privacy, terms, or cookie pages. |

---

## Cross-category bleed (hard)

A question is legal only if a shopper of **this** page’s category would ask it.

| Question theme | Allowed on | Forbidden on |
| --- | --- | --- |
| Automated dock / mop pad / self-empty | `robot-vacuums` 02/03/04/06/18 | Every other category |
| Portafilter / steam wand / grind-into-basket | `espresso-machines` | Hair dryers, vacuums, … |
| Pint rating / basement sq ft | `dehumidifiers` | Speakers, bikes, … |
| Floors, pets, weekly vacuum jobs | Vacuums / litter boxes as relevant | Hair dryers, air fryers, bikes |
| Dual voltage / diffuser / concentrator | `hair-dryers` | Vacuums, espresso, … |

If a generator cannot supply a category-specific question, **ship fewer FAQs** — do not fall back to the robot-vac template.

---

## Implementation notes (follow-on, not this PR)

1. Rewrite visible FAQ HTML per type, then regenerate JSON-LD via `seo_geo.py` (or keep hand-sync if a page is hand-baked).
2. Add `tests/faq_by_page_type_assert.py` once a first category’s FAQ matches this spec.
3. Do not conflict with an in-flight HTML scrub of robot-vac leftovers — that work can land first; this spec is the bar those rewrites should meet.
4. Speakable selectors (`.landing-faq`, `.geo-answer-first`) stay valid only if the visible FAQ still matches schema.
