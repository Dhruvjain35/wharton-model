"""EPS bridge (PRD A3): EPS factor ~= net income factor / diluted share factor."""

from datetime import date
import math

import pytest

from fre.eps_bridge import bridge
from fre.models import Company, Fact, FactStatus
from fre.normalize import Dataset


def mk(values, years=(2024, 2025)):
    ds = Dataset(company=Company(cik="1", legal_name="T", tickers=[], fiscal_year_end="1231"),
                 fiscal_years=list(years), snapshot_ids={})
    for metric, by_year in values.items():
        for y in years:
            v = by_year.get(y)
            ds.add(Fact(company="1", metric=metric, value=v, unit="USD", period_start=date(y, 1, 1),
                        period_end=date(y, 12, 31), fiscal_label=f"FY{y}",
                        status=FactStatus.MISSING if v is None else FactStatus.REPORTED))
    return ds


# Alphabet FY2024 -> FY2025 as filed (net income, diluted wavg shares, diluted EPS, buybacks, SBC)
GOOGL = {
    "net_income": {2024: 100_118e6, 2025: 132_170e6},
    "net_income_to_common": {2024: 100_118e6, 2025: 132_170e6},
    "shares_diluted": {2024: 12_447e6, 2025: 12_230e6},
    "eps_diluted": {2024: 8.04, 2025: 10.81},
    "buybacks": {2024: 62_222e6, 2025: 45_709e6},
    "sbc": {2024: 22_785e6, 2025: 24_953e6},
}


def test_identity_components_hand_calculated():
    row = bridge(mk(GOOGL))[0]
    ni_f = 132_170 / 100_118          # 1.32014
    sh_f = 12_230 / 12_447            # 0.98257
    assert row["net_income_factor"] == pytest.approx(ni_f)
    assert row["share_factor"] == pytest.approx(sh_f)
    assert row["implied_eps_factor"] == pytest.approx(ni_f / sh_f)
    assert row["reported_eps_factor"] == pytest.approx(10.81 / 8.04)
    assert row["method"] == "approximation"  # EPS numerator/share basis not reconciled to the class level


def test_log_decomposition_sums_to_reported_eps_growth():
    row = bridge(mk(GOOGL))[0]
    total = row["from_earnings_log"] + row["from_share_count_log"] + row["residual_log"]
    assert total == pytest.approx(math.log(10.81 / 8.04), abs=1e-12)
    # share count fell, so it contributed positively; earnings contributed most
    assert row["from_share_count_log"] > 0
    assert row["from_earnings_log"] > 5 * row["from_share_count_log"]


def test_recomputed_eps_is_compared_with_reported_eps():
    row = bridge(mk(GOOGL))[0]
    assert row["recomputed_eps"] == pytest.approx(132_170 / 12_230)   # 10.807
    assert abs(row["eps_recompute_gap"]) < 0.01
    assert row["eps_recompute_flag"] is None


def test_buyback_context_reports_spend_against_sbc_not_as_free_growth():
    row = bridge(mk(GOOGL))[0]
    assert row["buybacks"] == 45_709e6
    assert row["sbc"] == 24_953e6
    assert row["net_diluted_shares_retired"] == pytest.approx(217e6)
    assert "not free" in row["buyback_note"]


def test_missing_share_count_blocks_the_bridge_with_reason():
    vals = dict(GOOGL, shares_diluted={2024: None, 2025: 12_230e6})
    row = bridge(mk(vals))[0]
    assert row["status"] == "blocked"
    assert "shares_diluted@FY2024" in row["reason"]


def test_loss_year_is_not_bridged_with_factors():
    vals = dict(GOOGL, net_income_to_common={2024: -5e9, 2025: 1e9}, net_income={2024: -5e9, 2025: 1e9},
                eps_diluted={2024: -0.40, 2025: 0.08})
    row = bridge(mk(vals))[0]
    assert row["status"] == "not-applicable"
    assert "positive" in row["reason"]


def test_large_recompute_gap_is_flagged():
    vals = dict(GOOGL, eps_diluted={2024: 8.04, 2025: 11.50})
    row = bridge(mk(vals))[0]
    assert row["eps_recompute_flag"] is not None
