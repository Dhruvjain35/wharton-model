"""Multiples: every class counted, formulas by hand, undefined when the denominator is not positive."""

from datetime import date

import pytest

from fre.valuation.multiples import ClassShares, compute, symbol_for

D = date(2026, 9, 23)
CLASSES = [ClassShares("Class A", 5_868e6, "GOOGL", 337.83, D), ClassShares("Class B", 835e6, "GOOGL", 337.83, D),
           ClassShares("Class C", 5_527e6, "GOOG", 334.98, D)]


def test_market_cap_counts_every_class_at_its_own_price():
    m = compute("T", D, CLASSES, "TTM", "x", 244e9, 147e9, 53e9, 102e9, 18e9, 56e9, 186e9)
    assert m.market_cap == pytest.approx(5_868e6 * 337.83 + 835e6 * 337.83 + 5_527e6 * 334.98)


def test_pe_ev_ebit_and_fcf_yield_by_hand():
    m = compute("T", D, CLASSES, "TTM", "x", 244e9, 147e9, 53e9, 102e9, 18e9, 56e9, 186e9)
    ev = m.market_cap + 102e9 + 18e9 - 56e9 - 186e9
    assert m.enterprise_value == pytest.approx(ev)
    assert m.pe == pytest.approx(m.market_cap / 244e9)
    assert m.ev_ebit == pytest.approx(ev / 147e9)
    assert m.fcf_yield == pytest.approx(53e9 / m.market_cap)


def test_loss_makes_pe_undefined_not_negative():
    m = compute("T", D, CLASSES, "TTM", "x", -5e9, 147e9, 53e9, 102e9, 0, 56e9, 186e9)
    assert m.pe is None and any("nonpositive" in n for n in m.notes)


def test_missing_bridge_item_blocks_ev_not_everything():
    m = compute("T", D, CLASSES, "TTM", "x", 244e9, 147e9, 53e9, None, 0, 56e9, 186e9)
    assert m.enterprise_value is None and m.ev_ebit is None and m.pe is not None
    m = compute("T", D, CLASSES, "TTM", "x", 244e9, 147e9, 53e9, 10e9, None, 56e9, 186e9)
    assert m.enterprise_value is None and any("preferred" in n for n in m.notes)  # missing preferred is not zero


def test_class_symbol_mapping_with_default():
    mp = [["Class C", "GOOG"], ["", "GOOGL"]]
    assert symbol_for("Class C Capital Stock", mp)[0] == "GOOG"
    assert symbol_for("Class B Common Stock", mp)[0] == "GOOGL"
