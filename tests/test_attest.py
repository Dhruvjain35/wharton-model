"""Zero attestations: a missing component becomes 0 only when the filing proves it is not there."""

from datetime import date

from fre.attest import apply_zero_attestations
from fre.models import Company, Fact, FactStatus
from fre.normalize import Dataset
from fre.statements import Column, Row, Statement

BS = Statement(title="CONSOLIDATED BALANCE SHEETS - USD ($) $ in Millions", usd_scale=1e6,
               columns=[Column(None, date(2025, 12, 31))], url="bs-url", snapshot_id="bs",
               rows=[Row("Long-term debt", "us-gaap:LongTermDebtNoncurrent", [28_826])])
BS_WITH_CURRENT = Statement(title="CONSOLIDATED BALANCE SHEETS", usd_scale=1e6, columns=BS.columns, url="u",
                            snapshot_id="s", rows=BS.rows + [Row("Current portion of long-term debt",
                                                                 "meta:CustomCurrentDebt", [500])])
NOTE_WITH_TAG = Statement(title="Debt - Details", usd_scale=1e6, columns=BS.columns, url="n", snapshot_id="n",
                          rows=[Row("Current", "us-gaap:LongTermDebtCurrent", [0])])

RULE = {"metric": "debt_lt_current", "fiscal_labels": ["FY2025"],
        "absent_label_pattern": r"(?i)current portion of (long-term )?debt|short-term debt",
        "rationale": "Meta presents no current debt"}


def ds_with(value):
    ds = Dataset(company=Company(cik="1", legal_name="T", tickers=[], fiscal_year_end="1231"),
                 fiscal_years=[2025], snapshot_ids={})
    ds.annual_filings = {"FY2025": "A"}
    ds.add(Fact(company="1", metric="debt_lt_current", value=value, unit="USD", period_start=None,
                period_end=date(2025, 12, 31), fiscal_label="FY2025",
                status=FactStatus.MISSING if value is None else FactStatus.REPORTED))
    return ds


def run(ds, primary, notes):
    return apply_zero_attestations(ds, [RULE], fetch=lambda c, a: primary, fetch_notes=lambda c, a: notes)


def test_absent_everywhere_becomes_a_derived_zero_citing_the_statement():
    ds = ds_with(None)
    run(ds, [BS], [])
    f = ds.fact("debt_lt_current", "FY2025")
    assert f.value == 0.0 and f.status == FactStatus.DERIVED
    assert "not presented" in f.formula and f.sources[0].url == "bs-url"


def test_a_matching_line_on_the_statement_defeats_the_attestation():
    ds = ds_with(None)
    run(ds, [BS_WITH_CURRENT], [])
    assert ds.fact("debt_lt_current", "FY2025").value is None
    assert any(i.kind == "attestation-failed" and i.severity == "block" for i in ds.review)


def test_the_tag_in_a_note_table_defeats_the_attestation():
    ds = ds_with(None)
    run(ds, [BS], [NOTE_WITH_TAG])
    assert ds.fact("debt_lt_current", "FY2025").value is None


def test_reported_values_are_never_overridden():
    ds = ds_with(750e6)
    run(ds, [BS], [])
    assert ds.fact("debt_lt_current", "FY2025").value == 750e6


def test_no_balance_sheet_for_the_period_means_no_attestation():
    ds = ds_with(None)
    run(ds, [], [])
    assert ds.fact("debt_lt_current", "FY2025").value is None


def test_flow_metrics_are_checked_against_duration_columns():
    ds = Dataset(company=Company(cik="1", legal_name="T", tickers=[], fiscal_year_end="1231"),
                 fiscal_years=[2021], snapshot_ids={})
    ds.annual_filings = {"FY2021": "A"}
    ds.add(Fact(company="1", metric="dividends", value=None, unit="USD", period_start=date(2021, 1, 1),
                period_end=date(2021, 12, 31), fiscal_label="FY2021", status=FactStatus.MISSING))
    cfs = Statement(title="CONSOLIDATED STATEMENTS OF CASH FLOWS", usd_scale=1e6, url="cf", snapshot_id="cf",
                    columns=[Column(12, date(2021, 12, 31))],
                    rows=[Row("Repurchases of stock", "us-gaap:PaymentsForRepurchaseOfCommonStock", [-50_274])])
    rule = {"metric": "dividends", "fiscal_labels": ["FY2021"], "absent_label_pattern": r"(?i)dividend",
            "rationale": "none paid"}
    apply_zero_attestations(ds, [rule], fetch=lambda c, a: [cfs], fetch_notes=lambda c, a: [])
    assert ds.fact("dividends", "FY2021").value == 0.0


def test_a_verified_zero_resolves_the_missing_review_item():
    from fre.models import ReviewItem
    ds = ds_with(None)
    ds.review.append(ReviewItem(severity="warn", metric="debt_lt_current", fiscal_label="FY2025", kind="missing", message="m"))
    run(ds, [BS], [])
    assert not any(i.kind == "missing" for i in ds.review)
    assert any(i.kind == "zero-attested" for i in ds.review)
