"""Accounting review ledger (PRD A4): proposals are cheap, approval is human, originals survive."""

from datetime import date

import pytest

from fre.ledger import LedgerError, apply, build, evaluate
from fre.models import Company, Fact, FactStatus
from fre.normalize import Dataset


def mk():
    ds = Dataset(company=Company(cik="1", legal_name="T", tickers=[], fiscal_year_end="1231"),
                 fiscal_years=[2025], snapshot_ids={})
    for metric, v, unit in [("net_income", 132_170e6, "USD"), ("net_income_to_common", 132_170e6, "USD"),
                            ("equity_securities_gain", 24_080e6, "USD"), ("shares_diluted", 12_230e6, "shares"),
                            ("shares_basic", 12_116e6, "shares"), ("eps_diluted", 10.81, "USD/shares"),
                            ("eps_basic", 10.91, "USD/shares"), ("operating_income", 129_039e6, "USD")]:
        ds.add(Fact(company="1", metric=metric, value=v, unit=unit, period_start=date(2025, 1, 1),
                    period_end=date(2025, 12, 31), fiscal_label="FY2025", status=FactStatus.REPORTED))
    return ds


def entry(**kw):
    base = dict(id="A1", metric="net_income", fiscal_label="FY2025", category="investment-gains",
                delta_formula="-equity_securities_gain * (1 - 0.21)", rationale="r", evidence="e",
                author="Claude (AI-proposed)", status="proposed", reviewer=None)
    return base | kw


def test_delta_formula_is_evaluated_from_verified_facts():
    adj = build(mk(), [entry()])[0]
    assert adj.original == 132_170e6
    assert adj.delta == pytest.approx(-24_080e6 * 0.79)
    assert adj.resulting == pytest.approx(132_170e6 - 24_080e6 * 0.79)


@pytest.mark.parametrize("expr", ["__import__('os').system('x')", "open('f')", "net_income.real", "[1][0]", "2**100"])
def test_formula_evaluator_rejects_anything_but_arithmetic_on_fact_names(expr):
    with pytest.raises(LedgerError):
        evaluate(expr, {"net_income": 1.0})


def test_formula_referencing_a_missing_fact_is_rejected():
    with pytest.raises(LedgerError, match="missing"):
        build(mk(), [entry(delta_formula="-restructuring")])


def test_ai_cannot_approve_and_author_cannot_self_approve():
    with pytest.raises(LedgerError, match="reviewer"):
        build(mk(), [entry(status="approved", reviewer=None)])
    with pytest.raises(LedgerError, match="reviewer"):
        build(mk(), [entry(status="approved", author="Priya", reviewer="Priya")])
    with pytest.raises(LedgerError, match="reviewer"):
        build(mk(), [entry(status="approved", author="Priya", reviewer="Claude")])
    assert build(mk(), [entry(status="approved", author="Claude (AI-proposed)", reviewer="Priya")])[0].status == "approved"


def test_only_approved_adjustments_apply_and_switching_off_restores_reported():
    ds = mk()
    proposed = build(ds, [entry()])
    assert apply(ds, proposed).value("net_income", "FY2025") == 132_170e6
    approved = build(ds, [entry(status="approved", reviewer="Priya")])
    adj = apply(ds, approved)
    assert adj.value("net_income", "FY2025") == pytest.approx(132_170e6 - 24_080e6 * 0.79)
    assert apply(ds, approved, enabled=False).value("net_income", "FY2025") == 132_170e6
    # the reported dataset is never mutated
    assert ds.value("net_income", "FY2025") == 132_170e6


def test_net_income_adjustment_flows_to_eps_on_the_same_share_basis():
    ds = mk()
    adj = apply(ds, build(ds, [entry(status="approved", reviewer="Priya")]))
    f = adj.fact("eps_diluted", "FY2025")
    assert f.status == FactStatus.ANALYST_ADJUSTED
    assert f.value == pytest.approx(10.81 - 24_080e6 * 0.79 / 12_230e6)
    assert adj.fact("eps_basic", "FY2025").value == pytest.approx(10.91 - 24_080e6 * 0.79 / 12_116e6)
    assert any("A1" in n for n in f.notes)


def test_operating_adjustment_does_not_silently_change_net_income():
    ds = mk()
    adj = apply(ds, build(ds, [entry(id="L1", metric="operating_income", category="legal",
                                     delta_formula="3500e6 + 1400e6", status="approved", reviewer="Priya")]))
    assert adj.value("operating_income", "FY2025") == 129_039e6 + 4_900e6
    assert adj.value("net_income", "FY2025") == 132_170e6


def test_ai_name_check_matches_words_not_prefixes():
    assert build(mk(), [entry(status="approved", reviewer="Aisha")])[0].reviewer == "Aisha"
    with pytest.raises(LedgerError):
        build(mk(), [entry(status="approved", author="Priya", reviewer="claude-code")])


# ---- constants from filing prose must be quoted verbatim and contain their number

from fre.ledger import verify_quotes

TEXT = ("In January 2023, we announced a reduction of our workforce, and as a result we recorded employee "
        "severance and related charges of $2.1 billion for the year ended December 31, 2023. "
        "Office space charges ... were $796 million, a decrease")


def const_entry(value, quote):
    return entry(id="R1", metric="operating_income", category="restructuring", delta_formula="severance",
                 constants={"severance": {"value": value, "quote": quote, "snapshot_id": "S"}})


def test_constant_with_verbatim_quote_containing_its_number_verifies():
    e = const_entry(2.1e9, "employee severance and related charges of $2.1 billion")
    assert verify_quotes([e], lambda sid: TEXT) == []
    assert build(mk(), [e])[0].delta == 2.1e9


def test_quote_not_in_filing_is_rejected():
    e = const_entry(2.1e9, "severance charges of $2.1 billion")  # paraphrase, not verbatim
    assert verify_quotes([e], lambda sid: TEXT)


def test_number_not_in_its_quote_is_rejected():
    e = const_entry(2.4e9, "employee severance and related charges of $2.1 billion")
    problems = verify_quotes([e], lambda sid: TEXT)
    assert problems and "2.4" in problems[0]


def test_million_figures_verify_too():
    e = const_entry(796e6, "were $796 million")
    assert verify_quotes([e], lambda sid: TEXT) == []


def test_assumptions_resolve_by_name_and_need_a_rationale():
    e = entry(assumptions={"tax_rate": {"value": 0.21, "rationale": "US federal statutory rate"}},
              delta_formula="-equity_securities_gain * (1 - tax_rate)")
    assert build(mk(), [e])[0].delta == pytest.approx(-24_080e6 * 0.79)
    with pytest.raises(LedgerError, match="rationale"):
        build(mk(), [entry(assumptions={"tax_rate": {"value": 0.21}},
                           delta_formula="-equity_securities_gain * (1 - tax_rate)")])


def test_eps_cannot_keep_its_reported_value_when_net_income_moved_but_shares_are_missing():
    ds = mk()
    key = "shares_diluted@FY2025"
    ds.facts[key] = ds.facts[key].model_copy(update={"value": None, "status": FactStatus.MISSING})
    adj = apply(ds, build(ds, [entry(status="approved", reviewer="Priya")]))
    f = adj.fact("eps_diluted", "FY2025")
    assert f.value is None and f.status == FactStatus.MISSING
    assert any("shares_diluted" in n for n in f.notes)
