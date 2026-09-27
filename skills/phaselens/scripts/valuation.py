#!/usr/bin/env python3
"""PhaseLens valuation helper: reverse DCF, scenario values and price bands.

Convention (equity basis)
-------------------------
Owner FCF = operating cash flow - capex - stock-based compensation. Interest has
already been paid out of it, so it is cash flow to *shareholders*. It is therefore
compared with, and discounted into, *market capitalisation* - never enterprise
value. Debt is not subtracted again (that would count it twice).

Standard library only. Python 3.8+.

Example
-------
    python3 valuation.py --price 69.62 --shares 2043 --fcf 8200 \\
        --growth 0.05 0.11 0.16 --mos 0.30

Units: --shares in millions; --fcf in the same currency millions as the price.
"""
import argparse
import json
import re
import sys

GROWTH_FLOOR = -0.50   # lowest stage-one growth the reverse DCF searches
GROWTH_CEILING = 1.00  # highest stage-one growth the reverse DCF searches
REVERSE_DCF_RATES = (0.08, 0.10, 0.12)
SCENARIO_WEIGHTS = {"bear": 0.25, "base": 0.50, "bull": 0.25}
FULL_POSITION_STEP = 0.90  # full-position price = starter price x 0.90


def dcf_value(fcf0, growth, rate=0.10, terminal=0.03, years=10):
    """Present value of an owner-FCF stream.

    Stage one: `years` of growth at `growth` from the base `fcf0`.
    Stage two: Gordon growth at `terminal`, valued at the end of year `years`
    as year-N flow x (1 + terminal) / (rate - terminal), then discounted.
    """
    if rate <= terminal:
        raise ValueError("required return must be above terminal growth")
    if years < 1:
        raise ValueError("years must be at least 1")
    pv, flow = 0.0, fcf0
    for t in range(1, years + 1):
        flow *= 1 + growth
        pv += flow / (1 + rate) ** t
    terminal_value = flow * (1 + terminal) / (rate - terminal)
    return pv + terminal_value / (1 + rate) ** years


def implied_growth(market_cap, fcf0, rate=0.10, terminal=0.03, years=10,
                   lo=GROWTH_FLOOR, hi=GROWTH_CEILING):
    """Stage-one growth at which the DCF equals today's market cap.

    Raises ValueError when there is no answer inside [lo, hi] instead of
    silently returning a bound.
    """
    if fcf0 <= 0 or market_cap <= 0:
        raise ValueError("reverse DCF needs positive owner FCF and market cap")

    def gap(g):
        return dcf_value(fcf0, g, rate, terminal, years) - market_cap

    if gap(lo) > 0:
        raise ValueError(f"price implies growth below {lo:.0%} a year")
    if gap(hi) < 0:
        raise ValueError(f"price implies growth above {hi:.0%} a year")
    for _ in range(200):
        mid = (lo + hi) / 2
        if gap(mid) < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return (lo + hi) / 2


def _implied_label(market_cap, fcf0, rate, terminal, years):
    try:
        return round(100 * implied_growth(market_cap, fcf0, rate, terminal, years), 1)
    except ValueError:
        if dcf_value(fcf0, GROWTH_CEILING, rate, terminal, years) < market_cap:
            return f">{GROWTH_CEILING:.0%}"
        return f"<{GROWTH_FLOOR:.0%}"


def zone_for(price, starter, full, weighted, bull):
    if price <= full:
        return "full position (thesis must still hold)"
    if price <= starter:
        return "starter buy"
    if price <= weighted:
        return "hold - below fair value, above the starter price"
    if price <= bull:
        return "fair - hold, no new money"
    return "above bull case - trim / pass"


def build_parser():
    p = argparse.ArgumentParser(
        description="PhaseLens reverse DCF and price bands (equity basis)")
    p.add_argument("--price", type=float, required=True, help="current share price")
    p.add_argument("--shares", type=float, required=True, help="diluted shares, millions")
    p.add_argument("--fcf", type=float, required=True,
                   help="owner FCF = OCF - capex - SBC, millions (one-offs removed)")
    p.add_argument("--growth", type=float, nargs=3, required=True,
                   metavar=("BEAR", "BASE", "BULL"),
                   help="stage-one yearly owner-FCF growth per scenario, e.g. 0.04 0.08 0.12")
    p.add_argument("--mos", type=float, required=True,
                   help="required margin of safety, e.g. 0.25 for 25%%")
    p.add_argument("--rate", type=float, default=0.10,
                   help="required return for scenario values (default 0.10)")
    p.add_argument("--terminal", type=float, default=0.03,
                   help="growth after stage one (default 0.03)")
    p.add_argument("--years", type=int, default=10, help="stage-one length (default 10)")
    return p


def validate(p, a):
    if a.price <= 0 or a.shares <= 0:
        p.error("--price and --shares must be above zero")
    if a.fcf <= 0:
        p.error("owner FCF must be positive; a DCF does not apply - use the phase's "
                "methods (price/sales, price/gross profit, asset value)")
    if not 0 <= a.mos < 0.9:
        p.error("--mos must be between 0 and 0.9")
    bear, base, bull = a.growth
    if not bear <= base <= bull:
        p.error("--growth must be ordered BEAR <= BASE <= BULL")
    if a.years < 1:
        p.error("--years must be at least 1")
    if a.terminal >= min(min(REVERSE_DCF_RATES), a.rate):
        p.error("--terminal must be below --rate and below 8%")
    if max(a.growth) > GROWTH_CEILING or min(a.growth) < GROWTH_FLOOR:
        p.error("--growth values must be between -0.5 and 1.0")


def run(a):
    market_cap = a.price * a.shares
    values = {name: dcf_value(a.fcf, g, a.rate, a.terminal, a.years) / a.shares
              for name, g in zip(("bear", "base", "bull"), a.growth)}
    weighted = sum(SCENARIO_WEIGHTS[k] * v for k, v in values.items())
    starter = weighted * (1 - a.mos)
    full = starter * FULL_POSITION_STEP

    return {
        "basis": "equity (owner FCF vs market cap)",
        "market_cap_m": round(market_cap),
        "price_to_owner_fcf": round(market_cap / a.fcf, 1),
        "owner_fcf_yield_pct": round(100 * a.fcf / market_cap, 1),
        "implied_growth_pct": {
            f"r={round(r * 100)}%": _implied_label(market_cap, a.fcf, r, a.terminal, a.years)
            for r in REVERSE_DCF_RATES
        },
        f"value_per_share_r{round(a.rate * 100)}": {k: round(v, 2) for k, v in values.items()},
        "weighted_value": round(weighted, 2),
        "starter_buy_below": round(starter, 2),
        "full_position_below": round(full, 2),
        "trim_above": round(values["bull"], 2),
        "discount_to_value_now_pct": round(100 * (weighted - a.price) / weighted, 1),
        "zone_now": zone_for(a.price, starter, full, weighted, values["bull"]),
    }


_SCI_NEGATIVE = re.compile(r"-\d*\.?\d+[eE][-+]?\d+")


def _normalize_negatives(argv):
    """argparse mistakes '-6.9e-05' for an option flag; rewrite it as '-0.000069'."""
    out = []
    for tok in argv:
        if _SCI_NEGATIVE.fullmatch(tok):
            tok = f"{float(tok):.12f}".rstrip("0").rstrip(".")
        out.append(tok)
    return out


def main(argv=None):
    p = build_parser()
    a = p.parse_args(_normalize_negatives(sys.argv[1:] if argv is None else argv))
    validate(p, a)
    json.dump(run(a), sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
