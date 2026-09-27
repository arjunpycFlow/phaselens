"""Tests for skills/phaselens/scripts/valuation.py.

Run: python3 -m pytest -q
"""
import json
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "skills" / "phaselens" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from valuation import dcf_value, implied_growth  # noqa: E402


def closed_form(f, g, r=0.10, gt=0.03, n=10):
    """Growing annuity for stage one plus a discounted Gordon terminal value."""
    q = (1 + g) / (1 + r)
    stage_one = f * n if abs(q - 1) < 1e-12 else f * q * (1 - q ** n) / (1 - q)
    terminal = f * (1 + g) ** n * (1 + gt) / (r - gt) / (1 + r) ** n
    return stage_one + terminal


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "valuation.py"), *map(str, args)],
        capture_output=True, text=True,
    )


REFERENCE = ["--price", 69.62, "--shares", 2043, "--fcf", 8200,
             "--growth", 0.05, 0.11, 0.16, "--mos", 0.30]


# ---------------------------------------------------------------- dcf_value

@pytest.mark.parametrize("g", [-0.2, 0.0, 0.03, 0.08, 0.10, 0.25])
@pytest.mark.parametrize("r,gt", [(0.08, 0.02), (0.10, 0.03), (0.12, 0.04)])
def test_matches_closed_form(g, r, gt):
    assert dcf_value(100, g, r, gt) == pytest.approx(closed_form(100, g, r, gt), rel=1e-12)


def test_stage_one_equal_to_terminal_reduces_to_gordon():
    assert dcf_value(100, 0.03, 0.10, 0.03) == pytest.approx(100 * 1.03 / 0.07, rel=1e-12)


def test_zero_growth_perpetuity():
    assert dcf_value(100, 0.0, 0.10, 0.0) == pytest.approx(1000.0, rel=1e-12)


def test_terminal_multiple_is_14_7x_year_ten_flow():
    stage_one = sum(100 / 1.1 ** t for t in range(1, 11))
    terminal_at_year_ten = (dcf_value(100, 0.0) - stage_one) * 1.1 ** 10
    assert terminal_at_year_ten / 100 == pytest.approx(1.03 / 0.07, rel=1e-12)


def test_linear_in_fcf():
    assert dcf_value(250, 0.07) == pytest.approx(2.5 * dcf_value(100, 0.07), rel=1e-12)


def test_monotonic_in_growth_and_rate():
    values = [dcf_value(100, g / 100) for g in range(-40, 100, 5)]
    assert all(a < b for a, b in zip(values, values[1:]))
    assert dcf_value(100, 0.05, 0.08) > dcf_value(100, 0.05, 0.10) > dcf_value(100, 0.05, 0.12)


def test_rate_must_exceed_terminal():
    with pytest.raises(ValueError):
        dcf_value(100, 0.05, 0.03, 0.03)


# ----------------------------------------------------------- implied_growth

@pytest.mark.parametrize("g", [-0.3, -0.05, 0.0, 0.052, 0.15, 0.6])
@pytest.mark.parametrize("r", [0.08, 0.10, 0.12])
def test_implied_growth_round_trips(g, r):
    assert implied_growth(dcf_value(8200, g, r), 8200, r) == pytest.approx(g, abs=1e-9)


def test_implied_growth_refuses_answers_outside_the_search_range():
    with pytest.raises(ValueError):
        implied_growth(1e12, 100)   # needs more than 100% a year
    with pytest.raises(ValueError):
        implied_growth(1, 100)      # needs worse than -50% a year
    with pytest.raises(ValueError):
        implied_growth(1000, -100)  # negative FCF has no meaningful answer


# ---------------------------------------------------------------------- CLI

def test_reference_case():
    out = json.loads(run_cli(*REFERENCE).stdout)
    assert out["basis"].startswith("equity")
    assert out["market_cap_m"] == 142234
    assert out["implied_growth_pct"]["r=10%"] == pytest.approx(5.2, abs=0.05)
    assert out["value_per_share_r10"] == pytest.approx(
        {"bear": 68.44, "base": 106.85, "bull": 154.83}, abs=0.01)
    assert out["weighted_value"] == pytest.approx(109.24, abs=0.01)
    assert out["starter_buy_below"] == pytest.approx(76.47, abs=0.01)
    assert out["full_position_below"] == pytest.approx(68.82, abs=0.01)
    assert out["zone_now"] == "starter buy"


def test_bands_are_ordered():
    out = json.loads(run_cli(*REFERENCE).stdout)
    assert (out["full_position_below"] < out["starter_buy_below"]
            < out["weighted_value"] < out["trim_above"])


@pytest.mark.parametrize("price,zone", [
    (60, "full position"), (72, "starter buy"), (90, "hold"),
    (130, "fair"), (200, "above bull case"),
])
def test_zone_now(price, zone):
    args = list(REFERENCE)
    args[1] = price
    assert json.loads(run_cli(*args).stdout)["zone_now"].startswith(zone)


def test_saturated_implied_growth_is_labelled_not_invented():
    out = json.loads(run_cli("--price", 5000, "--shares", 100, "--fcf", 1,
                             "--growth", 0.04, 0.08, 0.12, "--mos", 0.25).stdout)
    assert out["implied_growth_pct"]["r=10%"] == ">100%"


BASE = {"--price": 50, "--shares": 100, "--fcf": 300,
        "--growth": (0.04, 0.08, 0.12), "--mos": 0.25}


@pytest.mark.parametrize("override", [
    {"--fcf": 0}, {"--fcf": -100}, {"--shares": 0}, {"--price": -1},
    {"--mos": 0.95}, {"--mos": -0.1}, {"--growth": (0.10, 0.05, 0.0)},
    {"--terminal": 0.08}, {"--years": 0}, {"--growth": (0.04, 0.08, 1.5)},
])
def test_bad_inputs_are_rejected_cleanly(override):
    merged = {**BASE, **override}
    args = []
    for flag, value in merged.items():
        args.append(flag)
        args.extend(value if isinstance(value, tuple) else [value])
    result = run_cli(*args)
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
