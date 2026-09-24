"""The reconciliation gate must block a normalized value that disagrees with its statement line."""

from datetime import date

from fre.models import Company, Fact, FactStatus, Source
from fre.normalize import Dataset
from fre.reconcile import reconcile
from fre.statements import Column, Row, Statement


def fact(metric, value, tag, status=FactStatus.REPORTED, instant=False, unit="USD"):
    src = Source(accession="A", form="10-K", filed=date(2026, 2, 5), url="u", locator=tag,
                 snapshot_id="s", retrieved_at="t")
    return Fact(company="1", metric=metric, value=value, unit=unit,
                period_start=None if instant else date(2025, 1, 1), period_end=date(2025, 12, 31),
                fiscal_label="FY2025", status=status, sources=[src])


def dataset(*facts):
    ds = Dataset(company=Company(cik="0000000001", legal_name="T", tickers=[], fiscal_year_end="1231"),
                 fiscal_years=[2025], snapshot_ids={})
    for f in facts:
        ds.add(f)
    return ds


INCOME = Statement(title="INCOME", columns=[Column(12, date(2025, 12, 31)), Column(12, date(2024, 12, 31))], rows=[
    Row("Revenues", "us-gaap:Revenues", "USD", [402_836e6, 350_018e6]),
    Row("Diluted EPS (in dollars per share)", "us-gaap:EarningsPerShareDiluted", "USD/shares", [10.81, 8.04]),
    Row("Other A", "us-gaap:Dup", "USD", [1e6, 0]),
    Row("Other B", "us-gaap:Dup", "USD", [2e6, 0]),
])
BALANCE = Statement(title="BALANCE", columns=[Column(None, date(2025, 12, 31))], rows=[
    Row("Long-term debt", "us-gaap:LongTermDebtNoncurrent", "USD", [46_547e6])])


def fetch(cik, accn):
    return [INCOME, BALANCE]


def outcomes(ds):
    return {r.fact: r.outcome for r in reconcile(ds, fetch=fetch)}


def test_value_within_presentation_rounding_matches_and_records_the_line():
    ds = dataset(fact("revenue", 402_836_000_000.0, "us-gaap:Revenues"))
    rec = reconcile(ds, fetch=fetch)[0]
    assert rec.outcome == "matched" and rec.line == "Revenues" and rec.statement == "INCOME"


def test_mismatch_blocks_the_fact():
    ds = dataset(fact("revenue", 400_000_000_000.0, "us-gaap:Revenues"))
    assert outcomes(ds)["revenue@FY2025"] == "mismatch"
    assert any(i.severity == "block" and i.kind == "reconciliation" for i in ds.review)


def test_wrong_period_is_not_a_match():
    # FY2025 revenue that accidentally carries the FY2024 value must not pass
    ds = dataset(fact("revenue", 350_018e6, "us-gaap:Revenues"))
    assert outcomes(ds)["revenue@FY2025"] == "mismatch"


def test_eps_tolerance_is_cents_not_millions():
    ds = dataset(fact("eps_diluted", 10.90, "us-gaap:EarningsPerShareDiluted", unit="USD/shares"))
    assert outcomes(ds)["eps_diluted@FY2025"] == "mismatch"


def test_instant_matches_only_balance_sheet_columns():
    ds = dataset(fact("debt", 46_547e6, "us-gaap:LongTermDebtNoncurrent", instant=True))
    assert outcomes(ds)["debt@FY2025"] == "matched"


def test_tag_absent_from_statements_is_from_notes_and_derived_is_not_checked():
    ds = dataset(fact("cash_taxes", 1.0, "us-gaap:IncomeTaxesPaidNet"),
                 fact("eps_basic", 1.0, "us-gaap:EarningsPerShareBasic", status=FactStatus.DERIVED))
    o = outcomes(ds)
    assert o["cash_taxes@FY2025"] == "from-notes" and o["eps_basic@FY2025"] == "not-checked"


def test_tag_on_two_lines_with_different_values_is_ambiguous():
    ds = dataset(fact("x", 1e6, "us-gaap:Dup"))
    assert outcomes(ds)["x@FY2025"] == "ambiguous"


CASHFLOW = Statement(title="CF", columns=[Column(12, date(2025, 12, 31))], rows=[
    Row("Purchases of property and equipment", "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", "USD", [-91_447e6]),
    Row("Net income", "us-gaap:NetIncomeLoss", "USD", [-5e6]),
])


def test_outflow_sign_presentation_matches_only_for_payment_tags():
    ds = dataset(fact("capex", 91_447e6, "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment"),
                 fact("net_income", 5e6, "us-gaap:NetIncomeLoss"))
    o = {r.fact: r.outcome for r in reconcile(ds, fetch=lambda c, a: [CASHFLOW])}
    assert o["capex@FY2025"] == "matched"
    assert o["net_income@FY2025"] == "mismatch"  # a sign flip on anything else is a real error
