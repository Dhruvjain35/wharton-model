"""Dossier sentences must say only what the numbers support."""

from types import SimpleNamespace

from fre.dossier import _eps_sentences, _what_if_sentences, definitions, money
from fre.models import Adjustment


def bridge_row(ni, sh, eps):
    import math
    return {"period": "FY2022->FY2023", "status": "ok", "net_income_factor": ni, "share_factor": sh,
            "reported_eps_factor": eps, "from_earnings_log": math.log(ni), "from_share_count_log": -math.log(sh),
            "residual_log": math.log(eps) - math.log(ni / sh), "buybacks": 1e9, "sbc": 1e9}


def test_share_attribution_is_not_stated_when_earnings_fell():
    # MSFT FY2022->FY2023: net income -0.5%, shares -0.9%, EPS +0.3% -> "explains 291.9%" is meaningless
    s = _eps_sentences(SimpleNamespace(eps_bridge=[bridge_row(0.995, 0.991, 1.003)]))[0]
    assert "explains" not in s and "only because" in s


def test_share_attribution_is_stated_when_both_parts_are_positive():
    s = _eps_sentences(SimpleNamespace(eps_bridge=[bridge_row(1.32, 0.9826, 1.3445)]))[0]
    assert "explains" in s


def adj(id_, metric, label):
    return Adjustment(id=id_, metric=metric, fiscal_label=label, original=1.0, delta=-0.5, category="c",
                      rationale="r", evidence="e", author="a", status="proposed")


def test_what_if_sentence_names_only_entries_that_move_eps_in_either_year():
    ds_r = SimpleNamespace(labels=["FY2024", "FY2025"], value=lambda m, l: {"eps_diluted": 10.81, "eps_growth": 0.345}[m])
    ds_w = SimpleNamespace(labels=["FY2024", "FY2025"], value=lambda m, l: {"eps_diluted": 9.25, "eps_growth": 0.186}[m])
    run = SimpleNamespace(reported=ds_r, what_if=ds_w, adjustments=[
        adj("EQ25", "net_income", "FY2025"), adj("LEGAL25", "operating_income", "FY2025"), adj("EQ24", "net_income", "FY2024")])
    s = _what_if_sentences(run)[0]
    assert "EQ25" in s and "EQ24" in s and "LEGAL25" not in s


def test_definitions_list_every_formula_a_metric_used_with_its_years():
    facts = {f"total_debt@FY{y}": SimpleNamespace(metric="total_debt", formula="a + b" if y < 2023 else "c + d",
                                                  status=SimpleNamespace(value="derived"), fiscal_label=f"FY{y}")
             for y in (2021, 2022, 2023)}
    rows = definitions(SimpleNamespace(facts=facts))
    assert any("a + b" in r and "FY2021, FY2022" in r for r in rows)
    assert any("c + d" in r and "FY2023" in r for r in rows)


def test_money_rounds_half_up():
    assert money(19.25e9) == "$19.3bn"
