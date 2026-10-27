#!/usr/bin/env python3
"""PhaseLens scenario helper for companies a DCF does not fit.

Three methods, each returning bear / base / bull values per share, the
25/50/25 weighted value and the same price bands as valuation.py:

  sales  Phases 1-2 and loss-making growers: revenue grows for N years,
         then trades at an exit price/sales (or price/gross-profit) multiple;
         the future market cap is discounted back at the hurdle and spread
         over a share count that keeps growing with dilution.
  ebitda Special situations, takeovers, cyclicals: a future EBITDA times an
         exit EV/EBITDA multiple, minus net debt, discounted back.
  book   Banks and insurers: justified price/book = (ROE - g) / (COE - g),
         times book (or tangible book) value per share.

Standard library only. Python 3.8+.

Examples
--------
    python3 scenarios.py sales --price 148.68 --shares 13176 --revenue 23044 \\
        --growth 0.20 0.35 0.50 --exit 5 8 12 --dilution 0.015 --mos 0
    python3 scenarios.py ebitda --price 4.53 --shares 88.47 --ebitda 30 65 95 \\
        --exit 8 12 14 --net-cash 63.6 --years 4 --dilution 0.03 --mos 0.30
    python3 scenarios.py book --price 343.06 --book 113.35 \\
        --roe 0.14 0.20 0.22 --coe 0.11 0.10 0.095 --g 0.03 0.04 0.045 --mos 0.10

Units: --shares in millions; --revenue, --ebitda and --net-cash in millions
of the price's currency (net cash is negative for net debt).
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from valuation import FULL_POSITION_STEP, SCENARIO_WEIGHTS, _normalize_negatives, zone_for  # noqa: E402

NAMES = ("bear", "base", "bull")


def sales_value(revenue, growth, multiple, shares, rate=0.10, years=5, dilution=0.0, net_cash=0.0):
    """Per-share value today of a future price/sales exit."""
    future_cap = revenue * (1 + growth) ** years * multiple + net_cash
    future_shares = shares * (1 + dilution) ** years
    return future_cap / (1 + rate) ** years / future_shares


def ebitda_value(ebitda, multiple, shares, net_cash=0.0, rate=0.10, years=0, dilution=0.0):
    """Per-share value today of a future EV/EBITDA exit (years=0 means now)."""
    equity = ebitda * multiple + net_cash
    return equity / (1 + rate) ** years / (shares * (1 + dilution) ** years)


def justified_pb(roe, coe, g):
    """Gordon-growth justified price/book: (ROE - g) / (COE - g)."""
    if coe <= g:
        raise ValueError("cost of equity must be above growth")
    if g > roe:
        raise ValueError("growth cannot exceed ROE")
    return (roe - g) / (coe - g)


def bands(price, values, mos):
    weighted = sum(SCENARIO_WEIGHTS[k] * values[k] for k in NAMES)
    starter = weighted * (1 - mos)
    full = starter * FULL_POSITION_STEP
    return {
        "value_per_share": {k: round(values[k], 2) for k in NAMES},
        "weighted_value": round(weighted, 2),
        "starter_buy_below": round(starter, 2),
        "full_position_below": round(full, 2),
        "trim_above": round(values["bull"], 2),
        "discount_to_value_now_pct": round(100 * (weighted - price) / weighted, 1) if weighted > 0 else None,
        "zone_now": zone_for(price, starter, full, weighted, values["bull"]),
    }


def three(p, name, **kw):
    p.add_argument(f"--{name}", type=float, nargs=3, metavar=("BEAR", "BASE", "BULL"), **kw)


def build_parser():
    p = argparse.ArgumentParser(description="PhaseLens scenario values when a DCF does not fit")
    sub = p.add_subparsers(dest="method", required=True)

    s = sub.add_parser("sales", help="five-year price/sales (or price/gross-profit) scenario")
    s.add_argument("--revenue", type=float, required=True, help="TTM revenue (or gross profit), millions")
    three(s, "growth", required=True, help="yearly revenue growth per scenario")
    three(s, "exit", required=True, help="exit price/sales multiple per scenario")
    s.add_argument("--years", type=int, default=5)
    s.add_argument("--dilution", type=float, default=0.0, help="yearly share-count growth")
    s.add_argument("--net-cash", type=float, default=0.0, help="net cash added at exit (negative = debt)")

    e = sub.add_parser("ebitda", help="EV/EBITDA exit, takeover or mid-cycle value")
    three(e, "ebitda", required=True, help="EBITDA per scenario at the exit date, millions")
    three(e, "exit", required=True, help="EV/EBITDA multiple per scenario")
    e.add_argument("--net-cash", type=float, default=0.0, help="net cash (negative = net debt), millions")
    e.add_argument("--years", type=int, default=0, help="years until the exit (0 = value today)")
    e.add_argument("--dilution", type=float, default=0.0)

    b = sub.add_parser("book", help="justified price/book for banks and insurers")
    b.add_argument("--book", type=float, required=True, help="(tangible) book value per share")
    three(b, "roe", required=True, help="normalized ROE / ROTCE per scenario")
    three(b, "coe", required=True, help="cost of equity per scenario")
    three(b, "g", required=True, help="long-run book growth per scenario")

    for sp in (s, e, b):
        sp.add_argument("--price", type=float, required=True)
        sp.add_argument("--mos", type=float, required=True, help="margin of safety, e.g. 0.30")
        sp.add_argument("--rate", type=float, default=0.10)
        if sp is not b:
            sp.add_argument("--shares", type=float, required=True, help="diluted shares, millions")
    return p


def validate(p, a):
    if a.price <= 0:
        p.error("--price must be above zero")
    if not 0 <= a.mos < 0.9:
        p.error("--mos must be between 0 and 0.9")
    if a.method != "book":
        if a.shares <= 0:
            p.error("--shares must be above zero")
        if a.years < 0 or (a.method == "sales" and a.years < 1):
            p.error("--years must be at least 1 for sales and 0 or more for ebitda")
        if a.rate <= -1:
            p.error("--rate must be above -100%")
        first = a.growth if a.method == "sales" else a.ebitda
        if not (first[0] <= first[1] <= first[2] and a.exit[0] <= a.exit[1] <= a.exit[2]):
            p.error("scenarios must be ordered BEAR <= BASE <= BULL")
        if min(a.exit) <= 0:
            p.error("--exit multiples must be above zero")
    else:
        if a.book <= 0:
            p.error("--book must be above zero")
        for roe, coe, g in zip(a.roe, a.coe, a.g):
            if coe <= g:
                p.error("each --coe must be above its --g")
            if g > roe:
                p.error("each --g must not exceed its --roe (growth needs retained returns)")


def run(a):
    if a.method == "sales":
        values = {k: sales_value(a.revenue, g, m, a.shares, a.rate, a.years, a.dilution, a.net_cash)
                  for k, g, m in zip(NAMES, a.growth, a.exit)}
        mcap = a.price * a.shares
        out = {"method": "sales", "market_cap_m": round(mcap),
               "price_to_sales": round(mcap / a.revenue, 1)}
        # revenue the price needs at the base exit multiple
        need = (mcap * (1 + a.rate) ** a.years * (1 + a.dilution) ** a.years - a.net_cash) / a.exit[1]
        out["revenue_needed_at_base_exit_m"] = round(need)
        out["growth_needed_at_base_exit_pct"] = round(100 * ((need / a.revenue) ** (1 / a.years) - 1), 1) if need > 0 else None
    elif a.method == "ebitda":
        values = {k: ebitda_value(eb, m, a.shares, a.net_cash, a.rate, a.years, a.dilution)
                  for k, eb, m in zip(NAMES, a.ebitda, a.exit)}
        out = {"method": "ebitda", "market_cap_m": round(a.price * a.shares)}
    else:
        multiples = {k: justified_pb(r, c, g) for k, r, c, g in zip(NAMES, a.roe, a.coe, a.g)}
        values = {k: m * a.book for k, m in multiples.items()}
        out = {"method": "book", "price_to_book": round(a.price / a.book, 2),
               "justified_pb": {k: round(v, 2) for k, v in multiples.items()}}
    out.update(bands(a.price, values, a.mos))
    return out


def main(argv=None):
    p = build_parser()
    a = p.parse_args(_normalize_negatives(sys.argv[1:] if argv is None else argv))
    validate(p, a)
    json.dump(run(a), sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
