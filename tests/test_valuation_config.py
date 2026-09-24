"""Assumption hygiene: every judgment carries range, rationale, owner, date and status."""

from fre.valuation.run import validate

GOOD = {"value": 0.03, "low": 0.02, "high": 0.04, "units": "g", "rationale": "r", "owner": "o",
        "as_of": "2026-09-24", "status": "proposed"}


def cfg(**assumptions):
    return {"forecast_years": 2, "assumptions": assumptions}


def test_complete_assumption_passes():
    assert validate(cfg(terminal_growth=GOOD)) == []


def test_missing_rationale_or_owner_is_a_problem():
    bad = {k: v for k, v in GOOD.items() if k not in ("rationale", "owner")}
    problems = validate(cfg(terminal_growth=bad))
    assert any("rationale" in p for p in problems) and any("owner" in p for p in problems)


def test_value_outside_its_range_is_a_problem():
    assert validate(cfg(terminal_growth=GOOD | {"value": 0.05}))


def test_yaml_exponent_text_is_caught_not_crashing():
    assert any("numbers" in p for p in validate(cfg(operating_cash=GOOD | {"value": 0.0, "low": 0.0, "high": "20.0e9"})))


def test_per_year_assumptions_need_one_value_per_forecast_year():
    per_year = GOOD | {"value": [0.1], "low": [0.0], "high": [0.2]}
    assert any("yearly" in p for p in validate(cfg(growth=per_year)))
