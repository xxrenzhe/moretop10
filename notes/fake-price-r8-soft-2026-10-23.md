# R8 soft fake list_price — L2 apply 2026-10-23

waiting_for_部署上线=yes. Draft only. No Live / wrangler / CF deploy. MoreTop10 only — not Lab / RR / OL.

Handoff: `fake-price-mt10-handoff-2026-10-23.md`  
Daily scan: `fake-price-daily-2026-10-23-mt10.json` (honest=134 · fake=0 · soft=2)

## L2 SoT (Mac Chrome CDP)

Copied from parent upload into `notes/mt10-soft-r8-l2-2026-10-23.md` (shared path `/workspace/shared/mt10-soft-r8-l2-2026-10-23.md` was not mounted).

- generated: 2026-10-23T21:59:56.101997+08:00 Asia/Shanghai
- machine: `a262b3cc-47db-4e1f-b094-cb569b0e89ff`
- method_used: `mac_chrome_cdp`
- port: **9334** (9333 WS 403; runbook fallback)
- ZIP / deliver_to: New York **10001** · USD
- L2 collection itself did not write catalog / Live. This draft PR applies the user-requested amend using that md as SoT.

**Amazon L2 buybox > affiliate invent.** R8 soft math still flags 72.99/149.99, but the gate allows that list when the queue action is `restore_list_ok` / L2-verified.

## ASINs (from L2 SoT)

| ASIN | Category | L2 verdict | now | list / strike | avail | honest |
| --- | --- | --- | ---: | --- | --- | --- |
| `B0FH1RFP91` | computer-speakers | **restore_list_ok** | $72.99 | **$149.99** (pct≈51.3 · ratio≈2.05) | In Stock | True |
| `B0GVDBKMVN` | tower-fans | **clear_keep** | **$99.99** | none — do not invent was | In Stock | False |

## Before → after

**B0FH1RFP91** (Edifier QD25)

- catalog soft: now $72.99 · list/was $149.99 (R8 51% / 2.05x) → first draft cleared list
- L2 SoT: now $72.99 · list **$149.99** · honest True · In Stock · ZIP 10001
- after (this draft): now $72.99 · `list_price` $149.99 · comparison card `<s class="pc-was">$149.99</s>` next to now
- CTA unchanged (`pboost.me/E5qe19Gc?uid=fromsll`)

**B0GVDBKMVN** (Levoit Windi Lift Pro)

- catalog soft: now $39.95 · was $99.99 (inverted junk)
- L2 SoT: now **$99.99** · list null · honest False · In Stock · ZIP 10001
- L2 note said collection would not write catalog price (list-only check). User amend for #48 **does** apply L2 now $99.99 on shortlist + baked HTML; still no was/%.
- after (this draft): now $99.99 · `list_price` / was / discount / % = blank
- CTA unchanged (`pboost.me/E5qetZHg?uid=fromsll`)

Product selection unchanged.

## Gate

- `list_price_for_pick`: drop R8-soft / queued list unless queue action is `restore_list_ok` (or `l2_verified`). L2 list must match; a later PB `original_price` that disagrees is still dropped.
- `price_html` still renders **now** as `pc-price-value`. L2 restore adds a native `<s class="pc-was">` on the comparison card only (existing strike token; no new CSS).
- `tests/r8_soft_list_price_assert.py` is wired into `build.py` verify.

Mac L2 TV merge (`merge_tv_l2.py`) is untouched.

## Bake

Local rebake of `computer-speakers` + `tower-fans` only (`python3 site/scripts/rebake_r8_soft.py`): align published now + JSON-LD Offer.price from cards, restore L2 list strike on the speaker card, no nav/footer rewrite, no Live refetch.

Bake gate for this PR: `python3 tests/r8_soft_list_price_unit.py && python3 tests/r8_soft_list_price_assert.py` (also hooked into `build.py` verify). Full-site `verify()` is already red on `main` for unrelated landing-css / densify leaks — not in scope.

Bake ≠ deploy.
