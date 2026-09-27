# Changelog

All notable changes to PhaseLens are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

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
