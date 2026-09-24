"""Normalizer failure modes: each test is a way real XBRL data has fooled analysts."""

from datetime import date

import pytest

from fre.models import FactStatus
from fre.normalize import CorporateAction, normalize

CIK = "0000000001"
SPLIT = CorporateAction(kind="split", ratio=20, effective=date(2022, 7, 15), source="test")


def obs(val, start, end, accn, filed, form="10-K"):
    o = {"end": end, "val": val, "accn": accn, "form": form, "filed": filed, "fy": 0, "fp": "FY"}
    if start:
        o["start"] = start
    return o


def facts(**tags):
    """tags: tag -> (unit, [observations])"""
    return {
        "cik": 1,
        "entityName": "TestCo",
        "facts": {"us-gaap": {t: {"units": {u: o}} for t, (u, o) in tags.items()}},
    }


SUBS = {"name": "TestCo", "tickers": ["TST"], "fiscalYearEnd": "1231", "filings": {"recent": {
    "accessionNumber": [], "primaryDocument": [], "form": [], "filingDate": []}}}


def run(cf, actions=(), years=(2021, 2022, 2023)):
    return normalize(cf, SUBS, snapshot_ids={"companyfacts": "cf", "submissions": "sb"},
                     retrieved_at="2026-09-24T00:00:00+00:00", actions=list(actions), fiscal_years=list(years))


def test_latest_filing_vintage_wins_and_older_value_is_kept_visible():
    cf = facts(Revenues=("USD", [
        obs(100.0, "2021-01-01", "2021-12-31", "a-22", "2022-02-01"),
        obs(101.0, "2021-01-01", "2021-12-31", "a-23", "2023-02-01"),
    ]))
    ds = run(cf, years=[2021])
    f = ds.fact("revenue", "FY2021")
    assert f.value == 101.0
    assert f.status == FactStatus.REPORTED
    assert f.sources[0].accession == "a-23"
    assert [r.value for r in f.restated_from] == [100.0]
    assert f.restated_from[0].reason == "unexplained"
    assert any(i.kind == "restated" and i.severity == "warn" for i in ds.review)


def test_split_explains_eps_restatement_despite_cent_rounding():
    cf = facts(EarningsPerShareDiluted=("USD/shares", [
        # Alphabet FY2020 as actually filed: 58.61 / 20 = 2.9305, reported post-split as 2.93
        obs(58.61, "2020-01-01", "2020-12-31", "a-21", "2021-02-02"),
        obs(2.93, "2020-01-01", "2020-12-31", "a-23", "2023-02-03"),
    ]))
    ds = run(cf, [SPLIT], years=[2020])
    f = ds.fact("eps_diluted", "FY2020")
    assert f.value == 2.93
    assert "split" in f.restated_from[0].reason
    # an explained split restatement is information, not a warning
    assert not any(i.kind == "restated" and i.severity != "info" for i in ds.review)


def test_value_only_available_pre_split_is_rebased_to_current_share_basis():
    cf = facts(
        EarningsPerShareDiluted=("USD/shares", [obs(58.61, "2020-01-01", "2020-12-31", "a-21", "2021-02-02")]),
        WeightedAverageNumberOfDilutedSharesOutstanding=("shares", [
            obs(687_000_000.0, "2020-01-01", "2020-12-31", "a-21", "2021-02-02")]),
    )
    ds = run(cf, [SPLIT], years=[2020])
    eps = ds.fact("eps_diluted", "FY2020")
    sh = ds.fact("shares_diluted", "FY2020")
    assert eps.status == FactStatus.DERIVED
    assert eps.value == pytest.approx(58.61 / 20)
    assert sh.value == pytest.approx(687_000_000 * 20)
    assert "split" in eps.formula
    assert any(i.kind == "split-adjusted" for i in ds.review)


def test_non_share_metric_is_never_split_adjusted():
    cf = facts(Revenues=("USD", [obs(100.0, "2020-01-01", "2020-12-31", "a-21", "2021-02-02")]))
    f = run(cf, [SPLIT], years=[2020]).fact("revenue", "FY2020")
    assert f.value == 100.0 and f.status == FactStatus.REPORTED


def test_two_values_in_the_same_filing_are_a_visible_conflict_not_a_silent_pick():
    cf = facts(Revenues=("USD", [
        obs(100.0, "2021-01-01", "2021-12-31", "a-22", "2022-02-01"),
        obs(90.0, "2021-01-01", "2021-12-31", "a-22", "2022-02-01"),
    ]))
    ds = run(cf, years=[2021])
    f = ds.fact("revenue", "FY2021")
    assert f.status == FactStatus.CONFLICTING
    assert f.value is None
    assert sorted(f.candidates) == [90.0, 100.0]
    assert any(i.kind == "conflicting" and i.severity == "block" for i in ds.review)


def test_missing_is_none_not_zero_and_is_reviewable():
    ds = run(facts(Revenues=("USD", [])), years=[2021])
    f = ds.fact("revenue", "FY2021")
    assert f.status == FactStatus.MISSING and f.value is None
    assert any(i.kind == "missing" and i.metric == "revenue" for i in ds.review)


def test_tag_fallback_is_recorded_and_checked_on_overlap():
    cf = facts(
        Revenues=("USD", [obs(300.0, "2023-01-01", "2023-12-31", "a-24", "2024-02-01")]),
        RevenueFromContractWithCustomerExcludingAssessedTax=("USD", [
            obs(280.0, "2022-01-01", "2022-12-31", "a-23", "2023-02-01"),
            obs(300.0, "2023-01-01", "2023-12-31", "a-24", "2024-02-01"),
        ]),
    )
    ds = run(cf, years=[2022, 2023])
    assert ds.fact("revenue", "FY2022").sources[0].locator == "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    assert ds.fact("revenue", "FY2023").sources[0].locator == "us-gaap:Revenues"
    switch = [i for i in ds.review if i.kind == "tag-switch"]
    assert switch and switch[0].severity == "info" and "agree" in switch[0].message


def test_tag_fallback_that_disagrees_on_overlap_is_a_warning():
    cf = facts(
        Revenues=("USD", [obs(300.0, "2023-01-01", "2023-12-31", "a-24", "2024-02-01")]),
        RevenueFromContractWithCustomerExcludingAssessedTax=("USD", [
            obs(280.0, "2022-01-01", "2022-12-31", "a-23", "2023-02-01"),
            obs(290.0, "2023-01-01", "2023-12-31", "a-24", "2024-02-01"),
        ]),
    )
    ds = run(cf, years=[2022, 2023])
    switch = [i for i in ds.review if i.kind == "tag-switch"]
    assert switch and switch[0].severity == "warn"


def test_quarterly_durations_off_cycle_periods_and_10q_forms_are_ignored():
    cf = facts(Revenues=("USD", [
        obs(25.0, "2021-10-01", "2021-12-31", "a-22", "2022-02-01"),  # Q4 inside a 10-K
        obs(99.0, "2021-01-01", "2021-12-31", "q-1", "2022-01-15", form="10-Q"),
        obs(77.0, "2021-07-01", "2022-06-30", "a-22", "2022-02-01"),  # annual but wrong FYE
        obs(100.0, "2021-01-01", "2021-12-31", "a-22", "2022-02-01"),
    ]))
    assert run(cf, years=[2021]).fact("revenue", "FY2021").value == 100.0


def test_balance_sheet_instants_are_matched_on_fiscal_year_end_date():
    cf = facts(CashAndCashEquivalentsAtCarryingValue=("USD", [
        obs(5.0, None, "2021-06-30", "q-1", "2021-07-30", form="10-Q"),
        obs(7.0, None, "2021-12-31", "a-22", "2022-02-01"),
    ]))
    f = run(cf, years=[2021]).fact("cash", "FY2021")
    assert f.value == 7.0 and f.period_start is None


def test_june_fiscal_year_end_is_labelled_by_end_year():
    subs = dict(SUBS, fiscalYearEnd="0630")
    cf = facts(Revenues=("USD", [obs(10.0, "2024-07-01", "2025-06-30", "m-25", "2025-07-30")]))
    ds = normalize(cf, subs, snapshot_ids={"companyfacts": "cf", "submissions": "sb"},
                   retrieved_at="x", actions=[], fiscal_years=[2025])
    assert ds.fact("revenue", "FY2025").value == 10.0


def test_rounded_disclosure_is_a_precision_difference_not_a_restatement_warning():
    # Alphabet cash taxes FY2022: 18,892m in one filing, "$18.9 billion" in a later one
    cf = facts(IncomeTaxesPaidNet=("USD", [
        obs(18_892_000_000.0, "2022-01-01", "2022-12-31", "a-23", "2023-02-03"),
        obs(18_900_000_000.0, "2022-01-01", "2022-12-31", "a-26", "2026-02-05"),
    ]))
    ds = run(cf, years=[2022])
    f = ds.fact("cash_taxes", "FY2022")
    assert f.restated_from[0].reason.startswith("precision")
    assert not any(i.kind == "restated" and i.severity == "warn" for i in ds.review)


def test_difference_larger_than_the_rounding_unit_still_warns():
    # 14,862m vs 13,000m: 13,000m rounds to the nearest 1,000m, but the gap is 1,862m
    cf = facts(LongTermDebtNoncurrent=("USD", [
        obs(14_862_000_000.0, None, "2023-12-31", "a-24", "2024-01-31"),
        obs(13_000_000_000.0, None, "2023-12-31", "a-25", "2025-02-05"),
    ]))
    ds = run(cf, years=[2023])
    assert any(i.kind == "restated" and i.severity == "warn" for i in ds.review)
