"""Derived metrics and ratios: arithmetic, traceability, and the suppression rules in PRD A2."""

from datetime import date

import pytest

from fre.fundamentals import compute
from fre.models import Company, Fact, FactStatus
from fre.normalize import Dataset


def mk(values: dict[str, dict[int, float | None]], years=(2023, 2024, 2025)) -> Dataset:
    ds = Dataset(company=Company(cik="1", legal_name="T", tickers=[], fiscal_year_end="1231"),
                 fiscal_years=list(years), snapshot_ids={})
    for metric, by_year in values.items():
        for y in years:
            v = by_year.get(y)
            ds.add(Fact(company="1", metric=metric, value=v, unit="USD", period_start=date(y, 1, 1),
                        period_end=date(y, 12, 31), fiscal_label=f"FY{y}",
                        status=FactStatus.MISSING if v is None else FactStatus.REPORTED))
    return ds


def test_fcf_is_cfo_minus_capex_and_links_its_inputs():
    ds = mk({"cfo": {2025: 164_713.0}, "capex": {2025: 91_447.0}})
    compute(ds)
    f = ds.fact("fcf", "FY2025")
    assert f.value == 73_266.0
    assert f.status == FactStatus.DERIVED
    assert f.inputs == ["cfo@FY2025", "capex@FY2025"]
    assert "cfo" in f.formula and "capex" in f.formula


def test_missing_input_suppresses_instead_of_treating_as_zero():
    ds = mk({"cfo": {2025: 100.0}, "capex": {2025: None}})
    compute(ds)
    f = ds.fact("fcf", "FY2025")
    assert f.value is None and f.status == FactStatus.MISSING
    assert any("capex@FY2025" in n for n in f.notes)


def test_gross_margin_uses_reported_gross_profit_when_the_company_reports_it():
    ds = mk({"revenue": {2025: 100e9}, "gross_profit": {2025: 70e9}, "cost_of_revenue": {2025: 31e9}})
    compute(ds)
    gm = ds.fact("gross_margin", "FY2025")
    assert gm.value == pytest.approx(0.70)
    assert gm.inputs[0] == "gross_profit@FY2025"
    # reported gross profit that disagrees with revenue - cost of revenue is surfaced
    assert any(i.kind == "gross-profit-check" for i in ds.review)


def test_gross_margin_falls_back_to_labelled_derived_gross_profit():
    ds = mk({"revenue": {2025: 100.0}, "gross_profit": {2025: None}, "cost_of_revenue": {2025: 40.0}})
    compute(ds)
    gm = ds.fact("gross_margin", "FY2025")
    assert gm.value == pytest.approx(0.60)
    assert gm.inputs[0] == "gross_profit_calc@FY2025"
    assert any("does not report gross profit" in n for n in gm.notes)


def test_cash_conversion_is_suppressed_for_a_loss_year():
    ds = mk({"cfo": {2025: 50.0}, "net_income": {2025: -10.0}})
    compute(ds)
    f = ds.fact("cash_conversion", "FY2025")
    assert f.value is None and any("net income" in n and "not positive" in n for n in f.notes)


def test_eps_growth_uses_absolute_change_label_across_a_loss_transition():
    ds = mk({"eps_diluted": {2024: -0.50, 2025: 1.20}})
    compute(ds)
    f = ds.fact("eps_growth", "FY2025")
    assert f.value is None
    assert any("loss-to-profit" in n and "+1.70" in n for n in f.notes)


def test_growth_needs_the_prior_period_in_the_dataset():
    ds = mk({"revenue": {2023: 100.0, 2024: 110.0, 2025: 121.0}})
    compute(ds)
    assert ds.fact("revenue_growth", "FY2025").value == pytest.approx(0.10)
    assert ds.fact("revenue_growth", "FY2023").status == FactStatus.MISSING  # no FY2022 loaded


def test_revenue_cagr_over_the_window_and_undefined_for_nonpositive_endpoint():
    ds = mk({"revenue": {2023: 100.0, 2024: 110.0, 2025: 121.0}})
    compute(ds)
    assert ds.fact("revenue_cagr", "FY2025").value == pytest.approx(0.10)
    ds2 = mk({"revenue": {2023: 0.0, 2024: 110.0, 2025: 121.0}})
    compute(ds2)
    assert ds2.fact("revenue_cagr", "FY2025").value is None


def test_total_debt_uses_notes_plus_finance_leases_plus_cp_with_either_presentation():
    # newer presentation: notes-only noncurrent line
    new = mk({"debt_lt_noncurrent": {2025: 46_547.0}, "debt_lt_current": {2025: 1_996.0},
              "finance_lease_liability": {2025: 2_500.0}, "commercial_paper": {2025: 0.0},
              "debt_and_finance_lease_noncurrent": {2025: None}})
    compute(new)
    assert new.fact("total_debt", "FY2025").value == 46_547 + 1_996 + 2_500
    # older presentation: noncurrent line already includes noncurrent finance leases
    old = mk({"debt_lt_noncurrent": {2025: None}, "debt_and_finance_lease_noncurrent": {2025: 14_701.0},
              "debt_lt_current": {2025: 0.0}, "finance_lease_liability_current": {2025: 600.0},
              "commercial_paper": {2025: 0.0}})
    compute(old)
    f = old.fact("total_debt", "FY2025")
    assert f.value == 14_701 + 0 + 600
    assert "debt_and_finance_lease_noncurrent" in f.formula


def test_net_debt_shows_components_and_can_be_negative():
    ds = mk({"debt_lt_noncurrent": {2025: 10.0}, "debt_lt_current": {2025: 0.0}, "finance_lease_liability": {2025: 0.0},
             "commercial_paper": {2025: 0.0}, "cash": {2025: 30.0}, "st_investments": {2025: 70.0}})
    compute(ds)
    f = ds.fact("net_debt", "FY2025")
    assert f.value == -90.0
    assert f.inputs == ["total_debt@FY2025", "liquid_investments@FY2025"]


def test_effective_tax_rate_suppressed_for_pretax_loss():
    ds = mk({"income_tax": {2025: 5.0}, "pretax_income": {2025: -20.0}})
    compute(ds)
    assert ds.fact("effective_tax_rate", "FY2025").value is None


def test_revenue_cagr_undefined_for_negative_start():
    ds = mk({"revenue": {2023: -100.0, 2024: 110.0, 2025: 121.0}})
    compute(ds)
    assert ds.fact("revenue_cagr", "FY2025").value is None
