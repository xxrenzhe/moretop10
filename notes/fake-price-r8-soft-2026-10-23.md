# R8 soft fake list_price scrub — 2026-10-23

waiting_for_部署上线=yes. Draft only. No Live / wrangler / CF deploy. MoreTop10 only — not Lab / RR / OL.

Handoff: `fake-price-mt10-handoff-2026-10-23.md`  
Evidence: `fake-price-daily-2026-10-23-mt10.json` (honest=134 · fake=0 · soft=2)

## ASINs

| ASIN | Category | now (kept) | was / list (cleared) | pct | ratio | file |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `B0FH1RFP91` | computer-speakers | $72.99 | $149.99 | 51 | 2.05 | `site/data/shortlist-computer-speakers.json` |
| `B0GVDBKMVN` | tower-fans | $39.95 | $99.99 | 60 | 2.50 | `site/data/shortlist-tower-fans.json` |

`B0GVDBKMVN` was scrubbed 2026-10-22 then `list_price` came back from affiliate/PB original_price. Cleared again. Restore strike **only** after Amazon L2 buybox. **Amazon L2 buybox > affiliate `list_price`.**

## Before → after

**B0FH1RFP91** (Edifier QD25)

- before: now $72.99 · list/was $149.99 · discount/% implied 51%
- after: now $72.99 · `list_price` / was / discount / % = blank
- comparison + review snapshot now $72.99 (no strike)

**B0GVDBKMVN** (Levoit Windi Lift Pro)

- before: now $39.95 · list/was $99.99 · discount/% implied 60%
- after: now $39.95 · `list_price` / was / discount / % = blank
- comparison + review snapshot now $39.95 (no strike)

CTA tracks unchanged (`pboost.me/E5qe19Gc?uid=fromsll`, `pboost.me/E5qetZHg?uid=fromsll`). Product selection unchanged.

## Gate (existing bake paths — no new strike UI)

- `price_html` already renders **now only** (`price_displayed`). It does not emit list/was/%.
- L1 / affiliate merge (`apply_day_add_l2.py`, `apply_day_add_densify.py`) drops `list_price` when the row is R8 soft or in `r8_soft_queue`.
- `tests/r8_soft_list_price_assert.py` is wired into `build.py` verify so a later PB original_price inject fails bake.

Mac L2 (`merge_tv_l2.py`) is untouched — that is the restore path after buybox verify.

## Bake

Local rebake of `computer-speakers` + `tower-fans` only (`python3 site/scripts/rebake_r8_soft.py`): align published now + JSON-LD Offer.price, no nav/footer rewrite, no Live refetch.

Bake gate for this PR: `python3 tests/r8_soft_list_price_unit.py && python3 tests/r8_soft_list_price_assert.py` (also hooked into `build.py` verify). Full-site `verify()` is already red on `main` for unrelated landing-css / densify leaks — not in scope.

Bake ≠ deploy.
