---
name: phaselens
description: Analyzes a listed company the way a long-term owner would and returns a verdict with exact starter-buy, full-position, hold and trim prices. Places the company in one of five lifecycle phases, lets the phase choose the metrics and valuation method, and runs a reverse DCF. Use when someone names a stock, ticker or company — in any sector, including banks, insurers and REITs — and asks whether to buy, hold or sell it, whether it is cheap or expensive, when to buy, or at what price.
---

# PhaseLens

Answers three questions for any listed company: **Is it a good business? Is it a good price? At exactly what price do I start buying, add, hold, or trim?**

Two ideas drive it:

- **Phase first.** Every company is in one of five lifecycle phases. The phase decides which numbers matter and which valuation methods are allowed.
- **Price last.** Business, moat, management and risks are judged before valuation, so the price tests the thesis instead of shaping it.

Copy this checklist and work through it in order:

```
PhaseLens progress
- [ ] 0. Research: live price, filings, 5–10 yr history, insiders
- [ ] 1. Business in one sentence
- [ ] 2. Lifecycle phase (and whether it changed)
- [ ] 3. Moat grade A–D with evidence
- [ ] 4. Management and capital allocation
- [ ] 5. Growth and returns, forensic scan
- [ ] 6. Thesis-break triggers, pre-mortem, bear case
- [ ] 7. Valuation → price bands
- [ ] 8. Portfolio fit
- [ ] 9. Buy Plan box
```

## 0. Research — never from memory

Prices, multiples and results change daily. Use web search and primary filings (10-K, 10-Q, 8-K, proxy, Form 4, 13F, company releases, call transcripts) for: price; diluted shares; cash and debt; 5–10 years of revenue, gross and operating margin, operating cash flow, capex, stock-based compensation (SBC), ROIC, share count, dividends and buybacks; insider trades in the last 90 days; latest guidance.

Record the raw numbers in a working file and compute from it. Mark anything unverified "n/v". Label every claim as fact (cite it), inference, or consensus.

## 1. Business

One sentence: what it sells, to whom, and how it gets paid. Then revenue by segment and by geography. If it can't be said simply, stop and say the company is outside the circle of competence.

## 2. Lifecycle phase

Place the company with three numbers: 3–5 year revenue growth and its direction; operating margin and its direction; what it does with cash (raises it / reinvests all / reinvests some / returns it).

| Phase | Signature | Key metric | Valuation methods | Run `valuation.py`? |
|---|---|---|---|---|
| 1 Startup | tiny revenue, deepening losses, raising cash | traction, gross-margin trend, runway | market size, price/sales | No |
| 2 Hyper Growth | fast growth, losses peak then narrow, dilution | growth vs peers, retention, gross margin | price/sales, price/gross profit | No (reverse DCF only as a sanity check if FCF is positive) |
| 3 Operating Leverage | breakeven crossed, margins expanding | margin expansion, FCF growth > revenue growth | forward P/E, forward P/FCF | Yes, with **next-year or normalized** owner FCF |
| 4 Capital Return | steady growth, high ROIC, buybacks, dividends | FCF, ROIC, payout coverage, share count | P/E, P/FCF, DCF, reverse DCF | Yes |
| 5 Decline | revenue and profit fading | balance-sheet runway, asset value | asset value, sum of the parts | No |

Say whether the phase changed in the last 3–5 years — a phase change is a thesis change. Boundary cases matter most: the market often still prices a company for the phase it is leaving. Detail: [references/lifecycle-phases.md](references/lifecycle-phases.md).

Setup category: **Cat 1** defensive compounder (Phase 4, wide moat, low volatility) · **Cat 2** quality business at a compressed multiple · **Cat 3** special situation or turnaround (needs a named, dated catalyst) · **Cat 4** deep value or asset play (needs a path to revaluation).

Banks, insurers, REITs, utilities, cyclicals, foreign listings and negative-FCF companies need different inputs: read [references/special-cases.md](references/special-cases.md) before valuing them.

## 3. Moat — grade A to D

Why can't a well-funded competitor take these customers? Name the source (network effects, switching costs, cost advantage, intangibles, efficient scale) and show evidence: gross margin held through cost inflation, market share over 3–5 years against the 2–3 closest competitors, ROIC above the cost of capital.

## 4. Management and capital allocation

Compare what management said three years ago with what happened. Check insider ownership, share-count direction, and how FCF is split between reinvestment, acquisitions, buybacks and dividends. Open-market purchases with personal money are high-signal; pre-planned (10b5-1) sales and exercise-and-sell are discounted.

## 5. Growth and returns

Show revenue growth beside ROIC and the margin trend — growth without returns burns cash; returns without growth stagnate. Forensic scan for companies older than five years: receivables growing faster than revenue, capitalized expenses, recurring "one-time" items, restatements, auditor or CFO changes.

## 6. What breaks the thesis — written before valuing

Write three specific, checkable triggers. Check the six yellow flags (declining share, a metric no longer disclosed, brand dilution, a large acquisition after organic growth slows, surprise CEO exit, auditor change). One flag: investigate. Two or three, or one that contradicts the thesis: it is broken. Then a pre-mortem ("it fell 50% in three years — what happened?") and the strongest bear case, argued as a believer would. Detail: [references/red-flags-and-selling.md](references/red-flags-and-selling.md).

## 7. Valuation → price bands

**7a. Owner FCF.** Operating cash flow − capex − SBC, with one-offs removed (settlements, termination fees, working-capital windfalls such as customer-deposit float). Use diluted shares today and deduct SBC; do not also project share-count growth or add back buybacks. For cyclicals use mid-cycle FCF, never peak.

**7b. Reverse DCF first** (Phases 3–4). What yearly owner-FCF growth for ten years does today's **market cap** imply at 8%, 10% and 12% required returns, with 3% growth afterwards? Compare it with the company's actual 5–10 year FCF growth and what its market allows. Implied growth well below history with the moat intact means the market is too pessimistic; at or above history means no room for disappointment.

**7c. Cross-check** with a second method from the phase table — for example the multiple against its own 5–10 year history and peers. If the two disagree widely, the value is genuinely uncertain: say so and size smaller.

**7d. Bear / base / bull** growth rates anchored to history, the implied growth and the industry's ceiling. Weighted 25 / 50 / 25.

**7e. Margin of safety** — scaled to predictability, not excitement:

| Business | Required margin of safety |
|---|---|
| Proven 15%+ ROIC compounder, A moat, a decade of execution | 0–10% at a 10% hurdle, **or** 20–25% at a 9% hurdle — never loosen both |
| Stable, predictable, B+ moat | 20–25% |
| Cyclical, competitive, levered, or turnaround | 35–40% or more |
| Value rests on growth a decade out (Phases 1–2) | no discount is enough — size smaller instead |
| Decline | a wide discount to **asset** value; a low P/E is not safety |

**7f. Run the helper** at `${CLAUDE_SKILL_DIR}/scripts/valuation.py` (Python 3, standard library). Use that path as written; don't search the filesystem. If the path appears unexpanded, the script is `scripts/valuation.py` in this skill's folder.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/valuation.py --price 69.62 --shares 2043 --fcf 8200 \
  --growth 0.05 0.11 0.16 --mos 0.30
```

`--shares` in millions; `--fcf` is owner FCF in millions of the price's currency. Optional: `--rate` (default 0.10), `--terminal` (0.03), `--years` (10). It prints price/owner-FCF, implied growth at 8/10/12%, bear/base/bull value per share, the weighted value, the bands, the current discount to value and which zone today's price is in. It refuses inputs where a DCF doesn't apply (non-positive FCF, unordered scenarios) — follow the phase's other methods then.

**Phases 1–2 (and any company with negative owner FCF) — no DCF, no script.** Don't discount projected cash flows; the inputs don't exist yet. Instead:

1. Today's price/sales and price/gross profit against the company's own history and 2–3 peers.
2. A five-year scenario: bear / base / bull revenue × a mature-company price/sales (or price/gross-profit) multiple → future market cap, discounted back five years at the hurdle, less dilution.
3. Size smaller rather than demand a bigger discount. State plainly that the value is a range, not a number.

**The bands:**

| Zone | Price range | Action |
|---|---|---|
| Full position | ≤ starter × 0.90 | add to full size, only if the thesis still holds at that price |
| Starter buy | ≤ weighted value × (1 − margin of safety) | first tranche |
| Hold | starter → weighted value | no new money |
| Fair | weighted value → bull value | hold; no new money |
| Trim / pass | above bull value | no plausible future justifies the price — trim, or pass if not owned |

If today's price is above the bull value, the verdict is Pass (or Trim if owned) and the buy prices are reference levels, not actions. Detail and the dividend-safety score: [references/margin-of-safety.md](references/margin-of-safety.md).

## 8. Portfolio fit

If the user has holdings or rules on record, check overlapping exposures (several names sharing one disruption risk), sector concentration, caps and sequencing rules. Size by conviction × evidence × asymmetry × fit, and say where the money comes from.

## 9. When to sell

Only four reasons hold up: the thesis changed (name the sentence that is now false — a price above the bull value counts, since no plausible future justifies it), the owner's priorities changed, tax, or the position can't be held calmly or has grown too large. A falling price, a big gain, a flat year, or "I'll buy back lower" are not reasons.

## Output

Full memo, in order: one-sentence thesis → summary → business → **phase and why** → moat grade → growth → financial quality and forensics → management → valuation (multiples table, reverse DCF, bear/base/bull math) → risks → bear case → insiders and holders → portfolio fit → recommendation → sources.

End every analysis with the Buy Plan:

```
Verdict: High-Conviction Buy | Qualified Buy | Watchlist | Pass | Hard Pass
Phase: N (name)   | Setup category: N | Moat: X
Price now: $__    | Weighted value: $__ | Discount to value now: __% (negative = premium)
Implied growth @10%: __% vs actual 5-yr owner-FCF growth __%
Starter buy ≤ $__ (size __%)
Full position ≤ $__ (size __%) — only if: <thesis-intact checks>
Hold: $__–$__   | Fair: $__–$__   | Trim above: $__
Thesis-break triggers: 1) 2) 3)
Next catalyst / re-check date: __
```

"Quick take: TICKER" returns only the phase, moat, reverse DCF and the Buy Plan.

## Rules

- Never predict prices or dates; give scenario ranges with their assumptions.
- No technical indicators as the basis for a call.
- A lower price adds value only if the thesis still holds at that price.
- State the hurdle rate and margin of safety used.
- Close with: this is analysis, not financial advice; the decision is the investor's.
