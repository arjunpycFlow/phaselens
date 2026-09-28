# Special cases

`valuation.py` assumes positive, reasonably stable owner FCF, and a single currency. When a company doesn't fit that, adjust the inputs or switch method.

## Contents

- Negative or erratic FCF
- Cyclicals
- Banks
- Insurers
- REITs
- Utilities
- Foreign listings and ADRs
- Large net cash or heavy debt
- Choosing bear / base / bull growth

## Negative or erratic FCF

No DCF. Use the phase's methods: price/sales or price/gross profit against the company's own history and peers (Phases 1–2), or asset value (Phase 5). Build a bear/base/bull market-share scenario and size smaller instead of demanding a bigger discount.

## Cyclicals

(Commodities, semiconductors, autos, homebuilders, airlines, freight, chemicals.)

- Use **mid-cycle** owner FCF — the average across a full cycle, or normalized margins × current revenue. Never the peak year.
- The lowest P/E usually appears at the top of the cycle, just before earnings fall.
- Margin of safety 35–40% or more.

## Banks

FCF and enterprise value don't apply.

- Value on **price / tangible book**. Justified P/TBV = (ROTCE − g) / (COE − g), where g is long-run growth in tangible book and must not exceed ROTCE × (1 − total payout ratio, dividends plus buybacks). Example: 20% ROTCE, 10% cost of equity, 4% growth → (0.20 − 0.04) / (0.10 − 0.04) = 2.67× tangible book. The zero-growth shortcut ROTCE / COE (2.0× here) undervalues any bank that grows, so never use it.
- Use normalized ROTCE (strip one-time gains such as security sales or share-exchange gains) and a through-cycle credit cost. Build bear / base / bull from (ROTCE, COE, g) triples, value each as multiple × tangible book per share, weight 25 / 50 / 25, then apply the margin of safety as usual.
- Check CET1 capital against the regulatory minimum and the bank's target, deposit mix and cost, credit losses through a cycle, and unrealized losses on securities.

## Insurers

- Value on price / book and ROE, with combined ratio (underwriting profit), reserve development (are past reserves proving adequate?) and investment-portfolio risk.
- Float is an asset only if underwriting is profitable over a cycle.

## REITs

- Use **AFFO** (adjusted funds from operations: net income + depreciation − maintenance capex − straight-line rent adjustments) against market cap, and price / net asset value. Most REITs add back stock-based compensation in AFFO: subtract it again, as with owner FCF.
- REITs grow by issuing shares, so base growth scenarios on AFFO **per share**, not total AFFO, and count unsettled forward-sale shares in the share count.
- Check leverage (net debt / EBITDA), debt maturities, occupancy and lease terms.

## Utilities

- Regulated returns cap growth. Value on P/E against allowed ROE and rate-base growth.
- Check dividend coverage by earnings and operating cash flow, and net debt / EBITDA.

## Foreign listings and ADRs

- Keep price, FCF and shares in one currency.
- Convert shares by the ADR ratio (for example, 1 ADR = 5 ordinary shares).
- Foreign filers don't file Form 4s; use local insider-dealing disclosures.

## Large net cash or heavy debt

- The helper works on an equity basis: owner FCF already reflects interest paid and earned, so debt is not subtracted again.
- **Heavy debt:** check that FCF covers interest comfortably and that maturities can be refinanced. A leveraged company needs a wider margin of safety.
- **Large excess cash that earns little:** you may add excess cash per share to the value, but say so explicitly.

## Choosing bear / base / bull growth

Anchor each scenario to evidence:

- **Base:** close to the company's 5–10 year owner-FCF growth, adjusted for where it is in its phase.
- **Bear:** the path if the thesis-break triggers start to happen.
- **Bull:** what the market could plausibly allow, not the best year on record.

Growth above ~15% for a full decade is rare. If the base case needs it, say so plainly.
