"""The reconciliation gate must block a normalized value that disagrees with its statement line."""

from datetime import date

from fre.models import Company, Fact, FactStatus, Source
from fre.normalize import Dataset
from fre.reconcile import reconcile
from fre.statements import Column, Row, Statement


def R(label, tag, raw):
    return Row(label, tag, raw)


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


INCOME = Statement(title="INCOME STATEMENTS - USD ($) $ in Millions", usd_scale=1e6,
                   columns=[Column(12, date(2025, 12, 31)), Column(12, date(2024, 12, 31))], rows=[
    R("Revenues", "us-gaap:Revenues", [402_836, 350_018]),
    R("Diluted", "us-gaap:EarningsPerShareDiluted", [10.81, 8.04]),
    R("Product", "us-gaap:Dup", [1, 0]),
    R("Service", "us-gaap:Dup", [2, 0]),
    R("Total", "us-gaap:Dup", [3, 0]),
])
BALANCE = Statement(title="BALANCE SHEETS", usd_scale=1e6, columns=[Column(None, date(2025, 12, 31))], rows=[
    R("Long-term debt", "us-gaap:LongTermDebtNoncurrent", [46_547])])


def fetch(cik, accn):
    return [INCOME, BALANCE]


def outcomes(ds):
    return {r.fact: r.outcome for r in reconcile(ds, fetch=fetch)}


def test_value_within_presentation_rounding_matches_and_records_the_line():
    ds = dataset(fact("revenue", 402_836_000_000.0, "us-gaap:Revenues"))
    rec = reconcile(ds, fetch=fetch)[0]
    assert rec.outcome == "matched" and rec.line == "Revenues" and rec.statement.startswith("INCOME")


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


def test_dimensional_breakdown_lines_resolve_to_the_total_line():
    rec = reconcile(dataset(fact("x", 3e6, "us-gaap:Dup")), fetch=fetch)[0]
    assert rec.outcome == "matched" and rec.line == "Total"


def test_tag_on_several_lines_none_equal_blocks():
    ds = dataset(fact("x", 4e6, "us-gaap:Dup"))
    assert outcomes(ds)["x@FY2025"] == "ambiguous"
    assert any(i.severity == "block" for i in ds.review)


CASHFLOW = Statement(title="CONSOLIDATED STATEMENTS OF CASH FLOWS - USD ($) $ in Millions", usd_scale=1e6,
                     columns=[Column(12, date(2025, 12, 31))], rows=[
    R("Purchases of property and equipment", "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", [-91_447]),
    R("Fair value adjustments", "us-gaap:EquitySecuritiesFvNiGainLoss", [232]),
])
INCOME_NEG = Statement(title="CONSOLIDATED STATEMENTS OF INCOME - USD ($) $ in Millions", usd_scale=1e6,
                       columns=[Column(12, date(2025, 12, 31))], rows=[R("Net income", "us-gaap:NetIncomeLoss", [-5])])


def test_negated_presentation_is_accepted_only_on_the_cash_flow_statement_and_labelled():
    ds = dataset(fact("capex", 91_447e6, "us-gaap:PaymentsToAcquirePropertyPlantAndEquipment"),
                 fact("gain", -232e6, "us-gaap:EquitySecuritiesFvNiGainLoss"),
                 fact("net_income", 5e6, "us-gaap:NetIncomeLoss"))
    o = {r.fact: r.outcome for r in reconcile(ds, fetch=lambda c, a: [CASHFLOW, INCOME_NEG])}
    assert o["capex@FY2025"] == "matched-negated"
    assert o["gain@FY2025"] == "matched-negated"
    assert o["net_income@FY2025"] == "mismatch"  # a sign flip on the income statement is a real error


NOTE = Statement(title="Debt - Details - USD ($) $ in Millions", usd_scale=1e6,
                 columns=[Column(None, date(2025, 12, 31)), Column(None, date(2024, 12, 31))], rows=[
    R("Short-term portion of long-term debt", "us-gaap:LongTermDebtCurrent", [1_996, 999])])


def test_note_detail_tables_verify_facts_that_are_not_on_the_face_statements():
    ds = dataset(fact("debt_lt_current", 1_996e6, "us-gaap:LongTermDebtCurrent", instant=True),
                 fact("debt_wrong_period", 999e6 + 0, "us-gaap:LongTermDebtCurrent", instant=True))
    recs = {r.fact: r for r in reconcile(ds, fetch=fetch, fetch_notes=lambda c, a: [NOTE])}
    assert recs["debt_lt_current@FY2025"].outcome == "matched-in-notes"
    assert recs["debt_lt_current@FY2025"].line == "Short-term portion of long-term debt"
    # the FY2024 column's value does not verify a FY2025 fact
    assert recs["debt_wrong_period@FY2025"].outcome == "from-notes"


def test_falls_back_to_the_fiscal_years_own_10k_statement():
    ds = dataset(fact("debt", 46_547e6, "us-gaap:LongTermDebtNoncurrent", instant=True))
    ds.annual_filings = {"FY2025": "OWN"}
    got = reconcile(ds, fetch=lambda c, a: [BALANCE] if a == "OWN" else [])[0]
    assert got.outcome == "matched"
