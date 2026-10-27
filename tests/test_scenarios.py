"""Tests for skills/phaselens/scripts/scenarios.py and the valuation.py add-ons.

Run: python3 -m pytest -q
"""
import json
import pathlib
import subprocess
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "skills" / "phaselens" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from scenarios import ebitda_value, justified_pb, sales_value  # noqa: E402


def cli(script, *args):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                          capture_output=True, text=True)


# ------------------------------------------------------------- pure functions

def test_justified_pb_matches_gordon_formula():
    assert justified_pb(0.20, 0.10, 0.04) == pytest.approx(0.16 / 0.06, rel=1e-12)


def test_zero_growth_pb_is_roe_over_coe():
    assert justified_pb(0.15, 0.10, 0.0) == pytest.approx(1.5, rel=1e-12)


def test_growth_raises_pb_when_roe_beats_coe():
    assert justified_pb(0.20, 0.10, 0.05) > justified_pb(0.20, 0.10, 0.0)


@pytest.mark.parametrize("roe,coe,g", [(0.10, 0.05, 0.06), (0.03, 0.10, 0.05)])
def test_justified_pb_rejects_impossible_inputs(roe, coe, g):
    with pytest.raises(ValueError):
        justified_pb(roe, coe, g)


def test_sales_value_closed_form():
    expected = 100 * 1.2 ** 5 * 4 / 1.1 ** 5 / (10 * 1.02 ** 5)
    assert sales_value(100, 0.2, 4, 10, 0.10, 5, 0.02) == pytest.approx(expected, rel=1e-12)


def test_ebitda_value_today_subtracts_net_debt():
    assert ebitda_value(100, 8, 10, net_cash=-300) == pytest.approx(50.0, rel=1e-12)


def test_ebitda_value_discounts_and_dilutes():
    expected = (50 * 12 + 60) / 1.1 ** 4 / (90 * 1.03 ** 4)
    assert ebitda_value(50, 12, 90, 60, 0.10, 4, 0.03) == pytest.approx(expected, rel=1e-12)


# ----------------------------------------------------------------------- CLI

def test_book_reference_case():
    out = json.loads(cli("scenarios.py", "book", "--price", 343.06, "--book", 113.35,
                         "--roe", 0.14, 0.20, 0.22, "--coe", 0.11, 0.10, 0.095,
                         "--g", 0.03, 0.04, 0.045, "--mos", 0.10).stdout)
    assert out["justified_pb"] == pytest.approx({"bear": 1.38, "base": 2.67, "bull": 3.5}, abs=0.01)
    assert out["weighted_value"] == pytest.approx(289.28, abs=0.01)
    assert out["zone_now"].startswith("fair")


def test_sales_reports_growth_needed():
    out = json.loads(cli("scenarios.py", "sales", "--price", 10, "--shares", 100,
                         "--revenue", 100, "--growth", 0.1, 0.2, 0.3,
                         "--exit", 2, 4, 6, "--mos", 0).stdout)
    needed = out["revenue_needed_at_base_exit_m"]
    assert needed == pytest.approx(1000 * 1.1 ** 5 / 4, abs=1)
    assert out["full_position_below"] < out["starter_buy_below"] <= out["weighted_value"]


@pytest.mark.parametrize("args", [
    ["book", "--price", 10, "--book", 5, "--roe", .1, .1, .1, "--coe", .05, .05, .05,
     "--g", .06, .06, .06, "--mos", .1],                                    # coe <= g
    ["sales", "--price", 10, "--shares", 10, "--revenue", 100, "--growth", .3, .2, .1,
     "--exit", 2, 3, 4, "--mos", .1],                                        # unordered
    ["ebitda", "--price", 10, "--shares", 10, "--ebitda", 1, 2, 3, "--exit", 0, 3, 4,
     "--mos", .1],                                                           # zero multiple
    ["sales", "--price", -1, "--shares", 10, "--revenue", 100, "--growth", .1, .2, .3,
     "--exit", 2, 3, 4, "--mos", .1],                                        # bad price
])
def test_bad_inputs_rejected_cleanly(args):
    out = cli("scenarios.py", *args)
    assert out.returncode == 2
    assert "Traceback" not in out.stderr


# ------------------------------------------------------ valuation.py add-ons

BASE = ["--price", 66.13, "--shares", 2050.2, "--fcf", 6177,
        "--growth", 0.05, 0.11, 0.16, "--mos", 0.30]


def test_float_sensitivity_equals_runs_with_float_added():
    with_float = json.loads(cli("valuation.py", *BASE, "--float", 2000).stdout)
    kept = list(BASE)
    kept[5] = 8177
    plain = json.loads(cli("valuation.py", *kept).stdout)
    assert with_float["sensitivity_float"]["fully_kept"]["weighted_value"] == plain["weighted_value"]
    half = with_float["sensitivity_float"]["half_kept"]["weighted_value"]
    assert with_float["weighted_value"] < half < plain["weighted_value"]


def test_no_float_flag_means_no_sensitivity_block():
    assert "sensitivity_float" not in json.loads(cli("valuation.py", *BASE).stdout)


@pytest.mark.parametrize("day,ok", [("2026-10-26", True), ("2026-10-25", False),
                                    ("2026-10-24", False), ("26-10-2026", False)])
def test_asof_rejects_weekends_and_bad_dates(day, ok):
    out = cli("valuation.py", *BASE, "--asof", day)
    assert (out.returncode == 0) is ok


def test_negative_terminal_allowed_for_decline():
    out = cli("valuation.py", "--price", 31.77, "--shares", 141.3, "--fcf", 1050,
              "--growth", -0.08, -0.05, -0.02, "--mos", 0.40, "--terminal", -0.02)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout)["value_per_share_r10"]["bear"] == pytest.approx(41.78, abs=0.01)
