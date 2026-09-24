"""WACC is arithmetic on supplied, sourced components; nothing is estimated."""

import pytest

from fre.valuation.wacc import WaccInputs, compute


def test_wacc_from_market_weights_hand_calculated():
    w = compute(WaccInputs(risk_free=0.05, equity_risk_premium=0.05, beta=1.0, pretax_cost_of_debt=0.05,
                           tax_rate=0.20, equity_value=900.0, debt_value=100.0))
    # ke = 10%, kd after tax = 4%, weights 90/10
    assert w.cost_of_equity == pytest.approx(0.10)
    assert w.after_tax_cost_of_debt == pytest.approx(0.04)
    assert w.wacc == pytest.approx(0.9 * 0.10 + 0.1 * 0.04)


def test_preferred_is_a_separate_capital_component():
    w = compute(WaccInputs(risk_free=0.05, equity_risk_premium=0.05, beta=1.0, pretax_cost_of_debt=0.05,
                           tax_rate=0.20, equity_value=800.0, debt_value=100.0, preferred_value=100.0,
                           cost_of_preferred=0.065))
    assert w.wacc == pytest.approx(0.8 * 0.10 + 0.1 * 0.04 + 0.1 * 0.065)


def test_preferred_without_its_cost_is_rejected():
    with pytest.raises(ValueError, match="preferred"):
        compute(WaccInputs(risk_free=0.05, equity_risk_premium=0.05, beta=1.0, pretax_cost_of_debt=0.05,
                           tax_rate=0.2, equity_value=800.0, debt_value=100.0, preferred_value=100.0))
