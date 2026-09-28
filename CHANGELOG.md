# Changelog

All notable changes to PhaseLens are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [1.2.0] — 2026-09-27

Fixes from a live accuracy test. Seven real quick takes (UBER, TSLA, SpaceX, GOOGL, AMZN, JPM, O) were checked against SEC filings by an independent reviewer. The calculator was exact in every run. These rules close the gaps the test found:

### Fixed
- **Bank valuation now accounts for growth.** The justified P/TBV is now (ROTCE − g) / (COE − g), with g capped at the sustainable growth rate. The old ROTCE / COE shortcut assumed zero growth. For JPM that shortcut gave 2.0× where the correct figure is 2.67×, which put the stock about 55% above value when the real gap is about 19%.
- **Growth-capex surge rule.** Covers Phase 3–4 companies whose owner FCF is depressed by capex above 1.5× depreciation. The model now shows both trough owner FCF and owner earnings (OCF − depreciation − SBC), cross-checks against a P/E on normalized EPS that strips every quarter's investment gains, and never uses price/sales for a company with positive operating income. Before this rule, Tesla, Alphabet and Amazon were each valued with a different improvised method.
- **REITs.** Stock-based compensation that is added back in AFFO is now deducted again. Growth is modeled per share, and forward-sale shares are counted.

### Added
- **More input audit rows.** The audit now records the largest working-capital lines (anything above 10% of OCF, named, with a call made on each) and net cash or net debt from the balance sheet. A "no one-offs" entry is no longer allowed until the working-capital lines have been reviewed. In the test, Uber's ~$2.0B insurance-reserve float had been missed, and Amazon had been wrongly called net cash.
- **Price date rule.** The price must be the last completed session's close, labeled with its date and weekday. Four of the seven runs had labeled prices with weekend dates.
- **Fresh-filing rule.** After an IPO, merger or capital raise, figures must come from the post-event filing. SpaceX's cash had been quoted from before its IPO.
- **Justification for off-table margins.** Any margin of safety outside the table now needs a one-line reason.
- **Consistent bands.** The Buy Plan's hold and fair bands are now written as starter→weighted and weighted→bull.
- **Bank eval grader** that requires a growth-adjusted multiple (3/3 passes).
- **README.** New "What it costs to run" section with measured costs, and the live-accuracy results.

## [1.1.0] — 2026-09-27

### Added
- **Input audit**, required before any valuation: owner FCF is built from cash-flow-statement line items (operating cash flow, capex including capitalized software, stock-based compensation, named one-offs) with sources and arithmetic, plus a market-cap check on the share count and a TTM arithmetic check. A live test had shown owner FCF overstated by about 8% when an aggregator's FCF figure was used.
- **One-off rules** applied the same way to every company: reversing float (customer deposits, insurance reserves) removed with a labeled sensitivity; tax-timing swings normalized; payouts to minority partners deducted; settlements and termination fees removed; acquisitions excluded from capex; interest on large new debt deducted.

## [1.0.2] — 2026-09-27

### Fixed
- The helper is now referenced as `${CLAUDE_SKILL_DIR}/scripts/valuation.py`, which Claude Code expands to the real path before Claude reads the skill. Live testing showed the 1.0.1 wording alone still led Claude to search the filesystem first.

## [1.0.1] — 2026-09-27

### Fixed
- `valuation.py` rejected growth rates written in scientific notation with a minus sign (for example `-6.9e-05`), because the argument parser read them as option flags. They are now accepted. Found by randomized testing; regression test added.
- `SKILL.md` now says the helper lives in the skill's own directory, so Claude runs it directly instead of searching the filesystem for it.

## [1.0.0] — 2026-09-27

### Added
- `phaselens` skill: a ten-step, phase-aware analysis that ends in a Buy Plan with starter-buy, full-position, hold, fair and trim prices.
- `valuation.py`: reverse DCF at 8 / 10 / 12%, bear / base / bull values, price bands and the current price zone. Standard library only.
- Reference notes: lifecycle phases, margin of safety and dividend safety, yellow flags and sell rules, and special cases (banks, insurers, REITs, utilities, cyclicals, ADRs, negative FCF).
- 61 unit tests, a SKILL.md rules check, and a five-case behavior eval suite for `claude plugin eval`.
- Claude Code plugin and single-plugin marketplace; release workflow that attaches `phaselens.zip` for the Claude apps.
