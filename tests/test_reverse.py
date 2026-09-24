"""Reverse DCF (PRD B5): recover inputs, and refuse to force a number when there is none."""

import pytest

from fre.valuation.dcf import Bridge, DCFInputs, SalesToCapital, value
from fre.valuation.reverse import reverse, solve


def base(**kw):
    d = dict(base_revenue=400.0, growth=[0.10] * 5, operating_margin=[0.32] * 5, tax_rate=0.17,
             reinvestment=SalesToCapital(1.5), wacc=0.09, terminal_growth=0.03, terminal_margin=0.32,
             terminal_roic=0.20, bridge=Bridge(90, 0, 50, 0, 12.2))
    return DCFInputs(**(d | kw))


@pytest.mark.parametrize("variable,truth", [("growth", 0.08), ("margin", 0.27), ("wacc", 0.095),
                                             ("terminal_growth", 0.025)])
def test_reverse_solving_a_generated_valuation_recovers_the_input(variable, truth):
    setters = {"growth": dict(growth=[truth] * 5), "margin": dict(operating_margin=[truth] * 5, terminal_margin=truth),
               "wacc": dict(wacc=truth), "terminal_growth": dict(terminal_growth=truth)}
    price = value(base(**setters[variable])).value_per_share
    r = reverse(base(), variable, price)
    assert r.status == "unique"
    assert r.roots[0] == pytest.approx(truth, abs=1e-6)
    assert "consistent with price under this model" in r.label


def test_no_solution_inside_bounds_is_reported_not_forced():
    r = reverse(base(), "growth", price=1e9)
    assert r.status == "none" and r.roots == []


def test_multiple_roots_and_nonmonotonic_behaviour_are_reported():
    r = solve(lambda x: (x - 0.2) * (x - 0.6), 0.0, 1.0)
    assert r.status == "multiple"
    assert r.roots == pytest.approx([0.2, 0.6], abs=1e-9)
    assert r.monotonic is False


def test_invalid_region_is_excluded_not_crashing():
    # WACC below terminal growth is invalid; the scan skips it and still finds the root
    price = value(base(wacc=0.10)).value_per_share
    r = reverse(base(), "wacc", price, lo=0.02, hi=0.20)
    assert r.status == "unique" and r.roots[0] == pytest.approx(0.10, abs=1e-6)
    assert r.invalid_points > 0


def test_other_assumptions_are_recorded_as_held_fixed():
    r = reverse(base(), "growth", value(base()).value_per_share)
    assert r.held_fixed["wacc"] == 0.09 and "growth" not in r.held_fixed
