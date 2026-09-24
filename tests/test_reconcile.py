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


def test_six_month_ytd_fact_matches_only_the_six_month_column():
    st = Statement(title="INCOME STATEMENTS - USD ($) $ in Millions", usd_scale=1e6,
                   columns=[Column(3, date(2026, 6, 30)), Column(6, date(2026, 6, 30))],
                   rows=[R("Revenues", "us-gaap:Revenues", [120_000, 229_690])])
    src = Source(accession="Q", form="10-Q", filed=date(2026, 7, 23), url="u", locator="us-gaap:Revenues",
                 snapshot_id="s", retrieved_at="t")
    f = Fact(company="1", metric="revenue", value=229_690e6, unit="USD", period_start=date(2026, 1, 1),
             period_end=date(2026, 6, 30), fiscal_label="YTD2026-06-30", status=FactStatus.REPORTED, sources=[src])
    ds = dataset(f)
    assert reconcile(ds, fetch=lambda c, a: [st])[0].outcome == "matched"
    g = f.model_copy(update={"value": 120_000e6})  # the 3-month value must not verify a 6-month fact
    assert reconcile(dataset(g), fetch=lambda c, a: [st])[0].outcome == "mismatch"


def test_a_mismatched_fact_is_withheld_from_every_calculation():
    from fre.fundamentals import compute
    ds = dataset(fact("revenue", 400_000_000_000.0, "us-gaap:Revenues"))
    reconcile(ds, fetch=fetch)
    f = ds.fact("revenue", "FY2025")
    assert f.value is None and f.status == FactStatus.CONFLICTING
    assert sorted(f.candidates) == [400_000_000_000.0, 402_836e6]
    compute(ds)
    assert ds.value("operating_margin", "FY2025") is None


TEXT = ("Short-Term Debt We have a commercial paper program of up to $ 25.0 billion. We had no commercial paper "
        "outstanding as of December 31, 2025. Our short-term debt balance also includes the current portion of "
        "certain long-term debt of $ 1,996 million. " + "Unrelated discussion of results. " * 12 + "Revenues were 402,836 million.")


def text_fact(metric, value, instant=True):
    src = Source(accession="A", form="10-K", filed=date(2026, 2, 5), url="https://x/doc.htm", locator="us-gaap:X",
                 snapshot_id="s", retrieved_at="t")
    return Fact(company="1", metric=metric, value=value, unit="USD", period_start=None if instant else date(2025, 1, 1),
                period_end=date(2025, 12, 31), fiscal_label="FY2025", status=FactStatus.REPORTED, sources=[src])


def run_text(*facts):
    return {r.fact: r for r in reconcile(dataset(*facts), fetch=lambda c, a: [], fetch_notes=lambda c, a: [],
                                         fetch_text=lambda url: TEXT)}


def test_value_printed_near_its_keyword_matches_in_text():
    r = run_text(text_fact("debt_lt_current", 1_996e6))["debt_lt_current@FY2025"]
    assert r.outcome == "matched-in-text" and "1,996" in r.line


def test_zero_needs_an_explicit_none_statement():
    assert run_text(text_fact("commercial_paper", 0.0))["commercial_paper@FY2025"].outcome == "matched-in-text"


def test_number_far_from_its_keyword_does_not_match():
    # 402,836 is in the text, but nowhere near "commercial paper"
    assert run_text(text_fact("commercial_paper", 402_836e6))["commercial_paper@FY2025"].outcome == "from-notes"


def test_billion_phrasing_verifies_a_round_value():
    t = "We had $2.3 billion of commercial paper outstanding as of December 31, 2024."
    r = reconcile(dataset(text_fact("commercial_paper", 2_300e6)), fetch=lambda c, a: [], fetch_notes=lambda c, a: [],
                  fetch_text=lambda url: t)[0]
    assert r.outcome == "matched-in-text"


def test_negated_match_needs_a_tag_that_is_presented_negated():
    cf = Statement(title="CONSOLIDATED STATEMENTS OF CASH FLOWS", usd_scale=1e6, columns=[Column(12, date(2025, 12, 31))],
                   rows=[R("Net cash provided by operating activities", "us-gaap:NetCashProvidedByUsedInOperatingActivities", [-164_713])])
    ds = dataset(fact("cfo", 164_713e6, "us-gaap:NetCashProvidedByUsedInOperatingActivities"))
    assert reconcile(ds, fetch=lambda c, a: [cf])[0].outcome == "mismatch"


def test_verified_fact_records_the_filing_presentation_scale():
    ds = dataset(fact("revenue", 402_836e6, "us-gaap:Revenues"))
    reconcile(ds, fetch=fetch)
    assert ds.fact("revenue", "FY2025").scale == 1_000_000
