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


# ---- sourced numbers must equal the number printed in their own quote

from fre.valuation.run import figure_value, check_sourced_values


def test_figure_text_parses_to_numbers():
    assert figure_value("4.80 %") == 0.048
    assert figure_value("6.25 %") == 0.0625
    assert figure_value("385 million") == 385e6
    assert figure_value("$ 50 per depositary share") == 50.0
    assert figure_value("12,230") == 12230.0


def test_a_value_that_disagrees_with_its_quoted_figure_is_a_problem():
    cfg = {"sourced": {"kd": {"value": 0.058, "figure": "4.80 %"}}, "class_shares": {}}
    assert any("kd" in p for p in check_sourced_values(cfg))
    cfg["sourced"]["kd"]["value"] = 0.048
    assert check_sourced_values(cfg) == []


def test_class_shares_must_appear_in_the_class_split_quote():
    cfg = {"sourced": {"class_split": {"value": 12230, "figure": "12,230",
                                        "quote": "12,230 (Class A 5,868 , Class B 835 , Class C 5,527 ) shares"}},
           "class_shares": {"class_a": {"shares": 5.868e9}, "class_b": {"shares": 0.835e9}, "class_c": {"shares": 5.527e9}}}
    assert check_sourced_values(cfg) == []
    cfg["class_shares"]["class_c"]["shares"] = 5.572e9  # transposed digits
    assert any("class_c" in p for p in check_sourced_values(cfg))
    cfg["class_shares"]["class_c"]["shares"] = 5.527e9
    cfg["class_shares"]["class_b"]["shares"] = 0.935e9   # sum no longer 12,230
    assert any("class_b" in p or "sum" in p for p in check_sourced_values(cfg))
