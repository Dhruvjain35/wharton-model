"""FCFF DCF (PRD B1-B4) against the valuation release gates in PRD section 9."""

import pytest

from fre.valuation.dcf import Bridge, DCFInputs, Explicit, SalesToCapital, ValuationError, value


def fixture(**kw) -> DCFInputs:
    base = dict(
        base_revenue=1000.0,
        growth=[0.10, 0.05],
        operating_margin=[0.20, 0.25],
        tax_rate=0.25,
        reinvestment=Explicit(capex_pct=[0.08, 0.07], dna_pct=[0.05, 0.05], nwc_pct=0.10, base_nwc=100.0),
        wacc=0.09,
        terminal_growth=0.03,
        terminal_margin=0.25,
        terminal_roic=0.15,
        bridge=Bridge(excess_cash=50.0, nonoperating_assets=30.0, debt=200.0, other_senior_claims=10.0,
                      diluted_shares=100.0),
    )
    return DCFInputs(**(base | kw))


# ---- hand calculation, written out line by line -------------------------------------------
# Y1: rev 1100, EBIT 220, tax 55, NOPAT 165, capex 88, D&A 55, NWC 110 (dNWC 10), reinv 43, FCFF 122
# Y2: rev 1155, EBIT 288.75, tax 72.1875, NOPAT 216.5625, capex 80.85, D&A 57.75, NWC 115.5 (dNWC 5.5),
#     reinv 28.6, FCFF 187.9625
# Terminal (year 3): rev 1189.65, NOPAT 1189.65*.25*.75 = 223.059375, RR .03/.15 = .2,
#     FCFF 178.4475, TV 178.4475/.06 = 2974.125
PV1 = 122 / 1.09
PV2 = 187.9625 / 1.09 ** 2
PV_TV = 2974.125 / 1.09 ** 2
EV = PV1 + PV2 + PV_TV
EQUITY = EV + 50 + 30 - 200 - 10


def test_hand_calculated_fixture_rows():
    r = value(fixture())
    y1, y2 = r.rows
    assert (y1.revenue, y1.ebit, y1.taxes, y1.nopat) == pytest.approx((1100, 220, 55, 165))
    assert (y1.capex, y1.dna, y1.delta_nwc, y1.net_reinvestment, y1.fcff) == pytest.approx((88, 55, 10, 43, 122))
    assert y2.fcff == pytest.approx(187.9625)


def test_hand_calculated_terminal_value_discounting_and_bridge():
    r = value(fixture())
    assert r.terminal_fcff == pytest.approx(178.4475)
    assert r.terminal_value == pytest.approx(2974.125)
    assert r.pv_terminal == pytest.approx(PV_TV)
    assert r.enterprise_value == pytest.approx(EV)
    assert r.equity_value == pytest.approx(EQUITY)
    assert r.value_per_share == pytest.approx(EQUITY / 100)
    assert r.terminal_share == pytest.approx(PV_TV / EV)


def test_fcff_is_not_levered_cash_flow():
    """Interest and borrowing change levered FCF (the memo) but never FCFF or enterprise value."""
    a = value(fixture())
    b = value(fixture(interest_expense=[20.0, 20.0], net_borrowing=[50.0, 0.0]))
    assert b.enterprise_value == pytest.approx(a.enterprise_value)
    assert b.rows[0].fcff == pytest.approx(122)
    assert b.rows[0].levered_fcf_memo == pytest.approx(122 - 20 * 0.75 + 50)


def test_raising_debt_reduces_equity_one_for_one():
    a = value(fixture())
    b = value(fixture(bridge=Bridge(excess_cash=50, nonoperating_assets=30, debt=300, other_senior_claims=10,
                                    diluted_shares=100)))
    assert a.equity_value - b.equity_value == pytest.approx(100)
    assert b.enterprise_value == pytest.approx(a.enterprise_value)


def test_cash_and_debt_are_counted_once():
    r = value(fixture())
    assert r.equity_value - r.enterprise_value == pytest.approx(50 + 30 - 200 - 10)


@pytest.mark.parametrize("g", [0.09, 0.10])
def test_terminal_growth_at_or_above_wacc_is_rejected(g):
    with pytest.raises(ValuationError, match="terminal growth"):
        value(fixture(terminal_growth=g))


def test_terminal_roic_must_exceed_growth_so_growth_is_not_free():
    with pytest.raises(ValuationError, match="ROIC"):
        value(fixture(terminal_roic=0.03))


def test_both_reinvestment_methods_at_once_is_rejected():
    with pytest.raises(ValuationError, match="one reinvestment method"):
        value(fixture(reinvestment=[Explicit([0.08, 0.07], [0.05, 0.05], 0.10, 100.0), SalesToCapital(2.0)]))


def test_sales_to_capital_reinvestment_and_no_capital_recovery_when_revenue_falls():
    r = value(fixture(growth=[0.10, -0.05], reinvestment=SalesToCapital(2.0)))
    assert r.rows[0].net_reinvestment == pytest.approx(100 / 2.0)
    assert r.rows[1].net_reinvestment == 0.0
    assert any("revenue falls" in f for f in r.flags)


def test_negative_operating_income_gets_no_tax_refund():
    r = value(fixture(operating_margin=[-0.05, 0.25]))
    assert r.rows[0].taxes == 0.0
    assert any("loss" in f.lower() for f in r.flags)


def test_partial_first_year_counts_only_the_remaining_cash_flow_and_shifts_discounting():
    r = value(fixture(stub=0.5))
    assert r.rows[0].fcff_counted == pytest.approx(61)
    assert r.rows[0].discount_factor == pytest.approx(1 / 1.09 ** 0.5)
    assert r.rows[1].discount_factor == pytest.approx(1 / 1.09 ** 1.5)


def test_flags_for_high_terminal_share_and_abrupt_margin_jump():
    r = value(fixture(terminal_margin=0.35))
    assert any("margin" in f for f in r.flags)
    assert any("terminal value" in f for f in r.flags)


def test_every_result_exports_its_assumptions():
    r = value(fixture())
    d = r.to_dict()
    assert d["inputs"]["growth"] == [0.10, 0.05]
    assert d["inputs"]["bridge"]["debt"] == 200.0
    assert d["value_per_share"] == pytest.approx(EQUITY / 100)
