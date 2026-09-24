"""Quarterly, YTD and TTM facts (PRD A1 quarterly support, section 8 correctness rules)."""

from datetime import date

import pytest

from fre.models import FactStatus
from fre.quarterly import QuarterlyError, instant, standalone_quarter, ttm, ytd


def o(val, start, end, accn, filed, form="10-Q"):
    d = {"end": end, "val": val, "accn": accn, "form": form, "filed": filed}
    if start:
        d["start"] = start
    return d


CF = {"cik": 1, "entityName": "T", "facts": {"us-gaap": {
    "Revenues": {"units": {"USD": [
        o(400.0, "2025-01-01", "2025-12-31", "k25", "2026-02-05", "10-K"),
        o(100.0, "2025-01-01", "2025-03-31", "q125", "2025-04-25"),
        o(190.0, "2025-01-01", "2025-06-30", "q225", "2025-07-24"),
        o(90.0, "2025-04-01", "2025-06-30", "q225", "2025-07-24"),
        o(110.0, "2026-01-01", "2026-03-31", "q126", "2026-04-30"),
        o(230.0, "2026-01-01", "2026-06-30", "q226", "2026-07-23"),
        o(120.0, "2026-04-01", "2026-06-30", "q226", "2026-07-23"),
        o(190.0, "2025-01-01", "2025-06-30", "q226", "2026-07-23"),  # prior-year comparative in the new 10-Q
    ]}},
    "PaymentsToAcquirePropertyPlantAndEquipment": {"units": {"USD": [
        o(20.0, "2026-01-01", "2026-03-31", "q126", "2026-04-30"),
        o(80.0, "2026-01-01", "2026-06-30", "q226", "2026-07-23"),  # cash flow: YTD only, no 3-month value
    ]}},
    "CashAndCashEquivalentsAtCarryingValue": {"units": {"USD": [
        o(55.0, None, "2026-06-30", "q226", "2026-07-23")]}},
}}}


def test_ytd_is_reported_with_its_filing():
    f = ytd(CF, "revenue", date(2026, 1, 1), date(2026, 6, 30))
    assert f.value == 230.0 and f.status == FactStatus.REPORTED
    assert f.sources[0].accession == "q226" and f.fiscal_label == "YTD2026-06-30"


def test_ttm_is_last_fiscal_year_plus_ytd_minus_prior_ytd():
    f = ttm(CF, "revenue", date(2026, 6, 30), fye="1231")
    assert f.value == 400 + 230 - 190
    assert f.status == FactStatus.DERIVED
    assert f.formula == "FY ending 2025-12-31 + YTD ending 2026-06-30 - YTD ending 2025-06-30"
    assert len(f.inputs) == 3


def test_standalone_quarter_uses_the_three_month_value_when_reported():
    f = standalone_quarter(CF, "revenue", date(2026, 4, 1), date(2026, 6, 30))
    assert f.value == 120.0 and f.status == FactStatus.REPORTED


def test_standalone_quarter_is_derived_from_cumulative_cash_flow_values():
    f = standalone_quarter(CF, "capex", date(2026, 4, 1), date(2026, 6, 30))
    assert f.value == 60.0 and f.status == FactStatus.DERIVED
    assert "YTD ending 2026-06-30 - YTD ending 2026-03-31" in f.formula


def test_balance_sheet_values_are_never_summed_into_a_ttm():
    with pytest.raises(QuarterlyError, match="balance-sheet"):
        ttm(CF, "cash", date(2026, 6, 30), fye="1231")
    assert instant(CF, "cash", date(2026, 6, 30)).value == 55.0


def test_missing_prior_ytd_blocks_the_ttm():
    f = ttm(CF, "capex", date(2026, 6, 30), fye="1231")
    assert f.value is None and f.status == FactStatus.MISSING
    assert any("capex" in n or "YTD" in n for n in f.notes)


def test_pre_split_quarterly_share_values_are_rebased():
    from fre.normalize import CorporateAction
    cf = {"cik": 1, "entityName": "T", "facts": {"us-gaap": {"EarningsPerShareDiluted": {"units": {"USD/shares": [
        o(20.0, "2022-01-01", "2022-03-31", "q122", "2022-04-26")]}}}}}
    split = CorporateAction(kind="split", ratio=20, effective=date(2022, 7, 15), source="t")
    f = ytd(cf, "eps_diluted", date(2022, 1, 1), date(2022, 3, 31), actions=[split])
    assert f.value == 1.0 and f.status == FactStatus.DERIVED
