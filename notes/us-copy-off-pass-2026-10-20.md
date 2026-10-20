# US visitor copy pass (2026-10-20) — MoreTop10 handoff

**Scope this draft:** visitor-facing jargon scrub. **No % off → OFF** needed on sampled MT10 pages (no discount badges found on home / air-fryers / standing-desks / robot-vacuums).

## Changed in this PR
- About H1: `We Help You to Make Smarter Decisions` → `We help you make smarter decisions`
- Home + kids-bikes FAQ/JSON-LD: drop internal `publishable` / `inventory-blocked` / heavy `completeness gate` wording for US shoppers

## Not changed (intentional)
- Amazon product titles containing `Sq.Ft` (merchant title SoT)
- Internal docs / FORK-PLAYBOOK gap labels (`inventory-blocked` as audit class)
- No deploy this round — teammate MoreTop10 owns Live

## Suggested deploy
1. Review HTML diffs under `site/`
2. Deploy with MT10 CF token only
3. Spot-check `https://moretop10.com/`, `/about-us/`, one category FAQ
